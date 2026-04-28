from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from sqlalchemy import select

from database_repository.dto.users import AdminUser, User, UserRole
from database_repository.models import UserORM, UserRoleORM, WalletORM
from ml_service_users.database.settings import Settings


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

    async def get_user_by_id(self, user_id: int) -> User | None:
        row = (
            await self.session.execute(select(UserORM).where(UserORM.id == user_id))
        ).scalar_one_or_none()
        return None if row is None else _to_user(row)

    async def get_user_by_username(self, username: str) -> User | None:
        row = (
            await self.session.execute(select(UserORM).where(UserORM.username == username))
        ).scalar_one_or_none()
        return None if row is None else _to_user(row)

    async def get_user_by_email(self, email: str) -> User | None:
        row = (
            await self.session.execute(select(UserORM).where(UserORM.email == email))
        ).scalar_one_or_none()
        return None if row is None else _to_user(row)

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        orm = UserORM(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRoleORM.ADMIN if role == UserRole.ADMIN else UserRoleORM.USER,
        )
        self.session.add(orm)
        await self.session.flush()

        wallet = WalletORM(user_id=orm.id, amount=0.0)
        self.session.add(wallet)
        await self.session.flush()
        return _to_user(orm)

    async def update_user(
        self,
        user: User,
        username: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
    ) -> User:
        orm = (
            await self.session.execute(select(UserORM).where(UserORM.id == user.user_id))
        ).scalar_one()
        if username is not None:
            orm.username = username
        if email is not None:
            orm.email = email
        if password_hash is not None:
            orm.password_hash = password_hash
        return _to_user(orm)


def get_service(settings: Settings | None = None) -> Service:
    return Service(settings=settings)
