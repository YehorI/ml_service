from datetime import datetime
from typing import Protocol

from loguru import logger

from database_repository.dto.users import User
from ml_service_common.messaging.errors import BillingError
from ml_service_common.messaging.schemas import PredictTaskMessage
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.domains.stored_model import StoredMLModel
from ml_service_model.domains.task import MLTask, PredictionResult, TaskStatus


class BillingHandler(Protocol):
    async def charge(self, user: User, task_id: int, amount: float) -> None: ...


class PredictMessageHandler:
    def __init__(self, db: SQLAlchemyService, billing: BillingHandler) -> None:
        self._db = db
        self._billing = billing

    async def handle(self, message: PredictTaskMessage) -> None:
        logger.info(f"Processing task_id={message.task_id} model={message.model_name!r}")
        async with self._db.transaction():
            task_repo = SqlAlchemyAltMLTaskRepository(self._db)
            result_repo = SqlAlchemyAltPredictionResultRepository(self._db)

            task = await task_repo.get_by_id(message.task_id)
            if task is None:
                logger.error(f"Task id={message.task_id} not found, skipping")
                return

            try:
                await self._billing.charge(
                    user=task.user,
                    task_id=task.task_id,
                    amount=task.model.cost_per_request,
                )
            except BillingError as exc:
                logger.warning(f"Billing failed for task_id={message.task_id}: {exc}")
                await self._fail(task_repo, task)
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

    @staticmethod
    async def _fail(task_repo: SqlAlchemyAltMLTaskRepository, task: MLTask) -> None:
        task._status = TaskStatus.FAILED  # noqa: SLF001
        task._completed_at = datetime.utcnow()  # noqa: SLF001
        await task_repo.update(task)
