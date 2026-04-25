from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from model.services.task_service import (
    InvalidInputDataError,
    ModelInactiveError,
    ModelNotFoundError,
)
from users.services.user_service import (
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from wallet.services.wallet_service import InsufficientFundsError


def _err(code: str, message: str, *, details: list[str] | None = None) -> dict:
    payload: dict = {"code": code, "message": message}
    if details:
        payload["details"] = details
    return {"error": payload}


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserAlreadyExistsError)
    async def _user_exists(_: Request, exc: UserAlreadyExistsError):
        return JSONResponse(status_code=409, content=_err("user_exists", str(exc)))

    @app.exception_handler(UserNotFoundError)
    async def _user_not_found(_: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=401, content=_err("invalid_credentials", str(exc)))

    @app.exception_handler(InvalidPasswordError)
    async def _invalid_password(_: Request, exc: InvalidPasswordError):
        return JSONResponse(status_code=401, content=_err("invalid_credentials", str(exc)))

    @app.exception_handler(InsufficientFundsError)
    async def _insufficient(_: Request, exc: InsufficientFundsError):
        return JSONResponse(status_code=402, content=_err("insufficient_funds", str(exc)))

    @app.exception_handler(ModelNotFoundError)
    async def _model_missing(_: Request, exc: ModelNotFoundError):
        return JSONResponse(status_code=404, content=_err("model_not_found", str(exc)))

    @app.exception_handler(ModelInactiveError)
    async def _model_inactive(_: Request, exc: ModelInactiveError):
        return JSONResponse(status_code=409, content=_err("model_inactive", str(exc)))

    @app.exception_handler(InvalidInputDataError)
    async def _bad_input(_: Request, exc: InvalidInputDataError):
        return JSONResponse(
            status_code=422,
            content=_err("invalid_input", str(exc), details=exc.details),
        )

    @app.exception_handler(ValidationError)
    async def _pydantic(_: Request, exc: ValidationError):
        details = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
        return JSONResponse(status_code=422, content=_err("validation_error", "Invalid request", details=details))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        return JSONResponse(status_code=500, content=_err("internal_error", str(exc)))

