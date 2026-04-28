import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from ml_service.messaging import PredictTaskMessage, TaskPublisher

router = APIRouter()


class SubmitTaskRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=128)
    input_data: dict[str, Any]


class SubmitTaskResponse(BaseModel):
    task_id: str
    queued_at: datetime


@router.post(
    "",
    response_model=SubmitTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_task(payload: SubmitTaskRequest, request: Request) -> SubmitTaskResponse:
    publisher: TaskPublisher | None = getattr(request.app.state, "task_publisher", None)
    if publisher is None:
        raise HTTPException(status_code=503, detail="Task queue is not available")

    message = PredictTaskMessage(
        task_id=str(uuid.uuid4()),
        model_name=payload.model_name,
        input_data=payload.input_data,
        submitted_at=datetime.now(timezone.utc),
    )
    try:
        await publisher.publish(message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to enqueue task: {exc}") from exc

    return SubmitTaskResponse(task_id=message.task_id, queued_at=message.submitted_at)
