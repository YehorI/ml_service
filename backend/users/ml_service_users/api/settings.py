from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "ML Service Users API"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
