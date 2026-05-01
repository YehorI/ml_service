from datetime import datetime
from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
        created_at: datetime | None = None,
    ) -> None:
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._created_at = created_at or datetime.utcnow()

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def verify_password(self, password_hash: str) -> bool:
        return self._password_hash == password_hash


class AdminUser(User):
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password_hash: str,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(
            user_id, username, email, password_hash, UserRole.ADMIN, created_at
        )
