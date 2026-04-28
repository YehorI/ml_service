import fastapi

from database_repository.dto.users import User
from ml_service_users.api.rest.dependencies import get_current_user, get_database
from ml_service_users.database.service import Service


class UserNotFoundError(Exception):
    pass


async def get_path_user(
    user_id: int = fastapi.Path(),
    database: Service = fastapi.Depends(get_database),
) -> User:
    user = await database.get_user_by_id(user_id)
    if user is None:
        raise UserNotFoundError(f"User id={user_id} not found")
    return user


async def get_authenticated_user(user: User = fastapi.Depends(get_current_user)) -> User:
    return user
