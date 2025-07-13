from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from nltk.corpus import words

def bulk_send_mongo(count: int):
    """
    Insère X count documents directement dans MongoDB.
    """
    word_bank = words.words()
    client = MongoClient("mongodb://localhost:27017/")
    collection = client["text_analysis"]["results"]
    base_time = datetime.now() - timedelta(days=365)
    bulk = []

    for i in range(count):
        doc = {
            "msg_id": f"msg_{i}",
            "user_id": f"u_{random.randint(1, 2499999)}",
            "text": " ".join(random.choices(word_bank, k=random.randint(1, 25))),
            "timestamp": (base_time + timedelta(seconds=i*3)).isoformat()
        }
        bulk.append(doc)

        if len(bulk) >= 10000:
            collection.insert_many(bulk)
            print(f"Inserted {len(bulk)} docs")
            bulk.clear()

    if bulk:
        collection.insert_many(bulk)
        print(f"Inserted final batch: {len(bulk)} docs")
