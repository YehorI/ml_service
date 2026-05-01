from typing import Any, Protocol, Self


class DTOInterface(Protocol):
    def as_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raise NotImplementedError

    def as_json(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_json(cls, value: str) -> Self:
        raise NotImplementedError

    @classmethod
    def from_object(cls, _object: Any) -> Self:
        raise NotImplementedError
