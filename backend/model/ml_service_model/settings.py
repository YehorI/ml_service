from ml_service_common.messaging.settings import (BillingMessagingSettings,
                                                  CompletedMessagingSettings,
                                                  MessagingSettings,
                                                  WorkerMessagingSettings)
from ml_service_model.api.settings import Settings as ApiSettings
from ml_service_model.database.settings import Settings as DatabaseSettings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api: ApiSettings = ApiSettings()
    database: DatabaseSettings = DatabaseSettings()
    billing_messaging: BillingMessagingSettings = BillingMessagingSettings()
    predict_messaging: MessagingSettings = MessagingSettings()
    worker_messaging: WorkerMessagingSettings = WorkerMessagingSettings()
    completed_messaging: CompletedMessagingSettings = CompletedMessagingSettings()
