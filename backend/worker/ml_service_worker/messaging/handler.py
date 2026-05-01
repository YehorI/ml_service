import asyncio
from datetime import datetime

from database_repository.models import MLTaskORM, PredictionResultORM
from database_repository.models.task import TaskStatusORM
from loguru import logger
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_common.messaging.schemas import TaskCompletedMessage, WorkerTaskMessage
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from sqlalchemy import select


class WorkerMessageHandler:
    def __init__(
        self,
        db: SQLAlchemyService,
        worker_id: str,
        completed_publisher: RabbitMQPublisher,
    ) -> None:
        self._db = db
        self._worker_id = worker_id
        self._completed_publisher = completed_publisher
        self._pipelines: dict[str, object] = {}

    def _get_hf_pipeline(self, model_id: str, task: str):
        if model_id not in self._pipelines:
            from transformers import pipeline as hf_pipeline
            logger.info(f"[{self._worker_id}] Loading HuggingFace model {model_id!r}")
            self._pipelines[model_id] = hf_pipeline(task, model=model_id)
            logger.info(f"[{self._worker_id}] Loaded {model_id!r}")
        return self._pipelines[model_id]

    async def _run_huggingface(self, model_config: dict, features: dict) -> dict:
        hf_model_id = model_config.get("model_id", "")
        hf_task = model_config.get("task", "text-classification")
        if not hf_model_id:
            raise ValueError("model_config missing 'model_id' for huggingface model")

        pipeline = self._get_hf_pipeline(hf_model_id, hf_task)
        text = features.get("text") or " ".join(f"{k}={v}" for k, v in features.items())

        if hf_task == "zero-shot-classification":
            raw_labels = features.get("candidate_labels", "")
            candidate_labels = [l.strip() for l in raw_labels.split(",") if l.strip()] if raw_labels else ["positive", "negative"]
            result = await asyncio.to_thread(pipeline, text, candidate_labels)
        else:
            result = await asyncio.to_thread(pipeline, text)

        if isinstance(result, list) and result:
            return result[0] if isinstance(result[0], dict) else {"output": result[0]}
        if isinstance(result, dict):
            return result
        return {"output": result}

    async def handle(self, body: bytes) -> None:
        try:
            message = WorkerTaskMessage.model_validate_json(body)
        except Exception as exc:
            logger.error(f"[{self._worker_id}] failed to parse message, discarding: {exc}")
            return

        logger.info(f"[{self._worker_id}] task_id={message.task_id} type={message.model_type!r}")

        try:
            if message.model_type == "huggingface":
                output = await self._run_huggingface(message.provider_config, message.features)
            else:
                raise NotImplementedError(f"Unsupported model_type: {message.model_type!r}")
        except Exception as exc:
            logger.error(f"[{self._worker_id}] task_id={message.task_id} failed: {exc}")
            async with self._db.transaction():
                task_orm = (await self._db.session.execute(
                    select(MLTaskORM).where(MLTaskORM.id == message.task_id)
                )).scalar_one_or_none()
                if task_orm is not None:
                    task_orm.status = TaskStatusORM.FAILED
                    task_orm.completed_at = datetime.utcnow()
            return

        logger.info(f"[{self._worker_id}] task_id={message.task_id} output={output}")

        async with self._db.transaction():
            task_orm = (await self._db.session.execute(
                select(MLTaskORM).where(MLTaskORM.id == message.task_id)
            )).scalar_one_or_none()

            if task_orm is None:
                logger.error(f"[{self._worker_id}] task_id={message.task_id} not found, skipping")
                return

            self._db.session.add(PredictionResultORM(
                task_id=task_orm.id,
                output_data=output,
                credits_charged=message.cost_per_request,
                created_at=datetime.utcnow(),
            ))
            task_orm.status = TaskStatusORM.COMPLETED
            task_orm.completed_at = datetime.utcnow()

        await self._completed_publisher.publish(TaskCompletedMessage(
            task_id=message.task_id,
            username=message.username,
            output_data=output,
            credits_charged=message.cost_per_request,
        ))
        logger.info(f"[{self._worker_id}] completed task_id={message.task_id}")
