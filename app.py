from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os
import datetime

VERSION_NUMBER = "0.1.0"

app = FastAPI()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["ralf-test"]
collection = db["questions"]

class Entry(BaseModel):
    name: str
    value: str
    prompt: str
    response: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now().isoformat(),
        version=VERSION_NUMBER
    )

@app.post("/add")
def add_entry(entry: Entry):
    # Check for duplicates based on the question
    existing = collection.find_one({"question": entry.prompt})
    if existing:
        return {"_id": str(existing["_id"]), "message": "Duplicate entry, returning existing record"}
    else:
        result = collection.insert_one(entry.dict())

    if result.inserted_id:
        return {"id": str(result.inserted_id), "message": "Entry added"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add entry")
