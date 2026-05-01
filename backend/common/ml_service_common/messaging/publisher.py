import aio_pika
import facet
from ml_service_common.messaging.settings import MessagingSettings
from pydantic import BaseModel


class RabbitMQPublisher(facet.AsyncioServiceMixin):
    def __init__(self, settings: MessagingSettings) -> None:
        super().__init__()
        self._settings = settings
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._settings.url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self._settings.queue_name, durable=True)

    async def stop(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            self._channel = None

    async def publish(self, message: BaseModel) -> None:
        if self._channel is None:
            raise RuntimeError("Publisher not started")
        body = message.model_dump_json().encode()
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=self._settings.queue_name,
        )
