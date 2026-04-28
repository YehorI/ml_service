from ml_service_users.domains.user import User
from ml_service_users.interfaces.repositories import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def register(self, username: str, email: str, password_hash: str) -> User:
        if await self._user_repository.get_by_username(username) is not None:
            raise UserAlreadyExistsError(f"User with username {username!r} already exists")
        if await self._user_repository.get_by_email(email) is not None:
            raise UserAlreadyExistsError(f"User with email {email!r} already exists")

        user = User(
            user_id=0,
            username=username,
            email=email,
            password_hash=password_hash,
        )
        return await self._user_repository.save(user)

    async def authenticate(self, username: str, password_hash: str) -> User:
        user = await self._user_repository.get_by_username(username)
        if user is None:
            raise UserNotFoundError(f"User {username!r} not found")
        if not user.verify_password(password_hash):
            raise InvalidPasswordError("Invalid password")
        return user

    async def get_by_id(self, user_id: int) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User id={user_id} not found")
        return user
