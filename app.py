from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("""
    <h1>Mobile Viewer Cloud Server</h1>
    <p>Server Online ✅</p>
    """)