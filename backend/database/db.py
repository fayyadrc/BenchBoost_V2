import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


client = MongoClient(MONGO_URI)


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


db = get_db()
if COLLECTION_NAME:
    collection = db[COLLECTION_NAME]
else:
    collection = None

# --- Chat Session Management ---
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

def get_chat_collection():
    return db["chat_sessions"]

def create_chat_session(title: str = "New Chat") -> str:
    """Create a new chat session and return its ID."""
    session_id = str(uuid.uuid4())
    collection = get_chat_collection()
    collection.insert_one({
        "session_id": session_id,
        "title": title,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "history": []
    })
    return session_id

def get_all_chat_sessions() -> List[Dict[str, Any]]:
    """Get all chat sessions sorted by updated_at desc."""
    collection = get_chat_collection()
    cursor = collection.find({}, {"_id": 0, "history": 0}).sort("updated_at", -1)
    return list(cursor)

def get_chat_history_db(session_id: str) -> Optional[List[Dict[str, Any]]]:
    """Get history for a session."""
    collection = get_chat_collection()
    doc = collection.find_one({"session_id": session_id}, {"_id": 0, "history": 1})
    if doc:
        return doc.get("history", [])
    return None

def save_chat_message(session_id: str, message: Dict[str, Any]):
    """Append a message to a session's history."""
    collection = get_chat_collection()
    
    # If this is the first user message, update the title
    if message.get("type") == "HumanMessage":
        doc = collection.find_one({"session_id": session_id}, {"history": 1})
        if not doc or not doc.get("history"):
             # Use first 30 chars as title
             new_title = message.get("content", "")[:30] + "..."
             collection.update_one(
                 {"session_id": session_id}, 
                 {"$set": {"title": new_title}}
             )

    collection.update_one(
        {"session_id": session_id},
        {
            "$push": {"history": message},
            "$set": {"updated_at": datetime.utcnow()},
            "$setOnInsert": {"created_at": datetime.utcnow(), "title": "New Chat"}
        },
        upsert=True
    )

def update_chat_title(session_id: str, title: str):
    """Update the title of a chat session."""
    collection = get_chat_collection()
    collection.update_one(
        {"session_id": session_id},
        {"$set": {"title": title}}
    )

def delete_chat_session(session_id: str):
    """Delete a chat session."""
    collection = get_chat_collection()
    collection.delete_one({"session_id": session_id})