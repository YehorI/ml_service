import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ml_service.api.errors import install_exception_handlers
from ml_service.api.routers import auth, balance, history, predict, tasks, users
from ml_service.messaging import RabbitMQSettings, TaskPublisher

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = RabbitMQSettings.from_env()
        publisher = TaskPublisher(settings)
        try:
            await publisher.connect()
        except Exception as exc:
            logger.warning("RabbitMQ publisher failed to connect at startup: %s", exc)
        app.state.task_publisher = publisher
        try:
            yield
        finally:
            await publisher.close()

    app = FastAPI(title="ML Service API", version="0.1.0", lifespan=lifespan)

    install_exception_handlers(app)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["ml_service_users"])
    app.include_router(balance.router, prefix="/balance", tags=["balance"])
    app.include_router(predict.router, prefix="/predict", tags=["predict"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(history.router, prefix="/history", tags=["history"])

    return app
