import asyncio

import typer
from loguru import logger

from .service import get_service
from .settings import Settings


@logger.catch
def run(ctx: typer.Context):
    loop: asyncio.AbstractEventLoop = ctx.obj["loop"]
    settings: Settings = ctx.obj["settings"]

    service = get_service(settings=settings)
    loop.run_until_complete(service.run())


def callback(ctx: typer.Context):
    ctx.obj = ctx.obj or {}

    if "loop" not in ctx.obj:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ctx.obj["loop"] = loop
    if settings := ctx.obj.get("settings"):
        ctx.obj["settings"] = settings.wallet
    else:
        ctx.obj["settings"] = Settings.load(env_prefix="WALLET__")


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.callback()(callback)
    cli.command(name="run")(run)

    return cli
