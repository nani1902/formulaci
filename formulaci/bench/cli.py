"""Typer sub-app for the bench stage. Mounted by formulaci/cli.py."""
import json

import typer

app = typer.Typer(help="bench: labelled sets and precision/recall measurement of the pipeline")


@app.command()
def build(out_dir: str = "data/bench", jobs: int = typer.Option(0, help="worker processes (0 = all cores)"),
          seed: int = 0, snapshot: bool = typer.Option(True, help="also refresh formulaci/bench/sets/")):
    """Build known_good.jsonl, mutated.jsonl and lacast_benchmark.jsonl."""
    from .build import build as _build

    st = _build(out_dir, jobs=jobs or None, seed=seed, snapshot=snapshot)
    kg, mu = st["known_good"], st["mutated"]
    typer.echo(f"known_good: {kg['n']} (rejected by oracle: {len(kg['rejected_by_oracle'])})")
    typer.echo(f"mutated:    {mu['n_kept']} from {mu['n_source']} identities; candidates dropped: "
               f"{sum(mu['dropped_candidates'].values())} (of which identity-preserving: "
               f"{mu['dropped_preserving_identity']})")
    for t, c in mu["per_type"].items():
        typer.echo(f"  {t:16s} kept {c.get('kept', 0):4d}  dropped " + json.dumps({k: v for k, v in c.items() if k != 'kept'}))
    typer.echo(f"lacast:     {st['lacast']['n']}")


@app.command()
def measure(stages: str = typer.Option("translate,semantics,verify", help="comma-separated stages to run"),
            sets: str = typer.Option("synthetic,lacast", help="synthetic and/or lacast"),
            bench_dir: str = "data/bench",
            limit: int = typer.Option(0, help="only the first N identities (+ their mutations); 0 = all")):
    """Run the stages over the bench sets; write metrics.json and REPORT.md."""
    from .measure import measure as _measure

    m = _measure(bench_dir, [s.strip() for s in stages.split(",") if s.strip()],
                 [s.strip() for s in sets.split(",") if s.strip()], limit or None)
    for name, run in m["runs"].items():
        st = {k: v.get("status") for k, v in run.get("stages", {}).items()}
        typer.echo(f"{name}: {run.get('n_formulas', 0)} formulas, stages {st}, {run.get('seconds')}s")
    o = (m.get("synthetic") or {}).get("overall", {})
    if "precision" in o:
        typer.echo(f"precision {o['precision']}  recall {o['recall']}  (TP {o['tp']}, FP {o['fp']})")
    typer.echo(f"wrote {bench_dir}/metrics.json and {bench_dir}/REPORT.md ({m['total_seconds']}s)")


@app.command()
def run(in_path: str = "data/bench", out_path: str = "data/bench", force: bool = False):
    """Uniform stage entry point: measure all stages over the sets in IN_PATH."""
    from . import run as _run

    _run(in_path, out_path, force=force)
