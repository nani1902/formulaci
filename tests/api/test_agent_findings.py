"""Regressions for the defects found by the black-box test agents (library and MCP), 2026-10-21.

Each case is a formula a user would reasonably submit; the verdict asserted is the one a careful
mathematician would expect. Slow-ish (real pipeline): ~20 s in total.
"""
from __future__ import annotations

import pytest

from formulaci.api import check


def v(latex, ctx=""):
    r = check(latex, ctx)
    return r.verdict, r


def test_wrong_polynomial_identity_fails_when_universally_quantified():
    verdict, r = v(r"(a+b)^2 = a^2 + ab + b^2", "for all real a and b")
    assert verdict == "FAIL", r.explain()
    verdict, r = v(r"\cosh^2 x + \sinh^2 x = 1", "for all real x")
    assert verdict == "FAIL", r.explain()
    verdict, r = v(r"(a+b)^2 = a^2 + 2ab + b^2", "for all real a and b")
    assert verdict == "PASS", r.explain()


def test_relation_shaped_skip_says_the_sides_differ():
    verdict, r = v(r"(a+b)^2 = a^2 + ab + b^2")
    assert verdict == "SKIP" and r.skip_reason == "statement_not_identity"
    assert "not identically equal" in r.reason and "for all real a and b" in r.reason


def test_near_unanimous_failure_is_a_fail_despite_degenerate_integer_points():
    verdict, r = v(r"a^3-b^3=(a-b)(a^2-ab+b^2)", "for all a and b")
    assert verdict == "FAIL", r.explain()


def test_chained_and_compound_constraints_are_kept():
    _, r = v(r"\sum_{k=0}^{n} \binom{n}{k} p^k (1-p)^{n-k} k = np", "for 0 < p < 1 and positive integers n")
    assert set(r.assumptions["constraints"]) >= {"0 < p", "p < 1"}, r.assumptions
    _, r = v(r"(1+x)^n \ge 1+nx", "for x > -1 and positive integers n")
    assert "x > -1" in r.assumptions["constraints"] and r.verdict == "PASS", r.explain()
    _, r = v(r"\sum_{k=0}^\infty k \frac{\lambda^k e^{-\lambda}}{k!} = \lambda", "for 0 < \\lambda < 10")
    assert "lambda < 10" in r.assumptions["constraints"], r.assumptions


def test_poisson_mean_passes_at_large_rate_too():
    # the direct accumulation used to stop after five tiny leading terms (lambda^k/k! peaks at k ~ lambda)
    verdict, r = v(r"\sum_{k=0}^\infty k \frac{\lambda^k e^{-\lambda}}{k!} = \lambda", "where e is Euler's number")
    assert verdict == "PASS", r.explain()


def test_juxtaposed_digit_power_and_plain_beta_function():
    verdict, r = v(r"\sum_{k=0}^{n} k\binom{n}{k} = n2^{n-1}", "for positive integers n")
    assert verdict == "PASS", r.explain()
    verdict, r = v(r"\sum_{k=0}^{n} k\binom{n}{k} = n2^{n}", "for positive integers n")
    assert verdict == "FAIL", r.explain()
    verdict, r = v(r"B(x,y) = \frac{\Gamma(x)\Gamma(y)}{\Gamma(x+y)}")
    assert verdict == "PASS", r.explain()
    verdict, r = v(r"h2 < h1")
    assert verdict != "FAIL"


def test_oscillatory_integral_with_wrong_value_fails_via_closed_form():
    verdict, r = v(r"\int_0^\infty \frac{\sin x}{x}\,dx = \pi")
    assert verdict == "FAIL", r.explain()
    assert r.counterexample and r.counterexample["lhs"].startswith("1.5707963")
    verdict, r = v(r"\int_0^\infty \frac{\sin x}{x}\,dx = \frac{\pi}{2}")
    assert verdict == "PASS", r.explain()
    assert "could not confirm" in r.reason and "0 evaluable" not in r.reason


def test_false_inequality_over_stated_reals_is_never_pass():
    verdict, r = v(r"x^2 \ge x", "for all real x")
    assert verdict != "PASS", r.explain()
    verdict, r = v(r"x^2 \ge x", "for 0 < x < 1")
    assert verdict == "FAIL", r.explain()


def test_integer_only_guard_needs_diverse_integer_samples():
    # |x| < 1 leaves x = 0 as the only admissible integer, where every mutation trivially agrees
    for latex in (r"\prod_{k=0}^{n - 1} \left(1 - x^{2^{k}}\right) = \frac{1 - x^{2^{n}}}{1 - x}",
                  r"\sum_{k=0}^{\infty} \binom{k + n}{k} x^{k} = \frac{1}{(1 + x)^{n + 1}}"):
        verdict, r = v(latex, "for |x| < 1 and positive integers n")
        assert verdict != "PASS", r.explain()
    verdict, r = v(r"\prod_{k=0}^{n - 1} \left(1 + x^{2^{k}}\right) = \frac{1 - x^{2^{n}}}{1 - x}", "for |x| < 1 and positive integers n")
    assert verdict == "PASS", r.explain()


def test_inequality_reason_reads_well():
    _, r = v(r"e^x \ge 1 + x", "for all real x")
    assert "ordering proved" not in r.reason and r.verdict == "PASS"


def test_explain_reports_unevaluable_points():
    _, r = v(r"\int_0^\infty \frac{\sin x}{x}\,dx = \frac{\pi}{2}")
    assert "not evaluable" in r.explain()
