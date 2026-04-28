from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings


class Service(SQLAlchemyService):
    def __init__(self, settings: SQLAlchemySettings | None = None) -> None:
        super().__init__(settings=settings or SQLAlchemySettings(), logger=None)
