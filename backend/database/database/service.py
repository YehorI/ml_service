import contextvars
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.exceptions import HaveNoSessionError
from database.interfaces import TransactionInterface
from database.settings import DatabaseSettings, get_settings


class SQLAlchemyService(TransactionInterface):
    def __init__(self, settings: DatabaseSettings | None = None) -> None:
        self._settings = settings or get_settings()

        engine_parameters: dict = {
            "url": self._settings.dsn,
            "echo": self._settings.echo,
            "pool_recycle": self._settings.pool_recycle,
        }
        if not self._settings.dsn.startswith("sqlite"):
            engine_parameters["pool_size"] = self._settings.pool_size

        engine = create_async_engine(**engine_parameters)
        self._sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        self._session_context: contextvars.ContextVar[AsyncSession | None] = (
            contextvars.ContextVar("session_context", default=None)
        )

    @property
    def session(self) -> AsyncSession:
        session = self._session_context.get(None)
        if session is None:
            raise HaveNoSessionError()
        return session

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        async with self._sessionmaker() as session:
            with self._set_session_to_context(session=session):
                async with session.begin():
                    yield

    @contextmanager
    def _set_session_to_context(self, session: AsyncSession) -> Generator[None, None, None]:
        token = self._session_context.set(session)
        yield
        self._session_context.reset(token)
