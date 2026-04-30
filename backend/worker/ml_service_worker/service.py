import facet
from loguru import logger
from ml_service_common.messaging import RabbitMQConsumer
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_worker.messaging.handler import WorkerMessageHandler
from ml_service_worker.settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, consumer: RabbitMQConsumer) -> None:
        self._consumer = consumer

    @property
    def dependencies(self) -> list:
        return [*super().dependencies, self._consumer]


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    db = SQLAlchemyService(settings=settings.database)

    logger.info(
        f"Loading HuggingFace model for worker_id={settings.worker_id!r}"
    )
    from transformers import pipeline as hf_pipeline
    model_pipeline = hf_pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )
    logger.info("Model loaded.")

    handler = WorkerMessageHandler(
        db=db,
        worker_id=settings.worker_id,
        model_pipeline=model_pipeline,
    )
    consumer = RabbitMQConsumer(
        settings=settings.worker_messaging, handler=handler.handle
    )
    return Service(consumer=consumer)
