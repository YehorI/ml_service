import asyncio
import json
import logging
import os
import signal
from datetime import datetime, timezone
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLModelRepository,
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.domains.task import PredictionResult, TaskStatus
from ml_service_users.database.repositories import SqlAlchemyAltUserRepository
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository,
    SqlAlchemyAltTransactionRepository,
)
from ml_service_wallet.services.wallet_service import WalletService
from pydantic import ValidationError

from database_repository import get_service
from database_repository.service import Service
from ml_service.messaging.config import RabbitMQSettings
from ml_service.messaging.predictor import MockPredictor
from ml_service.messaging.schemas import PredictTaskMessage

logger = logging.getLogger(__name__)


class TaskHandler:
    """Process a single async ML task end-to-end against the database.

    Splits work into short DB transactions so a long predict() call doesn't
    pin a connection or block other writers:

      1. tx: PENDING -> PROCESSING
      2. predict() outside any DB transaction
      3. tx: save result + mark COMPLETED  (or)
         tx: mark FAILED + refund the wallet

    Returns True on success, False on a non-retryable failure (the caller
    should still ack the message — the DB now reflects FAILED + refund).
    """

    def __init__(self, db_service: Service, predictor: MockPredictor) -> None:
        self._db = db_service
        self._predictor = predictor

    async def handle(self, msg: PredictTaskMessage) -> bool:
        ctx = await self._mark_processing(msg)
        if ctx is None:
            return False

        task_id, user_id, model_name, input_data, cost = ctx
        try:
            output = self._predictor.predict(model_name, input_data)
        except Exception as exc:
            logger.exception("Worker: predict failed for task %s: %s", task_id, exc)
            await self._mark_failed_and_refund(task_id, user_id, cost)
            return False

        await self._mark_completed(task_id, output, cost)
        return True

    async def _mark_processing(
        self, msg: PredictTaskMessage
    ) -> tuple[int, int, str, Any, float] | None:
        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            task = await task_repo.get_by_id(msg.task_id)
            if task is None:
                logger.error("Worker: task %s not found in DB", msg.task_id)
                return None
            if task.user.user_id != msg.user_id:
                logger.error(
                    "Worker: task %s user mismatch (msg=%s, db=%s)",
                    msg.task_id,
                    msg.user_id,
                    task.user.user_id,
                )
                return None
            if task.status != TaskStatus.PENDING:
                logger.warning(
                    "Worker: task %s status=%s (not PENDING); skipping",
                    msg.task_id,
                    task.status.value,
                )
                return None

            task._status = TaskStatus.PROCESSING  # noqa: SLF001
            await task_repo.update(task)
            return (
                task.task_id,
                task.user.user_id,
                task.model.name,
                task.input_data,
                float(task.model.cost_per_request),
            )

    async def _mark_completed(self, task_id: int, output: dict, cost: float) -> None:
        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            result_repo = SqlAlchemyAltPredictionResultRepository(self._db)
            task = await task_repo.get_by_id(task_id)
            if task is None:
                logger.error("Worker: task %s vanished before completion", task_id)
                return

            await result_repo.save(
                PredictionResult(
                    result_id=0,
                    task_id=task_id,
                    output_data=output,
                    credits_charged=cost,
                )
            )
            task._status = TaskStatus.COMPLETED  # noqa: SLF001
            task._completed_at = datetime.now(timezone.utc)  # noqa: SLF001
            await task_repo.update(task)

    async def _mark_failed_and_refund(self, task_id: int, user_id: int, cost: float) -> None:
        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            user_repo = SqlAlchemyAltUserRepository(self._db)
            balance_repo = SqlAlchemyAltBalanceRepository(self._db)
            tx_repo = SqlAlchemyAltTransactionRepository(self._db)
            wallet_service = WalletService(balance_repo, tx_repo)

            task = await task_repo.get_by_id(task_id)
            user = await user_repo.get_by_id(user_id)
            wallet = await balance_repo.get_by_user_id(user_id)
            if task is None or user is None or wallet is None:
                logger.error(
                    "Worker: cannot refund task=%s user=%s (missing rows)",
                    task_id,
                    user_id,
                )
                return

            task._status = TaskStatus.FAILED  # noqa: SLF001
            task._completed_at = datetime.now(timezone.utc)  # noqa: SLF001
            await task_repo.update(task)

            await wallet_service.refund_for_task(
                user=user,
                wallet=wallet,
                task_id=task_id,
                amount=cost,
            )


class PredictWorker:
    def __init__(
        self,
        settings: RabbitMQSettings,
        db_service: Service,
        predictor: MockPredictor | None = None,
        worker_id: str | None = None,
    ) -> None:
        self._settings = settings
        self._handler = TaskHandler(db_service, predictor or MockPredictor())
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
            await queue.consume(self._consume)
            await self._stop_event.wait()
        finally:
            await connection.close()
            logger.info("Worker %s stopped", self._worker_id)

    def stop(self) -> None:
        self._stop_event.set()

    async def _consume(self, message: AbstractIncomingMessage) -> None:
        try:
            payload = json.loads(message.body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("Worker %s: invalid JSON %s: %s", self._worker_id, message.message_id, exc)
            await message.reject(requeue=False)
            return

        try:
            task = PredictTaskMessage.model_validate(payload)
        except ValidationError as exc:
            logger.error(
                "Worker %s: schema validation failed %s: %s",
                self._worker_id,
                message.message_id,
                exc.errors(),
            )
            await message.reject(requeue=False)
            return

        try:
            await self._handler.handle(task)
        except Exception:
            logger.exception("Worker %s: unhandled error for task %s", self._worker_id, task.task_id)
            await message.reject(requeue=False)
            return

        await message.ack()


async def run_worker() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = RabbitMQSettings.from_env()
    db_service = get_service()
    worker = PredictWorker(settings=settings, db_service=db_service)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()
