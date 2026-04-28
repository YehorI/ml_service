import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass


class JWTError(Exception):
    pass


class TokenExpiredError(JWTError):
    pass


class InvalidTokenError(JWTError):
    pass


@dataclass(frozen=True)
class JWTSettings:
    secret: str
    algorithm: str = "HS256"
    access_ttl_seconds: int = 3600

    @classmethod
    def from_env(cls) -> "JWTSettings":
        return cls(
            secret=os.getenv("JWT_SECRET", "dev-secret-change-me"),
            algorithm="HS256",
            access_ttl_seconds=int(os.getenv("JWT_ACCESS_TTL_SECONDS", "3600")),
        )


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def create_access_token(user_id: int, settings: JWTSettings | None = None) -> tuple[str, int]:
    settings = settings or JWTSettings.from_env()
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.access_ttl_seconds,
        "type": "access",
    }
    header = {"alg": settings.algorithm, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(settings.secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}", settings.access_ttl_seconds


def decode_access_token(token: str, settings: JWTSettings | None = None) -> dict:
    settings = settings or JWTSettings.from_env()
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("Malformed token")
    header_b64, payload_b64, signature_b64 = parts

    try:
        header = json.loads(_b64url_decode(header_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise InvalidTokenError("Bad header") from exc
    if header.get("alg") != settings.algorithm:
        raise InvalidTokenError("Unsupported algorithm")

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected = hmac.new(settings.secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    try:
        actual = _b64url_decode(signature_b64)
    except ValueError as exc:
        raise InvalidTokenError("Bad signature encoding") from exc
    if not hmac.compare_digest(expected, actual):
        raise InvalidTokenError("Invalid signature")

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise InvalidTokenError("Bad payload") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise TokenExpiredError("Token expired")
    if payload.get("type") != "access":
        raise InvalidTokenError("Wrong token type")
    if "sub" not in payload:
        raise InvalidTokenError("Missing subject")
    return payload
