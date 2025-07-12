import argparse
import asyncio
import random
import yaml
import nltk
nltk.download("words")
from nltk.corpus import words
from datetime import datetime, timedelta
from rabbit_sender import send_message
from mongo_sender import send_texts

def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

async def bulk_send(count: int, msg_type: str):
    word_bank = words.words()
    base_time = datetime.now() - timedelta(days=5)
    print(count, msg_type)

    for i in range(count):
        text = " ".join(random.choices(word_bank, k=random.randint(1, 25)))
        msg = {
            "msg_id": f"msg_{i}",
            "user_id": f"u_{random.randint(1, 2499999)}",
            "text": text,
            "timestamp": (base_time + timedelta(seconds=i*3)).isoformat(),
            "type": msg_type
        }

        await send_message(msg)
        if i % 100 == 0:
            print(f"[{i}] messages envoyés...")

def main():
    config = load_config()

    parser = argparse.ArgumentParser(description="Load Generator RabbitMQ et mongoDB")
    parser.add_argument("--cible", type=str, default="rabbit", help="Service cible")

    args = parser.parse_args()
    if args.cible == "rabbit":
        count = config.get("count")
        msg_type = config.get("type")
        asyncio.run(bulk_send(count, msg_type))
    elif args.cible == "mongo":
        send_texts()
    else:
        print("ERROR - Unknown cible service")


if __name__ == "__main__":
    main()
