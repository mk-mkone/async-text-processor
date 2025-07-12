import aio_pika
import json
import os

RABBITMQ_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "incoming_texts")

async def send_message(payload: dict):
    if not QUEUE_NAME:
        raise ValueError("QUEUE_NAME is not set.")

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload).encode()),
        routing_key=QUEUE_NAME
    )
    await connection.close()
