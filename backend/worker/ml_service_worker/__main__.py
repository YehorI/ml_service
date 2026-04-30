import asyncio

from loguru import logger

from ml_service_worker.service import get_service
from ml_service_worker.settings import Settings


@logger.catch
def main() -> None:
    settings = Settings()
    service = get_service(settings=settings)
    asyncio.run(service.run())


if __name__ == "__main__":
    main()
