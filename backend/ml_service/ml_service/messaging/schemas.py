from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PredictTaskMessage(BaseModel):
    """Envelope put on RabbitMQ when /tasks enqueues an async prediction.

    Carries DB identifiers only — the worker reloads the full task, user,
    model, and input data from the database. Keeping the message minimal
    means the queue can never disagree with the source of truth.
    """

    task_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    model_id: int = Field(gt=0)
    submitted_at: datetime


class PredictTaskResult(BaseModel):
    task_id: int
    model_name: str
    output_data: dict[str, Any]
    processed_at: datetime
