from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.domains.task import MLTask
from ml_service_model.interfaces.repositories import MLModelRepository
from ml_service_model.services.task_service import (
    ModelInactiveError,
    ModelNotFoundError,
)
from ml_service_users.domains.user import User
from ml_service_wallet.services.wallet_service import (
    InsufficientFundsError,
    WalletService,
)
from pydantic import BaseModel, Field

from database_repository.service import Service
from ml_service.api.deps import (
    db_transaction,
    get_current_user,
    get_model_repository,
    get_wallet_service,
)
from ml_service.api.routers.predict import _get_wallet
from ml_service.messaging import PredictTaskMessage, TaskPublisher

router = APIRouter()


class SubmitTaskRequest(BaseModel):
    model_id: int = Field(gt=0)
    input_data: dict[str, Any]


class SubmitTaskResponse(BaseModel):
    task_id: int
    status: str
    queued_at: datetime


class TaskStatusResponse(BaseModel):
    task_id: int
    model_id: int
    status: str
    input_data: Any
    output_data: dict[str, Any] | None
    credits_charged: float | None
    created_at: datetime
    completed_at: datetime | None


@router.post("", response_model=SubmitTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_task(
    payload: SubmitTaskRequest,
    request: Request,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
    model_repo: MLModelRepository = Depends(get_model_repository),
    wallet_service: WalletService = Depends(get_wallet_service),
) -> SubmitTaskResponse:
    publisher: TaskPublisher | None = getattr(request.app.state, "task_publisher", None)
    if publisher is None:
        raise HTTPException(status_code=503, detail="Task queue is not available")

    model = await model_repo.get_by_id(payload.model_id)
    if model is None:
        raise ModelNotFoundError(f"Model id={payload.model_id} not found")
    if not model.is_active:
        raise ModelInactiveError(f"Model id={payload.model_id} is inactive")

    wallet = await _get_wallet(service, user)
    cost = float(model.cost_per_request)
    if not wallet.has_sufficient_funds(cost):
        raise InsufficientFundsError(
            f"Need {cost} for model {model.name}, wallet has {wallet.amount}"
        )

    task_repo = SqlAlchemyAltMLTaskRepository(service)
    saved_task = await task_repo.save(
        MLTask(task_id=0, user=user, model=model, input_data=payload.input_data)
    )
    await wallet_service.charge_for_task(
        user=user,
        wallet=wallet,
        task_id=saved_task.task_id,
        amount=cost,
    )

    submitted_at = datetime.now(timezone.utc)
    message = PredictTaskMessage(
        task_id=saved_task.task_id,
        user_id=user.user_id,
        model_id=model.model_id,
        submitted_at=submitted_at,
    )
    # Publish failure raises; the surrounding db_transaction rolls back so
    # the task row and the debit are both undone — the user is not charged
    # for a job that never made it onto the queue.
    try:
        await publisher.publish(message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to enqueue task: {exc}") from exc

    return SubmitTaskResponse(
        task_id=saved_task.task_id,
        status=saved_task.status.value,
        queued_at=submitted_at,
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
) -> TaskStatusResponse:
    task_repo = SqlAlchemyAltMLTaskRepository(service)
    task = await task_repo.get_by_id(task_id)
    if task is None or task.user.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    result_repo = SqlAlchemyAltPredictionResultRepository(service)
    result = await result_repo.get_by_task_id(task_id)
    return TaskStatusResponse(
        task_id=task.task_id,
        model_id=task.model.model_id,
        status=task.status.value,
        input_data=task.input_data,
        output_data=result.output_data if result else None,
        credits_charged=result.credits_charged if result else None,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )
