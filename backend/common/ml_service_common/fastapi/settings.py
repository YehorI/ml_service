from pydantic_settings import BaseSettings


class FastAPISettings(BaseSettings):
    title: str = ""
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
