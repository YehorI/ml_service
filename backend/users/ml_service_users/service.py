import facet

from ml_service_users import api, database
from ml_service_users.settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, api: api.Service) -> None:
        self._api = api

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        return [*super().dependencies, self._api]

    @property
    def api(self) -> api.Service:
        return self._api


def get_service(settings: Settings | None = None) -> Service:
    settings = settings or Settings()
    database_service = database.get_service(settings=settings.database)
    api_service = api.get_service(
        database=database_service,
        settings=settings.api,
    )
    return Service(api=api_service)
