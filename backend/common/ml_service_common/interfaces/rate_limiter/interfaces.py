from typing import Any, Protocol


class RateLimiterInterface(Protocol):
    async def is_ignore(self, token: str) -> bool:
        raise NotImplementedError

    async def is_expire(
            self,
            data: dict[str, Any],
            times: int = 1,
            seconds: int = 1,
    ) -> bool:
        raise NotImplementedError
