import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

DEVICE_NAME = os.environ.get('DEVICE_NAME', '1')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', '1')
MANUFACTURER = os.environ.get('MANUFACTURER', '1')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', '1')
PRIMARY_PROTOCOL = os.environ.get('PRIMARY_PROTOCOL', '1')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Mocked device data and command state for illustration purposes
device_state = {
    "command": None,
    "data_points": [
        {"timestamp": "2024-01-01T00:00:00Z", "value": "42"},
        {"timestamp": "2024-01-01T01:00:00Z", "value": "43"},
    ]
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_response()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER,
                "device_type": DEVICE_TYPE,
                "primary_protocol": PRIMARY_PROTOCOL
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))

        elif self.path == "/data":
            self._set_response(200, "text/csv")
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["timestamp", "value"])
            writer.writeheader()
            for row in device_state["data_points"]:
                writer.writerow(row)
            self.wfile.write(output.getvalue().encode('utf-8'))

        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                cmd = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._set_response(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return

            # Mock command handling logic: Store in device_state
            device_state["command"] = cmd

            self._set_response(200)
            self.wfile.write(json.dumps({"result": "Command received", "command": cmd}).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=DeviceHTTPRequestHandler):
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()