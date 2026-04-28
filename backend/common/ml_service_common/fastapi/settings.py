from collabry_common.pydantic_settings import PydanticSettings
from pydantic import AnyHttpUrl, conint


class FastAPISettings(PydanticSettings):
    allowed_origins: list[str] = []
    port: conint(ge=1, le=65535) = 8000
    root_path: str = ""
    root_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")
    session_secret_key: str = "supersecretsessionkey"
