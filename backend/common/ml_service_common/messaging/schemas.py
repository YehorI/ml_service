from datetime import datetime

from pydantic import BaseModel, Field


class PredictTaskMessage(BaseModel):
    task_id: int
    model_id: int
    user_id: int
    model_name: str = Field(min_length=1)
    input_data: dict
    submitted_at: datetime
