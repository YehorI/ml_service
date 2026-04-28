import fastapi

from ml_service_users.api.router import router
from ml_service_users.api.settings import Settings


class Service:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def get_app(self) -> fastapi.FastAPI:
        app = fastapi.FastAPI(title=self._settings.title, version=self._settings.version)
        self.setup_app(app)
        return app

    def setup_app(self, app: fastapi.FastAPI) -> None:
        app.include_router(router)

    @property
    def settings(self) -> Settings:
        return self._settings


def get_service(settings: Settings | None = None) -> Service:
    return Service(settings=settings)
