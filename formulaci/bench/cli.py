"""Typer sub-app for the bench stage. Mounted by formulaci/cli.py."""
import typer

app = typer.Typer(help="bench stage")


@app.command()
def run(in_path: str = "", out_path: str = "", force: bool = False):
    """Run the bench stage. Owner session: replace this stub."""
    raise typer.Exit("not implemented yet")
