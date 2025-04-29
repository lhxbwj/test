import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

DEVICE_NAME = os.environ.get("DEVICE_NAME", "1")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "1")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "1")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "1")
PRIMARY_PROTOCOL = os.environ.get("PRIMARY_PROTOCOL", "1")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device state and data
device_state = {
    "last_command": None,
    "data_points": [
        {"timestamp": "2024-06-01T12:00:00Z", "value": "23.5"},
        {"timestamp": "2024-06-01T12:05:00Z", "value": "23.8"}
    ]
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            self.handle_info()
        elif self.path == "/data":
            self.handle_data()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == "/cmd":
            self.handle_cmd()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_info(self):
        info = {
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE,
            "primary_protocol": PRIMARY_PROTOCOL,
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(info).encode("utf-8"))
    
    def handle_data(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "value"])
        for row in device_state["data_points"]:
            writer.writerow([row["timestamp"], row["value"]])
        csv_bytes = output.getvalue().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Disposition", "attachment; filename=data.csv")
        self.end_headers()
        self.wfile.write(csv_bytes)
    
    def handle_cmd(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON payload")
            return
        command = payload.get("command")
        if not command:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing 'command' in payload")
            return
        device_state["last_command"] = command
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success", "received_command": command}).encode("utf-8"))

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
