from ml_service.domains.task import InputDataType, MLTask
from ml_service.interfaces.repositories import (
    MLModelRepository,
    MLTaskRepository,
    PredictionResultRepository,
)
from ml_service.services.balance_service import BalanceService
from ml_service.domains.user import User


class TaskService:
    def __init__(
        self,
        task_repository: MLTaskRepository,
        model_repository: MLModelRepository,
        result_repository: PredictionResultRepository,
        balance_service: BalanceService,
    ) -> None:
        self._task_repository = task_repository
        self._model_repository = model_repository
        self._result_repository = result_repository
        self._balance_service = balance_service

    def create_task(
        self,
        user: User,
        model_id: int,
        input_data: object,
        input_type: InputDataType,
    ) -> MLTask:
        NotImplemented