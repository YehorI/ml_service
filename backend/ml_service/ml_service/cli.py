import typer
import uvicorn

from database.cli import get_cli as database_get_cli


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service", help="ML Service CLI")

    cli.add_typer(database_get_cli(), name="database")

    @cli.command("api")
    def api(
        host: str = typer.Option("127.0.0.1",),
        port: int = typer.Option(8000,),
    ) -> None:
        uvicorn.run(
            "ml_service.asgi:app",
            host=host,
            port=port,
        )

    return cli
