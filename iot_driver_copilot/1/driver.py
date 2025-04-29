```python
import os
import csv
import io
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Dict, Any

# Environment variable configuration
DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "9000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# Mock device data and commands for demonstration
MOCK_DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1",
    "connection_protocol": "1",
}
MOCK_DATA = [
    {"timestamp": "2024-01-01T00:00:01Z", "value": "123"},
    {"timestamp": "2024-01-01T00:00:02Z", "value": "124"},
]
MOCK_STATE = {}

# Command input schema
class CommandInput(BaseModel):
    command: str
    parameters: Dict[str, Any] = {}

app = FastAPI()

@app.get("/info")
async def get_info():
    info = {
        "device_info": {
            "device_name": MOCK_DEVICE_INFO["device_name"],
            "device_model": MOCK_DEVICE_INFO["device_model"],
            "manufacturer": MOCK_DEVICE_INFO["manufacturer"],
            "device_type": MOCK_DEVICE_INFO["device_type"],
        },
        "connection_info": {
            "primary_protocol": MOCK_DEVICE_INFO["connection_protocol"]
        }
    }
    return JSONResponse(content=info)

@app.post("/cmd")
async def send_command(cmd: CommandInput):
    # In a real implementation, send the command to the device over TCP or other protocol
    MOCK_STATE["last_command"] = {"command": cmd.command, "parameters": cmd.parameters}
    return {"status": "success", "details": MOCK_STATE["last_command"]}

def generate_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["timestamp", "value"])
    writer.writeheader()
    for row in MOCK_DATA:
        writer.writerow(row)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

@app.get("/data")
async def get_data():
    # In a real implementation, fetch CSV data directly from the device interface
    return StreamingResponse(generate_csv(), media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("driver:app", host=SERVER_HOST, port=SERVER_PORT)
```