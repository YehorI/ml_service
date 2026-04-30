from datetime import datetime

from ml_service_wallet.domains.transaction import Transaction, TransactionType
from pydantic import BaseModel, Field


class WalletBalanceResponse(BaseModel):
    user_id: int
    amount: float


class DepositRequest(BaseModel):
    amount: float = Field(gt=0)


class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    created_at: datetime
    is_applied: bool
    ml_task_id: int | None = None

    @classmethod
    def from_domain(cls, tx: Transaction) -> "TransactionResponse":
        return cls(
            id=tx.transaction_id,
            type=tx.transaction_type.value,
            amount=tx.amount,
            created_at=tx.created_at,
            is_applied=tx.is_applied,
            ml_task_id=getattr(tx, "ml_task_id", None),
        )
