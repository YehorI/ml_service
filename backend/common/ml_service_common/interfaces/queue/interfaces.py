from typing import Any, Protocol


class QueuePullerInterface(Protocol):
    async def pull(self) -> Any:
        raise NotImplementedError


class QueuePusherInterface(Protocol):
    async def push(self, value: Any):
        raise NotImplementedError


class QueueListenerInterface(QueuePullerInterface, Protocol):
    async def listen(self):
        while self.is_running:
            message = await self.pull()
            await self.handle(message=message)

    @property
    def is_running(self) -> bool:
        raise NotImplementedError

    async def handle(self, message: Any):
        raise NotImplementedError
