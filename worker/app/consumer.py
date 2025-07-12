import aio_pika
import asyncio
import json
import os

from app.processing import process_message
from app.models.message_data import MessageData

AMQP_URL = os.getenv("AMQP_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS"))

semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
active_tasks = set()

async def consume_messages():
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=MAX_CONCURRENT_TASKS)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    print(f"En écoute sur la file {QUEUE_NAME} avec {MAX_CONCURRENT_TASKS} workers")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            task = asyncio.create_task(handle_message(message))
            active_tasks.add(task)
            task.add_done_callback(active_tasks.discard)

async def handle_message(message: aio_pika.IncomingMessage):
    try:
        async with semaphore:
            async with message.process():
                raw_data = json.loads(message.body)
                data = MessageData(raw_data)
                print(f"[REÇU] {data.msg_id} ({data.type})")
                await process_message(data)
    except asyncio.CancelledError:
        print(f"Traitement annulé pour message : {message!r}")
        await message.nack(requeue=True)
    except Exception as e:
        print(f"Erreur de traitement : {e}")
        await message.nack(requeue=False)