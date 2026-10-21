"""Typer sub-app for the clinical stage. Mounted by formulaci/cli.py."""
import typer

app = typer.Typer(help="clinical stage")


@app.command()
def run(in_path: str = "", out_path: str = "", force: bool = False):
    """Run the clinical stage. Owner session: replace this stub."""
    raise typer.Exit("not implemented yet")
