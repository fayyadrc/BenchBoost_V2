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