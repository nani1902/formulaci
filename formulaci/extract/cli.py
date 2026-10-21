"""Typer sub-app for the extract stage. Mounted by formulaci/cli.py."""
import json
from typing import Optional

import typer

app = typer.Typer(help="extract stage: English Wikipedia <math> formulas -> data/raw/formulas.jsonl")


@app.command()
def pages(out: str = typer.Option("data/raw/pages.txt", help="page_id<TAB>title, sorted by views"),
          limit: Optional[int] = typer.Option(None, help="keep only the N most-viewed pages"),
          views: bool = typer.Option(True, help="--no-views: order by assessment class, skip pageviews"),
          views_upto: Optional[str] = typer.Option(None, help="fetch views only for classes up to this one "
                                                   "(FA FL A GA B List C Start Stub); others follow by class")):
    """Build the page list from WikiProject Mathematics/Physics/Statistics/Engineering assessments."""
    from .pages import build_pages

    n = build_pages(out, limit=limit, views=views, views_upto=views_upto)
    typer.echo(f"{n} pages -> {out}")


@app.command()
def run(pages: str = typer.Option("data/raw/pages.txt", "--pages", help="page list from `pages`"),
        out: str = typer.Option("data/raw/formulas.jsonl", help="output JSONL of Formula records"),
        limit: Optional[int] = typer.Option(None, help="process only the first N pages of the list"),
        force: bool = typer.Option(False, help="discard existing output and redo every page"),
        offline: bool = typer.Option(False, help="use only cached wikitext, no network"),
        workers: Optional[int] = typer.Option(None, help="parser processes (default min(4, CPUs))")):
    """Fetch wikitext (cached) and extract formulas. Resumable: done pages are skipped."""
    from .pipeline import run as run_extract, summarize

    totals = run_extract(pages, out, limit=limit, force=force, offline=offline, workers=workers)
    typer.echo(f"this run: {json.dumps(totals)}")
    typer.echo(f"cumulative: {json.dumps(summarize(out))}")


@app.command()
def stats(out: str = typer.Option("data/raw/formulas.jsonl")):
    """Print cumulative counts from the per-page log next to the output."""
    from .pipeline import summarize

    typer.echo(json.dumps(summarize(out), indent=2))
