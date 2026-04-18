import typer


def get_cli() -> typer.Typer:
    cli = typer.Typer(name="ml-service", help="ML Service CLI")

    return cli
