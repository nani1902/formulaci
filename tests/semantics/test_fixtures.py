"""Accuracy on the hand-labeled Wikipedia fixtures, and an end-to-end run of the stage."""
import json
from pathlib import Path

import pytest

from formulaci.schemas import Formula, Parsed, Semantics, read_jsonl
from formulaci.semantics import stage
from formulaci.semantics.accuracy import format_report, score_file

FIX = Path(__file__).parent / "fixtures" / "cases.jsonl"


@pytest.fixture(scope="module")
def report():
    return score_file(FIX)


def test_enough_real_cases():
    cases = [json.loads(l) for l in FIX.read_text().splitlines() if l.strip()]
    assert len(cases) >= 60
    assert len({c["formula"]["page_title"] for c in cases}) >= 9


def test_accuracy_floors(report):
    print("\n" + format_report(report))
    # precision of the checkable flag is what protects the verifier from false FAILs
    assert report["checkable_precision"] >= 0.97
    assert report["checkability_accuracy"] >= 0.95
    assert report["skip_reason_accuracy"] >= 0.90
    assert report["constants_accuracy"] >= 0.95
    assert report["domain_type_accuracy"] >= 0.85
    assert report["unsafe_cases"] <= 4


def test_stage_end_to_end_and_resume(tmp_path):
    cases = [json.loads(l) for l in FIX.read_text().splitlines() if l.strip()]
    fpath, ppath, out = tmp_path / "formulas.jsonl", tmp_path / "parsed.jsonl", tmp_path / "sem" / "semantics.jsonl"
    with fpath.open("w") as ff, ppath.open("w") as pf:
        for c in cases:
            ff.write(Formula.model_validate(c["formula"]).model_dump_json() + "\n")
            for p in c["parsed"]:
                pf.write(Parsed.model_validate(p).model_dump_json() + "\n")
    s1 = stage.run(str(ppath), str(out), formulas_path=str(fpath), limit=10)
    assert s1["written"] == 10
    s2 = stage.run(str(ppath), str(out), formulas_path=str(fpath))
    assert s2["written"] == len(cases) - 10
    recs = list(read_jsonl(out, Semantics))
    assert len(recs) == len(cases) == len({r.formula_id for r in recs})
    s3 = stage.run(str(ppath), str(out), formulas_path=str(fpath))
    assert s3["written"] == 0
    s4 = stage.run(str(ppath), str(out), formulas_path=str(fpath), force=True)
    assert s4["written"] == len(cases)
    # deterministic
    again = {r.formula_id: r.model_dump() for r in read_jsonl(out, Semantics)}
    assert again == {r.formula_id: r.model_dump() for r in recs}
    text = stage.explain(cases[0]["formula"]["formula_id"], str(fpath), str(ppath))
    assert "rules fired:" in text and "D.letter_integer" in text


def test_missing_formula_record_still_produces_semantics(tmp_path):
    ppath = tmp_path / "parsed.jsonl"
    ppath.write_text(Parsed(formula_id="wiki:en:1:1:0", status="ok", kind="equation",
                            lhs="Symbol('x')", rhs="Symbol('x')").model_dump_json() + "\n")
    out = tmp_path / "out.jsonl"
    st = stage.run(str(ppath), str(out), formulas_path=str(tmp_path / "nope.jsonl"))
    assert st["written"] == 1 and st["missing_formula"] == 1


def test_holdout_floors():
    """Held-out cases were labeled before the rules ever saw them and are never used for tuning."""
    rep = score_file(Path(__file__).parent / "fixtures" / "holdout.jsonl")
    print("\n" + format_report(rep))
    assert rep["n"] >= 30
    assert rep["checkable_precision"] >= 0.95
    assert rep["unsafe_cases"] <= 2


def test_review_cases_floors():
    """148 human-reviewed real FAILs: semantics-caused false positives must be skipped or fixed,
    and the confirmed real errors must stay checkable."""
    rep = score_file(Path(__file__).parent / "fixtures" / "review_cases.jsonl")
    print("\n" + format_report(rep))
    errors = [r for r in rep["results"] if r["case"].startswith("confirmed_error:")]
    assert sum(r["got"]["checkable"] for r in errors) >= len(errors) - 1     # the semigroup one is skipped by design
    fps = [r for r in rep["results"] if not r["case"].startswith("confirmed_error:")]
    still_checkable_wrongly = [r["case"] for r in fps if r["got"]["checkable"] and not r["expected"]["checkable"]]
    assert len(still_checkable_wrongly) <= 6, still_checkable_wrongly
