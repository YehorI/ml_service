from collections.abc import AsyncGenerator

import fastapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from database_repository.dto.users import User
from ml_service_users.database.service import Service, get_service

_database_singleton: Service | None = None


def _get_database_singleton() -> Service:
    global _database_singleton
    if _database_singleton is None:
        _database_singleton = get_service()
    return _database_singleton


async def get_database() -> AsyncGenerator[Service, None]:
    service = _get_database_singleton()
    async with service.transaction():
        yield service


basic_auth = HTTPBasic(auto_error=True)


async def get_current_user(
    credentials: HTTPBasicCredentials = fastapi.Depends(basic_auth),
    database: Service = fastapi.Depends(get_database),
) -> User:
    from ml_service_users.api.rest.users.handlers import (
        InvalidPasswordError,
        UserNotFoundError,
    )
    from ml_service_users.utils import hash_password

    user = await database.get_user_by_username(credentials.username)
    if user is None:
        raise UserNotFoundError(f"User {credentials.username!r} not found")
    if not user.verify_password(hash_password(credentials.password)):
        raise InvalidPasswordError("Invalid password")
    return user
