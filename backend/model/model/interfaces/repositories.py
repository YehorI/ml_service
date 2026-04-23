from abc import ABC, abstractmethod

from model.domains.ml_model import MLModel
from model.domains.task import MLTask, PredictionResult


class MLModelRepository(ABC):
    @abstractmethod
    async def get_by_id(self, model_id: int) -> MLModel | None: ...

    @abstractmethod
    async def list_active(self) -> list[MLModel]: ...

    @abstractmethod
    async def save(self, model: MLModel) -> MLModel: ...


class MLTaskRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_id: int) -> MLTask | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[MLTask]: ...

    @abstractmethod
    async def save(self, task: MLTask) -> MLTask: ...

    @abstractmethod
    async def update(self, task: MLTask) -> MLTask: ...


class PredictionResultRepository(ABC):
    @abstractmethod
    async def get_by_task_id(self, task_id: int) -> PredictionResult | None: ...

    @abstractmethod
    async def save(self, result: PredictionResult) -> PredictionResult: ...
