import fastapi

from database_repository.dto.users import User
from ml_service_users.api.rest.dependencies import get_database
from ml_service_users.api.rest.users.dependencies import get_path_user
from ml_service_users.api.rest.users.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from ml_service_users.database.service import Service
from ml_service_users.utils import hash_password


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


async def register(
    data: RegisterRequest = fastapi.Body(embed=False),
    database: Service = fastapi.Depends(get_database),
) -> UserResponse:
    if await database.get_user_by_username(data.username) is not None:
        raise UserAlreadyExistsError(f"User with username {data.username!r} already exists")
    if await database.get_user_by_email(data.email) is not None:
        raise UserAlreadyExistsError(f"User with email {data.email!r} already exists")

    user = await database.create_user(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    return UserResponse.from_db_model(user)


async def login(
    data: LoginRequest = fastapi.Body(embed=False),
    database: Service = fastapi.Depends(get_database),
) -> LoginResponse:
    user = await database.get_user_by_username(data.username)
    if user is None:
        raise UserNotFoundError(f"User {data.username!r} not found")
    if not user.verify_password(hash_password(data.password)):
        raise InvalidPasswordError("Invalid password")
    return LoginResponse(user=UserResponse.from_db_model(user))


async def get_user(user: User = fastapi.Depends(get_path_user)) -> UserResponse:
    return UserResponse.from_db_model(user)


async def update_user(
    user: User = fastapi.Depends(get_path_user),
    data: UserUpdateRequest = fastapi.Body(embed=False),
    database: Service = fastapi.Depends(get_database),
) -> UserResponse:
    updated = await database.update_user(
        user,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password) if data.password is not None else None,
    )
    return UserResponse.from_db_model(updated)
