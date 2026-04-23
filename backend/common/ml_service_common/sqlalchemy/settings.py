import os


class DatabaseSettings:
    def __init__(self) -> None:
        self.dsn: str = os.environ.get(
            "DATABASE__DSN",
            "postgresql+asyncpg://user:Passw0rd@localhost:5432/user",
        )
        self.echo: bool = os.environ.get("DATABASE__ECHO", "false").lower() == "true"
        self.pool_size: int = int(os.environ.get("DATABASE__POOL_SIZE", "10"))
        self.pool_recycle: int = int(os.environ.get("DATABASE__POOL_RECYCLE", "3600"))


_settings: DatabaseSettings | None = None


def get_settings() -> DatabaseSettings:
    global _settings
    if _settings is None:
        _settings = DatabaseSettings()
    return _settings
