import aio_pika
import json
import random
from datetime import datetime, timedelta
from nltk.corpus import words

RABBITMQ_URL = "amqp://guest:guest@localhost/"
QUEUE_NAME = "incoming_texts"

word_bank = words.words()

async def bulk_send_rabbit(count: int, update_ratio: float):
    """
    Envoie un nombre X de messages vers RabbitMQ, avec un ratio update/delete.
    """
    base_time = datetime.now() - timedelta(days=5)
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    for i in range(count):
        msg_type = "update" if random.random() < update_ratio else "delete"
        msg = {
            "msg_id": f"msg_{i}",
            "type": msg_type,
        }

        if msg_type == "update":
            msg.update({
                "user_id": f"u_{random.randint(1, 2499999)}",
                "text": " ".join(random.choices(word_bank, k=random.randint(3, 25))),
                "timestamp": (base_time + timedelta(seconds=i*3)).isoformat(),
            })

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(msg).encode()),
            routing_key=QUEUE_NAME
        )

        if i % 1000 == 0 and i > 0:
            print(f"[{i}] messages envoyés...")

    await connection.close()
