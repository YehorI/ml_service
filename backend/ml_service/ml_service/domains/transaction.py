from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from .user import User
from .task import MLTask


class TransactionType(Enum):
    DEPOSIT = "deposit"
    DEBIT = "debit"


class Transaction(ABC):
    def __init__(
        self,
        transaction_id: int,
        user: User,
        amount: float,
        created_at: datetime | None = None,
    ) -> None:
        self._transaction_id = transaction_id
        self._user = user
        self._amount = amount
        self._created_at = created_at or datetime.utcnow()
        self._is_applied = False

    @property
    def transaction_id(self) -> int:
        return self._transaction_id

    @property
    def user(self) -> User:
        return self._user

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_applied(self) -> bool:
        return self._is_applied

    @property
    @abstractmethod
    def transaction_type(self) -> TransactionType: ...

    @abstractmethod
    def apply(self) -> None: ...


class DepositTransaction(Transaction):
    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.DEPOSIT

    def apply(self) -> None:
        if self._is_applied:
            raise RuntimeError("Transaction already applied")
        self._user.deposit(self._amount)
        self._is_applied = True


class DebitTransaction(Transaction):
    def __init__(
        self,
        transaction_id: int,
        user: User,
        amount: float,
        ml_task: MLTask,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(transaction_id, user, amount, created_at)
        self._ml_task = ml_task

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.DEBIT

    @property
    def ml_task(self) -> MLTask:
        return self._ml_task

    def apply(self) -> None:
        if self._is_applied:
            raise RuntimeError("Transaction already applied")
        self._user.withdraw(self._amount)
        self._is_applied = True
