from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class TransactionTypeORM(PyEnum):
    DEPOSIT = "deposit"
    DEBIT = "debit"


class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_type: Mapped[TransactionTypeORM] = mapped_column(
        Enum(TransactionTypeORM), nullable=False
    )
    ml_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("ml_tasks.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    is_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
