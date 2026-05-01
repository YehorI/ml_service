from datetime import datetime

from pydantic import BaseModel, Field


class BillingRequestMessage(BaseModel):
    task_id: int
    user_id: int
    model_id: int
    model_name: str = Field(min_length=1)
    cost_per_request: float
    input_data: dict
    submitted_at: datetime


class PredictRequestMessage(BaseModel):
    task_id: int
    model_id: int
    model_name: str = Field(min_length=1)
    input_data: dict


class WorkerTaskMessage(BaseModel):
    task_id: int
    username: str
    features: dict
    model_name: str
    model_type: str
    provider_config: dict
    cost_per_request: float


class TaskCompletedMessage(BaseModel):
    task_id: int
    username: str
    output_data: dict
    credits_charged: float
