import fastapi
from ml_service_common.fastapi.exceptions import HTTPNotAuthenticated
from ml_service_common.fastapi.utils import set_cookie
from ml_service_common.jwt import JWTData, JWTMethods
from ml_service_common.jwt.utils import extract_jwt_data_from_http_request


async def get_jwt_data(
        response: fastapi.Response,
        request: fastapi.Request,
        access_token_from_cookie: str | None = fastapi.Cookie(None, alias="access_token"),
        refresh_token_from_cookie: str | None = fastapi.Cookie(None, alias="refresh_token"),
        access_token_from_header: str | None = fastapi.Header(None, alias="Authorization"),
) -> JWTData | None:
    if not hasattr(request.app.service, "jwt_methods"):
        raise NotImplementedError("No jwt object in service")
    jwt_methods: JWTMethods = request.app.service.jwt_methods

    jwt_data, need_refresh = extract_jwt_data_from_http_request(
        jwt_methods=jwt_methods,
        access_token_from_header=access_token_from_header,
        access_token_from_cookie=access_token_from_cookie,
        refresh_token_from_cookie=refresh_token_from_cookie,
    )

    if jwt_data and need_refresh:
        new_access_token = jwt_methods.issue_access_token(user_id=jwt_data.user_id)
        new_refresh_token = jwt_methods.issue_refresh_token(user_id=jwt_data.user_id)
        response = set_cookie(response=response, name="access_token", value=new_access_token,
                              expires=jwt_methods.access_token_expires_utc)
        response = set_cookie(response=response, name="refresh_token", value=new_refresh_token,
                              expires=jwt_methods.refresh_token_expires_utc)
    return jwt_data


async def is_auth(jwt_data: JWTData | None = fastapi.Depends(get_jwt_data)) -> JWTData:
    if jwt_data is None:
        raise HTTPNotAuthenticated()

    return jwt_data
