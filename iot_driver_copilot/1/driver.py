import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "1"),
    "device_model": os.environ.get("DEVICE_MODEL", "1"),
    "manufacturer": os.environ.get("DEVICE_MANUFACTURER", "1"),
    "device_type": os.environ.get("DEVICE_TYPE", "1")
}

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8000))

# Simulated data points (as the real device protocol is unspecified)
DATA_POINTS = {
    "temperature": "23",
    "humidity": "45",
    "status": "online"
}

# Simulated command processing
def process_command(xml_request):
    try:
        root = ET.fromstring(xml_request)
        command = root.findtext("command")
        # Simulate command execution and response
        response = ET.Element("response")
        status = ET.SubElement(response, "status")
        status.text = "success"
        result = ET.SubElement(response, "result")
        result.text = f"Executed: {command}"
        return ET.tostring(response, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        response = ET.Element("response")
        status = ET.SubElement(response, "status")
        status.text = "error"
        error = ET.SubElement(response, "error")
        error.text = str(e)
        return ET.tostring(response, encoding="utf-8", xml_declaration=True)

# HTTP Handler
class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            self._set_headers(200, "application/xml")
            data = ET.Element("data_points")
            for k, v in DATA_POINTS.items():
                e = ET.SubElement(data, k)
                e.text = v
            self.wfile.write(ET.tostring(data, encoding="utf-8", xml_declaration=True))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            result = process_command(post_body.decode("utf-8"))
            self._set_headers(200, "application/xml")
            self.wfile.write(result)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()