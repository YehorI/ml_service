import asyncio
from datetime import datetime

from database_repository.models import MLTaskORM, PredictionResultORM
from database_repository.models.task import TaskStatusORM
from loguru import logger
from ml_service_common.messaging.schemas import WorkerTaskMessage
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from sqlalchemy import func, select


class WorkerMessageHandler:
    def __init__(
        self,
        db: SQLAlchemyService,
        worker_id: str,
        model_pipeline,
    ) -> None:
        self._db = db
        self._worker_id = worker_id
        self._pipeline = model_pipeline

    async def handle(self, body: bytes) -> None:
        try:
            message = WorkerTaskMessage.model_validate_json(body)
        except Exception as exc:
            logger.error(f"[{self._worker_id}] failed to parse message, discarding: {exc}")
            return
        logger.info(f"[{self._worker_id}] received task_id={message.task_id} model={message.model!r}")

        text = " ".join(f"{k}={v}" for k, v in message.features.items())
        result = await asyncio.to_thread(self._pipeline, text)
        prediction = float(result[0]["score"])

        logger.info(f"[{self._worker_id}] prediction={prediction:.4f} for task_id={message.task_id}")

        async with self._db.transaction():
            task_orm = (
                await self._db.session.execute(
                    select(MLTaskORM).where(
                        func.json_extract_path_text(MLTaskORM.input_data, "_task_uuid") == message.task_id
                    )
                )
            ).scalar_one_or_none()

            if task_orm is None:
                logger.error(f"[{self._worker_id}] task_id={message.task_id} not found in DB, skipping")
                return

            result_orm = PredictionResultORM(
                task_id=task_orm.id,
                output_data={
                    "prediction": prediction,
                    "worker_id": self._worker_id,
                    "status": "success",
                },
                credits_charged=0.0,
                created_at=datetime.utcnow(),
            )
            self._db.session.add(result_orm)
            task_orm.status = TaskStatusORM.COMPLETED
            task_orm.completed_at = datetime.utcnow()

        logger.info(f"[{self._worker_id}] completed task_id={message.task_id}")
