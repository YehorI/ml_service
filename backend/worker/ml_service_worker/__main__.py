import asyncio
import os
import signal

from loguru import logger

from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings
from ml_service_common.messaging.settings import MessagingSettings
from ml_service_worker.worker import PredictWorker


async def run() -> None:
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    messaging = MessagingSettings()
    database = SQLAlchemySettings()
    worker = PredictWorker(messaging=messaging, database=database)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(run())
