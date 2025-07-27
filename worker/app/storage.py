import os

from core.logging_wrapper import LoggerFactory
from motor.motor_asyncio import AsyncIOMotorClient

logger = LoggerFactory.get_logger(__name__)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB", "text_analysis")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "results")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


async def store_result(result: dict):
    """
    Inserts or updates a document in MongoDB.

    Args:
        result (dict): Result to be stored, indexed by `msg_id`.
    """
    await collection.replace_one({"msg_id": result["msg_id"]}, result, upsert=True)
    logger.info(f"Résultat stocké pour {result['msg_id']}")


async def delete_result(document_id: str):
    """
    Deletes a document from MongoDB based on its ID.

    Args:
        document_id (str): The `msg_id` identifier to delete.
    """
    await collection.delete_one({"msg_id": document_id})
    logger.info(f"Résultat supprimé pour {document_id}")
