"""Stage: bench. See SPEC.md and formulaci/bench/README.md."""


def run(in_path="data/bench", out_path="data/bench", force=False, **opts):
    """Build the sets if missing (or ``force``), then measure the pipeline; returns metrics."""
    from pathlib import Path

    from .build import build
    from .measure import measure

    if force or not (Path(in_path) / "known_good.jsonl").exists():
        build(in_path)
    if Path(out_path) != Path(in_path):
        import shutil

        Path(out_path).mkdir(parents=True, exist_ok=True)
        for name in ("known_good.jsonl", "mutated.jsonl", "lacast_benchmark.jsonl"):
            shutil.copy(Path(in_path) / name, Path(out_path) / name)
    return measure(out_path, **opts)
