import asyncio
import json
import logging
import os
import signal

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from ml_service.messaging.config import RabbitMQSettings
from ml_service.messaging.predictor import MockPredictor
from ml_service.messaging.schemas import PredictTaskMessage

logger = logging.getLogger(__name__)


class PredictWorker:
    def __init__(
        self,
        settings: RabbitMQSettings,
        predictor: MockPredictor | None = None,
        worker_id: str | None = None,
    ) -> None:
        self._settings = settings
        self._predictor = predictor or MockPredictor()
        self._worker_id = worker_id or os.getenv("HOSTNAME", "worker")
        self._stop_event = asyncio.Event()

    async def run(self) -> None:
        connection = await aio_pika.connect_robust(self._settings.url)
        try:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=self._settings.prefetch_count)
            queue = await channel.declare_queue(self._settings.queue_name, durable=True)
            logger.info(
                "Worker %s consuming from queue=%s",
                self._worker_id,
                self._settings.queue_name,
            )
            await queue.consume(self._handle)
            await self._stop_event.wait()
        finally:
            await connection.close()
            logger.info("Worker %s stopped", self._worker_id)

    def stop(self) -> None:
        self._stop_event.set()

    async def _handle(self, message: AbstractIncomingMessage) -> None:
        try:
            payload = json.loads(message.body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            logger.error(
                "Worker %s: invalid JSON in message %s: %s",
                self._worker_id,
                message.message_id,
                exc,
            )
            await message.reject(requeue=False)
            return

        try:
            task = PredictTaskMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error(
                "Worker %s: validation failed for message %s: %s",
                self._worker_id,
                message.message_id,
                exc.errors(),
            )
            await message.reject(requeue=False)
            return

        try:
            result = self._predictor.predict(task)
        except Exception as exc:
            logger.exception(
                "Worker %s: prediction failed for task %s: %s",
                self._worker_id,
                task.task_id,
                exc,
            )
            await message.reject(requeue=False)
            return

        logger.info(
            "Worker %s processed task %s model=%s output=%s",
            self._worker_id,
            result.task_id,
            result.model_name,
            result.output_data,
        )
        await message.ack()


async def run_worker() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = RabbitMQSettings.from_env()
    worker = PredictWorker(settings)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()
