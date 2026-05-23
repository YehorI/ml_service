import fastapi
import socketio
from ml_service_common.fastapi import FastAPIService
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_model.api.router import router
from ml_service_model.api.settings import Settings
from ml_service_model.api.socketio import TaskNamespace
from ml_service_model.database.service import Service as DatabaseService


class Service(FastAPIService):
    def __init__(
        self,
        database: DatabaseService,
        publisher: RabbitMQPublisher,
        worker_publisher: RabbitMQPublisher,
        settings: Settings,
    ) -> None:
        super().__init__(settings=settings)
        self._database = database
        self._publisher = publisher
        self._worker_publisher = worker_publisher
        self._sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=settings.cors_origins,
        )
        self._sio.register_namespace(TaskNamespace("/"))

    @property
    def dependencies(self) -> list:
        return [*super().dependencies, self._publisher, self._worker_publisher]

    @property
    def database(self) -> DatabaseService:
        return self._database

    @property
    def publisher(self) -> RabbitMQPublisher:
        return self._publisher

    @property
    def worker_publisher(self) -> RabbitMQPublisher:
        return self._worker_publisher

    @property
    def sio(self) -> socketio.AsyncServer:
        return self._sio

    def get_app(self) -> socketio.ASGIApp:
        fastapi_app = super().get_app()
        return socketio.ASGIApp(self._sio, other_asgi_app=fastapi_app)

    def setup_app(self, app: fastapi.FastAPI) -> None:
        from ml_service_model.api.rest.dependencies import (
            InvalidPasswordError, UserNotFoundError)
        from ml_service_model.api.rest.predict.handlers import \
            ModelNotFoundError as PredictModelNotFoundError
        from ml_service_model.api.rest.tasks.dependencies import (
            TaskAccessDeniedError, TaskNotFoundError)
        from ml_service_model.services.task_service import (ModelInactiveError,
                                                            ModelNotFoundError)

        @app.exception_handler(UserNotFoundError)
        async def _user_not_found(_: fastapi.Request, exc: UserNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=401, content={"detail": str(exc)})

        @app.exception_handler(InvalidPasswordError)
        async def _invalid_password(_: fastapi.Request, exc: InvalidPasswordError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=401, content={"detail": str(exc)})

        @app.exception_handler(ModelNotFoundError)
        async def _model_not_found(_: fastapi.Request, exc: ModelNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=404, content={"detail": str(exc)})

        @app.exception_handler(PredictModelNotFoundError)
        async def _predict_model_not_found(_: fastapi.Request, exc: PredictModelNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=404, content={"detail": str(exc)})

        @app.exception_handler(ModelInactiveError)
        async def _model_inactive(_: fastapi.Request, exc: ModelInactiveError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=422, content={"detail": str(exc)})

        @app.exception_handler(TaskNotFoundError)
        async def _task_not_found(_: fastapi.Request, exc: TaskNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=404, content={"detail": str(exc)})

        @app.exception_handler(TaskAccessDeniedError)
        async def _task_access_denied(_: fastapi.Request, exc: TaskAccessDeniedError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=403, content={"detail": str(exc)})

        app.include_router(router)


def get_service(
    database: DatabaseService,
    publisher: RabbitMQPublisher,
    worker_publisher: RabbitMQPublisher,
    settings: Settings | None = None,
) -> Service:
    return Service(
        database=database,
        publisher=publisher,
        worker_publisher=worker_publisher,
        settings=settings or Settings(),
    )
