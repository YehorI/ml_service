import fastapi
from ml_service_common.fastapi import FastAPIService

from ml_service_model.api.router import router
from ml_service_model.api.settings import Settings
from ml_service_model.database.service import Service as DatabaseService


class Service(FastAPIService):
    def __init__(self, database: DatabaseService, settings: Settings) -> None:
        super().__init__(settings=settings)
        self._database = database

    @property
    def database(self) -> DatabaseService:
        return self._database

    def setup_app(self, app: fastapi.FastAPI) -> None:
        app.include_router(router)


def get_service(database: DatabaseService, settings: Settings | None = None) -> Service:
    return Service(database=database, settings=settings or Settings())
