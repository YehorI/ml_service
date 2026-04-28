from ml_service_users.service import Service as UsersService
from ml_service_users.service import get_service as get_users_service


class Service:
    def __init__(self, users: UsersService) -> None:
        self._users = users

    @property
    def users(self) -> UsersService:
        return self._users


def get_service() -> Service:
    return Service(users=get_users_service())
