import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import urllib.parse
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '8080'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8000'))

# Simulated device logic (replace with actual protocol/transport if needed)
def get_device_data():
    # Simulate XML data from device
    root = ET.Element("DeviceData")
    ET.SubElement(root, "Status").text = "OK"
    ET.SubElement(root, "Temperature").text = "25"
    ET.SubElement(root, "Humidity").text = "60"
    return ET.tostring(root, encoding='utf-8', method='xml')

def send_device_command(cmd_xml):
    # Simulate command acceptance
    try:
        root = ET.fromstring(cmd_xml)
        response = ET.Element("CommandResponse")
        ET.SubElement(response, "Status").text = "Accepted"
        ET.SubElement(response, "Received").append(root)
        return ET.tostring(response, encoding='utf-8', method='xml')
    except Exception as e:
        response = ET.Element("CommandResponse")
        ET.SubElement(response, "Status").text = "Error"
        ET.SubElement(response, "Error").text = str(e)
        return ET.tostring(response, encoding='utf-8', method='xml')

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/data":
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            data = get_device_data()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            response = send_device_command(post_data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
