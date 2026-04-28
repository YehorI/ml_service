from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PredictTaskMessage(BaseModel):
    task_id: str
    model_name: str = Field(min_length=1, max_length=128)
    input_data: dict[str, Any]
    submitted_at: datetime


class PredictTaskResult(BaseModel):
    task_id: str
    model_name: str
    output_data: dict[str, Any]
    processed_at: datetime
