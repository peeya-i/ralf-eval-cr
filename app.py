from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os

app = FastAPI()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["ralf-test"]
collection = db["questions"]

class Entry(BaseModel):
    name: str
    value: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now().isoformat(),
        version=VERSION_NUMBER
    )

@app.post("/add")
def add_entry(entry: Entry):
    # Check for duplicates based on the question
    existing = collection.find_one({"question": entry.question})
    if existing:
        return {"_id": str(existing["_id"]), "message": "Duplicate entry, returning existing record"}
    else:
        result = collection.insert_one(entry.dict())

    if result.inserted_id:
        return {"id": str(result.inserted_id), "message": "Entry added"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add entry")
