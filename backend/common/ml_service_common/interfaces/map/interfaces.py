from typing import Any, Protocol


class MapInterface(Protocol):
    async def set(self, key: str, value: Any):
        raise NotImplementedError

    async def get(self, key: str) -> Any:
        raise NotImplementedError

    async def delete(self, key: str):
        raise NotImplementedError
