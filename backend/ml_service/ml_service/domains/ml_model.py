from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class ModelType(Enum):
    LLM = "llm"
    OCR = "ocr"
    SPEECH_TO_TEXT = "stt"
    EMBEDDINGS = "embeddings"


class MLModel(ABC):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        model_type: ModelType,
        is_active: bool = True,
    ) -> None:
        self._model_id = model_id
        self._name = name
        self._description = description
        self._cost_per_request = cost_per_request
        self._model_type = model_type
        self._is_active = is_active

    @property
    def model_id(self) -> int:
        return self._model_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def cost_per_request(self) -> float:
        return self._cost_per_request

    @property
    def model_type(self) -> ModelType:
        return self._model_type

    @property
    def is_active(self) -> bool:
        return self._is_active

    @abstractmethod
    def predict(self, input_data: Any) -> Any: ...


class LLMModel(MLModel):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        provider: str,
        context_window: int,
        is_active: bool = True,
    ) -> None:
        super().__init__(model_id, name, description, cost_per_request, ModelType.LLM, is_active)
        self._provider = provider
        self._context_window = context_window

    @property
    def provider(self) -> str:
        return self._provider

    def predict(self, input_data: dict) -> dict:
        NotImplemented


class OCRModel(MLModel):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        is_active: bool = True,
    ) -> None:
        super().__init__(model_id, name, description, cost_per_request, ModelType.OCR, is_active)

    def predict(self, input_data: bytes) -> str:
        NotImplemented

class SpeechToTextModel(MLModel):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        supported_languages: list[str],
        is_active: bool = True,
    ) -> None:
        super().__init__(model_id, name, description, cost_per_request, ModelType.SPEECH_TO_TEXT, is_active)
        self._supported_languages = supported_languages

    @property
    def supported_languages(self) -> list[str]:
        return self._supported_languages

    def predict(self, input_data: bytes) -> str:
        raise NotImplementedError


class EmbeddingsModel(MLModel):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        vector_dimension: int,
        is_active: bool = True,
    ) -> None:
        super().__init__(model_id, name, description, cost_per_request, ModelType.EMBEDDINGS, is_active)

    def predict(self, input_data: str) -> list[float]:
        NotImplemented
