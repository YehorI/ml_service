from ml_service_common.fastapi import FastAPISettings


class Settings(FastAPISettings):
    title: str = "ML Service Users API"
    version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
