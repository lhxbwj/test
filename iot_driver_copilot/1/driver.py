```python
import os
from flask import Flask, request, Response, jsonify
import threading
import requests

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

app = Flask(__name__)

DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_info": {
        "primary_protocol": "1",
        "ip": DEVICE_IP,
        "port": DEVICE_PORT
    }
}

def get_device_data():
    try:
        url = f"http://{DEVICE_IP}:{DEVICE_PORT}/data"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

def send_device_command(cmd):
    try:
        url = f"http://{DEVICE_IP}:{DEVICE_PORT}/cmd"
        resp = requests.post(url, data=cmd, timeout=5)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Error sending command to device: {str(e)}"

@app.route("/info", methods=["GET"])
def info():
    return jsonify(DEVICE_INFO)

@app.route("/data", methods=["GET"])
def data():
    def generate():
        try:
            url = f"http://{DEVICE_IP}:{DEVICE_PORT}/data"
            with requests.get(url, stream=True, timeout=5) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
        except Exception as e:
            yield f"Error streaming data: {str(e)}\n"
    return Response(generate(), mimetype="text/plain")

@app.route("/cmd", methods=["POST"])
def cmd():
    cmd_data = request.get_data()
    result = send_device_command(cmd_data)
    return Response(result, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)
```