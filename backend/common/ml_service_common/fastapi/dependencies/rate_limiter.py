import fastapi
from ml_service_common.fastapi.dependencies.jwt import get_jwt_data
from ml_service_common.fastapi.exceptions import HTTPTooManyRequests
from ml_service_common.interfaces.rate_limiter import RateLimiterInterface
from ml_service_common.jwt import JWTData


class RateLimit:
    def __init__(
            self,
            times: int = 1,
            seconds: int = 0,
            minutes: int = 0,
            hours: int = 0,
            days: int = 0,
            name: str | None = None,
    ):
        self._times = times
        self._seconds = seconds
        self._minutes = minutes
        self._hours = hours
        self._days = days
        self._name = name

    async def __call__(
            self,
            request: fastapi.Request,
            jwt_data: JWTData | None = fastapi.Depends(get_jwt_data),
            real_ip: str | None = fastapi.Header(None, alias="X-Real-IP"),
            x_rate_limit_ignore_token: str | None = fastapi.Header(None),
    ):
        rate_limiter: RateLimiterInterface = request.app.service.rate_limiter
        if await rate_limiter.is_ignore(token=x_rate_limit_ignore_token):
            return

        session = request.scope["session"]
        session_id = session.get("id")
        real_ip = real_ip or (request.client and request.client.host)
        path = self._name or request.scope["path"]

        rate_limiter_data = {
            "ip": real_ip,
            "session_id": session_id,
            "user_id": jwt_data and str(jwt_data.user_id),
            "path": path,
        }
        is_expire = await rate_limiter.is_expire(
            data=rate_limiter_data,
            times=self._times,
            seconds=self.get_timeout_seconds(),
        )
        if is_expire:
            raise HTTPTooManyRequests()

    def get_timeout_seconds(self) -> int:
        timeout_seconds = (
            self._days * 86_400 +
            self._hours * 3_600 +
            self._minutes * 60 +
            self._seconds
        )

        return timeout_seconds
