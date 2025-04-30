```python
import os
from flask import Flask, request, Response, jsonify
import requests

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

app = Flask(__name__)

DEVICE_INFO = {
    "device_name": "·",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_info": {
        "primary_protocol": "1",
        "ip": DEVICE_IP,
        "port": DEVICE_PORT
    }
}

@app.route("/info", methods=["GET"])
def info():
    return jsonify(DEVICE_INFO)

@app.route("/data", methods=["GET"])
def data():
    def generate():
        try:
            url = f"http://{DEVICE_IP}:{DEVICE_PORT}/data"
            with requests.get(url, stream=True, timeout=10) as resp:
                resp.raise_for_status()
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
        except Exception as e:
            yield f"Error streaming data: {str(e)}\n"
    return Response(generate(), mimetype="text/csv")

@app.route("/cmd", methods=["POST"])
def cmd():
    try:
        url = f"http://{DEVICE_IP}:{DEVICE_PORT}/cmd"
        resp = requests.post(url, data=request.data, timeout=10)
        resp.raise_for_status()
        return Response(resp.text, mimetype="text/plain")
    except Exception as e:
        return Response(f"Error sending command to device: {str(e)}\n", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)
```