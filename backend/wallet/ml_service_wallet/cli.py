import typer
import uvicorn

from ml_service_wallet.settings import Settings


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service-wallet", help="ML Service Wallet CLI")

    @cli.command("api")
    def api(
        host: str = typer.Option(None),
        port: int = typer.Option(None),
    ) -> None:
        settings = Settings()
        uvicorn.run(
            "ml_service_wallet.asgi:app",
            host=host or settings.api.host,
            port=port or settings.api.port,
        )

    return cli
