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
        balance: float = 0.0,
        created_at: datetime | None = None,
    ) -> None:
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._balance = balance
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
    def balance(self) -> float:
        return self._balance

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._balance < amount:
            raise ValueError("Insufficient balance")
        self._balance -= amount

    def has_sufficient_balance(self, amount: float) -> bool:
        return self._balance >= amount

    def verify_password(self, password_hash: str) -> bool:
        return self._password_hash == password_hash


class AdminUser(User):
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password_hash: str,
        balance: float = 0.0,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(user_id, username, email, password_hash, UserRole.ADMIN, balance, created_at)

    def set_user_balance (self, user: User, amount: float) -> None:
        NotImplemented
