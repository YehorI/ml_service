from pydantic import AliasChoices, AnyUrl, Field, PositiveInt
from pydantic_settings import BaseSettings


class SQLAlchemySettings(BaseSettings):
    dsn: AnyUrl = Field(
        default="postgresql+asyncpg://user:Passw0rd@localhost:5432/user",
        validation_alias=AliasChoices("DATABASE__DSN", "dsn"),
    )
    pool_size: PositiveInt = Field(
        default=5,
        validation_alias=AliasChoices("DATABASE__POOL_SIZE", "pool_size"),
    )
    pool_recycle: PositiveInt = Field(
        default=60,
        validation_alias=AliasChoices("DATABASE__POOL_RECYCLE", "pool_recycle"),
    )  # in seconds: 1 minute
