import asyncio

from ml_service_common.messaging.consumer import RabbitMQConsumer
from ml_service_common.messaging.settings import MessagingSettings
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings
from ml_service_model.messaging.handler import PredictMessageHandler
from ml_service_wallet.messaging.handler import WalletBillingHandler


class PredictWorker:
    def __init__(self, messaging: MessagingSettings, database: SQLAlchemySettings) -> None:
        db = SQLAlchemyService(settings=database, logger=None)
        billing = WalletBillingHandler(db)
        handler = PredictMessageHandler(db, billing)
        self._consumer = RabbitMQConsumer(settings=messaging, handler=handler.handle)
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._consumer.stop()
        self._stop_event.set()

    async def run(self) -> None:
        await self._consumer.run()
