import asyncio

import typer
import uvicorn

from database.cli import get_cli as database_get_cli
from ml_service.messaging.worker import run_worker


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

    @cli.command("worker")
    def worker() -> None:
        """Run a RabbitMQ consumer that processes prediction tasks."""
        asyncio.run(run_worker())

    return cli
