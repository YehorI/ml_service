import facet

import ml_service_users


class Service(facet.AsyncioServiceMixin):
    def __init__(
            self,
            users: ml_service_users.Service | None,
    ) -> None:
        self._users = users

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        optional = [
            self._users,
        ]
        return [*super().dependencies, *filter(None, optional)]

    @property
    def users(self) -> ml_service_users.Service | None:
        return self._users


def get_service(
        users_settings: ml_service_users.Settings | None = None,
) -> Service:
    users_service = ml_service_users.get_service(settings=users_settings)
    return Service(users=users_service)
