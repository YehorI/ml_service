import time

import pytest

from ml_service.api.jwt_auth import (
    InvalidTokenError,
    JWTSettings,
    TokenExpiredError,
    create_access_token,
    decode_access_token,
)


class TestCreateAndDecode:
    def test_round_trip_returns_user_id(self) -> None:
        settings = JWTSettings(secret="unit-test-secret", access_ttl_seconds=60)
        token, ttl = create_access_token(user_id=42, settings=settings)
        assert ttl == 60

        payload = decode_access_token(token, settings=settings)
        assert payload["sub"] == "42"
        assert payload["type"] == "access"
        assert payload["exp"] > payload["iat"]

    def test_token_is_three_dot_separated(self) -> None:
        token, _ = create_access_token(user_id=1)
        assert token.count(".") == 2


class TestRejectsInvalidTokens:
    def test_malformed_token(self) -> None:
        with pytest.raises(InvalidTokenError):
            decode_access_token("not-a-jwt")

    def test_tampered_payload(self) -> None:
        settings = JWTSettings(secret="abc", access_ttl_seconds=60)
        token, _ = create_access_token(user_id=1, settings=settings)
        header, payload, signature = token.split(".")
        tampered = f"{header}.{payload}AAA.{signature}"
        with pytest.raises(InvalidTokenError):
            decode_access_token(tampered, settings=settings)

    def test_wrong_secret(self) -> None:
        a = JWTSettings(secret="one", access_ttl_seconds=60)
        b = JWTSettings(secret="two", access_ttl_seconds=60)
        token, _ = create_access_token(user_id=1, settings=a)
        with pytest.raises(InvalidTokenError):
            decode_access_token(token, settings=b)

    def test_expired_token(self) -> None:
        settings = JWTSettings(secret="abc", access_ttl_seconds=-1)
        token, _ = create_access_token(user_id=1, settings=settings)
        # Even with a fresh ttl=-1, exp is already in the past.
        with pytest.raises(TokenExpiredError):
            decode_access_token(token, settings=settings)

    def test_unsupported_algorithm(self) -> None:
        settings = JWTSettings(secret="abc", access_ttl_seconds=60)
        token, _ = create_access_token(user_id=1, settings=settings)
        # Force decoder to expect a different algorithm.
        other = JWTSettings(secret="abc", algorithm="HS512", access_ttl_seconds=60)
        with pytest.raises(InvalidTokenError):
            decode_access_token(token, settings=other)

    def test_decode_rejects_refresh_type(self) -> None:
        # The decoder only accepts type="access". Forge a token with a different
        # type to make sure that's enforced.
        import base64
        import hashlib
        import hmac
        import json

        settings = JWTSettings(secret="abc", access_ttl_seconds=60)
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"sub": "1", "iat": now, "exp": now + 60, "type": "refresh"}

        def b64(b: bytes) -> str:
            return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

        h = b64(json.dumps(header, separators=(",", ":")).encode())
        p = b64(json.dumps(payload, separators=(",", ":")).encode())
        sig = hmac.new(b"abc", f"{h}.{p}".encode(), hashlib.sha256).digest()
        token = f"{h}.{p}.{b64(sig)}"

        with pytest.raises(InvalidTokenError):
            decode_access_token(token, settings=settings)
