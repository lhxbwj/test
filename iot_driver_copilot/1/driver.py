import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class DeviceConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_data(self):
        # Simulate device connection and retrieve raw XML data.
        # In real implementation, connect to the device with its protocol.
        # Here, we just simulate with dummy XML.
        data = {
            "status": "OK",
            "temperature": "23.1",
            "humidity": "56"
        }
        root = ET.Element("DeviceData")
        for k, v in data.items():
            ET.SubElement(root, k).text = v
        return ET.tostring(root, encoding="utf-8")

    def send_command(self, xml_command):
        # Simulate sending command and getting response
        # In a real implementation, send XML to device and get real response
        try:
            tree = ET.fromstring(xml_command)
            cmd = tree.find('Command')
            response_root = ET.Element("Response")
            if cmd is not None:
                ET.SubElement(response_root, "Result").text = f"Command '{cmd.text}' executed"
                ET.SubElement(response_root, "Status").text = "Success"
            else:
                ET.SubElement(response_root, "Result").text = "No command found"
                ET.SubElement(response_root, "Status").text = "Failed"
            return ET.tostring(response_root, encoding="utf-8")
        except Exception as e:
            response_root = ET.Element("Response")
            ET.SubElement(response_root, "Result").text = str(e)
            ET.SubElement(response_root, "Status").text = "Error"
            return ET.tostring(response_root, encoding="utf-8")

device_conn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            xml_data = device_conn.get_data()
            self.wfile.write(xml_data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            response_xml = device_conn.send_command(post_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(response_xml)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress default logging

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()