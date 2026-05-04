import fastapi
from database_repository.dto.users import User
from ml_service_wallet.api.rest.dependencies import (get_current_user,
                                                     get_database)
from ml_service_wallet.api.rest.dependencies import require_admin
from ml_service_wallet.api.rest.wallet.dependencies import get_wallet
from ml_service_wallet.api.rest.wallet.schemas import (AdminDepositRequest,
                                                       DepositRequest,
                                                       TransactionResponse,
                                                       WalletBalanceResponse)
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository, SqlAlchemyAltTransactionRepository)
from ml_service_wallet.database.service import Service
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.services.wallet_service import WalletService


async def get_balance(
    user: User = fastapi.Depends(get_current_user),
    wallet: Wallet = fastapi.Depends(get_wallet),
) -> WalletBalanceResponse:
    return WalletBalanceResponse(user_id=user.user_id, amount=wallet.amount)


async def deposit(
    data: DepositRequest = fastapi.Body(embed=False),
    user: User = fastapi.Depends(get_current_user),
    wallet: Wallet = fastapi.Depends(get_wallet),
    database: Service = fastapi.Depends(get_database),
) -> WalletBalanceResponse:
    balance_repo = SqlAlchemyAltBalanceRepository(database)
    txn_repo = SqlAlchemyAltTransactionRepository(database)
    wallet_service = WalletService(balance_repo, txn_repo)
    await wallet_service.deposit(user=user, wallet=wallet, amount=data.amount)
    return WalletBalanceResponse(user_id=user.user_id, amount=wallet.amount)


async def admin_get_balance(
    target_user_id: int = fastapi.Path(),
    _admin: User = fastapi.Depends(require_admin),
    database: Service = fastapi.Depends(get_database),
) -> WalletBalanceResponse:
    balance_repo = SqlAlchemyAltBalanceRepository(database)
    wallet = await balance_repo.get_by_user_id(target_user_id)
    if wallet is None:
        raise fastapi.HTTPException(status_code=404, detail="Wallet not found.")
    return WalletBalanceResponse(user_id=target_user_id, amount=wallet.amount)


async def admin_deposit(
    data: AdminDepositRequest = fastapi.Body(embed=False),
    _admin: User = fastapi.Depends(require_admin),
    database: Service = fastapi.Depends(get_database),
) -> WalletBalanceResponse:
    target_user = await database.get_user_by_id(data.target_user_id)
    if target_user is None:
        raise fastapi.HTTPException(status_code=404, detail="Target user not found.")
    balance_repo = SqlAlchemyAltBalanceRepository(database)
    wallet = await balance_repo.get_by_user_id(data.target_user_id)
    if wallet is None:
        raise fastapi.HTTPException(status_code=404, detail="Wallet not found for target user.")
    txn_repo = SqlAlchemyAltTransactionRepository(database)
    wallet_service = WalletService(balance_repo, txn_repo)
    await wallet_service.deposit(user=target_user, wallet=wallet, amount=data.amount)
    return WalletBalanceResponse(user_id=target_user.user_id, amount=wallet.amount)


async def list_transactions(
    user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
) -> list[TransactionResponse]:
    txn_repo = SqlAlchemyAltTransactionRepository(database)
    transactions = await txn_repo.list_by_user(user.user_id)
    return [TransactionResponse.from_domain(tx) for tx in transactions]
