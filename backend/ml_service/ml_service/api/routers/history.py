from fastapi import APIRouter, Depends

from database_repository.repositories import (
    SqlAlchemyMLTaskRepository,
    SqlAlchemyTransactionRepository,
)
from ml_service.api.deps import db_transaction, get_current_user
from ml_service.api.schemas import TaskHistoryItem, TransactionItem
from ml_service_common.sqlalchemy.service import Service
from users.domains.user import User
from wallet.domains.transaction import DebitTransaction, DepositTransaction, Transaction


router = APIRouter()


def _tx_to_item(tx: Transaction) -> TransactionItem:
    ml_task_id = getattr(tx, "ml_task_id", None)
    tx_type = "deposit" if isinstance(tx, DepositTransaction) else "debit"
    return TransactionItem(
        id=tx.transaction_id,
        type=tx_type,
        amount=tx.amount,
        ml_task_id=ml_task_id,
        created_at=tx.created_at,
    )


@router.get("/transactions", response_model=list[TransactionItem])
async def transactions(
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
):
    repo = SqlAlchemyTransactionRepository(service)
    items = await repo.list_by_user(user.user_id)
    return [_tx_to_item(t) for t in items]


@router.get("/tasks", response_model=list[TaskHistoryItem])
async def tasks(
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
):
    repo = SqlAlchemyMLTaskRepository(service)
    tasks = await repo.list_by_user(user.user_id)
    return [
        TaskHistoryItem(
            task_id=t.task_id,
            model_id=t.model.model_id,
            status=t.status.value,
            created_at=t.created_at,
            completed_at=t.completed_at,
        )
        for t in tasks
    ]

