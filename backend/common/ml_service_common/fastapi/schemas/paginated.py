from typing import Any

from collabry_common.pydantic_dto import PydanticDTO
from pydantic import NonNegativeInt, PositiveInt


class PaginatedResponse(PydanticDTO):
    data: list[Any]
    page: PositiveInt
    per_page: PositiveInt
    total_pages: NonNegativeInt
    total_items: NonNegativeInt
