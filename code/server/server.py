from fastapi import FastAPI, WebSocket
import os
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mongo_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
notes = db["notes"]

# Serve frontend static files
static_dir = Path(__file__).parent / "static"
app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

@app.get("/test-db")
def test_db():
    note = {
        "title": "Test Note",
        "content": "This is a test note."
    }

    result = notes.insert_one(note)
    all_notes = list(notes.find({}, {"_id": 0}))

    return {
        "status": "Connected to MongoDB",
        "inserted_id": str(result.inserted_id),
        "notes": all_notes
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    all_notes = list(notes.find({}, {"_id": 0}))
    await websocket.send_json({"notes": all_notes})

    while True:
        await websocket.receive_text()

@app.get("/")
def serve_frontend():
    return FileResponse(static_dir / "index.html")
