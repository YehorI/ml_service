from ml_service.domains.transaction import DepositTransaction, DebitTransaction
from ml_service.domains.task import MLTask
from ml_service.domains.user import User
from ml_service.interfaces.repositories import TransactionRepository, UserRepository


class BalanceService:
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._user_repository = user_repository
        self._transaction_repository = transaction_repository

    def deposit(self, user: User, amount: float) -> DepositTransaction:
        NotImplemented

    def charge_for_task(self, user: User, task: MLTask) -> DebitTransaction:
        NotImplemented
