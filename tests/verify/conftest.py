import json
import os
from collections import Counter
from pathlib import Path

import pytest

from formulaci.schemas import Verdict, read_jsonl
from formulaci.verify.run import run

FIXTURES = Path(__file__).parent / "fixtures"
WORKERS = int(os.environ.get("FORMULACI_VERIFY_TEST_WORKERS", min(4, os.cpu_count() or 2)))


def load(name):
    return [json.loads(line) for line in (FIXTURES / name).open() if line.strip()]


def split_inputs(rows, tmp: Path):
    parsed, sem = tmp / "parsed.jsonl", tmp / "semantics.jsonl"
    with parsed.open("w") as fp, sem.open("w") as fs:
        for r in rows:
            for p in (r["parsed"] if isinstance(r["parsed"], list) else [r["parsed"]]):
                fp.write(json.dumps(p) + "\n")
            fs.write(json.dumps(r["semantics"]) + "\n")
    return parsed, sem


@pytest.fixture(scope="session")
def corpus_results(tmp_path_factory):
    """Run the whole fixture corpus once per test session."""
    rows = load("corpus.jsonl")
    tmp = tmp_path_factory.mktemp("corpus")
    parsed, sem = split_inputs(rows, tmp)
    out = tmp / "verdicts.jsonl"
    run(str(parsed), str(out), semantics_path=str(sem), workers=WORKERS, progress=False)
    verdicts = {v.formula_id: v for v in read_jsonl(out, Verdict)}
    table = Counter((r["category"], r["expected"], verdicts[r["parsed"]["formula_id"]].verdict) for r in rows)
    return rows, verdicts, table
