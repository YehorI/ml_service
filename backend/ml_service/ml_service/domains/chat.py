from datetime import datetime
from enum import Enum

from .user import User
from .ml_model import LLMModel


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage:
    def __init__(
        self,
        message_id: int,
        branch_id: int,
        role: MessageRole,
        content: str,
        parent_message_id: int | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self._message_id = message_id
        self._branch_id = branch_id
        self._role = role
        self._content = content
        self._parent_message_id = parent_message_id
        self._created_at = created_at or datetime.utcnow()

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def branch_id(self) -> int:
        return self._branch_id

    @property
    def role(self) -> MessageRole:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    @property
    def parent_message_id(self) -> int | None:
        return self._parent_message_id

    @property
    def created_at(self) -> datetime:
        return self._created_at


class ChatBranch:
    def __init__(
        self,
        branch_id: int,
        session_id: int,
        name: str,
        fork_message_id: int,
        parent_branch_id: int | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self._branch_id = branch_id
        self._session_id = session_id
        self._name = name
        self._fork_message_id = int
        self._parent_branch_id = parent_branch_id
        self._messages: list[ChatMessage] = []
        self._created_at = created_at or datetime.utcnow()

    @property
    def branch_id(self) -> int:
        return self._branch_id

    @property
    def session_id(self) -> int:
        return self._session_id
    
    @property
    def fork_message_id(self) -> int:
        return self._fork_message_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def messages(self) -> list[ChatMessage]:
        return list(self._messages)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def add_message(self, message: ChatMessage) -> None:
        self._messages.append(message)


class ChatSession:
    def __init__(
        self,
        session_id: int,
        user: User,
        model: LLMModel,
        title: str,
        created_at: datetime | None = None,
    ) -> None:
        self._session_id = session_id
        self._user = user
        self._model = model
        self._title = title
        self._branches: dict[int, ChatBranch] = {}
        self._active_branch_id: int | None = None
        self._created_at = created_at or datetime.utcnow()

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def user(self) -> User:
        return self._user

    @property
    def model(self) -> LLMModel:
        return self._model

    @property
    def title(self) -> str:
        return self._title

    @property
    def active_branch_id(self) -> int | None:
        return self._active_branch_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def active_branch(self) -> ChatBranch | None:
        NotImplemented

    def add_branch(self, branch: ChatBranch) -> None:
        NotImplemented

    def switch_branch(self, branch_id: int) -> None:
        NotImplemented

    def get_branch(self, branch_id: int) -> ChatBranch:
        NotImplemented
