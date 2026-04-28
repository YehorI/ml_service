import os

from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings


def get_settings() -> SQLAlchemySettings:
    return SQLAlchemySettings(
        dsn=os.environ.get(
            "DATABASE__DSN",
            "postgresql+asyncpg://user:Passw0rd@localhost:5432/user",
        ),
        pool_size=int(os.environ.get("DATABASE__POOL_SIZE", "10")),
        pool_recycle=int(os.environ.get("DATABASE__POOL_RECYCLE", "3600")),
    )


class Service(SQLAlchemyService):
    def __init__(
        self,
        settings: SQLAlchemySettings | None = None,
    ) -> None:
        super().__init__(settings=settings or get_settings(), logger=None)


DatabaseService = Service


def get_service(settings: SQLAlchemySettings | None = None) -> Service:
    return Service(settings=settings)
