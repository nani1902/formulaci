"""Stage driver: timeouts, resumability, CLI, and the end-to-end run on real Wikipedia fixtures."""
import json
from pathlib import Path

import sympy as sp
from typer.testing import CliRunner

from formulaci.schemas import Formula, Parsed, read_jsonl
from formulaci.translate import run
from formulaci.translate.cli import app
from formulaci.translate.runner import _Worker, translate_many

from .conftest import make_formula

FIXTURES = Path(__file__).parent / "fixtures" / "formulas.jsonl"


def test_fixture_has_enough_real_formulas():
    fs = list(read_jsonl(FIXTURES, Formula))
    assert len(fs) >= 200
    assert len({f.page_title for f in fs}) >= 8


def test_hard_timeout_kills_worker_and_records_error():
    import multiprocessing as mp

    w = _Worker(mp.get_context("spawn"), use_lark=False, soft_timeout=30)
    try:
        # first call must import sympy in the fresh worker: a 1 ms budget cannot be met
        recs = w.run(make_formula(r"x = 1", fid="slow:0"), hard_timeout=0.001)
        assert len(recs) == 1 and recs[0].status == "unparsed" and "timeout" in recs[0].error
        # the worker was restarted and still works
        recs = w.run(make_formula(r"x = 1", fid="ok:0"), hard_timeout=60)
        assert recs[0].status == "ok"
    finally:
        w.close()


def test_translate_many_in_process_and_pool_agree():
    fs = [make_formula(r"\sin^2 x + \cos^2 x = 1", fid=f"p:{i}") for i in range(3)]
    got = {}
    translate_many(fs, workers=0, on_result=lambda f, rs: got.setdefault("seq", []).extend(rs))
    translate_many(fs, workers=2, timeout=60, on_result=lambda f, rs: got.setdefault("pool", []).extend(rs))
    key = lambda r: r.formula_id  # noqa: E731
    assert [r.model_dump() for r in sorted(got["seq"], key=key)] == [r.model_dump() for r in sorted(got["pool"], key=key)]


def test_run_is_resumable_and_force_restarts(tmp_path):
    inp = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    lines = FIXTURES.read_text().splitlines()[:30]
    inp.write_text("\n".join(lines) + "\n")
    s1 = run(inp, out, limit=10, workers=0)
    assert s1["new_formulas"] == 10 and s1["formulas"] == 10
    s2 = run(inp, out, workers=0)
    assert s2["new_formulas"] == 20 and s2["formulas"] == 30
    s3 = run(inp, out, workers=0)
    assert s3["new_formulas"] == 0
    s4 = run(inp, out, force=True, limit=5, workers=0)
    assert s4["formulas"] == 5
    assert (tmp_path / "out.jsonl.summary.json").exists()


def test_cli_run_and_one(tmp_path):
    inp = tmp_path / "in.jsonl"
    out = tmp_path / "parsed.jsonl"
    inp.write_text("\n".join(FIXTURES.read_text().splitlines()[:8]) + "\n")
    runner = CliRunner()
    res = runner.invoke(app, ["run", "--in", str(inp), "--out", str(out), "--limit", "5", "--workers", "0"])
    assert res.exit_code == 0, res.output
    assert "equation-kind" in res.output
    assert len({r.formula_id for r in read_jsonl(out, Parsed)}) == 5
    res = runner.invoke(app, ["one", r"\Gamma(z+1) = z\Gamma(z)"])
    assert res.exit_code == 0 and '"status": "ok"' in res.output
    res = runner.invoke(app, ["run", "--in", str(tmp_path / "missing.jsonl"), "--out", str(out)])
    assert res.exit_code == 1


def test_end_to_end_on_wikipedia_fixtures(tmp_path):
    out = tmp_path / "parsed.jsonl"
    s = run(FIXTURES, out, workers=2, timeout=60)
    recs = list(read_jsonl(out, Parsed))
    fs = list(read_jsonl(FIXTURES, Formula))
    # every formula produced at least one record, none crashed the stage
    assert {r.formula_id for r in recs} == {f.formula_id for f in fs}
    assert not any(r.error and r.error.startswith(("internal", "timeout", "worker")) for r in recs)
    # every ok side round-trips through sympify(srepr)
    for r in recs:
        if r.status == "ok":
            for side in (r.lhs, r.rhs):
                assert sp.srepr(sp.sympify(side)) == side
            assert r.kind != "other"
    # coverage floor (measured 85.8% of equation-kind formulas when written; see README)
    rate = s["equation_formulas_any_ok"] / s["equation_formulas"]
    assert rate >= 0.80, json.dumps(s, indent=1)
    assert s["status"].get("unparsed", 0) / s["records"] < 0.02
