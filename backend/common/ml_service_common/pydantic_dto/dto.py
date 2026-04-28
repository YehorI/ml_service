from typing import Any, Protocol, Self

import pydantic
from ml_service_common.interfaces.dto import DTOInterface


class PydanticDTOMeta(type(pydantic.BaseModel), type(Protocol)):
    pass


class PydanticDTO(pydantic.BaseModel, DTOInterface, metaclass=PydanticDTOMeta):
    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)

    def as_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, value: str) -> Self:
        return cls.model_validate_json(value)

    @classmethod
    def from_object(cls, _object: Any) -> Self:
        return cls.model_validate(_object, from_attributes=True)
