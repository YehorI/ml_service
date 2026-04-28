import logging
from typing import Self

import aio_pika
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection

from ml_service.messaging.config import RabbitMQSettings
from ml_service.messaging.schemas import PredictTaskMessage

logger = logging.getLogger(__name__)


class TaskPublisher:
    """Publishes prediction tasks to RabbitMQ.

    Designed to be used as a long-lived singleton across the app's lifespan.
    """

    def __init__(self, settings: RabbitMQSettings) -> None:
        self._settings = settings
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def connect(self) -> None:
        if self._connection is not None and not self._connection.is_closed:
            return
        self._connection = await aio_pika.connect_robust(self._settings.url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self._settings.queue_name, durable=True)
        logger.info(
            "Publisher connected to RabbitMQ; queue=%s", self._settings.queue_name
        )

    async def close(self) -> None:
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None

    async def publish(self, message: PredictTaskMessage) -> None:
        if self._channel is None:
            raise RuntimeError("Publisher is not connected. Call connect() first.")
        body = message.model_dump_json().encode("utf-8")
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=message.task_id,
            ),
            routing_key=self._settings.queue_name,
        )
        logger.info("Published task %s to %s", message.task_id, self._settings.queue_name)

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
