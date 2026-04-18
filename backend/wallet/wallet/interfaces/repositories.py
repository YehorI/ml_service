from __future__ import annotations

from abc import ABC, abstractmethod

from wallet.domains.transaction import Transaction
from wallet.domains.wallet import Wallet


class BalanceRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Wallet | None: ...

    @abstractmethod
    def save(self, wallet: Wallet) -> Wallet: ...

    @abstractmethod
    def update(self, wallet: Wallet) -> Wallet: ...


class TransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Transaction | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Transaction]: ...

    @abstractmethod
    def list_all(self) -> list[Transaction]: ...

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction: ...
