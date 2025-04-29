import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Environment Variables
DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "9000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# Dummy Device Data & Command Handling (Mock)
# In a real scenario, replace with actual device communication logic.
class DeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.data_points = [
            {"timestamp": "2024-06-01T12:00:00Z", "value": "23.1"},
            {"timestamp": "2024-06-01T12:01:00Z", "value": "23.2"},
        ]
        self.device_info = {
            "device_name": "1",
            "device_model": "1",
            "manufacturer": "1",
            "device_type": "1",
            "connection_protocol": "1"
        }
        self.lock = threading.Lock()
    
    def read_csv_data(self):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "value"])
        writer.writeheader()
        for dp in self.data_points:
            writer.writerow(dp)
        return output.getvalue()
    
    def execute_command(self, cmd):
        # Simulate command execution and mutate data for demo
        with self.lock:
            self.data_points.append({"timestamp": "2024-06-01T12:02:00Z", "value": cmd.get("value", "unknown")})
        return {"status": "success", "executed": cmd}
    
    def get_info(self):
        return self.device_info

device = DeviceConnection(DEVICE_IP, DEVICE_PORT)

class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
    
    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = device.get_info()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path == "/data":
            csv_data = device.read_csv_data()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))
    
    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                cmd = json.loads(body)
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return
            result = device.execute_command(cmd)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), IoTHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()