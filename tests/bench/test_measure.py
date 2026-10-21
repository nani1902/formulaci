"""measure() with stub stages, so these tests never depend on the other sessions' code."""
import json
from pathlib import Path

import pytest

from formulaci.bench import lacast, measure, mutate
from formulaci.bench.sets import read_jsonl, write_jsonl

FIX = Path(__file__).parent / "fixtures" / "known_good_sample.jsonl"


def _ids(path):
    return [r["formula_id"] for r in read_jsonl(path)]


def stub_translate(in_path, out_path, force=False):
    rows = []
    for fid in _ids(in_path):
        status = "unparsed" if fid == "lacast:gold:002" else "ok"
        rows.append({"formula_id": fid, "status": status, "kind": "equation", "lhs": "Integer(0)", "rhs": "Integer(0)"})
    write_jsonl(out_path, rows)


def stub_semantics(in_path, out_path, formulas_path=None):
    assert formulas_path and Path(formulas_path).exists()
    write_jsonl(out_path, [{"formula_id": r["formula_id"], "checkable": r["status"] == "ok"} for r in read_jsonl(in_path)])


FALSE_POSITIVE = "bench:good:0008"
MISSED_SUFFIX = ":sign_flip"


def stub_verify(parsed_path, semantics_path, out_path):
    rows = []
    for r in read_jsonl(semantics_path):
        fid = r["formula_id"]
        if not r["checkable"]:
            v = "SKIP"
        elif fid == FALSE_POSITIVE:
            v = "FAIL"
        elif fid.startswith("bench:mut:"):
            v = "PASS" if fid.endswith(MISSED_SUFFIX) else "FAIL"
        else:
            v = "PASS"
        rows.append({"formula_id": fid, "verdict": v, "reason": "stub"})
    write_jsonl(out_path, rows)


@pytest.fixture(scope="module")
def bench_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("bench")
    (d / "known_good.jsonl").write_text(FIX.read_text())
    mutate.run(d / "known_good.jsonl", d / "mutated.jsonl", types=["sign_flip", "wrong_constant"], jobs=2)
    write_jsonl(d / "lacast_benchmark.jsonl", lacast.records()[:5])
    return d


def _patch(monkeypatch, available):
    fns = {"translate": stub_translate, "semantics": stub_semantics, "verify": stub_verify}
    monkeypatch.setattr(measure, "find_stage",
                        lambda name: (fns[name], f"stub.{name}") if name in available else (None, "not landed"))


def test_measure_with_stub_stages(bench_dir, monkeypatch):
    _patch(monkeypatch, {"translate", "semantics", "verify"})
    m = measure.measure(bench_dir)
    good = read_jsonl(bench_dir / "known_good.jsonl")
    mut = read_jsonl(bench_dir / "mutated.jsonl")
    n_missed = sum(r["formula_id"].endswith(MISSED_SUFFIX) for r in mut)
    o = m["synthetic"]["overall"]
    assert o["tp"] == len(mut) - n_missed and o["fp"] == 1
    assert o["precision"] == round(o["tp"] / (o["tp"] + 1), 4)
    assert o["recall"] == round((len(mut) - n_missed) / len(mut), 4)
    assert o["known_good"]["translate_ok_rate"] == 1.0
    assert [r["formula_id"] for r in m["synthetic"]["false_positives"]] == [FALSE_POSITIVE]
    assert len([r for r in m["synthetic"]["missed_mutations"] if r["verdict"] == "PASS"]) == n_missed
    pm = m["synthetic"]["per_mutation"]
    assert pm["sign_flip"]["recall"] == 0.0 and pm["wrong_constant"]["recall"] == 1.0
    assert set(m["synthetic"]["per_category"]) == {r["bench"]["category"] for r in good}
    assert m["lacast"]["overall"]["n"] == 5 and m["lacast"]["overall"]["translate_ok"] == 4
    report = (bench_dir / "REPORT.md").read_text()
    for s in ["Stage availability", "Per category", "Per mutation type", "False positives", "Missed mutations", "LaCASt"]:
        assert s in report
    assert json.loads((bench_dir / "metrics.json").read_text())["total_seconds"] >= 0


def test_measure_reports_unavailable_stage(bench_dir, monkeypatch):
    _patch(monkeypatch, {"translate"})
    m = measure.measure(bench_dir, sets=["synthetic"])
    st = m["runs"]["synthetic"]["stages"]
    assert st["translate"]["status"] == "ok"
    assert st["semantics"]["status"] == "unavailable"
    assert st["verify"]["status"] == "skipped_upstream_unavailable"
    o = m["synthetic"]["overall"]
    assert "precision" not in o and o["known_good"]["translate_ok_rate"] == 1.0
    assert "unavailable" in (bench_dir / "REPORT.md").read_text()


def test_stage_that_raises_is_reported(bench_dir, monkeypatch):
    def broken(in_path, out_path):
        raise SystemExit("not implemented yet")

    monkeypatch.setattr(measure, "find_stage", lambda name: (broken, "x") if name == "translate" else (None, "-"))
    m = measure.measure(bench_dir, sets=["synthetic"])
    assert m["runs"]["synthetic"]["stages"]["translate"]["status"] == "error"


def test_find_stage_on_skeleton_stub():
    fn, where = measure.find_stage("does_not_exist")
    assert fn is None


def test_chain_ids_are_joined():
    known = {"bench:good:0001"}
    assert measure._base_id("bench:good:0001#1", known) == "bench:good:0001"
    assert measure._base_id("bench:good:0001:1", known) == "bench:good:0001"
    assert measure.aggregate_verdict([{"verdict": "PASS"}, {"verdict": "FAIL"}]) == "FAIL"
    assert measure.aggregate_verdict([{"verdict": "PASS"}, {"verdict": "INCONCLUSIVE"}]) == "INCONCLUSIVE"
