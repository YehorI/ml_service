from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatusDTO(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MLTaskCreateDTO:
    user_id: int
    model_id: int
    input_data: Any
    status: TaskStatusDTO = field(default=TaskStatusDTO.PENDING)


@dataclass
class MLTaskReadDTO:
    id: int
    user_id: int
    model_id: int
    input_data: Any
    status: TaskStatusDTO
    created_at: datetime
    completed_at: datetime | None


@dataclass
class PredictionResultCreateDTO:
    task_id: int
    output_data: Any
    credits_charged: float


@dataclass
class PredictionResultReadDTO:
    id: int
    task_id: int
    output_data: Any
    credits_charged: float
    created_at: datetime
