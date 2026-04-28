from datetime import datetime
from typing import Any

from ml_service_model.domains.task import MLTask, PredictionResult, TaskStatus
from ml_service_model.interfaces.repositories import (
    MLModelRepository,
    MLTaskRepository,
    PredictionResultRepository,
)
from database_repository.dto.users import User
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.services.wallet_service import WalletService


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
        wallet_service: WalletService,
    ) -> None:
        self._task_repository = task_repository
        self._model_repository = model_repository
        self._result_repository = result_repository
        self._wallet_service = wallet_service

    async def create_task(self, user: User, model_id: int, input_data: Any) -> MLTask:
        model = await self._model_repository.get_by_id(model_id)
        if model is None:
            raise ModelNotFoundError(f"Model id={model_id} not found")
        if not model.is_active:
            raise ModelInactiveError(f"Model id={model_id} is inactive")

        if not isinstance(input_data, (dict, list, str, int, float, bool)) and input_data is not None:
            raise InvalidInputDataError("Input data must be JSON-serializable")

        task = MLTask(task_id=0, user=user, model=model, input_data=input_data)  # type: ignore[arg-type]
        return await self._task_repository.save(task)

    async def predict(self, user: User, wallet: Wallet, model_id: int, input_data: Any) -> tuple[MLTask, PredictionResult]:
        model = await self._model_repository.get_by_id(model_id)
        if model is None:
            raise ModelNotFoundError(f"Model id={model_id} not found")
        if not model.is_active:
            raise ModelInactiveError(f"Model id={model_id} is inactive")
        if not isinstance(input_data, dict):
            raise InvalidInputDataError("Input data must be an object", details=["expected JSON object"])

        task = MLTask(task_id=0, user=user, model=model, input_data=input_data)  # type: ignore[arg-type]
        task = await self._task_repository.save(task)

        await self._wallet_service.charge_for_task(
            user=user,
            wallet=wallet,
            task_id=task.task_id,
            amount=float(model.cost_per_request),
        )

        # TODO mock
        output = model.predict(input_data)

        result = PredictionResult(
            result_id=0,
            task_id=task.task_id,
            output_data=output,
            credits_charged=float(model.cost_per_request),
        )
        saved_result = await self._result_repository.save(result)

        task._status = TaskStatus.COMPLETED  # noqa: SLF001
        task._completed_at = datetime.utcnow()  # noqa: SLF001
        await self._task_repository.update(task)
        return task, saved_result
