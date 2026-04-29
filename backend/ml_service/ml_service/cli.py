import asyncio

import ml_service_model
import ml_service_users
import ml_service_wallet
import typer

from database.cli import get_cli as database_get_cli

from .service import get_service
from .settings import Settings


def callback(ctx: typer.Context) -> None:
    ctx.obj = ctx.obj or {}

    if "loop" not in ctx.obj:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ctx.obj["loop"] = loop

    if "settings" not in ctx.obj:
        ctx.obj["settings"] = Settings.load(env_prefix="ML_SERVICE__")


def run(ctx: typer.Context) -> None:
    loop: asyncio.AbstractEventLoop = ctx.obj["loop"]
    settings: Settings = ctx.obj["settings"]

    service = get_service(settings=settings)
    loop.run_until_complete(service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service", help="ML Service CLI")

    cli.callback()(callback)
    cli.command(name="run")(run)
    cli.add_typer(database_get_cli(), name="database")
    cli.add_typer(ml_service_users.get_cli(), name="users")
    cli.add_typer(ml_service_wallet.get_cli(), name="wallet")
    cli.add_typer(ml_service_model.get_cli(), name="model")

    return cli
