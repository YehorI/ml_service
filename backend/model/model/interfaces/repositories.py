from __future__ import annotations

from abc import ABC, abstractmethod

from model.domains.ml_model import MLModel
from model.domains.task import MLTask, PredictionResult


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
