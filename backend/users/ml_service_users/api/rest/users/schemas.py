from datetime import datetime

from database_repository.dto.users import User
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    @classmethod
    def from_db_model(cls, user: User) -> "UserResponse":
        return cls(
            id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
        )


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserResponse


class UserUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
