from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

connected_devices = 0


@app.get("/")
async def root():
    return HTMLResponse(f"""
    <html>
    <body style="font-family:Arial;text-align:center;padding:40px;">
        <h1>Mobile Viewer Cloud Server</h1>
        <h2>Server Online ✅</h2>
        <h3>Connected Devices: {connected_devices}</h3>
    </body>
    </html>
    """)


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
