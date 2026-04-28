from fastapi import APIRouter, Depends

from database_repository.dto.users import User
from ml_service.api.deps import get_current_user
from ml_service.api.schemas import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def me(user: User = Depends(get_current_user)):
    return UserPublic(
        id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
    )

