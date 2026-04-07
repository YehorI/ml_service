from __future__ import annotations

from abc import ABC, abstractmethod

from ml_service.domains.user import User
from ml_service.domains.ml_model import MLModel
from ml_service.domains.task import MLTask, PredictionResult
from ml_service.domains.transaction import Transaction
from ml_service.domains.chat import ChatSession, ChatBranch, ChatMessage
from ml_service.domains.document import Document


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


class ChatSessionRepository(ABC):
    @abstractmethod
    def get_by_id(self, session_id: int) -> ChatSession | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[ChatSession]: ...

    @abstractmethod
    def save(self, session: ChatSession) -> ChatSession: ...

    @abstractmethod
    def update(self, session: ChatSession) -> ChatSession: ...


class ChatBranchRepository(ABC):
    @abstractmethod
    def get_by_id(self, branch_id: int) -> ChatBranch | None: ...

    @abstractmethod
    def list_by_session(self, session_id: int) -> list[ChatBranch]: ...

    @abstractmethod
    def save(self, branch: ChatBranch) -> ChatBranch: ...


class ChatMessageRepository(ABC):
    @abstractmethod
    def list_by_branch(self, branch_id: int) -> list[ChatMessage]: ...

    @abstractmethod
    def save(self, message: ChatMessage) -> ChatMessage: ...


class DocumentRepository(ABC):
    @abstractmethod
    def get_by_id(self, document_id: int) -> Document | None: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Document]: ...

    @abstractmethod
    def save(self, document: Document) -> Document: ...

    @abstractmethod
    def update(self, document: Document) -> Document: ...

    @abstractmethod
    def delete(self, document_id: int) -> None: ...
