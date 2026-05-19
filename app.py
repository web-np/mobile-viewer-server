from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

connected_devices = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Mobile Viewer</title>
</head>
<body style="font-family:Arial;text-align:center;padding:40px;">
    <h1>Mobile Viewer Dashboard</h1>
    <h2>Server Online ✅</h2>
    <div id="status">Waiting for device...</div>
</body>

<script>
const ws = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://")
    + location.host + "/viewer"
);

ws.onmessage = (event) => {
    document.getElementById("status").innerText =
        event.data;
};
</script>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global connected_devices

    await websocket.accept()
    connected_devices += 1

    try:
        while True:
            message = await websocket.receive_text()
            print("Device:", message)

    except:
        connected_devices -= 1


@app.websocket("/viewer")
async def viewer_socket(websocket: WebSocket):
    await websocket.accept()

    while True:
        await websocket.send_text(
            f"Connected Devices: {connected_devices}"
        )
