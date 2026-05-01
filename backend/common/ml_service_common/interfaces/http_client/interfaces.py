from typing import IO, Any, Iterable, Protocol

from .enums import HTTPMethodEnum
from .models import HTTPResponse


class HTTPClientInterface(Protocol):
    async def send_get_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.GET,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_post_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.POST,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_put_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.PUT,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_delete_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.DELETE,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_patch_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.PATCH,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_head_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.HEAD,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_options_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.OPTIONS,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_trace_request(
            self,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        response = await self.send_request(
            method=HTTPMethodEnum.TRACE,
            path=path,
            parameters=parameters,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        return response

    async def send_request(
            self,
            method: HTTPMethodEnum,
            path: str,
            parameters: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            content: bytes | None = None,
            data: dict[str, str] | None = None,
            json: Any | None = None,
            files: Iterable[IO] | None = None,
            timeout: float | None = None,
            verify_ssl: bool = True,
    ) -> HTTPResponse:
        raise NotImplementedError
