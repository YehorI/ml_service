import asyncio
from collections.abc import Awaitable, Callable

import aio_pika

from ml_service_common.messaging.schemas import PredictTaskMessage
from ml_service_common.messaging.settings import MessagingSettings

MessageHandler = Callable[[PredictTaskMessage], Awaitable[None]]


class RabbitMQConsumer:
    def __init__(self, settings: MessagingSettings, handler: MessageHandler) -> None:
        self._settings = settings
        self._handler = handler
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        connection = await aio_pika.connect_robust(self._settings.url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=self._settings.prefetch_count)
            queue = await channel.declare_queue(self._settings.queue_name, durable=True)
            await queue.consume(self._on_message)
            await self._stop_event.wait()

    async def _on_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            data = PredictTaskMessage.model_validate_json(message.body)
            await self._handler(data)
