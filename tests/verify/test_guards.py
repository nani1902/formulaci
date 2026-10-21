import sympy as sp

from formulaci.schemas import Parsed, Semantics
from formulaci.verify.guards import (decimal_literal, decimal_sides, label_superscript, rational_approximation,
                                     sides_latex, tolerance_hints)
from formulaci.verify.policy import decide
from formulaci.verify.reconstruct import build_problem

x, a = sp.symbols("x a")


def problem(lhs, rhs, **sem):
    p = Parsed(formula_id="t", status="ok", kind="equation", lhs=sp.srepr(lhs), rhs=sp.srepr(rhs))
    return build_problem(p, Semantics(formula_id="t", **sem))


def test_decimal_literal_parsing():
    assert decimal_literal("0.74048")["decimals"] == 5
    assert decimal_literal(r"10.585.")["text"] == "10.585"
    assert decimal_literal(r"{1.7320\ldots}")["truncated"] is True
    assert decimal_literal(r"-\,.5")["text"] == "-0.5"
    for no in ["2", r"\frac{1}{2}", "0.5x", r"0.3\%", "355/113"]:
        assert decimal_literal(no) is None, no


def test_decimal_side_must_match_reconstruction():
    notes = "pre:x\nsides: \\frac{\\pi}{3\\sqrt{2}}  ||  0.74048"
    assert sides_latex(notes) == (r"\frac{\pi}{3\sqrt{2}}", "0.74048")
    p = problem(sp.pi/(3*sp.sqrt(2)), sp.Rational("0.74048"))
    assert decimal_sides(p, notes) == [{"side": 1, "text": "0.74048", "decimals": 5, "truncated": False}]
    assert decimal_sides(problem(sp.pi, sp.Rational(1, 3)), notes) == []  # notes disagree with the srepr


def test_rational_approximation():
    assert rational_approximation(problem(sp.pi, sp.Rational(355, 113)))
    assert not rational_approximation(problem(sp.Rational(2, 3), sp.Rational(67, 100)))
    assert not rational_approximation(problem(sp.pi*x, sp.Rational(355, 113)))


def test_tolerance_hints():
    assert tolerance_hints(["D.x", "tol:rel=1e-3"]) == {"rel": 1e-3}
    assert tolerance_hints(["tol:digits=2"]) == {"abs": 0.005}
    assert tolerance_hints(["tol:approx"]) == {"approx": True}
    assert tolerance_hints(["tol:rel=__import__"]) == {}


def test_label_superscript_detection():
    B, s, F, D, H = sp.symbols("B s F D H", positive=True)
    assert "s occurs only" in label_superscript(problem(B, B**s), None)
    assert label_superscript(problem(F, F**D + F**H), None)
    assert "multi-letter" in label_superscript(problem(B**(a*x), x/a), None)
    assert "parenthesised" in label_superscript(problem(sp.Integer(1), sp.Integer(0)), "sides: X^{(0)}  ||  0")
    assert "superscript 0" in label_superscript(problem(sp.Integer(1), sp.Integer(3)), "sides: C_3^0  ||  3")
    assert "translator" in label_superscript(problem(x, x), "superscript_label:e^iax")
    # genuine powers: exponents in arithmetic, shared with other terms, or bound summation indices
    k, n = sp.symbols("k n")
    assert label_superscript(problem(x**(a + 1), x*x**a), None) is None
    assert label_superscript(problem(sp.exp(a*sp.log(x)), x**a, domains={"x": {"type": "positive"}}), None) is None
    assert label_superscript(problem(sp.Sum(x**k, (k, 0, n)), (1 - x**(n + 1))/(1 - x)), None) is None
    assert label_superscript(problem(2**x, 4**(x/2)), "sides: 2^x  ||  4^{x/2}") is None
    alt = r"sides: 1 - \cos(x)  ||  1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}"
    assert label_superscript(problem(1 - sp.cos(x), x), alt) is None  # (-1)^{(k+1)} is a power
    assert label_superscript(problem(x**(2*a), (x**a)**3), None) is None  # 2a, 3a: arithmetic
    # more label shapes from the review of real FAILs
    J, f, g, U, M, X = sp.symbols("J f g U M X", positive=True)
    k = sp.Symbol("k", integer=True, nonnegative=True)
    assert label_superscript(problem(J**k*f*J**k*g, J**k*f*g), None)          # J^k J^k merged to J^{2k}
    assert "inverse" in label_superscript(problem(1/U, U), None)
    assert label_superscript(problem(X, M**X + f), None)
    assert "circle" in label_superscript(problem(x, x), r"sides: \frac{G}{N}  ||  \frac{G^\circ}{N}")
    assert "operator" in label_superscript(problem(x, x), r"sides: \operatorname{Ric}^g  ||  g")
    assert label_superscript(problem(x, x), r"sides: 30^\circ  ||  \pi/6") is None  # degrees
    # big-operator limits are bounds, not superscripts
    for bounds in [r"\int_0^\infty e^{-t}\,dt", r"\prod_{k=0}^{(n)} k", r"\sum_{k=0}^0 x",
                   r"\sum_{n=1}^{\infty} \frac{(-1)^{(n+1)}}{n}"]:
        assert label_superscript(problem(x, x), f"sides: {bounds}  ||  1") is None, bounds
    assert label_superscript(problem(x, x), r"sides: \sum_{n=1}^\infty a_n^{(0)}  ||  1")


def _constant_numeric(lhs, rhs):
    pt = {"point": {}, "status": "fail", "lhs": lhs, "rhs": rhs, "abs_diff": "1", "rel_diff": "1", "rel": 1.0,
          "error": ""}
    return {"regimes": [{"name": "constant", "n_points": 1, "n_fail": 1, "n_error": 0, "points": [pt]}],
            "constant": True, "eval_error": ""}


def test_rounding_policy():
    lit = {"side": 1, "text": "0.74048", "decimals": 5, "truncated": False}
    meta = {"relation": "=", "decimal_sides": [lit], "rational_approx": True}
    exact = "0.7404804896930610411180566132904956726882"
    assert decide(meta, "unknown", _constant_numeric(exact, "0.74048"))[0] == "PASS"
    wrong = {**meta, "decimal_sides": [{**lit, "text": "0.74084"}]}
    v, reason, ce = decide(wrong, "unknown", _constant_numeric(exact, "0.74084"))
    assert v == "FAIL" and "it would be 0.74048" in reason and ce is not None
    # half a unit is the limit: 9.41497... printed as 9.414 is a (confirmed) rounding error
    lit2 = {"side": 1, "text": "9.414", "decimals": 3, "truncated": False}
    v, reason, _ = decide({**meta, "decimal_sides": [lit2]}, "unknown", _constant_numeric("9.414977231", "9.414"))
    assert v == "FAIL" and "9.415" in reason
    assert decide({**meta, "decimal_sides": [{**lit2, "truncated": True}]}, "unknown",
                  _constant_numeric("9.414977231", "9.414"))[0] == "PASS"


def test_label_and_approx_guards_only_touch_fail():
    regs = [{"name": r, "n_points": 12, "n_fail": 12, "n_error": 0,
             "points": [{"point": {"x": "0.5"}, "status": "fail", "lhs": "1", "rhs": "2", "abs_diff": "1",
                         "rel_diff": "0.5", "rel": 0.5, "error": ""}] * 12}
            for r in ["small_positive", "unit_interval", "integers_small", "mixed_sign", "large"]]
    num = {"regimes": regs, "constant": False, "eval_error": ""}
    assert decide({"relation": "=", "label": "s occurs only as ..."}, "unknown", num)[0] == "INCONCLUSIVE"
    assert decide({"relation": "=", "tol": {"approx": True}}, "unknown", num)[0] == "INCONCLUSIVE"
    passing = {"regimes": [{**r, "n_fail": 0, "points": []} for r in regs], "constant": False, "eval_error": ""}
    v, reason, _ = decide({"relation": "=", "label": "x", "tol": {"rel": 1e-3}}, "unknown", passing)
    assert v == "PASS" and "rel 0.001" in reason
