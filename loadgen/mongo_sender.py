from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import nltk
nltk.download('words')
from nltk.corpus import words

def send_texts():
    word_bank = words.words()
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydb"]
    collection = db["texts"]

    bulk = []
    base_time = datetime.now() - timedelta(days=360)

    for i in range(2_000_000):
        text = " ".join(random.choices(word_bank, k=random.randint(0, 50)))
        doc = {
            "msg_id": f"msg_{i}",
            "user_id": f"u_{random.randint(1, 2499999)}",
            "text": text,
            "timestamp": (base_time + timedelta(seconds=i*3)).isoformat()
        }
        bulk.append(doc)

        if i % 10_000 == 0 and i > 0:
            collection.insert_many(bulk)
            print(f"Inserted {i} documents")
            bulk = []

    if bulk:
        collection.insert_many(bulk)
        print("Inserted final batch")
