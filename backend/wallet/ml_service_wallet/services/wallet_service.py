from database_repository.dto.users import User
from ml_service_wallet.domains.transaction import DebitTransaction, DepositTransaction
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.interfaces.repositories import BalanceRepository, TransactionRepository


class InsufficientFundsError(Exception):
    pass


class WalletService:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._balance_repository = balance_repository
        self._transaction_repository = transaction_repository

    async def deposit(self, user: User, wallet: Wallet, amount: float) -> DepositTransaction:
        transaction = DepositTransaction(
            transaction_id=0,
            user=user,
            wallet=wallet,
            amount=amount,
        )
        transaction.apply()

        await self._balance_repository.update(wallet)
        saved = await self._transaction_repository.save(transaction)
        return saved

    async def charge_for_task(
        self,
        user: User,
        wallet: Wallet,
        task_id: int,
        amount: float,
    ) -> DebitTransaction:
        if not wallet.has_sufficient_funds(amount):
            raise InsufficientFundsError(
                f"Insufficient funds: need {amount}, have {wallet.amount}"
            )

        transaction = DebitTransaction(
            transaction_id=0,
            user=user,
            wallet=wallet,
            amount=amount,
            ml_task_id=task_id,
        )
        transaction.apply()

        await self._balance_repository.update(wallet)
        saved = await self._transaction_repository.save(transaction)
        return saved
