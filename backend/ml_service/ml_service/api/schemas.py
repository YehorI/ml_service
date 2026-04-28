from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class ErrorResponse(BaseModel):
    error: dict[str, Any]


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserPublic
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class BalanceResponse(BaseModel):
    amount: float


class DepositRequest(BaseModel):
    amount: float = Field(gt=0)


class PredictRequest(BaseModel):
    model_id: int = Field(gt=0)
    input_data: dict[str, Any]


class PredictResponse(BaseModel):
    task_id: int
    status: str
    credits_charged: float
    output_data: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None


class TransactionItem(BaseModel):
    id: int
    type: str
    amount: float
    ml_task_id: int | None
    created_at: datetime


class TaskHistoryItem(BaseModel):
    task_id: int
    model_id: int
    status: str
    created_at: datetime
    completed_at: datetime | None


class ModelItem(BaseModel):
    model_id: int
    name: str
    description: str
    cost_per_request: float
    is_active: bool


class BatchPredictRequest(BaseModel):
    model_id: int = Field(gt=0)
    items: list[Any] = Field(min_length=1)


class BatchPredictAccepted(BaseModel):
    index: int
    task_id: int
    output_data: dict[str, Any]
    credits_charged: float


class BatchPredictRejected(BaseModel):
    index: int
    errors: list[str]


class BatchPredictResponse(BaseModel):
    accepted: list[BatchPredictAccepted]
    rejected: list[BatchPredictRejected]
    total_charged: float

