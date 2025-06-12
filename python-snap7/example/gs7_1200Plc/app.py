from flask import Flask, request, jsonify
from plc_util import connect_to_plc, write_to_plc

app = Flask(__name__)

PLC_IP = "192.168.0.1"  # Change to your actual PLC IP


@app.route('/insertDataToPLC', methods=['POST'])
def insert_data_to_plc():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        plc = connect_to_plc(PLC_IP)

        for tag_name, value in data.items():
            try:
                write_to_plc(plc, tag_name, value)
            except Exception as e:
                return jsonify({'status': 'error', 'message': f"Failed to write {tag_name}: {str(e)}"}), 500

        plc.disconnect()
        return jsonify({'status': 'success', 'message': 'Data written to PLC successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)
