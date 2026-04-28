from fastapi import APIRouter, Depends
from ml_service_model.interfaces.repositories import MLModelRepository
from ml_service_model.services.task_service import (
    InvalidInputDataError,
    ModelInactiveError,
    ModelNotFoundError,
    TaskService,
)
from ml_service_users.domains.user import User
from ml_service_wallet.database.repositories import SqlAlchemyAltBalanceRepository
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.services.wallet_service import InsufficientFundsError

from database_repository.service import Service
from ml_service.api.deps import (
    db_transaction,
    get_current_user,
    get_model_repository,
    get_task_service,
)
from ml_service.api.schemas import (
    BatchPredictAccepted,
    BatchPredictRejected,
    BatchPredictRequest,
    BatchPredictResponse,
    PredictRequest,
    PredictResponse,
)

router = APIRouter()


async def _get_wallet(service: Service, user: User) -> Wallet:
    repo = SqlAlchemyAltBalanceRepository(service)
    wallet = await repo.get_by_user_id(user.user_id)
    if wallet is None:
        wallet = await repo.save(Wallet(user_id=user.user_id, amount=0.0))
    return wallet


def _validate_item(item) -> list[str]:
    errors: list[str] = []
    if not isinstance(item, dict):
        errors.append("expected JSON object")
        return errors
    if not item:
        errors.append("object must not be empty")
    return errors


@router.post("", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
    task_service: TaskService = Depends(get_task_service),
):
    wallet = await _get_wallet(service, user)
    task, result = await task_service.predict(
        user=user,
        wallet=wallet,
        model_id=payload.model_id,
        input_data=payload.input_data,
    )
    return PredictResponse(
        task_id=task.task_id,
        status=task.status.value,
        credits_charged=result.credits_charged,
        output_data=result.output_data,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(
    payload: BatchPredictRequest,
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
    task_service: TaskService = Depends(get_task_service),
    model_repo: MLModelRepository = Depends(get_model_repository),
):
    model = await model_repo.get_by_id(payload.model_id)
    if model is None:
        raise ModelNotFoundError(f"Model id={payload.model_id} not found")
    if not model.is_active:
        raise ModelInactiveError(f"Model id={payload.model_id} is inactive")

    rejected: list[BatchPredictRejected] = []
    valid_indexed: list[tuple[int, dict]] = []
    for idx, item in enumerate(payload.items):
        errs = _validate_item(item)
        if errs:
            rejected.append(BatchPredictRejected(index=idx, errors=errs))
        else:
            valid_indexed.append((idx, item))

    if not valid_indexed:
        return BatchPredictResponse(accepted=[], rejected=rejected, total_charged=0.0)

    cost_per_item = float(model.cost_per_request)
    total_required = cost_per_item * len(valid_indexed)
    wallet = await _get_wallet(service, user)
    if not wallet.has_sufficient_funds(total_required):
        raise InsufficientFundsError(
            f"Need {total_required} for {len(valid_indexed)} item(s), wallet has {wallet.amount}"
        )

    accepted: list[BatchPredictAccepted] = []
    for idx, item in valid_indexed:
        try:
            task, result = await task_service.predict(
                user=user,
                wallet=wallet,
                model_id=payload.model_id,
                input_data=item,
            )
        except InvalidInputDataError as exc:
            rejected.append(BatchPredictRejected(index=idx, errors=[str(exc), *exc.details]))
            continue
        accepted.append(
            BatchPredictAccepted(
                index=idx,
                task_id=task.task_id,
                output_data=result.output_data,
                credits_charged=result.credits_charged,
            )
        )

    total_charged = sum(a.credits_charged for a in accepted)
    return BatchPredictResponse(accepted=accepted, rejected=rejected, total_charged=total_charged)
