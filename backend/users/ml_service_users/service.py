from ml_service_users.api.service import Service as ApiService
from ml_service_users.api.service import get_service as get_api_service
from ml_service_users.database.service import Service as DatabaseService
from ml_service_users.database.service import get_service as get_database_service
from ml_service_users.settings import Settings


class Service:
    def __init__(self, api: ApiService, database: DatabaseService) -> None:
        self._api = api
        self._database = database

    @property
    def api(self) -> ApiService:
        return self._api

    @property
    def database(self) -> DatabaseService:
        return self._database


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    return Service(
        api=get_api_service(settings=settings.api),
        database=get_database_service(settings=settings.database),
    )
