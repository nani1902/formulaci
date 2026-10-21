"""Typer sub-app for the clinical stage. Mounted by formulaci/cli.py."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="clinical track: reference formulas, vectors, calculator audit")

MOCK_TARGETS = Path(__file__).parent / "mock" / "targets.yaml"
DEFAULT_OUT = "data/clinical/audit.jsonl"


@app.command()
def vectors(regenerate: bool = typer.Option(False, help="rewrite vectors.json from vectorgen.py"),
            rel: float = 1e-9):
    """Self-check: every reference vector is reproduced by formulas.py."""
    from . import formulas as F, vectorgen

    if regenerate:
        typer.echo(f"wrote {vectorgen.write()} vectors to {vectorgen.VECTORS_PATH}")
    vecs = json.loads(vectorgen.VECTORS_PATH.read_text())["vectors"]
    bad = 0
    for v in vecs:
        got = F.evaluate(v["formula"], v["inputs"], v["units"])
        if abs(got - v["expected"]) > rel * max(1.0, abs(v["expected"])):
            bad += 1
            typer.echo(f"FAIL {v['formula']} {v['inputs']} {v['units']}: "
                       f"got {got!r}, expected {v['expected']!r}")
    covered = {v["formula"] for v in vecs}
    missing = sorted(set(F.REGISTRY) - covered)
    typer.echo(f"{len(vecs) - bad}/{len(vecs)} vectors OK across {len(covered)} formulas"
               + (f"; no vectors for: {', '.join(missing)}" if missing else ""))
    if bad:
        raise typer.Exit(1)


@app.command("mock-serve")
def mock_serve(port: int = 8765):
    """Serve the mock calculator pages on http://127.0.0.1:PORT (Ctrl-C to stop)."""
    from .mock.server import make_server

    srv = make_server(port)
    typer.echo(f"mock calculators on http://127.0.0.1:{srv.server_port}/ (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


@app.command()
def audit(targets: Path = typer.Option(MOCK_TARGETS, help="targets YAML"),
          base_url: Optional[str] = typer.Option(None, help="base for relative target URLs"),
          out: Path = typer.Option(Path(DEFAULT_OUT)),
          mock: bool = typer.Option(False, help="start the mock server in-process and use it"),
          only: Optional[list[str]] = typer.Option(None, help="target id(s) to run"),
          max_cases: int = 3, force: bool = False, headed: bool = False,
          allow_live: bool = typer.Option(
              False, "--allow-live",
              help="permit non-local hosts. Requires the user's explicit go-ahead.")):
    """Drive calculator pages with reference inputs and write match/mismatch/unreadable records."""
    from . import audit as A

    srv = None
    if mock:
        from .mock.server import serve_in_thread
        srv, base_url = serve_in_thread()
    try:
        recs = A.run(targets, out, base_url=base_url, allow_live=allow_live, force=force,
                     max_cases=max_cases, only=only, headless=not headed)
    except A.LiveSiteRefused as e:
        typer.echo(f"refused: {e}", err=True)
        raise typer.Exit(2)
    finally:
        if srv:
            srv.shutdown()
    for tid, counts in A.summarize(recs).items():
        diag = sorted({d for r in recs if r.target == tid for d in r.diagnosis})
        typer.echo(f"{A.target_status(counts):10s} {tid}  {counts}"
                   + (f"\n           likely: {diag[0]}" if diag else ""))
    typer.echo(f"{len(recs)} new records -> {out}")


@app.command()
def run(in_path: str = str(MOCK_TARGETS), out_path: str = DEFAULT_OUT,
        base_url: Optional[str] = None, force: bool = False):
    """Stage entry point (same as `audit`, without the in-process mock)."""
    from . import audit as A

    recs = A.run(in_path, out_path, base_url=base_url, force=force)
    typer.echo(json.dumps(A.summarize(recs), indent=1))
