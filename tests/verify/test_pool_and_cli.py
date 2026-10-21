import json
import time

import pytest
import sympy as sp
from typer.testing import CliRunner

from formulaci.schemas import Verdict, read_jsonl
from formulaci.verify.cli import app
from formulaci.verify.pool import TaskTimeout, Worker
from formulaci.verify.run import run

from .conftest import load, split_inputs


def test_worker_is_killed_on_timeout_and_respawned():
    w = Worker()
    try:
        w.warm()
        t0 = time.monotonic()
        with pytest.raises(TaskTimeout):
            w.call("sleep", {"seconds": 60}, timeout=1.0)
        assert time.monotonic() - t0 < 10
        assert w.call("sleep", {"seconds": 0}, timeout=10) == {"slept": 0}
        assert w.restarts == 1
    finally:
        w.close()


def test_hanging_formula_does_not_hang_the_batch(tmp_path):
    # sympy evaluates factorial(10**7) eagerly while rebuilding the srepr: it would run for minutes
    rows = [{
        "parsed": {"formula_id": "hang", "status": "ok", "kind": "equation",
                   "lhs": sp.srepr(sp.factorial(sp.Integer(10), evaluate=False)).replace("10", "10000000"),
                   "rhs": "Integer(1)"},
        "semantics": {"formula_id": "hang"},
    }, {
        "parsed": {"formula_id": "fine", "status": "ok", "kind": "equation",
                   "lhs": sp.srepr(sp.sin(sp.Symbol("x"))**2 + sp.cos(sp.Symbol("x"))**2), "rhs": "Integer(1)"},
        "semantics": {"formula_id": "fine"},
    }]
    parsed, sem = split_inputs(rows, tmp_path)
    out = tmp_path / "v.jsonl"
    t0 = time.monotonic()
    run(str(parsed), str(out), semantics_path=str(sem), workers=2, cap=3.0, progress=False)
    assert time.monotonic() - t0 < 30
    v = {r.formula_id: r for r in read_jsonl(out, Verdict)}
    assert v["hang"].verdict == "INCONCLUSIVE"
    assert v["fine"].verdict == "PASS"


@pytest.mark.timeout(600)
def test_cli_end_to_end_on_wikipedia_sample(tmp_path):
    rows = load("wiki_sample.jsonl")
    parsed, sem = split_inputs(rows, tmp_path)
    out = tmp_path / "verdicts" / "verdicts.jsonl"
    runner = CliRunner()
    args = ["run", "--parsed", str(parsed), "--semantics", str(sem), "--out", str(out), "--quiet", "--workers", "4"]
    res = runner.invoke(app, args)
    assert res.exit_code == 0, res.output
    verdicts = {v.formula_id: v for v in read_jsonl(out, Verdict)}
    assert set(verdicts) == {r["formula_id"] for r in rows}
    assert list(verdicts) == [r["formula_id"] for r in rows]  # rewritten in input order
    for r in rows:
        got = verdicts[r["formula_id"]].verdict
        # true Wikipedia formulas: never FAIL; slow ones (infinite products, peaked integrals) may
        # run out of time and come back INCONCLUSIVE
        allowed = {r["expected"], "INCONCLUSIVE"} if r["expected"] == "PASS" else {r["expected"]}
        assert got in allowed, (r["formula_id"], got, verdicts[r["formula_id"]].reason)
    assert sum(v.verdict == "PASS" for v in verdicts.values()) >= 9
    chain = verdicts["wiki:en:4668:1376065730:4"]
    assert chain.verdict == "PASS" and "3 links" in chain.reason

    # resumable: a second run does nothing; --limit and --force behave
    res = runner.invoke(app, args)
    assert json.loads(res.output.strip().splitlines()[-1])["processed"] == 0
    res = runner.invoke(app, args + ["--force", "--limit", "2"])
    assert json.loads(res.output.strip().splitlines()[-1])["processed"] == 2
    assert len(list(read_jsonl(out, Verdict))) == 2

    # `one` prints every regime and point
    res = runner.invoke(app, ["one", "wiki:en:4668:1376065730:6", "--parsed", str(parsed), "--semantics", str(sem)])
    assert res.exit_code == 0, res.output
    assert "regime small_positive" in res.output and "VERDICT PASS" in res.output
    assert res.output.count("pass ") >= 20


def test_missing_semantics_is_skip(tmp_path):
    rows = load("wiki_sample.jsonl")[:1]
    parsed, sem = split_inputs(rows, tmp_path)
    sem.write_text("")
    out = tmp_path / "v.jsonl"
    run(str(parsed), str(out), semantics_path=str(sem), workers=1, progress=False)
    (v,) = read_jsonl(out, Verdict)
    assert v.verdict == "SKIP" and "semantics" in v.reason
