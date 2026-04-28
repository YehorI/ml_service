import random
import string

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SessionIDMiddleware(BaseHTTPMiddleware):
    SYMBOLS = string.digits + string.ascii_letters
    LENGTH = 32

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        session = request.scope["session"]
        if "id" not in session:
            session["id"] = self.generate_session_id()

        return response

    @classmethod
    def generate_session_id(cls) -> str:
        return "".join(random.choice(cls.SYMBOLS) for _ in range(cls.LENGTH))
