from ml_service.domains.chat import ChatBranch, ChatMessage, ChatSession
from ml_service.domains.user import User
from ml_service.interfaces.repositories import (
    ChatBranchRepository,
    ChatMessageRepository,
    ChatSessionRepository,
    MLModelRepository,
)
from ml_service.services.balance_service import BalanceService
from ml_service.services.task_service import TaskService


class ChatService:
    def __init__(
        self,
        session_repository: ChatSessionRepository,
        branch_repository: ChatBranchRepository,
        message_repository: ChatMessageRepository,
        model_repository: MLModelRepository,
        balance_service: BalanceService,
        task_service: TaskService,
    ) -> None:
        self._session_repository = session_repository
        self._branch_repository = branch_repository
        self._message_repository = message_repository
        self._model_repository = model_repository
        self._balance_service = balance_service
        self._task_service = task_service

    def create_session(self, user: User, model_id: int, title: str) -> ChatSession:
        ...

    def send_message(
        self,
        session: ChatSession,
        branch_id: int,
        content: str,
    ) -> ChatMessage:
        ...

    def fork_branch(
        self,
        session: ChatSession,
        parent_branch_id: int,
        message_id: int,
        title: None | str,
    ) -> ChatBranch:
        ...

    def load_session(self, session_id: int) -> ChatSession:
        ...