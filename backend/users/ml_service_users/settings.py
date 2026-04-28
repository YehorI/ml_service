from pydantic_settings import BaseSettings

from ml_service_users.api.settings import Settings as ApiSettings
from ml_service_users.database.settings import Settings as DatabaseSettings


class Settings(BaseSettings):
    api: ApiSettings = ApiSettings()
    database: DatabaseSettings = DatabaseSettings()
