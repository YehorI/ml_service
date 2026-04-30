from datetime import datetime

import socketio
from loguru import logger
from ml_service_common.messaging.schemas import PredictRequestMessage
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLTaskRepository, SqlAlchemyAltPredictionResultRepository)
from ml_service_model.domains.stored_model import StoredMLModel
from ml_service_model.domains.task import MLTask, PredictionResult, TaskStatus


class PredictMessageHandler:
    def __init__(self, db: SQLAlchemyService, sio: socketio.AsyncServer) -> None:
        self._db = db
        self._sio = sio

    async def handle(self, body: bytes) -> None:
        message = PredictRequestMessage.model_validate_json(body)
        logger.info(f"Processing task_id={message.task_id} model={message.model_name!r}")
        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            result_repo = SqlAlchemyAltPredictionResultRepository(self._db)

            task = await task_repo.get_by_id(message.task_id)
            if task is None:
                logger.error(f"Task id={message.task_id} not found, skipping")
                return

            model = StoredMLModel(
                model_id=task.model.model_id,
                name=task.model.name,
                description=task.model.description,
                cost_per_request=task.model.cost_per_request,
                is_active=task.model.is_active,
            )
            output = model.predict(message.input_data)

            result = PredictionResult(
                result_id=0,
                task_id=task.task_id,
                output_data=output,
                credits_charged=task.model.cost_per_request,
            )
            await result_repo.save(result)

            task._status = TaskStatus.COMPLETED  # noqa: SLF001
            task._completed_at = datetime.utcnow()  # noqa: SLF001
            await task_repo.update(task)
            logger.info(f"Task id={message.task_id} completed")

        await self._sio.emit(
            "task_updated",
            {"task_id": task.task_id, "status": "completed"},
            room=f"user_{task.user.username}",
        )
