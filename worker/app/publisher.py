import aio_pika
import os
import json

AMQP_URL = os.getenv("AMQP_URL")
OUTPUT_QUEUE = os.getenv("OUTPUT_QUEUE")

async def publish_result(result: dict):
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()

    await channel.declare_queue(OUTPUT_QUEUE, durable=True)

    message_body = json.dumps(result).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key=OUTPUT_QUEUE
    )

    await connection.close()
