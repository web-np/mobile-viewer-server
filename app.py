import os
import io
import json
import base64
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from datetime import datetimefrom fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
SAVE_FOLDER = "screenshots"
os.makedirs(SAVE_FOLDER, exist_ok=True)
app = FastAPI()
# Google Drive Setup
FOLDER_ID = os.getenv(
    "GOOGLE_DRIVE_FOLDER_ID"
)

SERVICE_ACCOUNT_JSON = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON"
)

credentials_info = json.loads(
    SERVICE_ACCOUNT_JSON
)

credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=[
        "https://www.googleapis.com/auth/drive.file"
    ]
)

drive_service = build(
    "drive",
    "v3",
    credentials=credentials
)


def upload_to_drive(
    image_bytes
):

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S.jpg"
    )

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(image_bytes),
        mimetype="image/jpeg"
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(
        "Uploaded:",
        file.get("id")
    )
latest_frame = None
connected_devices = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Mobile Viewer</title>
</head>
<body style="font-family:Arial;text-align:center;padding:20px;">
<h1>Mobile Viewer Dashboard</h1>

<div id="status">Waiting...</div>

<img id="screen"
style="width:320px;border:2px solid #444;
border-radius:12px;" />

<script>
const ws = new WebSocket(
(location.protocol === "https:" ? "wss://" : "ws://")
+ location.host + "/viewer"
);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    document.getElementById("status")
    .innerText =
    "Connected Devices: " + data.devices;

    if(data.frame){
        document.getElementById("screen").src =
        "data:image/jpeg;base64," + data.frame;
    }
};
</script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global latest_frame, connected_devices

    await websocket.accept()
    connected_devices += 1

    try:
        while True:
            message = await websocket.receive_text()

            if message:
                latest_frame = message
                try:

    image_bytes = base64.b64decode(
        message
    )

    upload_to_drive(
        image_bytes
    )

except Exception as e:

    print(
        "Drive upload error:",
        e
    )
try:

    image_data = base64.b64decode(
        message
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S.jpg"
    )

    filepath = os.path.join(
        SAVE_FOLDER,
        filename
    )

    with open(
        filepath,
        "wb"
    ) as f:
        f.write(image_data)

except Exception as e:
    print("Save error:", e)
    except WebSocketDisconnect:
        pass

    finally:
        connected_devices -= 1


@app.websocket("/viewer")
async def viewer_socket(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:

            await websocket.send_json({
                "devices": connected_devices,
                "frame": latest_frame
            })

            await asyncio.sleep(0.3)

    except WebSocketDisconnect:
        pass
