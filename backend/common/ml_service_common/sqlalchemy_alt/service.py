import contextvars
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .exceptions import HaveNoSessionError
from .settings import SQLAlchemySettings


class SQLAlchemyService:
    def __init__(self, settings: SQLAlchemySettings, logger=None):
        self._settings = settings
        self._logger = logger

        engine_parameters = {
            "url": str(self._settings.dsn),
            "pool_recycle": self._settings.pool_recycle,
        }
        if not str(self._settings.dsn).startswith("sqlite"):
            engine_parameters["pool_size"] = self._settings.pool_size

        engine = create_async_engine(**engine_parameters)
        self._sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        self._session_context = contextvars.ContextVar("session_context")

    @property
    def session(self) -> AsyncSession:
        session = self._session_context.get(None)
        if session is None:
            raise HaveNoSessionError()

        return session

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        async with self._sessionmaker() as session:
            with self._set_session_to_session_context(session=session):
                async with session.begin():
                    yield

    @contextmanager
    def _set_session_to_session_context(self, session: AsyncSession) -> Generator[None, None, None]:
        token = self._session_context.set(session)
        yield
        self._session_context.reset(token)
