```python
import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_protocol": "1"
}

# Simulated device data and action
class SimulatedDevice:
    def __init__(self):
        self.data_points = [
            ["timestamp", "value1", "value2"],
            ["2024-06-01T12:00:00Z", "100", "200"],
            ["2024-06-01T12:01:00Z", "105", "208"]
        ]
        self.command_log = []

    def fetch_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        for row in self.data_points:
            writer.writerow(row)
        return output.getvalue()

    def execute_command(self, command):
        self.command_log.append(command)
        # Simulate response
        return {"status": "success", "executed_command": command}

    def get_info(self):
        return DEVICE_INFO

device = SimulatedDevice()

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(device.get_info()).encode("utf-8"))
        elif self.path == "/data":
            csv_data = device.fetch_csv()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error": "Invalid JSON"}')
                return

            command = payload.get("command")
            if not command:
                self._set_headers(400)
                self.wfile.write(b'{"error": "No command provided"}')
                return

            resp = device.execute_command(command)
            self._set_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

def run_server():
    server = ThreadingHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP Device Driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
```