import asyncio
from collections.abc import Awaitable, Callable

import aio_pika
import facet
from ml_service_common.messaging.settings import MessagingSettings

MessageHandler = Callable[[bytes], Awaitable[None]]


class RabbitMQConsumer(facet.AsyncioServiceMixin):
    def __init__(self, settings: MessagingSettings, handler: MessageHandler) -> None:
        super().__init__()
        self._settings = settings
        self._handler = handler
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self.add_task(self._consume())

    async def stop(self) -> None:
        self._stop_event.set()

    async def _consume(self) -> None:
        connection = await aio_pika.connect_robust(self._settings.url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=self._settings.prefetch_count)
            queue = await channel.declare_queue(self._settings.queue_name, durable=True)
            await queue.consume(self._on_message)
            await self._stop_event.wait()

    async def _on_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            await self._handler(message.body)
