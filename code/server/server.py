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


SHARED_NOTE_ID = "shared_note"

def get_or_create_shared_note():

    note = notes.find_one({"_id": SHARED_NOTE_ID}, {"_id": 0})
    if not note:
        new_note = {
            "_id": SHARED_NOTE_ID,
            "title": "Shared Note",
            "content": "Write something..."
        }
        notes.insert_one(new_note)

        return {
            "title": new_note["title"],
            "content": new_note["content"]
        }

    return note

@app.get("/test-db")
def test_db():
    
    note = get_or_create_shared_note()
    return {
        "status": "Connected to MongoDB",
        "note": note
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    note = get_or_create_shared_note()
    await websocket.send_json({"note": note})

    while True:
        await websocket.receive_text()

@app.get("/")
def serve_frontend():
    return FileResponse(static_dir / "index.html")
