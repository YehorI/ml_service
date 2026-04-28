from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLModelRepository,
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.services.task_service import TaskService
from ml_service_users.api.rest.users.handlers import (
    InvalidPasswordError,
    UserNotFoundError,
)
from ml_service_users.database.service import Service as UserDatabaseService
from ml_service_users.database.service import get_service as get_user_database
from ml_service_users.utils import hash_password
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository,
    SqlAlchemyAltTransactionRepository,
)
from ml_service_wallet.services.wallet_service import WalletService

from database_repository import get_service
from database_repository.service import Service

_service: Service | None = None
_users_database: UserDatabaseService | None = None


def _get_service_singleton() -> Service:
    global _service
    if _service is None:
        _service = get_service()
    return _service


def _get_users_database_singleton() -> UserDatabaseService:
    global _users_database
    if _users_database is None:
        _users_database = get_user_database()
    return _users_database


async def db_transaction() -> AsyncGenerator[Service, None]:
    service = _get_service_singleton()
    async with service.transaction():
        yield service


async def users_database() -> AsyncGenerator[UserDatabaseService, None]:
    database = _get_users_database_singleton()
    async with database.transaction():
        yield database


basic_auth = HTTPBasic(auto_error=True)


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


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    database: UserDatabaseService = Depends(users_database),
):
    user = await database.get_user_by_username(credentials.username)
    if user is None:
        raise UserNotFoundError(f"User {credentials.username!r} not found")
    if not user.verify_password(hash_password(credentials.password)):
        raise InvalidPasswordError("Invalid password")
    return user
