"""Typer sub-app for the translate stage. Mounted by formulaci/cli.py as `formulaci translate`."""
from __future__ import annotations

import json

import typer

app = typer.Typer(help="translate stage: Wikipedia LaTeX -> SymPy (srepr)", no_args_is_help=True)


@app.command()
def run(
    in_path: str = typer.Option("data/raw/formulas.jsonl", "--in", help="Formula JSONL from the extract stage"),
    out_path: str = typer.Option("data/parsed/parsed.jsonl", "--out", help="Parsed JSONL to append to"),
    limit: int = typer.Option(None, "--limit", help="Translate at most N new formulas"),
    force: bool = typer.Option(False, "--force", help="Discard existing output and redo everything"),
    workers: int = typer.Option(4, "--workers", help="Worker processes (0 = in-process, soft timeout only)"),
    timeout: float = typer.Option(20.0, "--timeout", help="Hard per-formula timeout in seconds"),
    lark: bool = typer.Option(False, "--lark/--no-lark",
                              help="Fall back to sympy's lark parser on parse errors (off: see README)"),
):
    """Translate formulas; resumable (skips formula ids already in --out)."""
    from .runner import run as run_stage
    from .stats import format_summary

    try:
        s = run_stage(in_path, out_path, limit=limit, force=force, workers=workers, timeout=timeout,
                      use_lark=lark, progress=True)
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"translated {s['new_formulas']} new formulas in {s['seconds']}s -> {out_path}")
    typer.echo(format_summary(s))


@app.command()
def one(latex: str, context: str = typer.Option("", help="Prose before the formula (for definition detection)"),
        lark: bool = typer.Option(False, "--lark/--no-lark")):
    """Translate a single LaTeX string and print the Parsed records (debugging aid)."""
    import sympy as sp

    from formulaci.schemas import Formula

    from .core import translate

    f = Formula(formula_id="cli:0", page_title="", page_id=0, revision_id=0, url="", index=0, latex=latex,
                context_before=context)
    for r in translate(f, use_lark=lark):
        d = r.model_dump()
        for k in ("lhs", "rhs"):
            if d[k]:
                d[k + "_str"] = str(sp.sympify(d[k]))
        typer.echo(json.dumps(d, indent=1))


@app.command()
def stats(path: str = typer.Argument("data/parsed/parsed.jsonl")):
    """Coverage summary of an existing parsed.jsonl."""
    from formulaci.schemas import Parsed, read_jsonl

    from .stats import format_summary, summarize

    typer.echo(format_summary(summarize(list(read_jsonl(path, Parsed)))))
