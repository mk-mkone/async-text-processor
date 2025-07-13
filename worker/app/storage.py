import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB", "text_analysis")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "results")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

async def store_result(result: dict):
    await collection.replace_one(
        {"msg_id": result["msg_id"]},
        result,
        upsert=True
    )

async def delete_result(document_id: str):
    await collection.delete_one({"msg_id": document_id})