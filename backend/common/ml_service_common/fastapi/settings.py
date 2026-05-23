from pydantic_settings import BaseSettings


class FastAPISettings(BaseSettings):
    title: str = ""
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
