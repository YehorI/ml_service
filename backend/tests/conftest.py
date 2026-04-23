import pytest

from database_repository.service import Service as DatabaseService


@pytest.fixture
async def service() -> DatabaseService:
    return DatabaseService()
