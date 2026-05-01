from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


async def health() -> HealthResponse:
    return HealthResponse()
