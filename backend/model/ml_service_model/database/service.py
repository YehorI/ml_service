from database_repository.dto.users import AdminUser, User, UserRole
from database_repository.models import UserORM, UserRoleORM
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_model.database.settings import Settings
from sqlalchemy import select


def _to_user(orm: UserORM) -> User:
    if orm.role == UserRoleORM.ADMIN:
        return AdminUser(
            user_id=orm.id,
            username=orm.username,
            email=orm.email,
            password_hash=orm.password_hash,
            created_at=orm.created_at,
        )
    return User(
        user_id=orm.id,
        username=orm.username,
        email=orm.email,
        password_hash=orm.password_hash,
        role=UserRole.USER,
        created_at=orm.created_at,
    )


class Service(SQLAlchemyService):
    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__(settings=settings or Settings(), logger=None)

    async def get_user_by_username(self, username: str) -> User | None:
        row = (
            await self.session.execute(select(UserORM).where(UserORM.username == username))
        ).scalar_one_or_none()
        return None if row is None else _to_user(row)


def get_service(settings: Settings | None = None) -> Service:
    return Service(settings=settings)
