import typer

from database.cli import get_cli as database_get_cli


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service", help="ML Service CLI")

    cli.add_typer(database_get_cli(), name="database")

    return cli
