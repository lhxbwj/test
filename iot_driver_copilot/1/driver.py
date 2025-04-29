import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

# Device configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy device properties (simulate a device with CSV data and command interface)
DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_info": {
        "primary_protocol": "1",
        "ip": DEVICE_IP,
        "port": DEVICE_PORT
    },
    "key_characteristics": {
        "data_points": "1",
        "commands": "1"
    },
    "data_format": {
        "format": "CSV"
    }
}

# Simulated device state/data
class DummyDevice:
    def __init__(self):
        self.state = {"value": 0}

    def get_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.state.keys())
        writer.writerow(self.state.values())
        return output.getvalue()

    def send_command(self, command):
        # Command is a dictionary
        if "set_value" in command:
            try:
                self.state["value"] = int(command["set_value"])
            except ValueError:
                return {"status": "error", "message": "Invalid value"}
            return {"status": "ok", "message": f"Value set to {self.state['value']}"}
        return {"status": "error", "message": "Unknown command"}

device = DummyDevice()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
                "connection_info": DEVICE_INFO["connection_info"]
            }
            self.wfile.write(json.dumps(info).encode())
        elif self.path == "/data":
            csv_data = device.get_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(csv_data.encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)
            try:
                body = json.loads(raw_body)
            except Exception:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
                return
            result = device.send_command(body)
            self.send_response(200 if result["status"] == "ok" else 400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def log_message(self, format, *args):
        return  # Silence default logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()