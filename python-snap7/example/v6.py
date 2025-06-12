import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# --------------------------
# Configuration
# --------------------------
PLC_IP = '192.168.0.1'  # Replace with your PLC IP
PLC_RACK = 0            # Default for S7-1200
PLC_SLOT = 1            # Default for S7-1200
PLC_PORT = 102          # Default S7 port

# Tag configuration - Only DB1.DBD0 and DB1.DBD4 as DINT values
TAG_CONFIG = {
    'DB1_DBD0': {'db': 1, 'offset': 0, 'dtype': 'DINT'},    # Double Integer (4 bytes)
    'DB1_DBD4': {'db': 1, 'offset': 4, 'dtype': 'DINT'},    # Floating point (4 bytes)
    # REAL (32-bit floating point) tags
    'DB1_DBD12': {'db': 1, 'offset': 12, 'dtype': 'REAL' },
    'DB1_DBD16': {'db': 1, 'offset': 16, 'dtype': 'REAL' },
        # STRING tag (P#DB1.DBX24.0)
    'DB1_DBX24': {'db': 1, 'offset': 24, 'dtype': 'STRING', 'max_length': 254  }
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
logger = logging.getLogger("S7-1200-DINT-API")

# --------------------------
# PLC Communication Functions (DINT specific)
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

def read_plc_value(plc: snap7.client.Client, db: int, offset: int, dtype: str) -> int:
    """Read DINT value from PLC data block"""
    try:
        if dtype == 'DINT':
            data = plc.db_read(db, offset, 4)
            return int.from_bytes(data, byteorder='big', signed=True)  # Correct DINT reading
        logger.error(f"Unsupported data type: {dtype}")
        return None
    except Exception as e:
        logger.error(f"Read error at DB{db}.DBD{offset}: {str(e)}")
        return None

def write_plc_value(plc: snap7.client.Client, db: int, offset: int, dtype: str, value: int) -> bool:
    """Write DINT value to PLC data block"""
    try:
        if dtype == 'DINT':
            data = int(value).to_bytes(4, byteorder='big', signed=True)  # Correct DINT writing
            plc.db_write(db, offset, data)
            return True
        logger.error(f"Unsupported data type: {dtype}")
        return False
    except Exception as e:
        logger.error(f"Write error at DB{db}.DBD{offset}: {str(e)}")
        return False

# --------------------------
# API Routes (Corrected endpoints)
# --------------------------
@app.route('/insertDataToPlc', methods=['POST'])
def insert_data_to_plc():
    """Write multiple DINT values to PLC"""
    try:
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"message": "IP parameter missing", "error": "No IP provided"}), 400

        data_list = request.json
        if not isinstance(data_list, list):
            return jsonify({"message": "Payload must be a list", "error": "Invalid format"}), 400

        plc = get_plc_connection()
        if not plc:
            return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

        results = {}
        for item in data_list:
            if not isinstance(item, dict):
                continue
                
            tag_name = item.get('tag')
            value = item.get('value')
            
            if tag_name not in TAG_CONFIG:
                results[tag_name] = {"status": "Failed", "error": "Tag not defined"}
                continue
            
            try:
                config = TAG_CONFIG[tag_name]
                success = write_plc_value(plc, config['db'], config['offset'], config['dtype'], value)
                results[tag_name] = {
                    "status": "Success" if success else "Failed",
                    "value_written": value
                }
            except Exception as e:
                results[tag_name] = {"status": "Failed", "error": str(e)}

        plc.disconnect()
        return jsonify({
            "message": "Write operation completed",
            "data": results,
            "error": None
        }), 200

    except Exception as e:
        return jsonify({"message": "Write operation failed", "error": str(e)}), 500

@app.route('/readDataFromPlcByTags', methods=['GET'])
def read_data_from_plc():
    """Read all predefined DINT tags from PLC"""
    try:
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"message": "IP parameter missing", "error": "No IP provided"}), 400

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
    """Read specific DINT tags provided in request"""
    try:
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"message": "IP parameter missing", "error": "No IP provided"}), 400

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)