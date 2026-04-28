from ml_service_common.pydantic_dto import PydanticDTO


class HealthResponse(PydanticDTO):
    version: str
    name: str
