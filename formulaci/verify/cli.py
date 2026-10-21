"""Typer sub-app for the verify stage. Mounted by formulaci/cli.py."""
from __future__ import annotations

import json
from typing import Optional

import typer

app = typer.Typer(help="verify stage: PASS / FAIL / INCONCLUSIVE / SKIP for each checkable formula")


@app.command()
def run(
    parsed: str = typer.Option("data/parsed/parsed.jsonl", "--parsed", "--in-path", help="Parsed JSONL"),
    semantics: str = typer.Option("data/semantics/semantics.jsonl", "--semantics", help="Semantics JSONL"),
    out: str = typer.Option("data/verdicts/verdicts.jsonl", "--out", "--out-path", help="Verdict JSONL"),
    limit: Optional[int] = typer.Option(None, "--limit", help="verify at most N new formulas"),
    force: bool = typer.Option(False, "--force", help="discard existing verdicts and redo everything"),
    workers: Optional[int] = typer.Option(None, "--workers", help="parallel worker processes (default min(4, cpus))"),
    cap: float = typer.Option(20.0, "--cap", help="wall-clock seconds per formula"),
    quiet: bool = typer.Option(False, "--quiet", help="no progress bar"),
):
    """Verify every formula in --parsed joined with --semantics; append Verdicts to --out (resumable)."""
    from formulaci.verify.run import run as run_stage

    stats = run_stage(parsed, out, semantics_path=semantics, limit=limit, force=force, workers=workers,
                      cap=cap, progress=not quiet)
    typer.echo(json.dumps(stats))


@app.command()
def one(
    formula_id: str = typer.Argument(..., help="formula_id to verify"),
    parsed: str = typer.Option("data/parsed/parsed.jsonl", "--parsed"),
    semantics: str = typer.Option("data/semantics/semantics.jsonl", "--semantics"),
    cap: float = typer.Option(20.0, "--cap"),
    as_json: bool = typer.Option(False, "--json", help="print the Verdict JSON only"),
):
    """Verify one formula and print every regime and sample point (debugging)."""
    from formulaci.verify.pool import Worker
    from formulaci.verify.run import load_inputs, verify_formula

    groups, sems = load_inputs(parsed, semantics)
    if formula_id not in groups:
        raise typer.BadParameter(f"{formula_id} not in {parsed}")
    w = Worker()
    try:
        w.warm()
        verdict, details = verify_formula(w, groups[formula_id], sems.get(formula_id), cap)
    finally:
        w.close()
    if as_json:
        typer.echo(verdict.model_dump_json(indent=2))
        return
    for d in details:
        meta = d.get("meta") or {}
        typer.echo(f"== link {d['index']}: {meta.get('lhs', '?')}  {meta.get('relation', '=')}  {meta.get('rhs', '?')}")
        if meta:
            typer.echo(f"   symbols: {meta['symbols']}  branch-cut functions: {meta['branch']}")
            for note in meta["notes"] + [f"constraint ignored: {c}" for c in meta["constraint_errors"]]:
                typer.echo(f"   note: {note}")
        typer.echo(f"   symbolic: {d.get('symbolic')}  steps: {' > '.join(d.get('trace', []))}")
        for note in d.get("notes", []):
            typer.echo(f"   note: {note}")
        num = d.get("numeric") or {}
        if num.get("eval_error"):
            typer.echo(f"   numeric error: {num['eval_error']}")
        for r in num.get("regimes", []):
            typer.echo(f"   -- regime {r['name']}: points={r['n_points']} fail={r['n_fail']} error={r['n_error']}")
            for pt in r["points"]:
                where = ", ".join(f"{k}={v}" for k, v in pt["point"].items())
                if pt["status"] == "error":
                    typer.echo(f"      error  {where}: {pt['error']}")
                else:
                    rel = f"{pt['rel']:.2e}" if pt["rel"] is not None else "?"
                    typer.echo(f"      {pt['status']:<6} {where}: lhs={pt['lhs'][:24]} rhs={pt['rhs'][:24]} rel={rel}")
        typer.echo(f"   link verdict: {d['verdict']} — {d['reason']}")
    typer.echo(f"\nVERDICT {verdict.verdict}: {verdict.reason}")
    if verdict.counterexample:
        typer.echo(verdict.counterexample.model_dump_json(indent=2))
