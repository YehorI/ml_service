import fastapi
from ml_service_common.fastapi.dependencies.jwt import get_jwt_data
from ml_service_common.fastapi.exceptions import HTTPForbidden, HTTPNotAuthenticated
from ml_service_common.jwt import JWTData
from ml_service_common.sqlalchemy import SQLAlchemyService
from ml_service_database_repository.models import User


async def get_jwt_user(
        request: fastapi.Request,
        jwt_data: JWTData | None = fastapi.Depends(get_jwt_data),
) -> User | None:
    if jwt_data is None:
        return None

    database_service: SQLAlchemyService = request.app.service.database
    async with database_service.transaction():
        return await database_service.get_user(user_id=jwt_data.user_id)


async def is_auth_user(user: User | None = fastapi.Depends(get_jwt_user)) -> User:
    if user is None:
        raise HTTPNotAuthenticated()

    return user


async def is_activated_user(
        request: fastapi.Request,
        user: User = fastapi.Depends(is_auth_user),
) -> User:
    database_service: SQLAlchemyService = request.app.service.database

    if not database_service.user_is_activated(user):
        raise HTTPForbidden()

    return user
