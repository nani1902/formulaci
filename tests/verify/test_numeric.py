import random

import mpmath as mp
import sympy as sp

from formulaci.schemas import Domain, Parsed, Semantics
from formulaci.verify.numeric import Evaluator
from formulaci.verify.reconstruct import SymSpec, build_problem
from formulaci.verify.sampler import REGIMES, in_domain, sample_value, seed_for

x, n, k, t = sp.symbols("x n k t")


def ev(lhs, rhs, relation=None, **sem):
    kind = "inequality" if relation else "equation"
    p = Parsed(formula_id="t", status="ok", kind=kind, relation=relation, lhs=sp.srepr(lhs), rhs=sp.srepr(rhs))
    return Evaluator.build(build_problem(p, Semantics(formula_id="t", **sem)))


def test_cancellation_at_large_arguments_is_not_a_failure():
    e = ev(sp.cosh(x)**2 - sp.sinh(x)**2, 1)
    for v in ["102.738", "211.42", "915.417"]:
        assert e.evaluate({"x": v}, False).status == "pass", v


def test_rounding_noise_around_zero_passes():
    e = ev(sp.sin(sp.pi * n), 0)
    assert e.evaluate({"n": 7}, False).status == "pass"


def test_genuine_failure_is_confirmed():
    r = ev(sp.sin(2*x), -2*sp.sin(x)*sp.cos(x)).evaluate({"x": "0.5"}, False)
    assert r.status == "fail" and r.rel_diff > 1


def test_tiny_but_different_values_fail():
    # both sides ~1e-300: no absolute floor may hide a 100x discrepancy
    y = sp.Symbol("y")
    e = ev(sp.beta(x, y), sp.gamma(x)*sp.gamma(y)/sp.gamma(x + y + 1),
           domains={"x": Domain(type="positive"), "y": Domain(type="positive")})
    assert e.evaluate({"x": "400.5", "y": "300.25"}, False).status == "fail"


def test_exact_zero_that_persists_is_a_failure():
    e = ev(sp.floor(x) + sp.floor(-x), -1)
    assert e.evaluate({"x": 3}, False).status == "fail"
    assert e.evaluate({"x": "3.5"}, False).status == "pass"


def test_series_products_integrals():
    assert ev(sp.Sum(1/k**2, (k, 1, sp.oo)), sp.pi**2/6).evaluate({}, True).status == "pass"
    assert ev(sp.Sum(1/k**2, (k, 1, sp.oo)), sp.pi**2/8).evaluate({}, True).status == "fail"
    assert ev(sp.Sum(k, (k, 1, sp.oo)), 0).evaluate({}, True).status == "error"  # divergent
    assert ev(sp.Product(1 - 1/k**2, (k, 2, sp.oo)), sp.Rational(1, 2)).evaluate({}, True).status == "pass"
    assert ev(sp.Integral(sp.exp(-t**2), (t, -sp.oo, sp.oo)), sp.sqrt(sp.pi)).evaluate({}, True).status == "pass"


def test_sharply_peaked_integral_is_an_error_not_a_failure():
    z = sp.Symbol("z")
    e = ev(sp.gamma(z)**2/sp.gamma(2*z), sp.Integral(t**(z - 1)*(1 - t)**(z - 1), (t, 0, 1)),
           domains={"z": Domain(type="positive")})
    assert e.evaluate({"z": "300"}, False).status == "error"
    assert e.evaluate({"z": "2.5"}, False).status == "pass"


def test_real_regime_rejects_complex_values():
    r = ev(sp.sqrt(x), x).evaluate({"x": "-2"}, False)
    assert r.status == "error" and "real" in r.error


def test_inequality_directional():
    a, b = sp.symbols("a b")
    dom = {"a": Domain(type="positive"), "b": Domain(type="positive")}
    good = ev((a + b)/2, sp.sqrt(a*b), relation=">=", domains=dom)
    bad = ev((a + b)/2, sp.sqrt(a*b), relation="<=", domains=dom)
    assert good.evaluate({"a": "1.5", "b": "2"}, False).status == "pass"
    assert good.evaluate({"a": "2", "b": "2"}, False).status == "pass"  # equality is fine
    assert bad.evaluate({"a": "1.5", "b": "2"}, False).status == "fail"


def test_sampler_is_deterministic_and_respects_domains():
    spec = SymSpec("x", sp.Symbol("x"), "real", lower=0.5, upper=2.0)
    ispec = SymSpec("n", sp.Symbol("n"), "positive_integer")
    for name, regime in REGIMES.items():
        r1, r2 = random.Random(seed_for("f", name)), random.Random(seed_for("f", name))
        a = [sample_value(spec, regime, r1) for _ in range(20)]
        assert a == [sample_value(spec, regime, r2) for _ in range(20)]
        assert all(in_domain(spec, v) for v in a), name
        ints = [sample_value(ispec, regime, r1) for _ in range(20)]
        assert all(isinstance(v, int) and v >= 1 for v in ints), name
    assert mp.mpf(sample_value(spec, REGIMES["large"], random.Random(1))) <= 2
