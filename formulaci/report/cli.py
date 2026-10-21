"""Typer sub-app for the report stage. Owned by the coordinator."""
import typer

from formulaci.report.report import run as _run

app = typer.Typer(help="report stage: join stage outputs into findings + HTML")


@app.command()
def run(data_dir: str = "data", out_dir: str = "", include_inconclusive: bool = False):
    """Build data/findings/findings.jsonl and report.html from all stage outputs."""
    res = _run(data_dir, out_dir or None, include_inconclusive)
    typer.echo(res)
