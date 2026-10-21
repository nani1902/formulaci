"""Stage: extract. See SPEC.md and formulaci/extract/README.md."""


def run(in_path="data/raw/pages.txt", out_path="data/raw/formulas.jsonl", **opts):
    from .pipeline import run as _run

    return _run(in_path, out_path, **opts)
