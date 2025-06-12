import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging
import os
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from functools import wraps

# --------------------------
# Configuration
# --------------------------
# Environment variables (fallback to defaults)
PLC_RACK = int(os.getenv("PLC_RACK", 0))  # Default for S7-1200/1500
PLC_SLOT = int(os.getenv("PLC_SLOT", 1))  # Default for S7-1200/1500
CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", 2000))  # ms
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 10))  # Matches S7-1200 connection limit
API_KEYS = os.getenv("API_KEYS", "secret_key").split(",")  # Comma-separated keys

# --------------------------
# Logging Setup
# --------------------------
logger = logging.getLogger("Siemens-PROFINET-API")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Log to file and console
file_handler = logging.FileHandler('plc_api.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# --------------------------
# Flask & Thread Safety
# --------------------------
app = Flask(__name__)
CORS(app)  # Configure in production!
plc_lock = Lock()

# --------------------------
# Data Models (Pydantic)
# --------------------------
class PLCWriteRequest(BaseModel):
    db: int
    start: int
    data: List[int]  # Byte array

class PLCReadRequest(BaseModel):
    db: int
    start: int
    size: int

class TagRequest(BaseModel):
    name: str
    db: int
    offset: int
    dtype: str  # 'BOOL', 'REAL', 'INT', etc.

# --------------------------
# Connection Pooling
# --------------------------
class PLCConnectionPool:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._pool = {}
        return cls._instance
    
    def get_connection(self, ip: str) -> Optional[snap7.client.Client]:
        with self._lock:
            if ip not in self._pool or not self._pool[ip].get_connected():
                self._pool[ip] = self._connect(ip)
            return self._pool[ip]
    
    def _connect(self, ip: str) -> Optional[snap7.client.Client]:
        plc = snap7.client.Client()
        plc.set_connection_params(ip, PLC_RACK, PLC_SLOT, CONNECTION_TIMEOUT)
        try:
            plc.connect()
            if plc.get_connected():
                logger.info(f"Connected to PLC at {ip}")
                return plc
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Connection failed: {e}")
        return None
    
    def release_connection(self, ip: str):
        with self._lock:
            if ip in self._pool:
                self._pool[ip].disconnect()
                del self._pool[ip]

plc_pool = PLCConnectionPool()

# --------------------------
# Auth Decorator
# --------------------------
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key not in API_KEYS:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# --------------------------
# Core PLC Functions
# --------------------------
def read_bytes(ip: str, db: int, start: int, size: int) -> Optional[list]:
    """Thread-safe byte read with connection pooling"""
    plc = plc_pool.get_connection(ip)
    if not plc:
        return None
    try:
        return list(plc.db_read(db, start, size))
    except snap7.exceptions.Snap7Exception as e:
        logger.error(f"Read failed: {e}")
        plc_pool.release_connection(ip)  # Force reconnect on error
        return None

def write_bytes(ip: str, db: int, start: int, data: list) -> bool:
    """Thread-safe byte write with connection pooling"""
    plc = plc_pool.get_connection(ip)
    if not plc:
        return False
    try:
        plc.db_write(db, start, bytearray(data))
        return True
    except snap7.exceptions.Snap7Exception as e:
        logger.error(f"Write failed: {e}")
        plc_pool.release_connection(ip)
        return False

# --------------------------
# Data Type Helpers
# --------------------------
def read_real(ip: str, db: int, offset: int) -> float:
    data = read_bytes(ip, db, offset, 4)
    return struct.unpack('>f', bytes(data))[0] if data else 0.0

def write_real(ip: str, db: int, offset: int, value: float) -> bool:
    return write_bytes(ip, db, offset, list(struct.pack('>f', value)))

# --------------------------
# API Routes
# --------------------------
@app.route('/write', methods=['POST'])
@cross_origin()
@require_api_key
def write_to_plc():
    """Write data to PLC DB blocks (batch support)"""
    try:
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"error": "Missing 'ip' parameter"}), 400
        
        requests = [PLCWriteRequest(**item) for item in request.json]
        results = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(
                    write_bytes,
                    plc_ip,
                    req.db,
                    req.start,
                    req.data
                ) for req in requests
            ]
            results = [future.result() for future in as_completed(futures)]
        
        if not all(results):
            return jsonify({"error": "Partial write failure"}), 207
        
        return jsonify({"message": "Write successful"}), 200
    
    except ValidationError as e:
        return jsonify({"error": f"Invalid payload: {e}"}), 400
    except Exception as e:
        logger.error(f"Write error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/read', methods=['POST'])
@cross_origin()
#@require_api_key
def read_from_plc():
    """Read data from PLC DB blocks (batch support)"""
    try:
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"error": "Missing 'ip' parameter"}), 400
        
        requests = [PLCReadRequest(**item) for item in request.json]
        results = {}
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    read_bytes,
                    plc_ip,
                    req.db,
                    req.start,
                    req.size
                ): req for req in requests
            }
            for future in as_completed(futures):
                req = futures[future]
                data = future.result()
                key = f"DB{req.db}.{req.start}"
                results[key] = data if data else None
        
        return jsonify({"data": results}), 200
    
    except ValidationError as e:
        return jsonify({"error": f"Invalid payload: {e}"}), 400
    except Exception as e:
        logger.error(f"Read error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/tags', methods=['GET'])
@cross_origin()
# @require_api_key
def list_tags():
    """Get predefined tag mappings (customize per project)"""
    try:
        # Example: Replace with your actual DB/tag mapping
        tags = [
            {"name": "Temperature", "db": 1, "offset": 0, "dtype": "REAL"},
            {"name": "Pressure", "db": 1, "offset": 4, "dtype": "REAL"}
        ]
        return jsonify({"tags": tags}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Endpoint for load balancers/health checks"""
    return jsonify({"status": "healthy"}), 200

# --------------------------
# Main
# --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, threaded=True)