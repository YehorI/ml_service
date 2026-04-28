import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from ml_service_model.interfaces.repositories import MLModelRepository
from ml_service_model.services.task_service import (
    ModelInactiveError,
    ModelNotFoundError,
)
from ml_service_users.domains.user import User
from ml_service_wallet.services.wallet_service import InsufficientFundsError
from pydantic import BaseModel, Field

from database_repository.service import Service
from ml_service.api.deps import (
    db_transaction,
    get_current_user,
    get_model_repository,
)
from ml_service.api.routers.predict import _get_wallet
from ml_service.messaging import PredictTaskMessage, TaskPublisher

router = APIRouter()


class SubmitTaskRequest(BaseModel):
    model_id: int = Field(gt=0)
    input_data: dict[str, Any]


class SubmitTaskResponse(BaseModel):
    task_id: str
    queued_at: datetime


# NOTE: Async path. Currently this endpoint enqueues a task to RabbitMQ for
# the worker to consume; the worker does not yet write task status/results
# back to the database. Until that integration lands the wallet is NOT
# deducted here — instead we only require the user to have a positive
# balance, mirroring the spec's "must have sufficient funds" check without
# committing to a charge that we cannot refund on worker failure. See
# `/predict` for the synchronous, fully wallet-integrated path.
@router.post(
    "",
    response_model=SubmitTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_task(
    payload: SubmitTaskRequest,
    request: Request,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
    model_repo: MLModelRepository = Depends(get_model_repository),
) -> SubmitTaskResponse:
    model = await model_repo.get_by_id(payload.model_id)
    if model is None:
        raise ModelNotFoundError(f"Model id={payload.model_id} not found")
    if not model.is_active:
        raise ModelInactiveError(f"Model id={payload.model_id} is inactive")

    wallet = await _get_wallet(service, user)
    if not wallet.has_sufficient_funds(float(model.cost_per_request)):
        raise InsufficientFundsError(
            f"Need {model.cost_per_request} for model {model.name}, wallet has {wallet.amount}"
        )

    publisher: TaskPublisher | None = getattr(request.app.state, "task_publisher", None)
    if publisher is None:
        raise HTTPException(status_code=503, detail="Task queue is not available")

    message = PredictTaskMessage(
        task_id=str(uuid.uuid4()),
        model_name=model.name,
        input_data=payload.input_data,
        submitted_at=datetime.now(timezone.utc),
    )
    try:
        await publisher.publish(message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to enqueue task: {exc}") from exc

    return SubmitTaskResponse(task_id=message.task_id, queued_at=message.submitted_at)
