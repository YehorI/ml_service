from contextlib import asynccontextmanager
from typing import AsyncGenerator, Protocol


class TransactionInterface(Protocol):
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        yield
