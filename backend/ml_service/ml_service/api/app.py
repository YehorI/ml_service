from fastapi import FastAPI

from ml_service.api.errors import install_exception_handlers
from ml_service.api.routers import auth, balance, history, predict, users


def create_app() -> FastAPI:
    app = FastAPI(title="ML Service API", version="0.1.0")

    install_exception_handlers(app)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(balance.router, prefix="/balance", tags=["balance"])
    app.include_router(predict.router, prefix="/predict", tags=["predict"])
    app.include_router(history.router, prefix="/history", tags=["history"])

    return app

