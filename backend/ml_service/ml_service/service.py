from model.services.task_service import TaskService
from users.services.user_service import UserService
from wallet.services.wallet_service import WalletService


class MLService:
    """
    Top-level orchestration service.
    Owns no domain logic — delegates entirely to injected sub-services.
    """

    def __init__(
        self,
        user_service: UserService,
        wallet_service: WalletService,
        task_service: TaskService,
    ) -> None:
        self._user_service = user_service
        self._wallet_service = wallet_service
        self._task_service = task_service

    @property
    def users(self) -> UserService:
        return self._user_service

    @property
    def wallet(self) -> WalletService:
        return self._wallet_service

    @property
    def tasks(self) -> TaskService:
        return self._task_service
