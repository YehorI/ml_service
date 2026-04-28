import io
import json
from dataclasses import dataclass

from ml_service_common.interfaces.http_client.exceptions import HTTPException


@dataclass
class HTTPResponse:
    url: str
    status_code: int
    headers: dict[str, str]
    body: io.BytesIO

    def __post_init__(self):
        self.validate_status_code(value=self.status_code)
        self.validate_headers(value=self.headers)

    @staticmethod
    def validate_status_code(value: int):
        if not isinstance(value, int):
            raise ValueError("Field 'status_code' must be int.")
        if not 100 <= value <= 599:
            raise ValueError("Field 'status_code' incorrect.")

    @staticmethod
    def validate_headers(value: dict[str, str]):
        if not isinstance(value, dict):
            raise ValueError("Field 'headers' must be dict.")
        for key in value.keys():
            if not isinstance(key, str):
                raise ValueError("Every key in field 'headers' must be str.")
        for _value in value.values():
            if not isinstance(_value, str):
                raise ValueError("Every value in field 'headers' must be str.")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPException(url=self.url, status_code=self.status_code)

    def bytes(self) -> bytes:
        return self.body.read()

    def text(self, encoding: str = "utf-8") -> str:
        body_bytes = self.bytes()
        body_text = body_bytes.decode(encoding=encoding)
        return body_text

    def json(self):
        body_text = self.text()
        body_data = json.loads(body_text)
        return body_data
