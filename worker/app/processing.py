import asyncio
import random
import time
from concurrent.futures import ProcessPoolExecutor

from app.models.message_data import MessageData
from app.publisher import publish_result
from app.storage import delete_result, store_result
from core.logging_wrapper import LoggerFactory

logger = LoggerFactory.get_logger(__name__)
executor = ProcessPoolExecutor(max_workers=4)


def heavy_analysis(data: MessageData) -> dict:
    """
    Simule une tâche métier intensive (IO + CPU).

    - Ajoute un délai aléatoire en 2 et 15 secondes.
    - Fait un calcul de hash du texte.
    - Retourne un dictionnaire enrichi.

    Args:
        data (MessageData): Données du message.

    Returns:
        dict: Résultat enrichi avec durée, score, etc.
    """
    # Simule tache métier avec un délai IO-bound entre 2 et 15 secondes
    duration = random.randint(2, 15)
    time.sleep(duration)

    # Charge CPU légère
    _ = sum(i * i for i in range(10_000))

    # Scoring factice
    if data.text:
        score = hash(data.text) % 100
    else:
        score = None

    result = {
        "msg_id": data.msg_id,
        "user_id": data.user_id,
        "text": data.text,
        "type": data.type,
        "timestamp": data.timestamp,
        "status": "done",
        "duration": duration,
        "score": score,
    }

    result.update(data.get_extra())
    return result


async def process_message(data: MessageData):
    """
    Dirige le traitement d’un message selon son type.

    - "update" : traitement, stockage, publication.
    - "delete" : suppression MongoDB.
    - autre : log warning.

    Args:
        data (MessageData): Message structuré à traiter.
    """
    if data.type == "update":
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, heavy_analysis, data)
        store_payload = {
            k: v for k, v in result.items() if k not in {"type", "status", "duration"}
        }
        publish_payload = {
            k: v for k, v in result.items() if k in {"msg_id", "type", "status"}
        }

        await store_result(store_payload)
        await publish_result(publish_payload)
        logger.info(f"Message traité : {data.msg_id} (update)")
    elif data.type == "delete":
        await delete_result(data.msg_id)
        await publish_result(
            {"msg_id": data.msg_id, "type": "delete", "status": "deleted"}
        )
        logger.info(f"Document supprimé : {data.msg_id}")
    else:
        logger.warning(f"Type inconnu : {data.type}")
