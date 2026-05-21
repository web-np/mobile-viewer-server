import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

latest_frame = None
connected_devices = 0


HTML = """
<html>
<body style="text-align:center;font-family:Arial">
<h1>Mobile Viewer</h1>
<h3 id="status">
Connected Devices: 0
</h3>

<img id="screen"
style="width:320px;border:2px solid black;"/>

<script>

const ws = new WebSocket(
(location.protocol==="https:"?
"wss://":"ws://")
+ location.host + "/viewer"
);

ws.onmessage = (event)=>{

    const data =
    JSON.parse(event.data);

    document.getElementById(
    "status"
    ).innerText =
    "Connected Devices: "
    + data.devices;

    if(data.frame){

        document.getElementById(
        "screen"
        ).src =
        "data:image/jpeg;base64,"
        + data.frame;
    }
}

</script>
</body>
</html>
"""


@app.get("/")
async def home():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def mobile_socket(ws: WebSocket):

    global latest_frame
    global connected_devices

    await ws.accept()

    connected_devices += 1

    try:

        while True:

            message = (
                await ws.receive_text()
            )

            latest_frame = message

    except:
        pass

    connected_devices -= 1


@app.websocket("/viewer")
async def viewer_socket(
    ws: WebSocket
):

    await ws.accept()

    while True:

        await ws.send_json({
            "devices":
            connected_devices,

            "frame":
            latest_frame
        })

        await asyncio.sleep(0.5)
