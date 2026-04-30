from ml_service_common.pydantic_settings import PydanticSettings
from pydantic import AnyUrl, conint


class SocketIOSettings(PydanticSettings):
    port: conint(ge=1, le=65535) = 8000
    root_path: str = ""
    allowed_origins: list[str] = []
    redis_url: AnyUrl = AnyUrl("redis://localhost:6379/0")
