from datetime import datetime

import fastapi

COOKIE_SETTINGS = {
    "path": "/",
    "domain": None,
    "secure": True,
    "httponly": True,
    "samesite": "none",
}


def set_cookie(
        response: fastapi.Response,
        name: str,
        value: str,
        expires: datetime,
) -> fastapi.Response:
    response.set_cookie(
        key=name,
        value=value,
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        **COOKIE_SETTINGS,
    )

    return response


def delete_cookie(response: fastapi.Response, name: str) -> fastapi.Response:
    response.delete_cookie(key=name, **COOKIE_SETTINGS)

    return response
