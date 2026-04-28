import asyncio

import ml_service_users
import typer

from database.cli import get_cli as database_get_cli

from .messaging.worker import run_worker
from .service import get_service


def callback(ctx: typer.Context) -> None:
    ctx.obj = ctx.obj or {}

    if "loop" not in ctx.obj:
        ctx.obj["loop"] = asyncio.get_event_loop()


def run(ctx: typer.Context) -> None:
    loop: asyncio.AbstractEventLoop = ctx.obj["loop"]

    service = get_service()
    loop.run_until_complete(service.run())


def worker() -> None:
    """Run a RabbitMQ consumer that processes prediction tasks."""
    asyncio.run(run_worker())


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service", help="ML Service CLI")

    cli.callback()(callback)
    cli.command(name="run")(run)
    cli.command(name="worker")(worker)
    cli.add_typer(database_get_cli(), name="database")
    cli.add_typer(ml_service_users.get_cli(), name="users")

    return cli
