from typing import Any

from database_repository.dto.users import User
from ml_service_model.domains.task import MLTask
from ml_service_model.interfaces.repositories import (
    MLModelRepository, MLTaskRepository, PredictionResultRepository)


class ModelNotFoundError(Exception):
    pass


class ModelInactiveError(Exception):
    pass


class InvalidInputDataError(Exception):
    def __init__(self, message: str, details: list[str] | None = None) -> None:
        super().__init__(message)
        self.details = details or []


class TaskService:
    def __init__(
        self,
        task_repository: MLTaskRepository,
        model_repository: MLModelRepository,
        result_repository: PredictionResultRepository,
    ) -> None:
        self._task_repository = task_repository
        self._model_repository = model_repository
        self._result_repository = result_repository

    async def create_task(self, user: User, model_id: int, input_data: Any) -> MLTask:
        model = await self._model_repository.get_by_id(model_id)
        if model is None:
            raise ModelNotFoundError(f"Model id={model_id} not found")
        if not model.is_active:
            raise ModelInactiveError(f"Model id={model_id} is inactive")
        if not isinstance(input_data, dict):
            raise InvalidInputDataError("Input data must be a JSON object", details=["expected JSON object"])

        task = MLTask(task_id=0, user=user, model=model, input_data=input_data)  # type: ignore[arg-type]
        return await self._task_repository.save(task)
