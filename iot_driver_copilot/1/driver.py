import os
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import threading

# Environment Variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulated device data and command handler
class DeviceSimulator:
    def __init__(self):
        self.data_points = {
            'temperature': '22.5',
            'humidity': '45',
            'status': 'OK'
        }
        self.commands_executed = []

    def get_data_xml(self):
        root = ET.Element('DeviceData')
        for k, v in self.data_points.items():
            el = ET.SubElement(root, k)
            el.text = v
        return ET.tostring(root, encoding='utf-8', method='xml')

    def execute_command(self, cmd):
        self.commands_executed.append(cmd)
        # Simulate command effect
        if cmd.get('action') == 'set_temperature':
            self.data_points['temperature'] = cmd.get('value', self.data_points['temperature'])
        elif cmd.get('action') == 'set_humidity':
            self.data_points['humidity'] = cmd.get('value', self.data_points['humidity'])
        elif cmd.get('action') == 'reset_status':
            self.data_points['status'] = 'OK'
        return "<Response>Command Executed</Response>"

device_sim = DeviceSimulator()

class IoTDeviceHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/data':
            # Proxy data from device and return as XML
            xml_data = device_sim.get_data_xml()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            try:
                # Expect XML command
                cmd_xml = ET.fromstring(post_body)
                cmd_dict = {child.tag: child.text for child in cmd_xml}
                response_xml = device_sim.execute_command(cmd_dict)
                self._set_headers(200, "application/xml")
                self.wfile.write(response_xml.encode('utf-8'))
            except Exception as e:
                self._set_headers(400, "application/xml")
                self.wfile.write(f"<Error>Invalid Command: {e}</Error>".encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), IoTDeviceHTTPRequestHandler) as httpd:
        print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
