from users.domains.user import User
from wallet.domains.transaction import DebitTransaction, DepositTransaction
from wallet.domains.wallet import Wallet
from wallet.interfaces.repositories import BalanceRepository, TransactionRepository


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

    def charge_for_task(
        self,
        user: User,
        wallet: Wallet,
        task_id: int,
        amount: float,
    ) -> DebitTransaction:
        raise NotImplementedError
