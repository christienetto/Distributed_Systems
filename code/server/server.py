import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

app = FastAPI()

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

@app.get("/")
def serve_frontend():
    return FileResponse(static_dir / "index.html")
