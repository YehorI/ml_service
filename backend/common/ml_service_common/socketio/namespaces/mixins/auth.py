from http.cookies import CookieError, SimpleCookie
from typing import Any

from ml_service_common.jwt.methods import JWTMethods
from ml_service_common.jwt.models import JWTData
from ml_service_common.jwt.utils import extract_jwt_data_from_http_request
from ml_service_common.socketio.exceptions import NotAuthenticatedError


class AuthNamespaceMixin:
    def __init__(self, jwt_methods: JWTMethods):
        self._jwt_methods = jwt_methods

    @property
    def jwt_methods(self) -> JWTMethods:
        return self._jwt_methods

    def auth(self, environ: dict[str, Any]) -> JWTData | None:
        access_token_from_header = environ.get("HTTP_AUTHORIZATION")
        access_token_from_cookie, refresh_token_from_cookie = None, None

        if (cookie_header := environ.get("HTTP_COOKIE")) is not None:
            try:
                cookies = SimpleCookie(cookie_header)
            except CookieError:
                cookies = SimpleCookie()
            access_token_from_cookie = cookies.get("access_token")
            access_token_from_cookie = (
                access_token_from_cookie and str(access_token_from_cookie.value).strip()
            )
            refresh_token_from_cookie = cookies.get("refresh_token")
            refresh_token_from_cookie = (
                refresh_token_from_cookie and str(refresh_token_from_cookie.value).strip()
            )

        jwt_data, _ = extract_jwt_data_from_http_request(
            jwt_methods=self._jwt_methods,
            access_token_from_header=access_token_from_header,
            access_token_from_cookie=access_token_from_cookie,
            refresh_token_from_cookie=refresh_token_from_cookie,
        )
        return jwt_data

    async def on_connect(self, sid: str, environ: dict[str, Any]):
        jwt_data = self.auth(environ=environ)
        if jwt_data is None:
            raise NotAuthenticatedError()

        await self.save_session(sid, {"user_id": jwt_data.user_id})
