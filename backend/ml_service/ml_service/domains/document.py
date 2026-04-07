from datetime import datetime
from enum import Enum

from .user import User


class DocumentType(Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    IMAGE = "image"
    AUDIO = "audio"


class Document:
    def __init__(
        self,
        document_id: int,
        user: User,
        filename: str,
        doc_type: DocumentType,
        file_data: bytes,
        created_at: datetime | None = None,
    ) -> None:
        self._document_id = document_id
        self._user = user
        self._filename = filename
        self._doc_type = doc_type
        self._file_data = file_data
        self._extracted_text: str | None = None
        self._embeddings: list[float] | None = None
        self._created_at = created_at or datetime.utcnow()

    @property
    def document_id(self) -> int:
        return self._document_id

    @property
    def user(self) -> User:
        return self._user

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def doc_type(self) -> DocumentType:
        return self._doc_type

    @property
    def extracted_text(self) -> str | None:
        return self._extracted_text

    @property
    def embeddings(self) -> list[float] | None:
        return self._embeddings

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def get_file_data(self) -> bytes:
        return self._file_data

    def set_extracted_text(self, text: str) -> None:
        self._extracted_text = text

    def set_embeddings(self, embeddings: list[float]) -> None:
        self._embeddings = embeddings
