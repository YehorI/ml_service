from datetime import datetime
from enum import Enum
from typing import Any

from ml_service_model.domains.ml_model import MLModel
from database_repository.dto.users import User


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PredictionResult:
    def __init__(
        self,
        result_id: int,
        task_id: int,
        output_data: Any,
        credits_charged: float,
        created_at: datetime | None = None,
    ) -> None:
        self._result_id = result_id
        self._task_id = task_id
        self._output_data = output_data
        self._credits_charged = credits_charged
        self._created_at = created_at or datetime.utcnow()

    @property
    def result_id(self) -> int:
        return self._result_id

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def output_data(self) -> Any:
        return self._output_data

    @property
    def credits_charged(self) -> float:
        return self._credits_charged

    @property
    def created_at(self) -> datetime:
        return self._created_at


class MLTask:
    def __init__(
        self,
        task_id: int,
        user: User,
        model: MLModel,
        input_data: Any,
        created_at: datetime | None = None,
    ) -> None:
        self._task_id = task_id
        self._user = user
        self._model = model
        self._input_data = input_data
        self._status = TaskStatus.PENDING
        self._result: PredictionResult | None = None
        self._validation_errors: list[str] = []
        self._created_at = created_at or datetime.utcnow()
        self._completed_at: datetime | None = None

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def user(self) -> User:
        return self._user

    @property
    def model(self) -> MLModel:
        return self._model

    @property
    def input_data(self) -> Any:
        return self._input_data

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def result(self) -> PredictionResult | None:
        return self._result

    @property
    def validation_errors(self) -> list[str]:
        return list(self._validation_errors)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at
    
    def process(self) -> PredictionResult:
        raise NotImplementedError
