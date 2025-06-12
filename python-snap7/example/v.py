import snap7
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_plc_connected(ip, rack=0, slot=1):
    """Utility function to check if PLC is connected."""
    try:
        plc = snap7.client.Client()
        plc.connect(ip, rack, slot)
        state = plc.get_cpu_state()
        plc.disconnect()
        return state == "RUN"
    except Exception as e:
        print(f"PLC connection check failed for IP {ip}: {e}")
        return False

def read_tag(plc_ip, db_number, start, size):
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)
        data = plc.db_read(db_number, start, size)
        plc.disconnect()
        return {"db": db_number, "start": start, "value": list(data)}
    except Exception as e:
        print(f"Error reading tag from DB {db_number}, start {start}: {e}")
        return None

def batch_read(plc_ip, tags, max_workers=20):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(read_tag, plc_ip, tag['db'], tag['start'], tag['size']): tag for tag in tags}
        for future in as_completed(futures):
            tag_data = future.result()
            if tag_data:
                results[f"DB{tag_data['db']}_Start{tag_data['start']}"] = tag_data['value']
    return results

def write_tag(plc_ip, db_number, start, data):
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)
        plc.db_write(db_number, start, bytearray(data))
        plc.disconnect()
        print(f"Data written to PLC successfully for DB {db_number} at start {start}")
    except Exception as e:
        print(f"Error writing data to DB {db_number}, start {start}: {e}")

app = Flask(__name__)
CORS(app)

@app.before_request
def check_plc_connection():
    if request.endpoint in ['insert_data_to_plc', 'read_data_from_plc']:
        ip_address = request.args.get('ip')
        if not ip_address:
            return jsonify({"message": "IP address is missing.", "error": "No IP provided"}), 400
        if not is_plc_connected(ip_address):
            return jsonify({"message": f"PLC with IP {ip_address} is not connected.", "error": "PLC not connected"}), 400

@app.route('/insertDataToPlc', methods=['POST'])
@cross_origin()
def insert_data_to_plc():
    try:
        plc_ip = request.args.get('ip')
        data_list = request.json
        if not isinstance(data_list, list):
            raise ValueError("Payload must be a list of tag-value dictionaries.")
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            for item in data_list:
                executor.submit(write_tag, plc_ip, item['db'], item['start'], item['value'])
        end_time = time.time()
        print(f"Time taken to write to PLC: {end_time - start_time:.4f} seconds")
        return jsonify({"message": "Data written to PLC successfully.", "error": None}), 200
    except Exception as e:
        return jsonify({"message": "Error writing data to PLC.", "error": str(e)}), 500

@app.route('/readDataFromPlc', methods=['POST'])
@cross_origin()
def read_data_from_plc():
    try:
        ip_address = request.args.get('ip')
        tags_to_read = request.json.get('tags', [])
        if not tags_to_read:
            raise ValueError("No tags provided in the payload.")
        start_time = time.time()
        results = batch_read(ip_address, tags_to_read, max_workers=20)
        end_time = time.time()
        print(f"Time taken to read from PLC: {end_time - start_time:.4f} seconds")
        return jsonify({"message": "Data read from PLC successfully.", "data": results, "error": None}), 200
    except Exception as e:
        return jsonify({"message": "Error reading data from PLC.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8083)
