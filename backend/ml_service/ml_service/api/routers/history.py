from fastapi import APIRouter, Depends
from ml_service_model.database.repositories import SqlAlchemyAltMLTaskRepository
from ml_service_users.domains.user import User
from ml_service_wallet.database.repositories import SqlAlchemyAltTransactionRepository
from ml_service_wallet.domains.transaction import DebitTransaction, DepositTransaction, Transaction

from database_repository.service import Service
from ml_service.api.deps import db_transaction, get_current_user
from ml_service.api.schemas import TaskHistoryItem, TransactionItem

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
    repo = SqlAlchemyAltTransactionRepository(service)
    items = await repo.list_by_user(user.user_id)
    return [_tx_to_item(t) for t in items]


@router.get("/tasks", response_model=list[TaskHistoryItem])
async def tasks(
    user: User = Depends(get_current_user),
    service: Service = Depends(db_transaction),
):
    repo = SqlAlchemyAltMLTaskRepository(service)
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

