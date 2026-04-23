import asyncio
import os
import pathlib

import typer
from alembic import command
from alembic.config import Config
from ml_service_common.sqlalchemy.service import Service as SQLAlchemyService

from database.fixtures import apply_fixtures, json_fixture_loader, yaml_fixture_loader


def get_alembic_cfg() -> Config:
    alembic_ini = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    )
    cfg = Config(alembic_ini)
    migrations_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "migrations")
    )
    cfg.set_main_option("script_location", migrations_dir)
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

    @cli.command("loadfixtures")
    def loadfixtures(path: str) -> None:
        
        fixture_path = pathlib.Path(path)
        if not fixture_path.is_file():
            raise typer.BadParameter(f"Fixture file not found: {fixture_path}")

        suffix = fixture_path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            loader = yaml_fixture_loader
        elif suffix == ".json":
            loader = json_fixture_loader
        else:
            raise typer.BadParameter(
                f"Unsupported fixture extension {suffix!r}; use .yaml/.yml/.json"
            )

        async def _run() -> int:
            service = SQLAlchemyService()
            return await apply_fixtures(service, loader(fixture_path))

        inserted = asyncio.run(_run())
        typer.echo(f"Loaded {inserted} fixture item(s) from {fixture_path}")

    return cli
