from ml_service_model.services.task_service import TaskService
from ml_service_users.database.service import Service as UserDatabaseService
from ml_service_wallet.services.wallet_service import WalletService


class MLService:
    def __init__(
        self,
        users: UserDatabaseService,
        wallet_service: WalletService,
        task_service: TaskService,
    ) -> None:
        self._users = users
        self._wallet_service = wallet_service
        self._task_service = task_service

    @property
    def users(self) -> UserDatabaseService:
        return self._users

    @property
    def wallet(self) -> WalletService:
        return self._wallet_service

    @property
    def tasks(self) -> TaskService:
        return self._task_service
