from pydantic_settings import BaseSettings

from ml_service_common.messaging.settings import MessagingSettings
from ml_service_model.api.settings import Settings as ApiSettings
from ml_service_model.database.settings import Settings as DatabaseSettings


class Settings(BaseSettings):
    api: ApiSettings = ApiSettings()
    database: DatabaseSettings = DatabaseSettings()
    messaging: MessagingSettings = MessagingSettings()
