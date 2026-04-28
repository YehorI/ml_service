import typer
import uvicorn

from ml_service_users.settings import Settings


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service-users", help="ML Service Users CLI")

    @cli.command("api")
    def api(
        host: str = typer.Option(None),
        port: int = typer.Option(None),
    ) -> None:
        settings = Settings()
        uvicorn.run(
            "ml_service_users.asgi:app",
            host=host or settings.api.host,
            port=port or settings.api.port,
        )

    return cli
