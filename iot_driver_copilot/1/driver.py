import os
import csv
import io
from flask import Flask, jsonify, request, Response, abort

app = Flask(__name__)

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device meta
DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_protocol": "1"
}

# Simulated device state & data
DEVICE_DATA = [
    {"timestamp": "2024-06-01T12:00:00Z", "value": "23.1"},
    {"timestamp": "2024-06-01T12:01:00Z", "value": "23.3"},
]
DEVICE_COMMAND_STATE = {}

def fetch_device_data_csv():
    # In a real driver, replace this with actual protocol communication.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=DEVICE_DATA[0].keys())
    writer.writeheader()
    for row in DEVICE_DATA:
        writer.writerow(row)
    csv_data = output.getvalue()
    output.close()
    return csv_data

def send_command_to_device(command):
    # In a real driver, send the command over the configured protocol.
    DEVICE_COMMAND_STATE["last_command"] = command
    return {"result": "success", "echo": command}

@app.route("/info", methods=["GET"])
def device_info():
    return jsonify(DEVICE_INFO)

@app.route("/data", methods=["GET"])
def device_data():
    csv_data = fetch_device_data_csv()
    return Response(csv_data, mimetype="text/csv")

@app.route("/cmd", methods=["POST"])
def device_cmd():
    if not request.is_json:
        abort(400, "Request must be JSON")
    command = request.get_json()
    if not isinstance(command, dict):
        abort(400, "Command must be a JSON object")
    result = send_command_to_device(command)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)