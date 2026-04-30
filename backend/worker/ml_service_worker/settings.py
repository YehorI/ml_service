from ml_service_common.messaging.settings import WorkerMessagingSettings
from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(SQLAlchemySettings):
    model_config = SettingsConfigDict(extra="ignore")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    # Falls back to container's HOSTNAME if WORKER_ID is not set
    worker_id: str = Field(
        default="worker",
        validation_alias=AliasChoices("WORKER_ID", "HOSTNAME"),
    )
    database: DatabaseSettings = DatabaseSettings()
    worker_messaging: WorkerMessagingSettings = WorkerMessagingSettings()
