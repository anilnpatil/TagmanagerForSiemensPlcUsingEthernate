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
MAX_STRING_LENGTH = 254  # Maximum length for S7 STRING type

# Tag configuration
TAG_CONFIG = {
    'DB1_DBD0': {'db': 1, 'offset': 0, 'dtype': 'DINT'},    # Double Integer (4 bytes)
    'DB1_DBD4': {'db': 1, 'offset': 4, 'dtype': 'DINT'},    # Floating point (4 bytes)
    'DB1_DBD5': {'db': 1, 'offset': 5, 'dtype': 'DINT'},    # Double Integer (4 bytes)
    'DB1_DBD6': {'db': 1, 'offset': 6, 'dtype': 'DINT'},    # Floating point (4 bytes)
    'DB1_DBD7': {'db': 1, 'offset': 7, 'dtype': 'DINT'},    # Double Integer (4 bytes)
    'DB1_DBD8': {'db': 1, 'offset': 8, 'dtype': 'DINT'},    # Floating point (4 bytes)
    'DB1_DBD9': {'db': 1, 'offset': 9, 'dtype': 'DINT'},    # Double Integer (4 bytes)
    'DB1_DBD10': {'db': 1, 'offset': 10, 'dtype': 'DINT'},    # Floating point (4 bytes)
    # REAL (32-bit floating point) tags
    'DB1_DBD12': {
        'db': 1,          # Data Block number
        'offset': 12,     # Byte offset (DBD12 starts at byte 12)
        'dtype': 'REAL'   # Data type (32-bit float)
    },
    'DB1_DBD16': {
        'db': 1,
        'offset': 16,
        'dtype': 'REAL'
    },
    
    # STRING tag (P#DB1.DBX24.0)
    'DB1_DBX24': {
        'db': 1,          # Data Block number
        'offset': 24,     # Byte offset (DBX24.0 means byte 24, bit 0)
        'dtype': 'STRING', # Data type
        'max_length': 254 # Maximum string length (1-254)
    }
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

# def read_plc_value(plc: snap7.client.Client, db: int, offset: int, dtype: str, max_length: int = None) -> any:
#     """Read value from PLC data block"""
#     try:
#         if dtype == 'DINT':
#             data = plc.db_read(db, offset, 4)
#             return int.from_bytes(data, byteorder='big', signed=True)
#         elif dtype == 'REAL':
#             data = plc.db_read(db, offset, 4)
#             return struct.unpack('>f', bytes(data))[0]
#         elif dtype == 'STRING':
#             data = plc.db_read(db, offset, max_length + 2)
#             current_length = data[1]
#             return data[2:2+current_length].decode('ascii')
#         else:
#             logger.error(f"Unsupported data type: {dtype}")
#             return None
#     except Exception as e:
#         logger.error(f"Read error at DB{db}.{dtype}{offset}: {str(e)}")
#         return None
def read_plc_value(plc: snap7.client.Client, db: int, offset: int, dtype: str, max_length: int = None) -> any:
    """Read value from PLC data block (simplified for Angular)"""
    try:
        if dtype == 'REAL':
            data = plc.db_read(db, offset, 4)
            return round(struct.unpack('>f', bytes(data))[0], 2)  # Rounded to 2 decimal places
        elif dtype == 'DINT':
            data = plc.db_read(db, offset, 4)
            return int.from_bytes(data, byteorder='big', signed=True)
        elif dtype == 'STRING':
            data = plc.db_read(db, offset, max_length + 2)
            current_length = data[1]
            return data[2:2+current_length].decode('ascii').strip('\x00')
        return None
    except Exception as e:
        logger.error(f"Read error: {str(e)}")
        return None

def write_plc_value(plc: snap7.client.Client, db: int, offset: int, dtype: str, value: any, max_length: int = None) -> bool:
    """Write value to PLC data block"""
    try:
        if dtype == 'DINT':
            data = int(value).to_bytes(4, byteorder='big', signed=True)
            plc.db_write(db, offset, data)
            return True
        elif dtype == 'REAL':
            data = struct.pack('>f', float(value))
            plc.db_write(db, offset, data)
            return True
        elif dtype == 'STRING':
            if not isinstance(value, str):
                value = str(value)
            if len(value) > max_length:
                value = value[:max_length]
            data = bytearray(max_length + 2)
            data[0] = max_length
            data[1] = len(value)
            data[2:2+len(value)] = value.encode('ascii')
            plc.db_write(db, offset, data)
            return True
        else:
            logger.error(f"Unsupported data type: {dtype}")
            return False
    except Exception as e:
        logger.error(f"Write error at DB{db}.{dtype}{offset}: {str(e)}")
        return False

# --------------------------
# API Routes
# --------------------------
@app.route('/insertDataToPlc', methods=['POST'])
def insert_data_to_plc():
    """Write values to PLC"""
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
            
            config = TAG_CONFIG[tag_name]
            success = write_plc_value(
                plc,
                config['db'],
                config['offset'],
                config['dtype'],
                value,
                config.get('max_length')
            )
            results[tag_name] = {
                "status": "Success" if success else "Failed",
                "value_written": value,
                "data_type": config['dtype']
            }

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
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"message": "IP parameter missing", "error": "No IP provided"}), 400

        plc = get_plc_connection()
        if not plc:
            return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

        results = {}
        for tag_name, config in TAG_CONFIG.items():
            value = read_plc_value(
                plc,
                config['db'],
                config['offset'],
                config['dtype'],
                config.get('max_length')
            )
            results[tag_name] = {
                "value": value,
                "data_type": config['dtype']
            }

        plc.disconnect()
        return jsonify({
            "message": "Read operation completed",
            "data": results,
            "error": None
        }), 200

    except Exception as e:
        return jsonify({"message": "Read operation failed", "error": str(e)}), 500

# @app.route('/getTagValues', methods=['POST'])
# def get_tag_values():
#     """Read specific tags provided in request"""
#     try:
#         plc_ip = request.args.get('ip')
#         if not plc_ip:
#             return jsonify({"message": "IP parameter missing", "error": "No IP provided"}), 400

#         requested_tags = request.json.get('tags', [])
#         if not requested_tags:
#             return jsonify({"message": "No tags specified", "error": "Empty request"}), 400

#         plc = get_plc_connection()
#         if not plc:
#             return jsonify({"message": "PLC connection failed", "error": "Connection error"}), 500

#         results = {}
#         for tag_name in requested_tags:
#             if tag_name in TAG_CONFIG:
#                 config = TAG_CONFIG[tag_name]
#                 value = read_plc_value(
#                     plc,
#                     config['db'],
#                     config['offset'],
#                     config['dtype'],
#                     config.get('max_length')
#                 )
#                 results[tag_name] = {
#                     "value": value,
#                     "data_type": config['dtype']
#                 }
#             else:
#                 results[tag_name] = None

#         plc.disconnect()
#         return jsonify({
#             "message": "Read operation completed",
#             "data": results,
#             "error": None
#         }), 200

#     except Exception as e:
#         return jsonify({"message": "Read operation failed", "error": str(e)}), 500

@app.route('/getTagValues', methods=['POST'])
def get_tag_values():
    """Endpoint specifically designed for Angular frontend's fetchTagValues()"""
    try:
        # 1. Validate input
        plc_ip = request.args.get('ip')
        if not plc_ip:
            return jsonify({"data": None}), 400

        requested_tags = request.json.get('tags', [])
        if not requested_tags:
            return jsonify({"data": None}), 400

        # 2. Connect to PLC
        plc = get_plc_connection()
        if not plc:
            return jsonify({"data": None}), 500

        # 3. Read all requested tags
        results = {}
        for tag_name in requested_tags:
            if tag_name in TAG_CONFIG:
                config = TAG_CONFIG[tag_name]
                value = read_plc_value(
                    plc,
                    config['db'],
                    config['offset'],
                    config['dtype'],
                    config.get('max_length')
                )
                results[tag_name] = value
            else:
                results[tag_name] = None

        plc.disconnect()
        
        # 4. Return response in exact format expected by Angular
        return jsonify({
            "data": results  # Directly mapping tag names to values
        }), 200

    except Exception as e:
        logger.error(f"Error in getTagValues: {str(e)}")
        return jsonify({"data": None}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)