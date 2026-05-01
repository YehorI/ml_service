import ml_service_model
import ml_service_users
import ml_service_wallet
from ml_service_common.pydantic_settings import PydanticSettings


class Settings(PydanticSettings):
    users: ml_service_users.Settings = ml_service_users.Settings()
    wallet: ml_service_wallet.Settings = ml_service_wallet.Settings()
    model: ml_service_model.Settings = ml_service_model.Settings()
