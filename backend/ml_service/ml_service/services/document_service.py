from ml_service.domains.document import Document, DocumentType
from ml_service.domains.user import User
from ml_service.interfaces.repositories import DocumentRepository, MLModelRepository
from ml_service.services.task_service import TaskService


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        model_repository: MLModelRepository,
        task_service: TaskService,
    ) -> None:
        self._document_repository = document_repository
        self._model_repository = model_repository
        self._task_service = task_service

    def upload(
        self,
        user: User,
        filename: str,
        doc_type: DocumentType,
        file_data: bytes,
    ) -> Document:
        ...

    def extract_text(self, document: Document) -> str:
        ...

    def get_user_documents(self, user_id: int) -> list[Document]:
        ...

    def delete(self, document_id: int) -> None:
        ...
