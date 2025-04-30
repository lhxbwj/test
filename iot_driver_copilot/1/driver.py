import os
import csv
import io
from flask import Flask, jsonify, request, Response, abort

app = Flask(__name__)

DEVICE_NAME = os.environ.get('DEVICE_NAME', '1')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', '1')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', '1')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', '1')
DEVICE_PROTOCOL = os.environ.get('DEVICE_PROTOCOL', '1')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))
DATA_CSV_HEADER = os.environ.get('DATA_CSV_HEADER', 'timestamp,value')
DATA_CSV_VALUE = os.environ.get('DATA_CSV_VALUE', '2024-06-01T00:00:00Z,42')

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'device_name': DEVICE_NAME,
        'device_model': DEVICE_MODEL,
        'manufacturer': DEVICE_MANUFACTURER,
        'device_type': DEVICE_TYPE,
        'primary_protocol': DEVICE_PROTOCOL
    })

@app.route('/cmd', methods=['POST'])
def cmd():
    if not request.is_json:
        abort(400, description='Invalid JSON')
    payload = request.get_json()
    # Simulate command execution and response
    command = payload.get('command', None)
    params = payload.get('params', {})
    # Here we simulate only success; real implementation would interact with device
    return jsonify({'status': 'success', 'command': command, 'params': params})

@app.route('/data', methods=['GET'])
def data():
    header = DATA_CSV_HEADER.split(',')
    value = DATA_CSV_VALUE.split(',')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerow(value)
    output.seek(0)
    return Response(output.read(), mimetype='text/csv')

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)