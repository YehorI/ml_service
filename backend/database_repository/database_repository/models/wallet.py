from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WalletORM(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
