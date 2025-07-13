import aio_pika
import asyncio
import json
import os

from app.processing import process_message
from app.models.message_data import MessageData
from app.publisher import republish_with_retries
from core.logging_wrapper import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
AMQP_URL = os.getenv("AMQP_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS"))

semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
active_tasks = set()

async def consume_messages():
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=MAX_CONCURRENT_TASKS)

    dlx = await channel.declare_exchange("dlx", aio_pika.ExchangeType.DIRECT, durable=True)
    dlq = await channel.declare_queue("failed_texts", durable=True)
    await dlq.bind(dlx, routing_key="failed_texts")

    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "failed_texts"
        }
    )

    logger.info(f"En écoute sur la file '{QUEUE_NAME}' avec {MAX_CONCURRENT_TASKS} workers")

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
                logger.info(f"[REÇU] {data.msg_id} ({data.type})")
                await process_message(data)

    except Exception as e:
        retries = int(message.headers.get("x-retries", 0)) + 1
        if retries >= MAX_RETRIES:
            await message.nack(requeue=False)
            logger.warning(f"Message abandonné après {retries} tentatives.")
        else:
            await republish_with_retries(message, retries)
            await message.ack()
            logger.warning(f"Re-publication (retry {retries})")
