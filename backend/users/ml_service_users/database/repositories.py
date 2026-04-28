from ml_service_users.database.service import Service
from ml_service_users.domains.user import AdminUser, User, UserRole
from ml_service_users.interfaces.repositories import UserRepository
from sqlalchemy import select

from database_repository.models import UserORM, UserRoleORM, WalletORM


def to_domain_user(orm: UserORM) -> User:
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


class SqlAlchemyAltUserRepository(UserRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_id(self, user_id: int) -> User | None:
        row = (await self._service.session.execute(select(UserORM).where(UserORM.id == user_id))).scalar_one_or_none()
        return None if row is None else to_domain_user(row)

    async def get_by_username(self, username: str) -> User | None:
        row = (
            await self._service.session.execute(select(UserORM).where(UserORM.username == username))
        ).scalar_one_or_none()
        return None if row is None else to_domain_user(row)

    async def get_by_email(self, email: str) -> User | None:
        row = (await self._service.session.execute(select(UserORM).where(UserORM.email == email))).scalar_one_or_none()
        return None if row is None else to_domain_user(row)

    async def save(self, user: User) -> User:
        role = UserRoleORM.ADMIN if isinstance(user, AdminUser) else UserRoleORM.USER
        orm = UserORM(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            role=role,
            created_at=user.created_at,
        )
        self._service.session.add(orm)
        await self._service.session.flush()

        wallet = WalletORM(user_id=orm.id, amount=0.0)
        self._service.session.add(wallet)
        await self._service.session.flush()
        return to_domain_user(orm)

    async def update(self, user: User) -> User:
        orm = (await self._service.session.execute(select(UserORM).where(UserORM.id == user.user_id))).scalar_one()
        orm.username = user.username
        orm.email = user.email
        orm.password_hash = user.password_hash
        return to_domain_user(orm)
