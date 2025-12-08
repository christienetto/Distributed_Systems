from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import json
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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

# Store active WebSocket connections
active_connections: List[WebSocket] = []

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

async def broadcast_to_all(message: dict, sender: WebSocket = None):
    """Broadcast message to all connected clients except sender"""
    for connection in active_connections:
        if connection != sender:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                active_connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send initial notes to new client
    all_notes = list(notes.find({}, {"_id": 0}))
    await websocket.send_json({"type": "init", "notes": all_notes})

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "text_change":
                # Broadcast text changes to other clients
                await broadcast_to_all({
                    "type": "text_change",
                    "content": message["content"]
                }, websocket)
            
            elif message["type"] == "save_note":
                # Save to database and broadcast to all clients
                note = {
                    "title": message.get("title", "Untitled"),
                    "content": message["content"]
                }
                
                # Clear existing notes and insert new one (simple approach)
                notes.delete_many({})
                result = notes.insert_one(note)
                
                # Broadcast saved note to all clients
                await broadcast_to_all({
                    "type": "note_saved",
                    "note": {"title": note["title"], "content": note["content"]}
                }, websocket)
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
def serve_frontend():
    return FileResponse(static_dir / "index.html")
