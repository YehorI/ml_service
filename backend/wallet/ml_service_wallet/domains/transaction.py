from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from ml_service_users.domains.user import User
from ml_service_wallet.domains.wallet import Wallet


class TransactionType(Enum):
    DEPOSIT = "deposit"
    DEBIT = "debit"


class Transaction(ABC):
    def __init__(
        self,
        transaction_id: int,
        user: User,
        wallet: Wallet,
        amount: float,
        created_at: datetime | None = None,
    ) -> None:
        self._transaction_id = transaction_id
        self._user = user
        self._wallet = wallet
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
    def wallet(self) -> Wallet:
        return self._wallet

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
            raise ValueError("Transaction already applied")
        self._wallet.deposit(self._amount)
        self._is_applied = True


class DebitTransaction(Transaction):
    def __init__(
        self,
        transaction_id: int,
        user: User,
        wallet: Wallet,
        amount: float,
        ml_task_id: int,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(transaction_id, user, wallet, amount, created_at)
        self._ml_task_id = ml_task_id

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.DEBIT

    @property
    def ml_task_id(self) -> int:
        return self._ml_task_id

    def apply(self) -> None:
        if self._is_applied:
            raise ValueError("Transaction already applied")
        self._wallet.withdraw(self._amount)
        self._is_applied = True
