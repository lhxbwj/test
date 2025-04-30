import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class DeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_command(self, command):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((self.ip, self.port))
            s.sendall(command.encode('utf-8'))
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')

    def get_data(self):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((self.ip, self.port))
            s.sendall(b"GET_DATA\n")
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')

device_conn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="text/plain"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            response = device_conn.send_command(body.strip())
            self._set_headers(200)
            self.wfile.write(response.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def do_GET(self):
        if self.path == "/data":
            response = device_conn.get_data()
            self._set_headers(200)
            self.wfile.write(response.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
