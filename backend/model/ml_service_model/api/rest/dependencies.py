from collections.abc import AsyncGenerator

import fastapi
from database_repository.dto.users import User
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ml_service_common.auth import hash_password
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_model.database.service import Service


async def get_database(request: fastapi.Request) -> AsyncGenerator[Service, None]:
    service: Service = request.app.service.database
    async with service.transaction():
        yield service


async def get_publisher(request: fastapi.Request) -> RabbitMQPublisher:
    return request.app.service.publisher


async def get_worker_publisher(request: fastapi.Request) -> RabbitMQPublisher:
    return request.app.service.worker_publisher


basic_auth = HTTPBasic(auto_error=True)


class UserNotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


async def get_current_user(
    credentials: HTTPBasicCredentials = fastapi.Depends(basic_auth),
    database: Service = fastapi.Depends(get_database),
) -> User:
    user = await database.get_user_by_username(credentials.username)
    if user is None:
        raise UserNotFoundError(f"User {credentials.username!r} not found")
    if not user.verify_password(hash_password(credentials.password)):
        raise InvalidPasswordError("Invalid password")
    return user
