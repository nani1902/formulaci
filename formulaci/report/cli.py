"""Typer sub-app for the report stage. Owned by the coordinator."""
import typer

from formulaci.report.report import run as _run

app = typer.Typer(help="report stage: join stage outputs into findings + HTML")


@app.command()
def run(data_dir: str = "data", out_dir: str = "", include_inconclusive: bool = False):
    """Build data/findings/findings.jsonl and report.html from all stage outputs."""
    res = _run(data_dir, out_dir or None, include_inconclusive)
    typer.echo(res)


@app.command("export-review")
def export_review(data_dir: str = "data", out_dir: str = "", batch_size: int = 25, limit: int = 0,
                  include_inconclusive: bool = False):
    """Write Markdown review batches for FAIL verdicts (skips already-reviewed ids)."""
    from formulaci.report.review import export
    typer.echo(export(data_dir, out_dir or None, batch_size, limit, include_inconclusive))


@app.command("import-reviews")
def import_reviews_cmd(in_path: str, data_dir: str = "data", reviewer: str = ""):
    """Append reviewer Finding JSONL to data/findings/reviews.jsonl."""
    from formulaci.report.review import import_reviews
    typer.echo(import_reviews(data_dir, in_path, reviewer))
