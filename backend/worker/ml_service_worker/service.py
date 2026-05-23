import facet
from ml_service_common.messaging import RabbitMQConsumer, RabbitMQPublisher
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_worker.messaging.handler import WorkerMessageHandler
from ml_service_worker.settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, consumer: RabbitMQConsumer, completed_publisher: RabbitMQPublisher) -> None:
        self._consumer = consumer
        self._completed_publisher = completed_publisher

    @property
    def dependencies(self) -> list:
        return [*super().dependencies, self._completed_publisher, self._consumer]


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    db = SQLAlchemyService(settings=settings.database)
    completed_publisher = RabbitMQPublisher(settings=settings.completed_messaging)
    handler = WorkerMessageHandler(
        db=db,
        worker_id=settings.worker_id,
        completed_publisher=completed_publisher,
    )
    consumer = RabbitMQConsumer(settings=settings.worker_messaging, handler=handler.handle)
    return Service(consumer=consumer, completed_publisher=completed_publisher)
