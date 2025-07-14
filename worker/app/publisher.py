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


async def republish_with_retries(original_message: aio_pika.IncomingMessage, retries: int):
    try:
        connection = await aio_pika.connect_robust(AMQP_URL)
        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=original_message.body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={**original_message.headers, "x-retries": retries}
            ),
            routing_key=original_message.routing_key
        )

        print(f"Message re-publié (tentative {retries})")

        await connection.close()

    except Exception as e:
        print(f"Re-publication échouée : {e}")
