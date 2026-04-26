from fastapi import APIRouter, Depends
from ml_service_common.sqlalchemy.service import Service

from database_repository.repositories import SqlAlchemyBalanceRepository
from ml_service.api.deps import db_transaction, get_current_user, get_task_service
from ml_service.api.schemas import PredictRequest, PredictResponse
from ml_service_model.services.task_service import TaskService
from ml_service_users.domains.user import User
from ml_service_wallet.domains.wallet import Wallet

router = APIRouter()


async def _get_wallet(service: Service, user: User) -> Wallet:
    repo = SqlAlchemyBalanceRepository(service)
    wallet = await repo.get_by_user_id(user.user_id)
    if wallet is None:
        wallet = await repo.save(Wallet(user_id=user.user_id, amount=0.0))
    return wallet


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

