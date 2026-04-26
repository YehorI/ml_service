from fastapi import APIRouter, Depends, status

from ml_service.api.deps import get_user_service
from ml_service.api.schemas import LoginRequest, LoginResponse, RegisterRequest, UserPublic
from ml_service.api.security import hash_password
from ml_service_users.domains.user import User
from ml_service_users.services.user_service import UserService

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
async def register(payload: RegisterRequest, user_service: UserService = Depends(get_user_service)):
    user = await user_service.register(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    return _to_public(user)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, user_service: UserService = Depends(get_user_service)):
    user = await user_service.authenticate(payload.username, hash_password(payload.password))
    return LoginResponse(user=_to_public(user))

