import asyncio
import time
import random
import hashlib

from concurrent.futures import ProcessPoolExecutor

from app.storage import store_result, delete_result
from app.publisher import publish_result
from app.models.message_data import MessageData

executor = ProcessPoolExecutor()

def heavy_analysis(data: MessageData) -> dict:
    # Simule tache métier avec un délai IO-bound entre 2 et 15 secondes
    duration = random.randint(2, 15)
    time.sleep(duration)

    # Charge CPU légère
    _ = sum(i * i for i in range(10_000))

    # Scoring factice
    text_hash = int(hashlib.md5(data.text.encode()).hexdigest(), 16)
    score = text_hash % 100

    return {
        "msg_id": data.msg_id,
        "user_id": data.user_id,
        "text": data.text,
        "type": data.type,
        "timestamp": data.timestamp,
        "status": "done",
        "duration": duration,
        "score": score
    }

async def process_message(data: MessageData):
    if data.type == "update":
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, heavy_analysis, data)
        await store_result(result)
        await publish_result(result)
        print(f"Message traité : {data.msg_id} (update)")

    elif data.type == "delete":
        await delete_result(data.msg_id)
        print(f"Document supprimé : {data.msg_id} (delete)")

    else:
        print(f"Type inconnu : {data.type}")