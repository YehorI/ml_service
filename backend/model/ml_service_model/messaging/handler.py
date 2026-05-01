import socketio
from loguru import logger
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_common.messaging.schemas import (PredictRequestMessage,
                                                  TaskCompletedMessage,
                                                  WorkerTaskMessage)
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_model.database.repositories import SqlAlchemyAltMLTaskRepository
from ml_service_model.domains.task import TaskStatus


class PredictMessageHandler:
    def __init__(self, db: SQLAlchemyService, sio: socketio.AsyncServer, worker_publisher: RabbitMQPublisher) -> None:
        self._db = db
        self._sio = sio
        self._worker_publisher = worker_publisher

    async def handle(self, body: bytes) -> None:
        message = PredictRequestMessage.model_validate_json(body)
        logger.info(f"Forwarding task_id={message.task_id} to worker")

        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            task = await task_repo.get_by_id(message.task_id)
            if task is None:
                logger.error(f"Task id={message.task_id} not found, skipping")
                return
            task._status = TaskStatus.PROCESSING  # noqa: SLF001
            await task_repo.update(task)

        worker_msg = WorkerTaskMessage(
            task_id=message.task_id,
            username=task.user.username,
            features=message.input_data,
            model_name=message.model_name,
            model_type=task.model.model_type,
            provider_config=task.model.model_config,
            cost_per_request=task.model.cost_per_request,
        )
        await self._worker_publisher.publish(worker_msg)
        logger.info(f"Task id={message.task_id} forwarded to worker")


class CompletedMessageHandler:
    def __init__(self, sio: socketio.AsyncServer) -> None:
        self._sio = sio

    async def handle(self, body: bytes) -> None:
        message = TaskCompletedMessage.model_validate_json(body)
        logger.info(f"Task id={message.task_id} completed, notifying user {message.username!r}")
        try:
            await self._sio.emit(
                "task_updated",
                {"task_id": message.task_id, "status": "completed"},
                room=f"user_{message.username}",
            )
        except Exception:
            logger.exception(f"Failed to emit task_updated for task_id={message.task_id}")
