from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLModelRepository,
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.interfaces.repositories import MLModelRepository
from ml_service_model.services.task_service import TaskService
from ml_service_users.database.repositories import SqlAlchemyAltUserRepository
from ml_service_users.services.user_service import UserService
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository,
    SqlAlchemyAltTransactionRepository,
)
from ml_service_wallet.services.wallet_service import WalletService

from database_repository import get_service
from database_repository.service import Service
from ml_service.api.jwt_auth import decode_access_token

_service: Service | None = None


def _get_service_singleton() -> Service:
    global _service
    if _service is None:
        _service = get_service()
    return _service


async def db_transaction() -> AsyncGenerator[Service, None]:
    service = _get_service_singleton()
    async with service.transaction():
        yield service


bearer_scheme = HTTPBearer(auto_error=True)


async def get_user_service(service: Service = Depends(db_transaction)) -> UserService:
    return UserService(user_repository=SqlAlchemyAltUserRepository(service))


async def get_wallet_service(service: Service = Depends(db_transaction)) -> WalletService:
    return WalletService(
        balance_repository=SqlAlchemyAltBalanceRepository(service),
        transaction_repository=SqlAlchemyAltTransactionRepository(service),
    )


async def get_task_service(service: Service = Depends(db_transaction)) -> TaskService:
    wallet_service = WalletService(
        balance_repository=SqlAlchemyAltBalanceRepository(service),
        transaction_repository=SqlAlchemyAltTransactionRepository(service),
    )
    return TaskService(
        task_repository=SqlAlchemyAltMLTaskRepository(service),
        model_repository=SqlAlchemyAltMLModelRepository(service),
        result_repository=SqlAlchemyAltPredictionResultRepository(service),
        wallet_service=wallet_service,
    )


async def get_model_repository(service: Service = Depends(db_transaction)) -> MLModelRepository:
    return SqlAlchemyAltMLModelRepository(service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
):
    payload = decode_access_token(credentials.credentials)
    return await user_service.get_by_id(int(payload["sub"]))
