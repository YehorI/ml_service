import facet
from ml_service_common.messaging import RabbitMQConsumer, RabbitMQPublisher
from ml_service_wallet import api, database
from ml_service_wallet.messaging.handler import BillingMessageHandler
from ml_service_wallet.settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, api: api.Service, consumer: RabbitMQConsumer, publisher: RabbitMQPublisher) -> None:
        self._api = api
        self._consumer = consumer
        self._publisher = publisher

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        return [*super().dependencies, self._api, self._publisher, self._consumer]

    @property
    def api(self) -> api.Service:
        return self._api


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    database_service = database.get_service(settings=settings.database)
    publisher = RabbitMQPublisher(settings=settings.predict_messaging)
    api_service = api.get_service(
        database=database_service,
        settings=settings.api,
    )
    handler = BillingMessageHandler(db=database_service, publisher=publisher)
    consumer = RabbitMQConsumer(settings=settings.billing_messaging, handler=handler.handle)
    return Service(api=api_service, consumer=consumer, publisher=publisher)
