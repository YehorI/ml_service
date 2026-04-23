from abc import ABC, abstractmethod

from wallet.domains.transaction import Transaction
from wallet.domains.wallet import Wallet


class BalanceRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Wallet | None: ...

    @abstractmethod
    async def save(self, wallet: Wallet) -> Wallet: ...

    @abstractmethod
    async def update(self, wallet: Wallet) -> Wallet: ...


class TransactionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, transaction_id: int) -> Transaction | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[Transaction]: ...

    @abstractmethod
    async def list_all(self) -> list[Transaction]: ...

    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction: ...
