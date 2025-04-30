import os
import csv
from io import StringIO
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
import uvicorn
import asyncio

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

# Simulated Device State (for demonstration)
DEVICE_INFO = {
    "device_name": "1",
    "device_model": "1",
    "manufacturer": "1",
    "device_type": "1"
}
DEVICE_DATA_POINTS = ["temperature", "humidity", "pressure"]
DEVICE_DATA = {
    "temperature": "22.5",
    "humidity": "55.0",
    "pressure": "101.2"
}
SUPPORTED_COMMANDS = ["reset", "calibrate"]

app = FastAPI()

class CommandRequest(BaseModel):
    command: str
    params: dict = {}

@app.get("/info")
async def get_info():
    return JSONResponse(content=DEVICE_INFO)

@app.get("/data")
async def get_data():
    # Simulate retrieving data from the device (replace with actual protocol as needed)
    # Data is returned in CSV format
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(DEVICE_DATA_POINTS)
    writer.writerow([DEVICE_DATA[k] for k in DEVICE_DATA_POINTS])
    output.seek(0)
    return PlainTextResponse(content=output.read(), media_type="text/csv")

@app.post("/cmd")
async def send_command(cmd_req: CommandRequest):
    # Simulate sending a command to the device and getting a response
    if cmd_req.command not in SUPPORTED_COMMANDS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Unsupported command"}
        )
    # Simulated command execution
    result = {"result": "success", "command": cmd_req.command, "params": cmd_req.params}
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)
