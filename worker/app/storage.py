import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB", "text_analysis")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "results")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

async def store_result(result: dict):
    result_copy = result.copy()
    insert_result = await collection.insert_one(result_copy)
    print(f"Résultat stocké dans MongoDB avec _id={insert_result.inserted_id}")
