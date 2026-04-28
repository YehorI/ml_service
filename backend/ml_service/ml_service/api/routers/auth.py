from fastapi import APIRouter, Depends, status
from ml_service_users.api.rest.users.handlers import (
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ml_service_users.database.service import Service as UserDatabaseService
from ml_service_users.utils import hash_password

from database_repository.dto.users import User
from ml_service.api.deps import users_database
from ml_service.api.schemas import LoginRequest, LoginResponse, RegisterRequest, UserPublic

router = APIRouter()


def _to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    database: UserDatabaseService = Depends(users_database),
):
    if await database.get_user_by_username(payload.username) is not None:
        raise UserAlreadyExistsError(f"User with username {payload.username!r} already exists")
    if await database.get_user_by_email(payload.email) is not None:
        raise UserAlreadyExistsError(f"User with email {payload.email!r} already exists")

    user = await database.create_user(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    return _to_public(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    database: UserDatabaseService = Depends(users_database),
):
    user = await database.get_user_by_username(payload.username)
    if user is None:
        raise UserNotFoundError(f"User {payload.username!r} not found")
    if not user.verify_password(hash_password(payload.password)):
        raise InvalidPasswordError("Invalid password")
    return LoginResponse(user=_to_public(user))
