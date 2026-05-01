from datetime import datetime
from enum import Enum as PyEnum

from database_repository.models.base import Base
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TaskStatusORM(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MLTaskORM(Base):
    __tablename__ = "ml_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("ml_models.id"), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[TaskStatusORM] = mapped_column(
        Enum(TaskStatusORM), nullable=False, default=TaskStatusORM.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="tasks")  # noqa: F821
    model: Mapped["MLModelORM"] = relationship("MLModelORM", back_populates="tasks")  # noqa: F821
    result: Mapped["PredictionResultORM"] = relationship("PredictionResultORM", back_populates="task", uselist=False)  # noqa: F821
    transactions: Mapped[list["TransactionORM"]] = relationship("TransactionORM", back_populates="ml_task")  # noqa: F821


class PredictionResultORM(Base):
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("ml_tasks.id"), unique=True, nullable=False
    )
    output_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    credits_charged: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    task: Mapped["MLTaskORM"] = relationship("MLTaskORM", back_populates="result")  # noqa: F821
