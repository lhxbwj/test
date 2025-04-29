import os
from flask import Flask, Response, request, jsonify
from xml.etree.ElementTree import Element, tostring
from threading import Lock

app = Flask(__name__)

# Environment Variables for Configuration
DEVICE_NAME = os.environ.get('DEVICE_NAME', '1')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', '1')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', '1')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', '1')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# In-memory simulation for data points and commands
data_lock = Lock()
device_data_points = {
    "temperature": "22.5",
    "humidity": "45"
}
device_commands = []

def build_xml_data(data_dict):
    root = Element("DeviceData")
    for key, value in data_dict.items():
        child = Element(key)
        child.text = str(value)
        root.append(child)
    return tostring(root, encoding='utf-8', method='xml')

@app.route('/info', methods=['GET'])
def get_info():
    info = {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE
    }
    return jsonify(info)

@app.route('/data', methods=['GET'])
def get_data():
    with data_lock:
        xml_data = build_xml_data(device_data_points)
    return Response(xml_data, mimetype='application/xml')

@app.route('/cmd', methods=['POST'])
def send_command():
    cmd_data = request.get_json(force=True)
    if not cmd_data or 'command' not in cmd_data:
        return jsonify({"error": "Missing 'command' in request body"}), 400
    with data_lock:
        device_commands.append(cmd_data['command'])
        # Simulate command effect for demo
        if cmd_data['command'] == "toggle":
            if "status" in device_data_points:
                device_data_points["status"] = "off" if device_data_points["status"] == "on" else "on"
            else:
                device_data_points["status"] = "on"
    return jsonify({"result": "Command received", "command": cmd_data['command']}), 200

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)