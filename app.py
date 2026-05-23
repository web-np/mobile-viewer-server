import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

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
oauth_credentials = None
def get_flow():

    oauth_json = json.loads(
        os.getenv(
            "GOOGLE_OAUTH_JSON"
        )
    )

    flow = Flow.from_client_config(
        oauth_json,
        scopes=[
            "https://www.googleapis.com/auth/drive.file"
        ],
        redirect_uri="https://mobile-viewer-server.onrender.com/oauth2callback"
    )

    return flow
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

        print("Upload success ✅")

        print("Uploaded ✅")

    except Exception as e:

        print(
            "Upload Error:",
            e
        )
latest_frame = None
connected_devices = 0
last_upload_time = 0

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
@app.get("/login")
async def login():

def get_flow():

    oauth_json = json.loads(
        os.getenv(
            "GOOGLE_OAUTH_JSON"
        )
    )

    flow = Flow.from_client_config(
        oauth_json,
        scopes=[
            "https://www.googleapis.com/auth/drive.file"
        ]
    )

    flow.redirect_uri = (
        "https://mobile-viewer-server.onrender.com/oauth2callback"
    )

    return flow

@app.get("/")
async def home():
    return HTMLResponse(HTML)

@app.get("/oauth2callback")
async def oauth2callback(code: str):

    flow = get_flow()

    flow.fetch_token(
        code=code
    )

    creds = flow.credentials

    global drive_service

    drive_service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return {
        "message":
        "Google Drive Connected ✅"
    }
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

  except WebSocketDisconnect:
    print("Mobile disconnected")


@app.websocket("/viewer")
async def viewer_socket(ws: WebSocket):

    await ws.accept()

    try:

        while True:

            if latest_frame:

                try:

                    await ws.send_json({
                        "image": latest_frame
                    })

                except Exception as e:

                    print(
                        "Viewer disconnected:",
                        e
                    )
                    break

            await asyncio.sleep(1)

    except Exception as e:

        print(
            "Viewer socket error:",
            e
        )
