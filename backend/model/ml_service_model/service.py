import facet
from ml_service_common.messaging import RabbitMQConsumer, RabbitMQPublisher
from ml_service_model import api, database
from ml_service_model.messaging.handler import PredictMessageHandler
from ml_service_model.settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, api: api.Service, consumer: RabbitMQConsumer) -> None:
        self._api = api
        self._consumer = consumer

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        return [*super().dependencies, self._api, self._consumer]

    @property
    def api(self) -> api.Service:
        return self._api


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    database_service = database.get_service(settings=settings.database)
    publisher = RabbitMQPublisher(settings=settings.billing_messaging)
    worker_publisher = RabbitMQPublisher(settings=settings.worker_messaging)
    api_service = api.get_service(
        database=database_service,
        publisher=publisher,
        worker_publisher=worker_publisher,
        settings=settings.api,
    )
    handler = PredictMessageHandler(db=database_service, sio=api_service.sio)
    consumer = RabbitMQConsumer(settings=settings.predict_messaging, handler=handler.handle)
    return Service(api=api_service, consumer=consumer)
