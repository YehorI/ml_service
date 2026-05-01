import enum

from database_repository.models.base import Base
from sqlalchemy import Boolean, Enum, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ModelTypeORM(str, enum.Enum):
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


class MLModelORM(Base):
    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_type: Mapped[ModelTypeORM] = mapped_column(
        Enum(ModelTypeORM, values_callable=lambda x: [e.value for e in x], name="modeltypeorm"),
        nullable=False,
        default=ModelTypeORM.HUGGINGFACE,
    )
    provider_config: Mapped[dict] = mapped_column("model_config", JSON, nullable=False, default=dict)
    cost_per_request: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tasks: Mapped[list["MLTaskORM"]] = relationship("MLTaskORM", back_populates="model")  # noqa: F821
