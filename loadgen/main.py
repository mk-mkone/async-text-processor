import asyncio
import yaml
from rabbit_sender import bulk_send_rabbit
from mongo_sender import bulk_send_mongo

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    cible = config.get("cible").lower()
    count = int(config.get("nb_messages", 1000))
    ratio = float(config.get("update_ratio", 0.7))

    if cible == "rabbit":
        asyncio.run(bulk_send_rabbit(count, ratio))
    elif cible == "mongo":
        bulk_send_mongo(count)

if __name__ == "__main__":
    main()
