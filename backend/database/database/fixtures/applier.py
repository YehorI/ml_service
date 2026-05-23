import enum
from typing import Any, AsyncIterable

from database.fixtures.models import FixtureItem
from ml_service_common.sqlalchemy.service import Service as SQLAlchemyService


def _build_model_registry() -> dict[str, Any]:
    from database_repository import models as repo_models

    registry: dict[str, Any] = {}
    for name in repo_models.__all__:
        cls = getattr(repo_models, name)
        tablename = getattr(cls, "__tablename__", None)
        if tablename:
            registry[tablename] = cls
    return registry


def _coerce_fields(cls: Any, fields: dict[str, Any]) -> dict[str, Any]:
    coerced: dict[str, Any] = {}
    mapper = cls.__mapper__
    for key, value in fields.items():
        column = mapper.columns.get(key)
        if column is not None and isinstance(value, str):
            python_type = getattr(column.type, "python_type", None)
            try:
                is_enum = isinstance(python_type, type) and issubclass(python_type, enum.Enum)
            except TypeError:
                is_enum = False
            if is_enum:
                coerced[key] = python_type[value]
                continue
        coerced[key] = value
    return coerced


async def apply_fixtures(
    service: SQLAlchemyService,
    items: AsyncIterable[FixtureItem],
) -> int:
    registry = _build_model_registry()
    count = 0
    async with service.transaction():
        session = service.session
        async for item in items:
            cls = registry.get(item.model)
            if cls is None:
                raise ValueError(f"Unknown fixture model/table: {item.model!r}")
            await session.merge(cls(**_coerce_fields(cls, item.fields)))
            await session.flush()
            count += 1
    return count
