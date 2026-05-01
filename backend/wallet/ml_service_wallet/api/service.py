import fastapi
from ml_service_common.fastapi import FastAPIService
from ml_service_wallet.api.router import router
from ml_service_wallet.api.settings import Settings
from ml_service_wallet.database.service import Service as DatabaseService


class Service(FastAPIService):
    def __init__(self, database: DatabaseService, settings: Settings) -> None:
        super().__init__(settings=settings)
        self._database = database

    @property
    def database(self) -> DatabaseService:
        return self._database

    def setup_app(self, app: fastapi.FastAPI) -> None:
        from ml_service_wallet.api.rest.dependencies import (
            InvalidPasswordError, UserNotFoundError)
        from ml_service_wallet.api.rest.wallet.dependencies import \
            WalletNotFoundError

        @app.exception_handler(UserNotFoundError)
        async def _user_not_found(_: fastapi.Request, exc: UserNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=401, content={"detail": str(exc)})

        @app.exception_handler(InvalidPasswordError)
        async def _invalid_password(_: fastapi.Request, exc: InvalidPasswordError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=401, content={"detail": str(exc)})

        @app.exception_handler(WalletNotFoundError)
        async def _wallet_not_found(_: fastapi.Request, exc: WalletNotFoundError) -> fastapi.responses.JSONResponse:
            return fastapi.responses.JSONResponse(status_code=404, content={"detail": str(exc)})

        app.include_router(router)


def get_service(database: DatabaseService, settings: Settings | None = None) -> Service:
    return Service(database=database, settings=settings or Settings())
