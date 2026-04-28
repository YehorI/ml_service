from ml_service_common.fastapi import FastAPISettings


class Settings(FastAPISettings):
    title: str = "ML Service Wallet API"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8001
