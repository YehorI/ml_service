from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrolrorm RENAME TO userroleorm")


def downgrade() -> None:
    op.execute("ALTER TYPE userroleorm RENAME TO userrolrorm")
