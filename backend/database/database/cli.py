import os

import typer
from alembic import command
from alembic.config import Config


def get_alembic_cfg() -> Config:
    alembic_ini = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    cfg = Config(os.path.abspath(alembic_ini))
    return cfg


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    @cli.command()
    def migrate() -> None:
        """Apply all pending migrations (upgrade to head)."""
        command.upgrade(get_alembic_cfg(), "head")

    @cli.command()
    def downgrade(revision: str = "-1") -> None:
        """Downgrade by one revision (or to a specific revision)."""
        command.downgrade(get_alembic_cfg(), revision)

    @cli.command()
    def revision(message: str, autogenerate: bool = True) -> None:
        """Create a new migration revision."""
        command.revision(get_alembic_cfg(), message=message, autogenerate=autogenerate)

    @cli.command()
    def current() -> None:
        """Show the current migration revision."""
        command.current(get_alembic_cfg())

    return cli
