import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Siemens-PROFINET-API")

# Constants
PLC_RACK = 0  # Default for S7-1200/1500
PLC_SLOT = 1  # Default for S7-1200/1500
CONNECTION_TIMEOUT = 2000  # ms (PROFINET recommendation)
MAX_WORKERS = 10  # Matches S7-1200 connection limit

# Thread safety
plc_lock = Lock()

app = Flask(__name__)
CORS(app)

# --------------------------
# Core PROFINET Functions
# --------------------------
def connect_plc(ip: str) -> snap7.client.Client:
    """Establish PROFINET connection to Siemens PLC"""
    plc = snap7.client.Client()
    plc.set_connection_params(
        ip, 
        PLC_RACK, 
        PLC_SLOT, 
        connection_timeout=CONNECTION_TIMEOUT
    )
    try:
        plc.connect()
        if plc.get_connected():
            logger.info(f"Connected to Siemens PLC at {ip}")
            return plc
    except snap7.exceptions.Snap7Exception as e:
        logger.error(f"PROFINET connection failed: {e}")
    return None

def read_bytes(ip: str, db: int, start: int, size: int) -> list:
    """Thread-safe byte read from Siemens DB"""
    with plc_lock:
        plc = connect_plc(ip)
        if not plc:
            return None
        try:
            data = plc.db_read(db, start, size)
            return list(data)
        finally:
            plc.disconnect()

def write_bytes(ip: str, db: int, start: int, data: list) -> bool:
    """Thread-safe byte write to Siemens DB"""
    with plc_lock:
        plc = connect_plc(ip)
        if not plc:
            return False
        try:
            plc.db_write(db, start, bytearray(data))
            return True
        finally:
            plc.disconnect()

# --------------------------
# Data Type Helpers
# --------------------------
def read_real(ip: str, db: int, offset: int) -> float:
    """Read REAL (32-bit float) from Siemens DB"""
    data = read_bytes(ip, db, offset, 4)
    return struct.unpack('>f', bytes(data))[0] if data else 0.0

def write_real(ip: str, db: int, offset: int, value: float) -> bool:
    """Write REAL (32-bit float) to Siemens DB"""
    return write_bytes(ip, db, offset, list(struct.pack('>f', value)))

# --------------------------
# Flask Routes (Combined Functionality)
# --------------------------
@app.before_request
def check_plc_connection():
    """Middleware to validate PLC connection before route execution."""
    if request.endpoint in ['insert_data_to_plc', 'read_data_from_plc', 'get_tag_values']:
        ip_address = request.args.get('ip')
        if not ip_address:
            return jsonify({"message": "IP address parameter 'ip' is missing.", "error": "No IP provided"}), 400
        if not connect_plc(ip_address):
            return jsonify({"message": f"PLC with IP {ip_address} is not connected or not active.", "error": "PLC not connected"}), 400

@app.route('/insertDataToPlc', methods=['POST'])
@cross_origin()
def insert_data_to_plc():
    """Write multiple values to PLC DB blocks (Siemens version)"""
    try:
        plc_ip = request.args.get('ip')
        data_list = request.json
        
        if not isinstance(data_list, list):
            raise ValueError("Payload must be a list of DB-write dictionaries.")
        
        start_time = time.time()
        batch_size = 10
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for item in data_list:
                if all(k in item for k in ['db', 'start', 'data']):
                    futures.append(
                        executor.submit(
                            write_bytes,
                            plc_ip,
                            item['db'],
                            item['start'],
                            item['data']
                        )
                    )
            
            for future in as_completed(futures):
                if not future.result():
                    logger.error("Failed to complete one or more write operations")
        
        end_time = time.time()
        logger.info(f"Write operation completed in {end_time-start_time:.2f}s")
        
        return jsonify({
            "message": "Data written to PLC successfully",
            "error": None
        }), 200
        
    except Exception as e:
        logger.error(f"Write operation failed: {str(e)}")
        return jsonify({
            "message": "Error writing to PLC",
            "error": str(e)
        }), 500

@app.route('/readDataFromPlc', methods=['POST'])
@cross_origin()
def read_data_from_plc():
    """Batch read from multiple DB blocks (Siemens version)"""
    try:
        plc_ip = request.args.get('ip')
        tags_to_read = request.json.get('tags', [])
        
        if not tags_to_read:
            raise ValueError("No tags provided in the payload")
            
        start_time = time.time()
        results = {}
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    read_bytes,
                    plc_ip,
                    tag['db'],
                    tag['start'],
                    tag['size']
                ): tag for tag in tags_to_read
            }
            
            for future in as_completed(futures):
                tag = futures[future]
                data = future.result()
                if data:
                    key = f"DB{tag['db']}.{tag['start']}"
                    results[key] = data
        
        end_time = time.time()
        logger.info(f"Read operation completed in {end_time-start_time:.2f}s")
        
        return jsonify({
            "message": "Data read successfully",
            "data": results,
            "error": None
        }), 200
        
    except Exception as e:
        logger.error(f"Read operation failed: {str(e)}")
        return jsonify({
            "message": "Error reading from PLC",
            "error": str(e)
        }), 500

@app.route('/getTagValues', methods=['POST'])
@cross_origin()
def get_tag_values():
    """Alternative endpoint with same functionality as readDataFromPlc"""
    return read_data_from_plc()

@app.route('/readDataTagsFromPlc', methods=['GET'])
@cross_origin()
def read_data_tags_from_plc():
    """Get list of available DB blocks (Siemens version)"""
    try:
        # Note: Siemens doesn't have tags like Rockwell, so we return DB list
        # You would need to maintain your own DB mapping
        return jsonify({
            "tags": ["DB1", "DB2", "DB3"],  # Example - customize with your DBs
            "message": "Siemens PLCs use DB blocks rather than tags",
            "error": None
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Error getting DB list",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)