from __future__ import annotations

from abc import ABC, abstractmethod

from ml_service.domains.wallet import Wallet
from ml_service.domains.user import User
from ml_service.domains.ml_model import MLModel
from ml_service.domains.task import MLTask, PredictionResult
from ml_service.domains.transaction import Transaction


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def update(self, user: User) -> User: ...


class BalanceRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Wallet | None: ...

    @abstractmethod
    def save(self, wallet: Wallet) -> Wallet: ...

    @abstractmethod
    def update(self, wallet: Wallet) -> Wallet: ...


class MLModelRepository(ABC):
    @abstractmethod
    def get_by_id(self, model_id: int) -> MLModel | None: ...

    @abstractmethod
    def list_active(self) -> list[MLModel]: ...

    @abstractmethod
    def save(self, model: MLModel) -> MLModel: ...


class MLTaskRepository(ABC):
    @abstractmethod
    def get_by_id(self, task_id: int) -> MLTask | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[MLTask]: ...

    @abstractmethod
    def save(self, task: MLTask) -> MLTask: ...

    @abstractmethod
    def update(self, task: MLTask) -> MLTask: ...


class PredictionResultRepository(ABC):
    @abstractmethod
    def get_by_task_id(self, task_id: int) -> PredictionResult | None: ...

    @abstractmethod
    def save(self, result: PredictionResult) -> PredictionResult: ...


class TransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Transaction | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Transaction]: ...

    @abstractmethod
    def list_all(self) -> list[Transaction]: ...

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction: ...
