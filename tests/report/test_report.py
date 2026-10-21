import json
from pathlib import Path

from formulaci.report.report import run
from formulaci.schemas import Counterexample, Finding, Formula, Parsed, RegimeResult, Review, Semantics, Verdict


def _w(path, recs):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(r.model_dump_json() + "\n" for r in recs))


def test_report_end_to_end(tmp_path: Path):
    d = tmp_path / "data"
    f1 = Formula(formula_id="wiki:en:1:1:0", page_title="Gamma function", page_id=1, revision_id=1,
                 url="https://en.wikipedia.org/wiki/Gamma_function", section="Properties", index=0,
                 latex=r"\Gamma(n+1) = n!", context_before="For positive integers n,", context_after="holds.")
    f2 = f1.model_copy(update={"formula_id": "wiki:en:1:1:1", "index": 1, "latex": r"\sin^2 x + \cos^2 x = 2"})
    _w(d / "raw/formulas.jsonl", [f1, f2])
    _w(d / "parsed/parsed.jsonl", [Parsed(formula_id=f1.formula_id, status="ok", kind="equation", lhs="x", rhs="x"),
                                   Parsed(formula_id=f2.formula_id, status="ok", kind="equation", lhs="x", rhs="x")])
    _w(d / "semantics/semantics.jsonl", [Semantics(formula_id=f1.formula_id), Semantics(formula_id=f2.formula_id)])
    _w(d / "verdicts/verdicts.jsonl", [
        Verdict(formula_id=f1.formula_id, verdict="PASS", symbolic="equal", reason="holds"),
        Verdict(formula_id=f2.formula_id, verdict="FAIL", symbolic="not_equal",
                regimes=[RegimeResult(name="small_positive", n_points=20, n_fail=20, n_error=0)],
                counterexample=Counterexample(assignments={"x": "0.5"}, lhs="1.0", rhs="2.0", abs_diff="1.0", rel_diff="0.5"),
                reason="LHS is identically 1, RHS is 2"),
    ])
    _w(d / "findings/reviews.jsonl", [Finding(formula_id=f2.formula_id, verdict="FAIL",
                                              review=Review(status="confirmed_error", reviewer="test", notes="typo"),
                                              suggested_fix=r"\sin^2 x + \cos^2 x = 1")])
    res = run(d)
    assert res["findings"] == 1
    out = [json.loads(l) for l in (d / "findings/findings.jsonl").read_text().splitlines()]
    assert out[0]["formula_id"] == f2.formula_id
    assert out[0]["review"]["status"] == "confirmed_error"
    assert out[0]["confidence"] > 0.5
    page = (d / "findings/report.html").read_text()
    assert "Gamma function" in page and "confirmed_error" in page and "cos^2 x = 1" in page


def test_review_export_import(tmp_path: Path):
    from formulaci.report.review import export, import_reviews
    d = tmp_path / "data"
    f = Formula(formula_id="wiki:en:9:9:0", page_title="Beta function", page_id=9, revision_id=9,
                url="https://en.wikipedia.org/wiki/Beta_function", section="Properties", index=0,
                latex=r"B(x,y) = \frac{\Gamma(x)\Gamma(y)}{\Gamma(x+y+1)}", context_before="For x, y > 0,", context_after="")
    _w(d / "raw/formulas.jsonl", [f])
    _w(d / "parsed/parsed.jsonl", [Parsed(formula_id=f.formula_id, status="ok", kind="equation",
                                          lhs="Function('B')(Symbol('x'), Symbol('y'))", rhs="Mul(gamma(Symbol('x')), gamma(Symbol('y')), Pow(gamma(Add(Symbol('x'), Symbol('y'), Integer(1))), Integer(-1)))")])
    _w(d / "semantics/semantics.jsonl", [Semantics(formula_id=f.formula_id, constants={"B": "beta"})])
    _w(d / "verdicts/verdicts.jsonl", [Verdict(formula_id=f.formula_id, verdict="FAIL", symbolic="not_equal",
                                               regimes=[RegimeResult(name="small_positive", n_points=20, n_fail=20, n_error=0)],
                                               counterexample=Counterexample(assignments={"x": "1", "y": "1"}, lhs="1", rhs="0.5", abs_diff="0.5", rel_diff="0.5"),
                                               reason="fails everywhere")])
    res = export(d, batch_size=10)
    assert res["items"] == 1 and res["batches"] == 1
    text = Path(res["paths"][0]).read_text()
    assert "Beta function" in text and "gamma(x)*gamma(y)/gamma(x + y + 1)" in text and "B': 'beta'" in text
    rv = tmp_path / "r.jsonl"
    rv.write_text(json.dumps({"formula_id": f.formula_id, "review": {"status": "confirmed_error", "notes": "denominator should be Γ(x+y)"},
                              "suggested_fix": r"B(x,y) = \frac{\Gamma(x)\Gamma(y)}{\Gamma(x+y)}"}) + "\n")
    assert import_reviews(d, rv, reviewer="test")["imported"] == 1
    assert export(d)["items"] == 0  # reviewed ids are skipped
