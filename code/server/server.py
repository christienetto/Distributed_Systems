from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import json
import asyncio
import threading
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
mongo_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/?replicaSet=rs0")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
notes = db["notes"]

# Store active WebSocket connections
active_connections: List[WebSocket] = []

change_stream_task = None
main_loop = None # Fixes “no current event loop in thread” error

# Serve frontend static files
static_dir = Path(__file__).parent / "static"
app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")


SHARED_NOTE_ID = "shared_note"

def get_or_create_shared_note():
    note = notes.find_one({"_id": SHARED_NOTE_ID})
    if not note:
        new_note = {
            "_id": SHARED_NOTE_ID,
            "title": "Shared Note",
            "content": "Start typing to collaborate..."
        }
        notes.insert_one(new_note)
        return {
            "title": new_note["title"],
            "content": new_note["content"]
        }
    return {
        "title": note.get("title", "Shared Note"),
        "content": note.get("content", "")
    }

@app.get("/test-db")
def test_db():
    note = get_or_create_shared_note()
    return {
        "status": "Connected to MongoDB",
        "note": note
    }

async def broadcast_to_all(message: dict, sender: WebSocket = None):
    """Broadcast message to all connected clients except sender"""
    dead_connections = []
    for connection in active_connections:
        if connection != sender:
            try:
                await connection.send_json(message)
            except:
                # Mark dead connections for removal
                dead_connections.append(connection)
    
    # Remove dead connections
    for dead_conn in dead_connections:
        if dead_conn in active_connections:
            active_connections.remove(dead_conn)

def watch_database_changes():
    global main_loop
    try:
        # Watch for changes in the notes collection
        with notes.watch([
            {"$match": {"operationType": {"$in": ["insert", "update", "replace"]}}}
        ]) as stream:
            for change in stream:
                # Create the message to broadcast
                if change["operationType"] in ["insert", "update", "replace"]:
                    doc = change.get("fullDocument", {})
                    if doc:
                        message = {
                            "type": "db_change",
                            "operation": change["operationType"],
                            "note": {
                                "title": doc.get("title", "Untitled"),
                                "content": doc.get("content", "")
                            }
                        }
                        
                        # Schedule the broadcast in the main event loop
                        if main_loop is not None:
                            asyncio.run_coroutine_threadsafe(
                                broadcast_to_all(message),
                                main_loop
                            )
    except Exception as e:
        print(f"Change stream error: {e}")

async def start_change_stream():
    global change_stream_task, main_loop
    if change_stream_task is None:
        main_loop = asyncio.get_running_loop()
        change_stream_task = main_loop.run_in_executor(None, watch_database_changes)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Start change stream monitoring if this is the first connection
    if len(active_connections) == 1:
        await start_change_stream()
    
    # Send initial shared note to new client
    shared_note = get_or_create_shared_note()
    await websocket.send_json({
        "type": "init", 
        "note": shared_note
    })

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
                note_data = {
                    "title": message.get("title", "Shared Note"),
                    "content": message["content"]
                }
                
                notes.update_one(
                    {"_id": SHARED_NOTE_ID},
                    {"$set": note_data},
                    upsert=True
                )
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
def serve_frontend():
    return FileResponse(static_dir / "index.html")
