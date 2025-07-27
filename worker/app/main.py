import asyncio
import signal

from app.consumer import active_tasks, consume_messages
from core.logging_wrapper import LoggerFactory

LoggerFactory._configure()
logger = LoggerFactory.get_logger(__name__)

shutdown_event = asyncio.Event()


def setup_signal_handlers():
    """
    Configure signal handlers for SIGINT and SIGTERM.

    Triggers a graceful shutdown by setting an asyncio event.
    """
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_event.set)


async def main():
    """
    Main entry point of the asynchronous worker.

    - Starts consuming messages.
    - Waits for a shutdown signal.
    - Cancels the consumption task.
    - Waits for any remaining active tasks to complete.
    """
    logger.info("Démarrage du worker...")
    setup_signal_handlers()
    consumer_task = asyncio.create_task(consume_messages())

    await shutdown_event.wait()
    logger.info("Signal reçu. Arrêt demandé..")

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Consommation annulée..")

    logger.info("En attente des tâches restantes..")

    await asyncio.gather(*active_tasks, return_exceptions=True)
    logger.info("Arrêt terminé.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Interruption via CTRL+C")
