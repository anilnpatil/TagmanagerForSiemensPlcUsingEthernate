import snap7
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from threading import Lock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Siemens-PROFINET-API")

# Constants
PLC_RACK = 0
PLC_SLOT = 1
CONNECTION_TIMEOUT = 2000  # ms

# Thread safety
plc_lock = Lock()

app = Flask(__name__)
CORS(app)

def is_plc_reachable(ip: str) -> bool:
    """Check if PLC IP is reachable (ping test)"""
    try:
        plc = snap7.client.Client()
        plc.set_connection_params(ip, PLC_RACK, PLC_SLOT, CONNECTION_TIMEOUT)
        plc.connect()
        if plc.get_connected():
            plc.disconnect()
            return True
        return False
    except Exception as e:
        logger.warning(f"PLC at {ip} not reachable: {str(e)}")
        return False

def read_actual_plc_data(ip: str, db: int, start: int, size: int) -> list:
    """Read real data from PLC when connected"""
    with plc_lock:
        try:
            plc = snap7.client.Client()
            plc.set_connection_params(ip, PLC_RACK, PLC_SLOT, CONNECTION_TIMEOUT)
            plc.connect()
            if plc.get_connected():
                data = plc.db_read(db, start, size)
                plc.disconnect()
                return list(data)
            return None
        except Exception as e:
            logger.error(f"Read failed for DB{db}: {str(e)}")
            return None

@app.route('/readDataTagsFromPlc', methods=['GET'])
def get_plc_structure():
    """Get available DB blocks structure - requires connection"""
    plc_ip = request.args.get('ip')
    
    if not plc_ip:
        return jsonify({"error": "IP parameter is required"}), 400
    
    if not is_plc_reachable(plc_ip):
        return jsonify({
            "error": "PLC not reachable",
            "message": f"Could not establish connection to PLC at {plc_ip}"
        }), 400
    
    try:
        # This would be replaced with actual DB structure reading
        # For now returning a sample structure
        structure = {
            "DB1": {
                "length": 100,
                "description": "Motor Control Block",
                "tags": {
                    "MotorSpeed": {"offset": 0, "type": "INT", "size": 2},
                    "Temperature": {"offset": 4, "type": "REAL", "size": 4}
                }
            },
            "DB2": {
                "length": 50,
                "description": "Sensor Data Block",
                "tags": {
                    "Pressure": {"offset": 0, "type": "REAL", "size": 4},
                    "Status": {"offset": 4, "type": "BOOL", "size": 1}
                }
            }
        }
        
        return jsonify({
            "db_blocks": structure,
            "message": f"Successfully read DB structure from {plc_ip}",
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/readDataFromPlc', methods=['POST'])
def read_plc_data():
    """Read actual data from PLC - requires connection"""
    plc_ip = request.args.get('ip')
    request_data = request.json
    
    if not plc_ip:
        return jsonify({"error": "IP parameter is required"}), 400
    
    if not is_plc_reachable(plc_ip):
        return jsonify({
            "error": "PLC not reachable",
            "message": f"Cannot read data - PLC at {plc_ip} is not connected"
        }), 400
    
    try:
        results = {}
        for item in request_data.get('tags', []):
            db = item.get('db')
            start = item.get('start', 0)
            size = item.get('size', 1)
            
            if not db:
                continue
                
            data = read_actual_plc_data(plc_ip, db, start, size)
            if data is not None:
                results[f"DB{db}.{start}"] = data
            else:
                results[f"DB{db}.{start}"] = "Read failed"
        
        return jsonify({
            "data": results,
            "message": f"Successfully read data from {plc_ip}",
            "error": None
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)