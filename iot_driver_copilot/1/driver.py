import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.parse

DEVICE_HOST = os.environ.get('DEVICE_HOST', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '8081'))
DEVICE_DATA_PATH = os.environ.get('DEVICE_DATA_PATH', '/data')
DEVICE_CMD_PATH = os.environ.get('DEVICE_CMD_PATH', '/cmd')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

class DeviceHTTPProxyHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/xml'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            try:
                url = f'http://{DEVICE_HOST}:{DEVICE_PORT}{DEVICE_DATA_PATH}'
                with urllib.request.urlopen(url) as response:
                    xml_data = response.read()
                self._set_headers(200, 'application/xml')
                self.wfile.write(xml_data)
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f'Failed to fetch device data: {str(e)}'.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            try:
                url = f'http://{DEVICE_HOST}:{DEVICE_PORT}{DEVICE_CMD_PATH}'
                req = urllib.request.Request(url, data=post_data, method='POST')
                req.add_header('Content-Type', 'application/xml')
                with urllib.request.urlopen(req) as response:
                    resp_data = response.read()
                self._set_headers(200, 'application/xml')
                self.wfile.write(resp_data)
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f'Failed to send command to device: {str(e)}'.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'Not Found')

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPProxyHandler)
    print(f"Starting HTTP server at {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
