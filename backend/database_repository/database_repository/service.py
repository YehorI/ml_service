from database.service import SQLAlchemyService
from database.settings import DatabaseSettings


def create_db_service(settings: DatabaseSettings | None = None) -> SQLAlchemyService:
    """Factory to create a configured SQLAlchemyService instance."""
    return SQLAlchemyService(settings=settings)
