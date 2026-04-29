from database_repository.dto.users import User
from ml_service_common.messaging.errors import BillingError
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository,
    SqlAlchemyAltTransactionRepository,
)
from ml_service_wallet.services.wallet_service import InsufficientFundsError, WalletService


class WalletBillingHandler:
    def __init__(self, db: SQLAlchemyService) -> None:
        self._db = db

    async def charge(self, user: User, task_id: int, amount: float) -> None:
        balance_repo = SqlAlchemyAltBalanceRepository(self._db)
        txn_repo = SqlAlchemyAltTransactionRepository(self._db)
        wallet = await balance_repo.get_by_user_id(user.user_id)
        if wallet is None:
            raise BillingError(f"Wallet not found for user_id={user.user_id}")
        try:
            wallet_service = WalletService(balance_repo, txn_repo)
            await wallet_service.charge_for_task(user=user, wallet=wallet, task_id=task_id, amount=amount)
        except InsufficientFundsError as exc:
            raise BillingError(str(exc)) from exc
