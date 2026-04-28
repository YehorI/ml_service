from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService

from ml_service_wallet.database.settings import Settings


class Service(SQLAlchemyService):
    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__(settings=settings or Settings(), logger=None)


def get_service(settings: Settings | None = None) -> Service:
    return Service(settings=settings)
