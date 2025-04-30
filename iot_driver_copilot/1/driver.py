```python
import os
from flask import Flask, request, jsonify, Response, stream_with_context
import threading
import queue
import time

# Device and Server configuration via environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

app = Flask(__name__)

# Mock device info (configurable if needed)
DEVICE_INFO = {
    "device_name": os.environ.get('DEVICE_NAME', '1'),
    "device_model": os.environ.get('DEVICE_MODEL', '1'),
    "manufacturer": os.environ.get('DEVICE_MANUFACTURER', '1'),
    "device_type": os.environ.get('DEVICE_TYPE', '1')
}

# Thread-safe queue for data streaming
data_queue = queue.Queue(maxsize=100)
COMMAND_RESULT = {"last_command": None, "last_result": None}

def device_reader():
    """Continuously read data from the device and place it in the queue."""
    import socket
    while True:
        try:
            with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
                f = s.makefile('r')
                while True:
                    line = f.readline()
                    if not line:
                        break
                    line = line.rstrip('\r\n')
                    try:
                        data_queue.put(line, timeout=0.5)
                    except queue.Full:
                        pass  # Drop data if queue is full
        except Exception as e:
            time.sleep(2)  # Retry after delay on failure

# Start device reading in background thread
threading.Thread(target=device_reader, daemon=True).start()

@app.route('/info', methods=['GET'])
def get_info():
    return jsonify(DEVICE_INFO)

@app.route('/cmd', methods=['POST'])
def send_command():
    cmd = request.json.get('command')
    result = None
    try:
        import socket
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall((cmd+'\n').encode('utf-8'))
            s.settimeout(2)
            result = s.recv(4096).decode('utf-8')
    except Exception as e:
        result = f"Error: {str(e)}"
    COMMAND_RESULT['last_command'] = cmd
    COMMAND_RESULT['last_result'] = result
    return jsonify({'command': cmd, 'response': result})

@app.route('/data', methods=['GET'])
def stream_data():
    def generate():
        # Stream lines as Server-Sent Events (SSE) to allow browser/CLI consumption
        while True:
            try:
                line = data_queue.get(timeout=5)
                yield f"data: {line}\n\n"
            except queue.Empty:
                yield ": keep-alive\n\n"
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    return Response(stream_with_context(generate()), headers=headers)

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)
```