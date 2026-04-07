from ml_service.domains.user import User
from ml_service.interfaces.repositories import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def register(self, username: str, email: str, password_hash: str) -> User:
        NotImplemented

    def authenticate(self, username: str, password_hash: str) -> User:
        NotImplemented
