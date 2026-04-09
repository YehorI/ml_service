from ml_service.domains.wallet import Wallet
from ml_service.domains.transaction import DepositTransaction, DebitTransaction
from ml_service.domains.task import MLTask
from ml_service.domains.user import User
from ml_service.interfaces.repositories import BalanceRepository, TransactionRepository


class WalletService:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._balance_repository = balance_repository
        self._transaction_repository = transaction_repository

    def deposit(self, user: User, wallet: Wallet, amount: float) -> DepositTransaction:
        raise NotImplementedError

    def charge_for_task(self, user: User, wallet: Wallet, task: MLTask) -> DebitTransaction:
        raise NotImplementedError
