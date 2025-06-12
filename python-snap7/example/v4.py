import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging
import os

# --------------------------
# Configuration
# --------------------------
PLC_RACK = int(os.getenv("PLC_RACK", 0))
PLC_SLOT = int(os.getenv("PLC_SLOT", 1))
CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", 2000))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 10))

# --------------------------
# Logging Setup
# --------------------------
logger = logging.getLogger("Siemens-PROFINET-API")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
CORS(app)
plc_lock = Lock()

# --------------------------
# Tag Configuration (Modify with your actual tags)
# --------------------------
# Format: {'tag_name': {'db': DB_NUMBER, 'offset': BYTE_OFFSET, 'dtype': DATA_TYPE}}
TAG_CONFIG = {
    'Temperature': {'db': 1, 'offset': 0, 'dtype': 'REAL'},
    'Pressure': {'db': 1, 'offset': 4, 'dtype': 'REAL'},
    'Speed': {'db': 2, 'offset': 0, 'dtype': 'INT'},
    'Running': {'db': 2, 'offset': 2, 'dtype': 'BOOL'}
}

# --------------------------
# PLC Connection Management
# --------------------------
def get_plc_connection(ip):
    """Create and return a new PLC connection"""
    plc = snap7.client.Client()
    plc.set_connection_params(ip, PLC_RACK, PLC_SLOT, CONNECTION_TIMEOUT)
    try:
        plc.connect()
        if plc.get_connected():
            return plc
    except Exception as e:
        logger.error(f"Connection failed to {ip}: {e}")
    return None

def is_plc_connected(ip):
    """Check if PLC is reachable"""
    plc = get_plc_connection(ip)
    if plc:
        plc.disconnect()
        return True
    return False

# --------------------------
# Data Type Helpers
# --------------------------
def read_tag_value(plc, db, offset, dtype):
    """Read a value from PLC based on data type"""
    try:
        if dtype == 'REAL':
            data = plc.db_read(db, offset, 4)
            return struct.unpack('>f', bytes(data))[0]
        elif dtype == 'INT':
            data = plc.db_read(db, offset, 2)
            return struct.unpack('>h', bytes(data))[0]
        elif dtype == 'BOOL':
            byte_value = plc.db_read(db, offset, 1)[0]
            bit = offset % 8
            return bool(byte_value & (1 << bit))
        else:
            logger.error(f"Unsupported data type: {dtype}")
            return None
    except Exception as e:
        logger.error(f"Error reading tag: {e}")
        return None

def write_tag_value(plc, db, offset, dtype, value):
    """Write a value to PLC based on data type"""
    try:
        if dtype == 'REAL':
            data = struct.pack('>f', float(value))
            plc.db_write(db, offset, data)
            return True
        elif dtype == 'INT':
            data = struct.pack('>h', int(value))
            plc.db_write(db, offset, data)
            return True
        elif dtype == 'BOOL':
            byte_value = plc.db_read(db, offset, 1)[0]
            bit = offset % 8
            if value:
                byte_value |= (1 << bit)
            else:
                byte_value &= ~(1 << bit)
            plc.db_write(db, offset, bytes([byte_value]))
            return True
        else:
            logger.error(f"Unsupported data type: {dtype}")
            return False
    except Exception as e:
        logger.error(f"Error writing tag: {e}")
        return False

# --------------------------
# Middleware
# --------------------------
@app.before_request
def check_plc_connection():
    """Middleware to validate PLC connection before route execution"""
    if request.endpoint in ['insert_data_to_plc', 'read_data_tags_from_plc', 
                          'read_data_from_plc', 'get_tag_values']:
        ip_address = request.args.get('ip')
        if not ip_address:
            return jsonify({"message": "IP address parameter 'ip' is missing.", "error": "No IP provided"}), 400
        if not is_plc_connected(ip_address):
            return jsonify({"message": f"PLC with IP {ip_address} is not connected or not active.", "error": "PLC not connected"}), 400

# --------------------------
# API Routes
# --------------------------
@app.route('/insertDataToPlc', methods=['POST'])
@cross_origin()
def insert_data_to_plc():
    """Write multiple tag values to PLC"""
    try:
        plc_ip = request.args.get('ip')
        data_list = request.json
        
        if not isinstance(data_list, list):
            return jsonify({"message": "Payload must be a list of tag-value dictionaries.", "error": "Invalid format"}), 400

        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "Failed to connect to PLC", "error": "Connection failed"}), 500

        results = {}
        for item in data_list:
            tag_name = item.get('tag')
            value = item.get('value')
            
            if tag_name not in TAG_CONFIG:
                results[tag_name] = {"status": "Failed", "error": "Tag not defined"}
                continue
            
            tag_config = TAG_CONFIG[tag_name]
            success = write_tag_value(plc, tag_config['db'], tag_config['offset'], 
                                    tag_config['dtype'], value)
            
            results[tag_name] = {"status": "Success" if success else "Failed"}
        
        plc.disconnect()
        return jsonify({
            "message": "Data write operation completed",
            "data": results,
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error occurred while writing data to PLC.", "error": str(e)}), 500

@app.route('/readDataTagsFromPlc', methods=['GET'])
@cross_origin()
def read_data_tags_from_plc():
    """Get list of available tags from PLC"""
    try:
        return jsonify({"tags": list(TAG_CONFIG.keys())}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred while reading tags from PLC.", "error": str(e)}), 500

@app.route('/readDataFromPlcByTags', methods=['GET'])
@cross_origin()
def read_data_from_plc():
    """Read all predefined tags from PLC"""
    try:
        plc_ip = request.args.get('ip')
        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "Failed to connect to PLC", "error": "Connection failed"}), 500

        results = {}
        for tag_name, config in TAG_CONFIG.items():
            value = read_tag_value(plc, config['db'], config['offset'], config['dtype'])
            results[tag_name] = value
        
        plc.disconnect()
        return jsonify({
            "message": "Data read from PLC successfully",
            "data": results,
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error occurred while reading data from PLC.", "error": str(e)}), 500

@app.route('/getTagValues', methods=['POST'])
@cross_origin()
def get_tag_values():
    """Read specific tags provided in request"""
    try:
        plc_ip = request.args.get('ip')
        requested_tags = request.json.get('tags', [])
        
        if not requested_tags:
            return jsonify({"message": "No tags provided in request.", "error": "No tags specified"}), 400

        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "Failed to connect to PLC", "error": "Connection failed"}), 500

        results = {}
        for tag_name in requested_tags:
            if tag_name in TAG_CONFIG:
                config = TAG_CONFIG[tag_name]
                value = read_tag_value(plc, config['db'], config['offset'], config['dtype'])
                results[tag_name] = value
            else:
                results[tag_name] = None
        
        plc.disconnect()
        return jsonify({
            "message": "Data read from PLC successfully",
            "data": results,
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error occurred while reading data from PLC.", "error": str(e)}), 500

# --------------------------
# Main
# --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, threaded=True)