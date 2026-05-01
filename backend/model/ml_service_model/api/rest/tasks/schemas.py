from datetime import datetime
from typing import Any

from ml_service_model.domains.task import MLTask, PredictionResult
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    model_id: int
    input_data: dict


class PredictionResultResponse(BaseModel):
    output_data: Any
    credits_charged: float
    created_at: datetime


class TaskResponse(BaseModel):
    id: int
    model_id: int
    status: str
    input_data: dict
    created_at: datetime
    completed_at: datetime | None = None
    result: PredictionResultResponse | None = None

    @classmethod
    def from_domain(cls, task: MLTask) -> "TaskResponse":
        result = None
        if task.result is not None:
            result = PredictionResultResponse(
                output_data=task.result.output_data,
                credits_charged=task.result.credits_charged,
                created_at=task.result.created_at,
            )
        return cls(
            id=task.task_id,
            model_id=task.model.model_id,
            status=task.status.value,
            input_data=task.input_data,
            created_at=task.created_at,
            completed_at=task.completed_at,
            result=result,
        )
