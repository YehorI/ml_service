from ml_service_common.messaging.settings import WorkerMessagingSettings
from ml_service_common.sqlalchemy_alt.settings import SQLAlchemySettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    worker_id: str = "worker-1"
    database: SQLAlchemySettings = SQLAlchemySettings()
    worker_messaging: WorkerMessagingSettings = WorkerMessagingSettings()
