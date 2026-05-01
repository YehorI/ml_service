from typing import Any, Protocol

from .enums import LoggerLevelEnum


class LoggerInterface(Protocol):
    async def debug(self, message: str, **extra: Any):
        await self.write(level=LoggerLevelEnum.DEBUG, message=message, **extra)

    async def info(self, message: str, **extra: Any):
        await self.write(level=LoggerLevelEnum.INFO, message=message, **extra)

    async def warning(self, message: str, **extra: Any):
        await self.write(level=LoggerLevelEnum.WARNING, message=message, **extra)

    async def error(self, message: str, **extra: Any):
        await self.write(level=LoggerLevelEnum.ERROR, message=message, **extra)

    async def critical(self, message: str, **extra: Any):
        await self.write(level=LoggerLevelEnum.CRITICAL, message=message, **extra)

    async def write(self, level: LoggerLevelEnum, message: str, **extra: Any):
        raise NotImplementedError
