import fastapi
from database_repository.dto.users import User
from ml_service_wallet.api.rest.dependencies import (get_current_user,
                                                     get_database)
from ml_service_wallet.database.repositories import \
    SqlAlchemyAltBalanceRepository
from ml_service_wallet.database.service import Service
from ml_service_wallet.domains.wallet import Wallet


class WalletNotFoundError(Exception):
    pass


async def get_wallet(
    user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
) -> Wallet:
    repo = SqlAlchemyAltBalanceRepository(database)
    wallet = await repo.get_by_user_id(user.user_id)
    if wallet is None:
        raise WalletNotFoundError(f"Wallet for user id={user.user_id} not found")
    return wallet
