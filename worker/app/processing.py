import asyncio
import time
import random
from concurrent.futures import ProcessPoolExecutor

from app.storage import store_result
from app.publisher import publish_result
from app.models.message_data import MessageData

executor = ProcessPoolExecutor()

def heavy_analysis(data: MessageData) -> dict:
    # Simule tache métier avec un délai IO-bound entre 2 et 15 secondes
    duration = random.randint(2, 15)
    time.sleep(duration)

    return {
        "msg_id": data.msg_id,
        "user_id": data.user_id,
        "text": data.text,
        "type": data.type,
        "timestamp": data.timestamp,
        "status": "done",
        "duration": duration
    }

async def process_message(data: MessageData):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, heavy_analysis, data)
    await store_result(result)
    await publish_result(result)
    print(f"Message traité : {result['msg_id']}")
