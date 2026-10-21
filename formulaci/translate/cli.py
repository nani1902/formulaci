"""Typer sub-app for the translate stage. Mounted by formulaci/cli.py."""
import typer

app = typer.Typer(help="translate stage")


@app.command()
def run(in_path: str = "", out_path: str = "", force: bool = False):
    """Run the translate stage. Owner session: replace this stub."""
    raise typer.Exit("not implemented yet")
