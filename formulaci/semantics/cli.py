"""Typer sub-app for the semantics stage. Mounted by formulaci/cli.py."""
import json
from typing import Optional

import typer

from formulaci.semantics import stage

app = typer.Typer(help="semantics stage: domains, constants, constraints, checkability (rules-based)")


@app.command()
def run(
    formulas: str = typer.Option(stage.DEFAULT_FORMULAS, help="Formula JSONL from the extract stage"),
    parsed: str = typer.Option(stage.DEFAULT_PARSED, help="Parsed JSONL from the translate stage"),
    out: str = typer.Option(stage.DEFAULT_OUT, help="Semantics JSONL to write"),
    limit: Optional[int] = typer.Option(None, help="Process at most N new formulas"),
    force: bool = typer.Option(False, help="Recompute everything (truncates --out)"),
    timeout: float = typer.Option(10.0, help="Per-formula time limit in seconds"),
):
    """Infer semantics for every parsed formula (resumable)."""
    stats = stage.run(parsed, out, formulas_path=formulas, limit=limit, force=force, timeout=timeout)
    typer.echo(json.dumps(stats, indent=2))


@app.command()
def explain(
    formula_id: str,
    formulas: str = typer.Option(stage.DEFAULT_FORMULAS),
    parsed: str = typer.Option(stage.DEFAULT_PARSED),
):
    """Print which rules fired for FORMULA_ID and why."""
    typer.echo(stage.explain(formula_id, formulas, parsed))


@app.command()
def score(
    fixtures: str = typer.Option("tests/semantics/fixtures/cases.jsonl", help="Hand-labeled cases"),
    verbose: bool = typer.Option(False, help="List every mismatch"),
):
    """Measure rule accuracy on the hand-labeled fixtures."""
    from formulaci.semantics.accuracy import format_report, score_file

    rep = score_file(fixtures)
    typer.echo(format_report(rep, verbose=verbose))
