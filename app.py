import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

import io
import os
import json
import base64
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import time
app = FastAPI()
# Google Drive Setup

drive_service = None

try:

    folder_id = os.getenv(
        "GOOGLE_DRIVE_FOLDER_ID"
    )

    service_json = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON"
    )

    if service_json:

        credentials_info = json.loads(
            service_json
        )

        credentials = (
            service_account.Credentials
            .from_service_account_info(
                credentials_info,
                scopes=[
                    "https://www.googleapis.com/auth/drive.file"
                ]
            )
        )

        drive_service = build(
            "drive",
            "v3",
            credentials=credentials
        )

        print(
            "Google Drive Connected ✅"
        )

except Exception as e:

    print(
        "Google Drive Error:",
        e
    )


def save_to_drive(image_b64):

    global last_upload_time

    if drive_service is None:
        return

    try:

        current_time = time.time()

        if (
            current_time
            - last_upload_time
            < 10
        ):
            return

        last_upload_time = (
            current_time
        )

        image_bytes = (
            base64.b64decode(
                image_b64
            )
        )

        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S.jpg"
        )

        metadata = {
            "name": filename,
            "parents": [folder_id]
        }

        media = MediaIoBaseUpload(
            io.BytesIO(image_bytes),
            mimetype="image/jpeg"
        )

        drive_service.files().create(
            body=metadata,
            media_body=media
        ).execute()

        print("Uploaded ✅")

    except Exception as e:

        print(
            "Upload Error:",
            e
        )
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
async def mobile_socket(
    ws: WebSocket
):

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

            save_to_drive(
                message
            )

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
