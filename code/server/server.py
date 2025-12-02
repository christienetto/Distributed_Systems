from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://mongodb:27017")
db = client["mydatabase"]
notes = db["notes"]

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


