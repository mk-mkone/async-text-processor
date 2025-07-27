import json
import os

import aio_pika
from core.logging_wrapper import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

AMQP_URL = os.getenv("AMQP_URL")
OUTPUT_QUEUE = os.getenv("OUTPUT_QUEUE")


async def publish_result(result: dict):
    """
    Publishes the final result to the `processed_texts` queue.

    Args:
        result (dict): Result to send to RabbitMQ.
    """
    try:
        connection = await aio_pika.connect_robust(AMQP_URL)
        channel = await connection.channel()
        await channel.declare_queue(OUTPUT_QUEUE, durable=True)

        message = aio_pika.Message(
            body=json.dumps(result).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await channel.default_exchange.publish(message, routing_key=OUTPUT_QUEUE)

        logger.info(f"Message publié dans '{OUTPUT_QUEUE}' : {result.get('msg_id')}")
        await connection.close()

    except Exception as e:
        logger.error(f"Erreur publication message : {e}")


async def republish_with_retries(
    original_message: aio_pika.IncomingMessage, retries: int
):
    """
    Republishes a message to RabbitMQ with an incremented retry counter.

    Args:
        original_message (aio_pika.IncomingMessage): The original message to republish.
        retries (int): Current retry count.
    """
    try:
        connection = await aio_pika.connect_robust(AMQP_URL)
        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=original_message.body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={**original_message.headers, "x-retries": retries},
            ),
            routing_key=original_message.routing_key,
        )

        logger.warning(f"Message re-publié (retry={retries})")
        await connection.close()

    except Exception as e:
        logger.error(f"Re-publication échouée : {e}")
