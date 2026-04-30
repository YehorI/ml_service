from database_repository.models.base import Base
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WalletORM(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="wallet")  # noqa: F821
    transactions: Mapped[list["TransactionORM"]] = relationship("TransactionORM", back_populates="wallet")  # noqa: F821
