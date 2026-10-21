import pytest
import sympy as sp

from formulaci.schemas import Domain, Parsed, Semantics
from formulaci.verify.reconstruct import (NotCheckable, UnsafeExpression, bare_symbol_side, build_problem,
                                          from_srepr, has_branch_cut, parse_constraint)

x, y = sp.symbols("x y")


def problem(lhs, rhs, **sem):
    p = Parsed(formula_id="t", status="ok", kind="equation", lhs=sp.srepr(lhs), rhs=sp.srepr(rhs))
    return build_problem(p, Semantics(formula_id="t", **sem))


def test_round_trip():
    e = sp.Sum(sp.binomial(sp.Symbol("n"), sp.Symbol("k")), (sp.Symbol("k"), 0, sp.oo)) + sp.Float("1.5") * sp.pi
    assert from_srepr(sp.srepr(e)) == e


@pytest.mark.parametrize("bad", [
    "__import__('os').system('true')",
    "Symbol('x').__class__",
    "sin('__import__(\"os\").system(\"true\")')",      # strings are sympified by most functions
    "lambdify(Symbol('x'), Symbol('x'))",
    "S('x')",
    "Integer('1; import os')",
    "[c for c in ()]",
    "Function('f').__init__",
    "Lambda(Symbol('x'), Symbol('x'))(Integer(1))",
])
def test_rejects_unsafe_srepr(bad):
    with pytest.raises((UnsafeExpression, SyntaxError)):
        from_srepr(bad)


def test_undefined_function_is_parsed_then_skipped():
    with pytest.raises(NotCheckable, match="undefined_function"):
        problem(sp.Function("f")(x), x**2)


def test_constants_and_domains():
    e, i = sp.symbols("e i")
    p = problem(e**(i*sp.pi) + x, x - 1, constants={"e": "E", "i": "I"}, domains={"x": Domain(type="positive")})
    assert p.lhs - p.rhs == 0  # E**(I*pi) evaluated to -1
    (spec,) = p.syms
    assert spec.symbol.is_positive and spec.type == "positive"


def test_summation_bound_inferred_integer():
    n, k = sp.symbols("n k")
    p = problem(sp.Sum(k, (k, 1, n)), n*(n + 1)/2)
    (spec,) = p.syms
    assert spec.type == "nonneg_integer" and spec.inferred


def test_constraints():
    syms = {"x": sp.Symbol("x"), "n": sp.Symbol("n")}
    c = parse_constraint("0 < x < 1", syms)
    assert c.subs(syms["x"], sp.Rational(1, 2)) is sp.true and c.subs(syms["x"], 2) is sp.false
    assert parse_constraint("Ne(x, 0) and n >= 1", syms).subs({syms["x"]: 1, syms["n"]: 1}) is sp.true
    for bad in ["__import__('os')", "x.real > 0", "open('f') > 0", "y > 0"]:
        with pytest.raises((UnsafeExpression, SyntaxError)):
            parse_constraint(bad, syms)


def test_bad_constraints_are_reported_not_fatal():
    p = problem(x, x, constraints=["x > 0", "x.__class__ > 0"])
    assert len(p.constraints) == 1 and p.constraint_errors


def test_relations():
    p = Parsed(formula_id="t", status="ok", kind="inequality", relation="\\le", lhs=sp.srepr(x), rhs=sp.srepr(y))
    assert build_problem(p, Semantics(formula_id="t")).relation == "<="
    p.relation = "\\approx"
    with pytest.raises(NotCheckable):
        build_problem(p, Semantics(formula_id="t"))


def test_bare_symbol_and_branch_detection():
    assert bare_symbol_side(problem(y, x**2 + 1)) == "y"
    assert bare_symbol_side(problem(x, sp.sqrt(x**2))) is None
    assert has_branch_cut(sp.sqrt(x) + 1) and has_branch_cut(sp.log(x)) and has_branch_cut(x**y)
    assert not has_branch_cut(sp.sin(x)**2 + sp.exp(x) + x**3)
