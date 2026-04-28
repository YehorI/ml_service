from fastapi import APIRouter, Depends
from ml_service_users.domains.user import User
from ml_service_wallet.database.repositories import SqlAlchemyAltBalanceRepository
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.services.wallet_service import WalletService

from database_repository.service import Service
from ml_service.api.deps import db_transaction, get_current_user, get_wallet_service
from ml_service.api.schemas import BalanceResponse, DepositRequest

router = APIRouter()


async def _get_wallet(service: Service, user: User) -> Wallet:
    repo = SqlAlchemyAltBalanceRepository(service)
    wallet = await repo.get_by_user_id(user.user_id)
    if wallet is None:
        wallet = await repo.save(Wallet(user_id=user.user_id, amount=0.0))
    return wallet


@router.get("", response_model=BalanceResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
):
    wallet = await _get_wallet(service, user)
    return BalanceResponse(amount=wallet.amount)


@router.post("/deposit", response_model=BalanceResponse)
async def deposit(
    payload: DepositRequest,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
    wallet_service: WalletService = Depends(get_wallet_service),
):
    wallet = await _get_wallet(service, user)
    await wallet_service.deposit(user=user, wallet=wallet, amount=payload.amount)
    return BalanceResponse(amount=wallet.amount)

