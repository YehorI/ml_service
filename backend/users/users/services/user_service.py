from users.domains.user import User
from users.interfaces.repositories import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def register(self, username: str, email: str, password_hash: str) -> User:
        raise NotImplementedError

    def authenticate(self, username: str, password_hash: str) -> User:
        raise NotImplementedError
