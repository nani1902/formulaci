"""Root CLI. Owned by the coordinator."""
import typer

app = typer.Typer(help="formulaci — a test suite for human knowledge")

for _name in ["extract", "translate", "semantics", "verify", "clinical", "bench", "report"]:
    try:
        _mod = __import__(f"formulaci.{_name}.cli", fromlist=["app"])
        app.add_typer(_mod.app, name=_name)
    except Exception as e:  # a stage that is mid-development must not break the others
        typer.echo(f"[cli] stage {_name} not mounted: {e}", err=True)


if __name__ == "__main__":
    app()
