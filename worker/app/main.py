import asyncio
import signal
from app.consumer import consume_messages, active_tasks

shutdown_event = asyncio.Event()

def setup_signal_handlers():
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_event.set)

async def main():
    setup_signal_handlers()
    consumer_task = asyncio.create_task(consume_messages())

    await shutdown_event.wait()
    print("Signal reçu. Arrêt demandé..")

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Consommation annulée..")

    print("En attente des tâches restantes..")

    await asyncio.gather(*active_tasks, return_exceptions=True)
    print("Arrêt terminé.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interruption via CTRL+C")