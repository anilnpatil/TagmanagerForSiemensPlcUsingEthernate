import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging
from typing import Dict, Any

# --------------------------
# Configuration
# --------------------------
PLC_IP = '192.168.0.1'  # Replace with your PLC IP
PLC_RACK = 0            # Default for S7-1200
PLC_SLOT = 1            # Default for S7-1200
PLC_PORT = 102          # Default S7 port

# Tag configuration - MODIFY THIS FOR YOUR PLC
# Format: {'tag_name': {'db': DB_NUMBER, 'offset': BYTE_OFFSET, 'dtype': DATA_TYPE}}
TAG_CONFIG = {
    'DB1_DBD0': {'db': 1, 'offset': 0, 'dtype': 'DINT'},
    'DB1_DBD4': {'db': 1, 'offset': 4, 'dtype': 'DINT'}
}

# --------------------------
# Setup
# --------------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("S7-1200-API")

# --------------------------
# PLC Communication Functions
# --------------------------
def get_plc_connection() -> snap7.client.Client:
    """Establish connection to S7-1200 PLC"""
    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT, PLC_PORT)
        if plc.get_connected():
            return plc
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
    return None

def read_plc_value(plc: snap7.client.Client, db: int, offset: float, dtype: str) -> Any:
    """Read value from PLC data block"""
    try:
        byte_offset = int(offset)
        if dtype == 'REAL':
            data = plc.db_read(db, byte_offset, 4)
            return struct.unpack('>f', bytes(data))[0]
        elif dtype == 'INT':
            data = plc.db_read(db, byte_offset, 2)
            return struct.unpack('>h', bytes(data))[0]
        elif dtype == 'BOOL':
            bit_offset = int((offset - byte_offset) * 10)
            data = plc.db_read(db, byte_offset, 1)
            return bool((data[0] >> bit_offset) & 1)
        else:
            logger.error(f"Unsupported data type: {dtype}")
            return None
    except Exception as e:
        logger.error(f"Read error: {str(e)}")
        return None

def write_plc_value(plc: snap7.client.Client, db: int, offset: float, dtype: str, value: Any) -> bool:
    """Write value to PLC data block"""
    try:
        byte_offset = int(offset)
        if dtype == 'REAL':
            data = struct.pack('>f', float(value))
            plc.db_write(db, byte_offset, data)
            return True
        elif dtype == 'INT':
            data = struct.pack('>h', int(value))
            plc.db_write(db, byte_offset, data)
            return True
        elif dtype == 'BOOL':
            bit_offset = int((offset - byte_offset) * 10)
            data = plc.db_read(db, byte_offset, 1)
            if value:
                data[0] |= (1 << bit_offset)
            else:
                data[0] &= ~(1 << bit_offset)
            plc.db_write(db, byte_offset, data)
            return True
        else:
            logger.error(f"Unsupported data type: {dtype}")
            return False
    except Exception as e:
        logger.error(f"Write error: {str(e)}")
        return False

# --------------------------
# API Routes (Same as Allen-Bradley version)
# --------------------------
@app.route('/insertDataToPlc', methods=['POST'])
def insert_data_to_plc():
    """Write multiple tag values to PLC"""
    try:
        data_list = request.json
        if not isinstance(data_list, list):
            return jsonify({"message": "Payload must be a list", "error": "Invalid format"}), 400

        plc = get_plc_connection()
        if not plc:
            return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

        results = {}
        for item in data_list:
            tag_name = item.get('tag')
            value = item.get('value')
            
            if tag_name not in TAG_CONFIG:
                results[tag_name] = None
                continue
            
            config = TAG_CONFIG[tag_name]
            success = write_plc_value(plc, config['db'], config['offset'], config['dtype'], value)
            results[tag_name] = "Success" if success else "Failed"

        plc.disconnect()
        return jsonify({
            "message": "Write operation completed",
            "data": results,
            "error": None
        }), 200

    except Exception as e:
        return jsonify({"message": "Write operation failed", "error": str(e)}), 500

@app.route('/readDataTagsFromPlc', methods=['GET'])
def read_data_tags_from_plc():
    """Get list of available tags from PLC"""
    try:
        return jsonify({"tags": list(TAG_CONFIG.keys())}), 200
    except Exception as e:
        return jsonify({"message": "Failed to get tag list", "error": str(e)}), 500

@app.route('/readDataFromPlcByTags', methods=['GET'])
def read_data_from_plc():
    """Read all predefined tags from PLC"""
    try:
        plc = get_plc_connection()
        if not plc:
            return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

        results = {}
        for tag_name, config in TAG_CONFIG.items():
            value = read_plc_value(plc, config['db'], config['offset'], config['dtype'])
            results[tag_name] = value

        plc.disconnect()
        return jsonify({
            "message": "Read operation completed",
            "data": results,
            "error": None
        }), 200

    except Exception as e:
        return jsonify({"message": "Read operation failed", "error": str(e)}), 500

@app.route('/getTagValues', methods=['POST'])
def get_tag_values():
    """Read specific tags provided in request"""
    try:
        requested_tags = request.json.get('tags', [])
        if not requested_tags:
            return jsonify({"message": "No tags specified", "error": "Empty request"}), 400

        plc = get_plc_connection()
        if not plc:
            return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

        results = {}
        for tag_name in requested_tags:
            if tag_name in TAG_CONFIG:
                config = TAG_CONFIG[tag_name]
                value = read_plc_value(plc, config['db'], config['offset'], config['dtype'])
                results[tag_name] = value
            else:
                results[tag_name] = None

        plc.disconnect()
        return jsonify({
            "message": "Read operation completed",
            "data": results,
            "error": None
        }), 200

    except Exception as e:
        return jsonify({"message": "Read operation failed", "error": str(e)}), 500

# --------------------------
# Health Check
# --------------------------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)