from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ml_service_common.sqlalchemy.service import Service

from database_repository import get_service
from database_repository.repositories import (
    SqlAlchemyBalanceRepository,
    SqlAlchemyMLModelRepository,
    SqlAlchemyMLTaskRepository,
    SqlAlchemyPredictionResultRepository,
    SqlAlchemyTransactionRepository,
    SqlAlchemyUserRepository,
)
from ml_service.api.security import hash_password
from ml_service_model.services.task_service import TaskService
from ml_service_users.services.user_service import UserService
from ml_service_wallet.services.wallet_service import WalletService

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


basic_auth = HTTPBasic(auto_error=True)


async def get_user_service(service: Service = Depends(db_transaction)) -> UserService:
    return UserService(user_repository=SqlAlchemyUserRepository(service))


async def get_wallet_service(service: Service = Depends(db_transaction)) -> WalletService:
    return WalletService(
        balance_repository=SqlAlchemyBalanceRepository(service),
        transaction_repository=SqlAlchemyTransactionRepository(service),
    )


async def get_task_service(service: Service = Depends(db_transaction)) -> TaskService:
    wallet_service = WalletService(
        balance_repository=SqlAlchemyBalanceRepository(service),
        transaction_repository=SqlAlchemyTransactionRepository(service),
    )
    return TaskService(
        task_repository=SqlAlchemyMLTaskRepository(service),
        model_repository=SqlAlchemyMLModelRepository(service),
        result_repository=SqlAlchemyPredictionResultRepository(service),
        wallet_service=wallet_service,
    )


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    user_service: UserService = Depends(get_user_service),
):
    # TODO JWT
    password_hash = hash_password(credentials.password)
    return await user_service.authenticate(credentials.username, password_hash)

