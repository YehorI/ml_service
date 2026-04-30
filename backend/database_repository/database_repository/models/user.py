from datetime import datetime
from enum import Enum as PyEnum

from database_repository.models.base import Base
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserRoleORM(PyEnum):
    USER = "user"
    ADMIN = "admin"


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleORM] = mapped_column(
        Enum(UserRoleORM), nullable=False, default=UserRoleORM.USER
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    wallet: Mapped["WalletORM"] = relationship("WalletORM", back_populates="user", uselist=False)  # noqa: F821
    tasks: Mapped[list["MLTaskORM"]] = relationship("MLTaskORM", back_populates="user")  # noqa: F821
    transactions: Mapped[list["TransactionORM"]] = relationship("TransactionORM", back_populates="user")  # noqa: F821
