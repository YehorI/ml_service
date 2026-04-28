import facet

import ml_service_users
from ml_service_users.settings import Settings as UsersSettings


class Service(facet.AsyncioServiceMixin):
    def __init__(self, users: ml_service_users.Service) -> None:
        self._users = users

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        return [*super().dependencies, self._users]

    @property
    def users(self) -> ml_service_users.Service:
        return self._users


def get_service(users_settings: UsersSettings | None = None) -> Service:
    users_service = ml_service_users.get_service(settings=users_settings)
    return Service(users=users_service)
