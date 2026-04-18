from model.domains.task import MLTask
from model.interfaces.repositories import (
    MLModelRepository,
    MLTaskRepository,
    PredictionResultRepository,
)
from users.domains.user import User
from wallet.services.wallet_service import WalletService


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

    def create_task(
        self,
        user: User,
        model_id: int,
        input_data: object,
    ) -> MLTask:
        raise NotImplementedError
