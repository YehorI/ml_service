from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TransactionTypeDTO(Enum):
    DEPOSIT = "deposit"
    DEBIT = "debit"


@dataclass
class TransactionCreateDTO:
    user_id: int
    wallet_id: int
    amount: float
    transaction_type: TransactionTypeDTO
    ml_task_id: int | None = None


@dataclass
class TransactionReadDTO:
    id: int
    user_id: int
    wallet_id: int
    amount: float
    transaction_type: TransactionTypeDTO
    ml_task_id: int | None
    created_at: datetime
    is_applied: bool
