from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE modeltypeorm AS ENUM ('huggingface', 'openai')")
    op.add_column(
        "ml_models",
        sa.Column(
            "model_type",
            sa.Enum("huggingface", "openai", name="modeltypeorm"),
            nullable=False,
            server_default="huggingface",
        ),
    )
    op.add_column(
        "ml_models",
        sa.Column("provider_config", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("ml_models", "provider_config")
    op.drop_column("ml_models", "model_type")
    op.execute("DROP TYPE IF EXISTS modeltypeorm")
