from abc import ABC, abstractmethod
from typing import Any


class MLModel(ABC):
    def __init__(
        self,
        model_id: int,
        name: str,
        description: str,
        cost_per_request: float,
        is_active: bool = True,
    ) -> None:
        self._model_id = model_id
        self._name = name
        self._description = description
        self._cost_per_request = cost_per_request
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
    def is_active(self) -> bool:
        return self._is_active

    @abstractmethod
    def predict(self, input_data: Any) -> Any: ...
