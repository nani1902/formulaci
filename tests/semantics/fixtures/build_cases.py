"""Build `cases.jsonl`: hand-labeled semantics fixtures from real Wikipedia formulas.

Each case = one real `<math>` from a cached English Wikipedia revision (latex, section and
~400 chars of plain-text context on each side, extracted by the crude stripper below), a
hand-written `Parsed` record (what a reasonable translator would emit; lhs/rhs given as
readable sympy strings and stored as srepr), and the hand label:

    expect.checkable / expect.skip_reason
    expect.constants   {symbol: canonical constant or sympy function}
    expect.domains     {symbol: Domain.type}           (checkable cases only)
    expect.constraints [sympy strings]                 the constraints the identity *needs*
                                                       beyond its domains (checkable only)

Labels are what is mathematically right for the verifier, not what the rules produce.

Regenerate (needs network once; raw API responses are cached in --cache):
    uv run python tests/semantics/fixtures/build_cases.py --cache /tmp/wiki-cache
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import sympy

HERE = Path(__file__).parent
UA = "formulaci-semantics-fixtures/0.1 (research test fixtures; https://github.com/ formulaci)"


def gp(a: str) -> str:
    """Expected constraint: `a` is not a pole of Gamma (non-positive integer)."""
    return f"Not(And(Eq({a}, floor(re({a}))), re({a}) <= 0))"


# (page title, <math> index, pieces, undefined functions, expect)
# piece = (lhs, rhs) or (lhs, rhs, {extra Parsed fields})
CASES = [
    # ------------------------------------------------------------------ Gamma function
    ("Gamma function", 2, [("Gamma(n)", "factorial(n - 1)")], [],
     dict(checkable=True, domains={"n": "positive_integer"})),
    ("Gamma function", 3, [("Gamma(z)", "Integral(t**(z - 1)*e**(-t), (t, 0, oo))", {"kind": "definition_like"})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"z": "complex"}, constraints=["re(z) > 0"])),
    ("Gamma function", 12, [("f(x + 1)", "x*f(x)", {"notes": "cond: x>0"})], ["f"],
     dict(checkable=False, skip_reason="functional_identity")),
    ("Gamma function", 14, [("g(x)", "g(x + 1)")], ["g"],
     dict(checkable=False, skip_reason="functional_identity")),
    ("Gamma function", 26, [("z*Gamma(z)", "Gamma(z + 1)")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=[gp("z")])),
    ("Gamma function", 38, [("Gamma(n + 1)", "factorial(n)")], [],
     dict(checkable=True, domains={"n": "nonneg_integer"})),
    ("Gamma function", 40, [("Gamma(x + 1)", "x*Gamma(x)")], [],
     dict(checkable=True, domains={"x": "real"}, constraints=[gp("x")])),
    ("Gamma function", 44, [("Gamma(z)", "e**(-gamma*z)/z*Product((1 + z/n)**(-1)*e**(z/n), (n, 1, oo))")], [],
     dict(checkable=True, constants={"e": "E", "gamma": "EulerGamma"}, domains={"z": "complex"}, constraints=[gp("z")])),
    ("Gamma function", 59, [("Gamma(1 - z)*Gamma(z)", "pi/sin(pi*z)")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=["Ne(sin(pi*z), 0)"])),
    ("Gamma function", 61, [("Gamma(z)*Gamma(z + 1/2)", "2**(1 - 2*z)*sqrt(pi)*Gamma(2*z)")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=[gp("z"), gp("2*z")])),
    ("Gamma function", 104, [("Gamma(1/2)", "sqrt(pi)")], [],
     dict(checkable=True)),
    ("Gamma function", 116, [("Derivative(Gamma(z), z)", "Gamma(z)*polygamma(0, z)")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=[gp("z")])),
    ("Gamma function", 118, [("Subs(Derivative(Gamma(u), u), u, m + 1)", "factorial(m)*(-gamma + Sum(1/k, (k, 1, m)))", {"index_in_chain": 0}),
                             ("factorial(m)*(-gamma + Sum(1/k, (k, 1, m)))", "factorial(m)*(-gamma + H(m))", {"index_in_chain": 1})], ["H"],
     dict(checkable=True, constants={"gamma": "EulerGamma", "H": "harmonic"}, domains={"m": "nonneg_integer"})),
    ("Gamma function", 29, [("Limit(factorial(n)*(n + 1)**m/factorial(n + m), n, oo)", "1")], [],
     dict(checkable=True, domains={"m": "integer"})),
    ("Gamma function", 45, [("gamma", "0.577216", {"kind": "other", "relation": "approx"})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    # ------------------------------------------------------------------ Beta function
    ("Beta function", 5, [("Beta(z_1, z_2)", "Beta(z_2, z_1)")], [],
     dict(checkable=True, domains={"z_1": "complex", "z_2": "complex"}, constraints=[gp("z_1"), gp("z_2")])),
    ("Beta function", 8, [("Beta(z_1, z_2)", "Gamma(z_1)*Gamma(z_2)/Gamma(z_1 + z_2)")], [],
     dict(checkable=True, domains={"z_1": "complex", "z_2": "complex"}, constraints=[gp("z_1"), gp("z_2")])),
    ("Beta function", 28, [("Beta(m, n)", "factorial(m - 1)*factorial(n - 1)/factorial(m + n - 1)", {"index_in_chain": 0}),
                           ("factorial(m - 1)*factorial(n - 1)/factorial(m + n - 1)", "((m + n)/(m*n))/binomial(m + n, m)", {"index_in_chain": 1})], [],
     dict(checkable=True, domains={"m": "positive_integer", "n": "positive_integer"})),
    ("Beta function", 29, [("Derivative(B(z_1, z_2), z_1)",
                            "B(z_1, z_2)*(Derivative(Gamma(z_1), z_1)/Gamma(z_1) - Subs(Derivative(Gamma(u), u), u, z_1 + z_2)/Gamma(z_1 + z_2))")], ["B"],
     dict(checkable=True, constants={"B": "beta"}, domains={"z_1": "complex", "z_2": "complex"}, constraints=[gp("z_1"), gp("z_2")])),
    ("Beta function", 32, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\sim"]})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Beta function", 49, [("Beta(x, y)", "Beta(x, y + 1) + Beta(x + 1, y)")], [],
     dict(checkable=True, domains={"x": "real", "y": "real"}, constraints=[gp("x"), gp("y")])),
    ("Beta function", 60, [("Beta(1, x)", "1/x")], [],
     dict(checkable=True, domains={"x": "real"}, constraints=[gp("x")])),
    ("Beta function", 61, [("Beta(x, 1 - x)", "pi/sin(pi*x)", {"notes": "cond: x \\not \\in \\mathbb{Z}"})], [],
     dict(checkable=True, domains={"x": "real"}, constraints=["Ne(sin(pi*x), 0)"])),
    ("Beta function", 76, [("B(x, a, b)", "Integral(t**(a - 1)*(1 - t)**(b - 1), (t, 0, x))")], ["B"],
     dict(checkable=False, skip_reason="has_undefined_function")),
    ("Beta function", 90, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\Pr"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    # ------------------------------------------------------------------ trigonometric identities
    ("List of trigonometric identities", 0, [("1 + cot(theta)**2", "csc(theta)**2")], [],
     dict(checkable=True, domains={"theta": "angle"}, constraints=["Ne(sin(theta), 0)"])),
    ("List of trigonometric identities", 1, [("tan(theta)**2 + 1", "sec(theta)**2")], [],
     dict(checkable=True, domains={"theta": "angle"}, constraints=["Ne(cos(theta), 0)"])),
    ("List of trigonometric identities", 2, [("sin(theta)**2 + cos(theta)**2", "1")], [],
     dict(checkable=True, domains={"theta": "angle"})),
    ("List of trigonometric identities", 7, [("x**2 + y**2", "1")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("List of trigonometric identities", 83, [("sin(-theta)", "-sin(theta)")], [],
     dict(checkable=True, domains={"theta": "angle"})),
    ("List of trigonometric identities", 87, [("sin(2*pi - theta)", "-sin(theta)", {"index_in_chain": 0}),
                                              ("-sin(theta)", "sin(-theta)", {"index_in_chain": 1})], [],
     dict(checkable=True, domains={"theta": "angle"})),
    ("List of trigonometric identities", 94, [("tan(pi/2 - theta)", "cot(theta)")], [],
     dict(checkable=True, domains={"theta": "angle"}, constraints=["Ne(sin(theta), 0)"])),
    ("List of trigonometric identities", 238, [("sin(alpha + beta)", "sin(alpha)*cos(beta) + cos(alpha)*sin(beta)")], [],
     dict(checkable=True, domains={"alpha": "angle", "beta": "angle"})),
    ("List of trigonometric identities", 289, [("tan(theta/2)", "csc(theta) - cot(theta)", {"index_in_chain": 0}),
                                               ("csc(theta) - cot(theta)", "sqrt((1 - cos(theta))/(1 + cos(theta)))", {"index_in_chain": 1})], [],
     dict(checkable=False, skip_reason="plus_minus")),
    ("List of trigonometric identities", 421, [("asin(x)", "-i*log(i*x + sqrt(1 - x**2))")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"x": "real"}, constraints=["x >= -1", "x <= 1"])),
    # ------------------------------------------------------------------ binomial coefficient
    ("Binomial coefficient", 2, [("binomial(n, k)", "factorial(n)/(factorial(k)*factorial(n - k))")], [],
     dict(checkable=True, domains={"n": "nonneg_integer", "k": "nonneg_integer"}, constraints=["k <= n"])),
    ("Binomial coefficient", 6, [("binomial(n, k)", "binomial(n - 1, k - 1) + binomial(n - 1, k)")], [],
     dict(checkable=True, domains={"n": "nonneg_integer", "k": "nonneg_integer"})),
    ("Binomial coefficient", 12, [("(x + y)**n", "Sum(binomial(n, k)*x**k*y**(n - k), (k, 0, n))")], [],
     dict(checkable=True, domains={"x": "real", "y": "real", "n": "nonneg_integer"})),
    ("Binomial coefficient", 22, [("binomial(n, k)", "factorial(n)/(factorial(k)*factorial(n - k))")], [],
     dict(checkable=True, domains={"n": "nonneg_integer", "k": "nonneg_integer"}, constraints=["k <= n"])),
    ("Binomial coefficient", 29, [("(1 + X)**alpha", "Sum(binomial(alpha, k)*X**k, (k, 0, oo))")], [],
     dict(checkable=True, domains={"alpha": "complex", "X": "complex"}, constraints=["Abs(X) < 1"])),
    ("Binomial coefficient", 34, [("binomial(n, k) + binomial(n, k + 1)", "binomial(n + 1, k + 1)")], [],
     dict(checkable=True, domains={"n": "nonneg_integer", "k": "nonneg_integer"})),
    ("Binomial coefficient", 61, [("Sum(binomial(n, k), (k, 0, n))", "2**n")], [],
     dict(checkable=True, domains={"n": "nonneg_integer"})),
    ("Binomial coefficient", 64, [("Sum(k**2*binomial(n, k), (k, 0, n))", "(n + n**2)*2**(n - 2)")], [],
     dict(checkable=True, domains={"n": "nonneg_integer"})),
    ("Binomial coefficient", 72, [("Sum(binomial(n - k, k), (k, 0, floor(n/2)))", "F(n + 1)")], ["F"],
     dict(checkable=True, constants={"F": "fibonacci"}, domains={"n": "nonneg_integer"})),
    # ------------------------------------------------------------------ Riemann zeta function
    ("Riemann zeta function", 0, [("zeta(s)", "Sum(1/n**s, (n, 1, oo))")], [],
     dict(checkable=True, domains={"s": "complex"}, constraints=["re(s) > 1"])),
    ("Riemann zeta function", 2, [("zeta(s)", "Sum(1/n**s, (n, 1, oo))", {"index_in_chain": 0}),
                                  ("Sum(1/n**s, (n, 1, oo))", "1/Gamma(s)*Integral(x**(s - 1)/(e**x - 1), (x, 0, oo))", {"index_in_chain": 1})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"s": "complex"}, constraints=["re(s) > 1"])),
    ("Riemann zeta function", 4, [("Limit((s - 1)*zeta(s), s, 1)", "1")], [],
     dict(checkable=True)),
    ("Riemann zeta function", 9, [("zeta(s)", "2**s*pi**(s - 1)*sin(pi*s/2)*Gamma(1 - s)*zeta(1 - s)")], [],
     dict(checkable=True, domains={"s": "complex"}, constraints=[gp("1 - s"), "Ne(s, 0)"])),
    ("Riemann zeta function", 5, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\prod_{p \\text{ prime}}"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Riemann zeta function", 46, [("Abs(N(T) - T/(2*pi)*log(T/(2*pi*e)))", "0.112*log(T) + 0.278*log(log(T)) + 2.51", {"kind": "inequality", "relation": "<="})], ["N"],
     dict(checkable=False, skip_reason="has_undefined_function")),
    # ------------------------------------------------------------------ normal distribution
    ("Normal distribution", 22, [("f(x)", "1/sqrt(2*pi*sigma**2)*exp(-(x - mu)**2/(2*sigma**2))", {"kind": "definition_like"})], ["f"],
     dict(checkable=False, skip_reason="definition")),
    ("Normal distribution", 49, [("Phi(x)", "(1 + erf(x/sqrt(2)))/2")], ["Phi"],
     dict(checkable=False, skip_reason="has_undefined_function")),
    ("Normal distribution", 48, [("erf(x)", "1/sqrt(pi)*Integral(e**(-t**2), (t, -x, x))", {"index_in_chain": 0}),
                                 ("1/sqrt(pi)*Integral(e**(-t**2), (t, -x, x))", "2/sqrt(pi)*Integral(e**(-t**2), (t, 0, x))", {"index_in_chain": 1})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"x": "real"})),
    ("Normal distribution", 26, [("varphi(z)", "e**(-z**2/2)/sqrt(2*pi)", {"kind": "definition_like"})], ["varphi"],
     dict(checkable=False, skip_reason="definition")),
    ("Normal distribution", 33, [("sigma**2", "1/(2*pi)")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Normal distribution", 2, [(None, None, {"status": "not_checkable", "kind": "other"})], [],
     dict(checkable=False, skip_reason="set_notation")),
    ("Normal distribution", 18, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["pmatrix"]})], [],
     dict(checkable=False, skip_reason="matrix_or_vector")),
    # ------------------------------------------------------------------ logarithm
    ("Logarithm", 0, [("log(x*y)/log(b)", "log(x)/log(b) + log(y)/log(b)")], [],
     dict(checkable=True, domains={"b": "positive", "x": "positive", "y": "positive"}, constraints=["Ne(b, 1)"])),
    ("Logarithm", 16, [("log(x**p)/log(b)", "p*log(x)/log(b)")], [],
     dict(checkable=True, domains={"b": "positive", "x": "positive", "p": "real"}, constraints=["Ne(b, 1)"])),
    ("Logarithm", 23, [("log(x)/log(b)", "(log(x)/log(k))/(log(b)/log(k))")], [],
     dict(checkable=True, domains={"b": "positive", "x": "positive", "k": "positive"}, constraints=["Ne(b, 1)", "Ne(k, 1)"])),
    ("Logarithm", 30, [("log(cos(theta) + i*sin(theta))", "i*theta")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"theta": "angle"}, constraints=["theta > -pi", "theta <= pi"])),
    ("Logarithm", 67, [("Derivative(log(x)/log(b), x)", "1/(x*log(b))")], [],
     dict(checkable=True, domains={"x": "positive", "b": "positive"}, constraints=["Ne(b, 1)"])),
    ("Logarithm", 13, [("log(243)/log(3)", "log(9)/log(3) + log(27)/log(3)", {"index_in_chain": 0}),
                       ("log(9)/log(3) + log(27)/log(3)", "5", {"index_in_chain": 1})], [],
     dict(checkable=True)),
    ("Logarithm", 69, [("Integral(log(x), x)", "x*log(x) - x + C")], [],
     dict(checkable=False, skip_reason="indefinite_integral")),
    ("Logarithm", 65, [("f(x*y)", "f(x) + f(y)")], ["f"],
     dict(checkable=False, skip_reason="functional_identity")),
    ("Logarithm", 3, [("y", "log(x)/log(b)")], [],
     dict(checkable=False, skip_reason="definition")),
    # ------------------------------------------------------------------ exponential function
    ("Exponential function", 17, [("exp(x + y)", "exp(x)*exp(y)")], [],
     dict(checkable=True, domains={"x": "real", "y": "real"})),
    ("Exponential function", 21, [("1/e**x", "e**(-x)")], [],
     dict(checkable=True, constants={"e": "E"}, domains={"x": "real"})),
    ("Exponential function", 24, [("b**x", "exp(x*log(b))")], [],
     dict(checkable=True, domains={"b": "positive", "x": "real"})),
    ("Exponential function", 26, [("log(e)", "1")], [],
     dict(checkable=True, constants={"e": "E"})),
    ("Exponential function", 25, [("e", "exp(1)")], [],
     dict(checkable=True, constants={"e": "E"})),
    ("Exponential function", 52, [("e**log(z)", "z")], [],
     dict(checkable=True, constants={"e": "E"}, domains={"z": "complex"}, constraints=["Ne(z, 0)"])),
    ("Exponential function", 56, [("e**(z + 2*i*k*pi)", "e**z")], [],
     dict(checkable=True, constants={"e": "E", "i": "I"}, domains={"z": "complex", "k": "integer"})),
    ("Exponential function", 59, [("e**(i*t)", "cos(t) + i*sin(t)")], [],
     dict(checkable=True, constants={"e": "E", "i": "I"}, domains={"t": "real"})),
    # ------------------------------------------------------------------ complex number
    ("Complex number", 2, [("z", "a + i*b", {"kind": "definition_like"})], [],
     dict(checkable=False, skip_reason="definition")),
    ("Complex number", 14, [("z*conjugate(z)", "(x + i*y)*(x - i*y)", {"index_in_chain": 0}),
                            ("(x + i*y)*(x - i*y)", "x**2 + y**2", {"index_in_chain": 1})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Complex number", 15, [("Abs(z)", "sqrt(x**2 + y**2)")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Complex number", 27, [("z_1*z_2", "r_1*r_2*(cos(phi_1 + phi_2) + i*sin(phi_1 + phi_2))")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Complex number", 29, [("(2 + i)*(3 + i)", "5 + 5*i")], [],
     dict(checkable=True, constants={"i": "I"})),
    ("Complex number", 30, [("pi/4", "atan(1/2) + atan(1/3)")], [],
     dict(checkable=True)),
    ("Complex number", 43, [("(cos(theta) + i*sin(theta))**n", "cos(n*theta) + i*sin(n*theta)")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"theta": "angle", "n": "integer"})),
    ("Complex number", 44, [("e**(i*theta)", "cos(theta) + i*sin(theta)")], [],
     dict(checkable=True, constants={"e": "E", "i": "I"}, domains={"theta": "angle"})),
    ("Complex number", 81, [("i**2 + 1", "0")], [],
     dict(checkable=True, constants={"i": "I"})),
    ("Complex number", 93, [("Abs(z)", "0", {"kind": "inequality", "relation": ">="})], [],
     dict(checkable=True, domains={"z": "complex"})),
    # ------------------------------------------------------------------ golden ratio
    ("Golden ratio", 7, [("varphi + 1", "varphi**2")], [],
     dict(checkable=True, constants={"varphi": "GoldenRatio"})),
    ("Golden ratio", 16, [("varphi**n", "varphi**(n - 1) + varphi**(n - 2)")], [],
     dict(checkable=True, constants={"varphi": "GoldenRatio"}, domains={"n": "real"})),
    ("Golden ratio", 3, [("varphi", "(1 + sqrt(5))/2")], [],
     dict(checkable=True, constants={"varphi": "GoldenRatio"})),
    ("Golden ratio", 21, [("Abs(xi - p/q)", "1/(sqrt(5)*q**2)", {"kind": "inequality", "relation": "<"})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Golden ratio", 26, [("F(n)", "(varphi**n - (-varphi)**(-n))/sqrt(5)", {"index_in_chain": 0})], ["F"],
     dict(checkable=True, constants={"varphi": "GoldenRatio", "F": "fibonacci"}, domains={"n": "nonneg_integer"})),
    # ------------------------------------------------------------------ Euler–Mascheroni constant
    ("Euler's constant", 7, [("gamma", "Sum(1/k - log(1 + 1/k), (k, 1, oo))")], [],
     dict(checkable=True, constants={"gamma": "EulerGamma"})),
    ("Euler's constant", 30, [("-gamma", "Subs(Derivative(Gamma(u), u), u, 1)", {"index_in_chain": 0}),
                              ("Subs(Derivative(Gamma(u), u), u, 1)", "polygamma(0, 1)", {"index_in_chain": 1})], [],
     dict(checkable=True, constants={"gamma": "EulerGamma"})),
    ("Euler's constant", 45, [("H_n", "log(n) + gamma + 1/(2*n) - 1/(12*n**2) + 1/(120*n**4) - varepsilon")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Euler's constant", 9, [("1/(2*(n + 1))", "gamma_n(0) - gamma", {"kind": "inequality", "relation": "<", "index_in_chain": 0}),
                             ("gamma_n(0) - gamma", "1/(2*n)", {"kind": "inequality", "relation": "<", "index_in_chain": 1})], ["gamma_n"],
     dict(checkable=False, skip_reason="has_undefined_function")),
    # ------------------------------------------------------------------ Euler's formula
    ("Euler's formula", 0, [("e**(i*x)", "cos(x) + i*sin(x)")], [],
     dict(checkable=True, constants={"e": "E", "i": "I"}, domains={"x": "real"})),
    ("Euler's formula", 18, [("1/(1 + x**2)", "(1/(1 - i*x) + 1/(1 + i*x))/2")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"x": "real"})),
    ("Euler's formula", 19, [("Integral(1/(1 + a*x), x)", "log(1 + a*x)/a + C")], [],
     dict(checkable=False, skip_reason="indefinite_integral")),
    ("Euler's formula", 42, [("log(z)", "log(Abs(z)) + i*varphi")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    # ------------------------------------------------------------------ factorial
    ("Factorial", 19, [("factorial(n)", "n*factorial(n - 1)")], [],
     dict(checkable=True, domains={"n": "positive_integer"})),
    ("Factorial", 23, [("factorial(0)", "1")], [],
     dict(checkable=True)),
    ("Factorial", 33, [("e**x", "Sum(x**n/factorial(n), (n, 0, oo))")], [],
     dict(checkable=True, constants={"e": "E"}, domains={"x": "real"})),
    ("Factorial", 71, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\sim"]})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Factorial", 60, [("log(factorial(n))/log(2)", "n*log(n)/log(2) - O(n)")], ["O"],
     dict(checkable=False, skip_reason="operator_notation")),
    # ------------------------------------------------------------------ inverse trigonometric functions
    ("Inverse trigonometric functions", 15, [("tan(asec(x))", "sqrt(x**2 - 1)")], [],
     dict(checkable=True, domains={"x": "real"}, constraints=["x >= 1"])),
    ("Inverse trigonometric functions", 55, [(None, None, {"status": "not_checkable", "kind": "other"})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    # ------------------------------------------------------------------ Fermat's little theorem
    ("Fermat's little theorem", 0, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\pmod"]})], [],
     dict(checkable=False, skip_reason="congruence")),
    ("Fermat's little theorem", 1, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\pmod"]})], [],
     dict(checkable=False, skip_reason="congruence")),
    # ------------------------------------------------------------------ hyperbolic functions
    ("Hyperbolic functions", 2, [("sinh(x)", "(e**x - e**(-x))/2", {"index_in_chain": 0, "kind": "definition_like"}),
                                 ("(e**x - e**(-x))/2", "(e**(2*x) - 1)/(2*e**x)", {"index_in_chain": 1})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"x": "real"})),
    ("Hyperbolic functions", 11, [("sinh(x)", "-i*sin(i*x)")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"x": "real"})),
    ("Hyperbolic functions", 35, [("cosh(t)", "e**(t**2/2)", {"kind": "inequality", "relation": "<="})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"t": "real"})),
    ("Hyperbolic functions", 0, [("i", "sqrt(-1)")], [],
     dict(checkable=True, constants={"i": "I"})),
    # ------------------------------------------------------------------ physics: kinetic energy
    ("Kinetic energy", 3, [("E_k", "m*v**2/2")], [],
     dict(checkable=False, skip_reason="definition")),
    ("Kinetic energy", 6, [("E_k", "12960", {"index_in_chain": 0})], [],
     dict(checkable=False, skip_reason="units")),
    ("Kinetic energy", 20, [("W", "m*a*(a*t**2/2)", {"index_in_chain": 0}),
                            ("m*a*(a*t**2/2)", "m*(a*t)**2/2", {"index_in_chain": 1}),
                            ("m*(a*t)**2/2", "m*v**2/2", {"index_in_chain": 2})], [],
     dict(checkable=False, skip_reason="definition")),
    ("Kinetic energy", 42, [("E**2", "(p*c)**2 + (m*c**2)**2")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Kinetic energy", 35, [("gamma", "1/sqrt(1 - v**2/c**2)")], [],
     dict(checkable=False, skip_reason="definition")),
    ("Kinetic energy", 21, [(None, None, {"status": "not_checkable", "kind": "other"})], [],
     dict(checkable=False, skip_reason="matrix_or_vector")),
    # ------------------------------------------------------------------ Pythagorean theorem
    ("Pythagorean theorem", 0, [("a**2 + b**2", "c**2")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Pythagorean theorem", 4, [("(b - a)**2 + 4*(a*b/2)", "(b - a)**2 + 2*a*b", {"index_in_chain": 0}),
                                ("(b - a)**2 + 2*a*b", "a**2 + b**2", {"index_in_chain": 1})], [],
     dict(checkable=True, domains={"a": "real", "b": "real"})),
    ("Pythagorean theorem", 20, [("1/(x*z)**2 + 1/(y*z)**2", "1/(x*y)**2")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    # ------------------------------------------------------------------ Cauchy's functional equation
    ("Cauchy's functional equation", 0, [("f(x + y)", "f(x) + f(y)")], ["f"],
     dict(checkable=False, skip_reason="functional_identity")),
    # ------------------------------------------------------------------ big O notation
    ("Big O notation", 93, [("f(x)", "O(x**10)")], ["f", "O"],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Big O notation", 92, [("Abs(6*x**4 - 2*x**3 + 5)", "13*x**4", {"kind": "inequality", "relation": "<="})], [],
     dict(checkable=True, domains={"x": "real"}, constraints=["x >= 1"])),
    # ------------------------------------------------------------------ expected value
    ("Expected value", 48, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\operatorname{E}"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Expected value", 41, [("log(1 - 1/2)", "-log(2)")], [],
     dict(checkable=True)),
]


# Held-out cases: labeled before the rules were ever run on them, never used for tuning.
HOLDOUT = [
    ("Geometric series", 16, [("S_n", "a*(1 - r**(n + 1))/(1 - r)")], [],
     dict(checkable=False, skip_reason="definition")),
    ("Error function", 0, [("erf(z)", "2/sqrt(pi)*Integral(e**(-t**2), (t, 0, z))", {"kind": "definition_like"})], [],
     dict(checkable=True, constants={"e": "E"}, domains={"z": "complex"})),
    ("Error function", 3, [("Derivative(erf(z), z)", "2/sqrt(pi)*e**(-z**2)")], [],
     dict(checkable=True, constants={"e": "E"}, domains={"z": "complex"})),
    ("Error function", 4, [("Integral(erf(z), z)", "z*erf(z) + e**(-z**2)/sqrt(pi) + C")], [],
     dict(checkable=False, skip_reason="indefinite_integral")),
    ("Error function", 17, [("erfc(z)", "1 - erf(z)")], [],
     dict(checkable=True, domains={"z": "complex"})),
    ("Error function", 18, [("erfi(z)", "-i*erf(i*z)")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"z": "complex"})),
    ("Error function", 45, [("erf(conjugate(z))", "conjugate(erf(z))")], [],
     dict(checkable=True, domains={"z": "complex"})),
    ("Error function", 58, [("erf(0)", "0")], [],
     dict(checkable=True)),
    ("Error function", 33, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\Pr"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Harmonic number", 6, [("H(n + 1)", "H(n) + 1/(n + 1)")], ["H"],
     dict(checkable=True, constants={"H": "harmonic"}, domains={"n": "nonneg_integer"})),
    ("Harmonic number", 8, [("Sum(H(k), (k, 1, n))", "(n + 1)*H(n) - n")], ["H"],
     dict(checkable=True, constants={"H": "harmonic"}, domains={"n": "nonneg_integer"})),
    ("Harmonic number", 10, [("Integral(log(y), (y, 0, x))", "x*log(x) - x")], [],
     dict(checkable=True, domains={"x": "positive"})),
    ("Harmonic number", 16, [("Integral(1/x, (x, 1, n + 1))", "log(n + 1)")], [],
     dict(checkable=True, domains={"n": "nonneg_integer"})),
    ("Harmonic number", 18, [("Limit(H(n) - log(n), n, oo)", "gamma")], ["H"],
     dict(checkable=True, constants={"H": "harmonic", "gamma": "EulerGamma"})),
    ("Harmonic number", 20, [("Sum(z**n*H(n), (n, 1, oo))", "-log(1 - z)/(1 - z)")], ["H"],
     dict(checkable=True, constants={"H": "harmonic"}, domains={"z": "complex"}, constraints=["Abs(z) < 1"])),
    ("Harmonic number", 13, [("H(n)", "Integral((1 - x**n)/(1 - x), (x, 0, 1))")], ["H"],
     dict(checkable=True, constants={"H": "harmonic"}, domains={"n": "nonneg_integer"})),
    ("Digamma function", 10, [("psi(z + 1)", "psi(z) + 1/z")], ["psi"],
     dict(checkable=True, constants={"psi": "digamma"}, domains={"z": "complex"}, constraints=[gp("z")])),
    ("Digamma function", 12, [("psi(n)", "H(n - 1) - gamma")], ["psi", "H"],
     dict(checkable=True, constants={"psi": "digamma", "H": "harmonic", "gamma": "EulerGamma"}, domains={"n": "positive_integer"})),
    ("Digamma function", 26, [("psi(z)", "1/Gamma(z)*Integral(t**(z - 1)*log(t)*e**(-t), (t, 0, oo))")], ["psi"],
     dict(checkable=True, constants={"psi": "digamma", "e": "E"}, domains={"z": "complex"}, constraints=["re(z) > 0"])),
    ("Digamma function", 8, [("Gamma(z + 1)", "z*Gamma(z)")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=[gp("z")])),
    ("Fibonacci sequence", 1, [("F_n", "F_n1 + F_n2")], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Fibonacci sequence", 5, [("F_n", "(varphi**n - psi**n)/(varphi - psi)", {"index_in_chain": 0})], [],
     dict(checkable=False, skip_reason="definition")),
    ("Fibonacci sequence", 7, [("psi", "-1/varphi")], [],
     dict(checkable=False, skip_reason="definition")),
    ("Fibonacci sequence", 30, [("Limit(F(n + 1)/F(n), n, oo)", "varphi")], ["F"],
     dict(checkable=True, constants={"F": "fibonacci", "varphi": "GoldenRatio"})),
    ("Fibonacci sequence", 34, [("Limit(F(n + m)/F(n), n, oo)", "varphi**m")], ["F"],
     dict(checkable=True, constants={"F": "fibonacci", "varphi": "GoldenRatio"}, domains={"m": "integer"})),
    ("Fibonacci sequence", 24, [("log(x)/log(varphi)", "log(x)/log(varphi)", {"index_in_chain": 0}),
                                ("log(x)/log(varphi)", "(log(x)/log(10))/(log(varphi)/log(10))", {"index_in_chain": 1})], [],
     dict(checkable=True, constants={"varphi": "GoldenRatio"}, domains={"x": "positive"})),
    ("Quadratic formula", 0, [("x", "(-b + sqrt(b**2 - 4*a*c))/(2*a)")], [],
     dict(checkable=False, skip_reason="plus_minus")),
    ("Quadratic formula", 14, [("x**2 + b/a*x + c/a", "(x - alpha)*(x - beta)", {"index_in_chain": 0}),
                               ("(x - alpha)*(x - beta)", "x**2 - (alpha + beta)*x + alpha*beta", {"index_in_chain": 1})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("Poisson distribution", 26, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\Pr"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Poisson distribution", 29, [(None, None, {"status": "not_checkable", "kind": "other", "has_unsupported": ["\\operatorname{E}"]})], [],
     dict(checkable=False, skip_reason="operator_notation")),
    ("Poisson distribution", 49, [("lambda_ - log(2)", "nu", {"kind": "inequality", "relation": "<="})], [],
     dict(checkable=False, skip_reason="statement_not_identity")),
    ("De Moivre's formula", 0, [("(cos(x) + i*sin(x))**n", "cos(n*x) + i*sin(n*x)")], [],
     dict(checkable=True, constants={"i": "I"}, domains={"x": "real", "n": "integer"})),
    ("De Moivre's formula", 10, [("(sqrt(3)/2 + i/2)**2", "1/2 + i*sqrt(3)/2")], [],
     dict(checkable=True, constants={"i": "I"})),
    ("De Moivre's formula", 12, [("(e**(i*x))**n", "e**(i*n*x)")], [],
     dict(checkable=True, constants={"e": "E", "i": "I"}, domains={"x": "real", "n": "integer"})),
    ("De Moivre's formula", 27, [("(cosh(x) + sinh(x))**n", "cosh(n*x) + sinh(n*x)")], [],
     dict(checkable=True, domains={"x": "real", "n": "real"})),
    ("De Moivre's formula", 19, [("z**(-1)", "conjugate(z)/Abs(z)**2")], [],
     dict(checkable=True, domains={"z": "complex"}, constraints=["Ne(z, 0)"])),
]

FILES = {
    "Gamma function": "Gamma_function", "Beta function": "Beta_function",
    "List of trigonometric identities": "List_of_trigonometric_identities",
    "Binomial coefficient": "Binomial_coefficient", "Riemann zeta function": "Riemann_zeta_function",
    "Normal distribution": "Normal_distribution", "Logarithm": "Logarithm",
    "Exponential function": "Exponential_function", "Complex number": "Complex_number",
    "Golden ratio": "Golden_ratio", "Euler's constant": "Euler–Mascheroni_constant",
    "Euler's formula": "Euler's_formula", "Factorial": "Factorial",
    "Inverse trigonometric functions": "Inverse_trigonometric_functions",
    "Fermat's little theorem": "Fermat's_little_theorem", "Hyperbolic functions": "Hyperbolic_functions",
    "Kinetic energy": "Kinetic_energy", "Pythagorean theorem": "Pythagorean_theorem",
    "Cauchy's functional equation": "Cauchy's_functional_equation", "Big O notation": "Big_O_notation",
    "Expected value": "Expected_value",
    "Geometric series": "Geometric_series", "Error function": "Error_function", "Harmonic number": "Harmonic_number",
    "Digamma function": "Digamma_function", "Fibonacci sequence": "Fibonacci_sequence",
    "Quadratic formula": "Quadratic_formula", "Poisson distribution": "Poisson_distribution",
    "De Moivre's formula": "De_Moivre's_formula",
}

# ------------------------------------------------------------------------- wikitext -> context

MATH = re.compile(r"<math[^>]*>(.*?)</math>", re.S)


def fetch(title_slug: str, cache: Path) -> dict:
    cache.mkdir(parents=True, exist_ok=True)
    f = cache / (urllib.parse.quote(title_slug, safe="") + ".json")
    if not f.exists():
        q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content|ids", "rvslots": "main",
                                    "format": "json", "formatversion": 2, "redirects": 1, "titles": title_slug})
        req = urllib.request.Request(f"https://en.wikipedia.org/w/api.php?{q}", headers={"User-Agent": UA})
        f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        time.sleep(0.3)
    d = json.loads(f.read_text())
    p = d["query"]["pages"][0]
    r = p["revisions"][0]
    return {"title": p["title"], "page_id": p["pageid"], "revision_id": r["revid"], "text": r["slots"]["main"]["content"]}


def strip(t: str) -> str:
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = MATH.sub(lambda m: m.group(1).strip(), t)
    t = re.sub(r"<sup>(.*?)</sup>", r"^\1", t)
    t = re.sub(r"<sub>(.*?)</sub>", r"_\1", t)
    t = re.sub(r"\{\{sup\|([^{}]*)\}\}", r"^\1", t)
    t = re.sub(r"\{\{sub\|([^{}]*)\}\}", r"_\1", t)
    for _ in range(4):
        t = re.sub(r"\{\{abs\|(?:1=)?([^{}]*)\}\}", r"|\1|", t)
        t = re.sub(r"\{\{(?:NumBlk2?)\|[^|{}]*\|([^{}]*?)\|[^|{}]*\}\}", r"\1", t)
        t = re.sub(r"\{\{bi\|[^{}]*?1=([^{}]*)\}\}", r"\1", t)
        t = re.sub(r"\{\{(?:math|mvar|nowrap|tmath|var)\|(?:1=)?([^{}]*)\}\}", r"\1", t)
        t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"\{\{[A-Za-z0-9 ]+\|(?:[^{}|]*\|)*?(?:1=)?(?=[^{}]*$)", "", t)
    t = re.sub(r"^(?:[^{}]*?\|)?\s*[0-9a-z∗*]*\s*\}\}", "", t)
    t = t.replace("{{", "").replace("}}", "")
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"'''?", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"={2,}([^=]+)={2,}", r"\1", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def section_at(text: str, pos: int) -> str:
    hs = [m.group(2).strip() for m in re.finditer(r"^(={2,})([^=].*?)\1\s*$", text[:pos], re.M)]
    return re.sub(r"<[^>]+>", "", hs[-1]).strip() if hs else ""


def formula_record(page: dict, index: int) -> dict:
    text = page["text"]
    for i, m in enumerate(MATH.finditer(text)):
        if i == index:
            tag = m.group(0)
            return {
                "formula_id": f"wiki:en:{page['page_id']}:{page['revision_id']}:{index}",
                "source": "wikipedia", "lang": "en", "page_title": page["title"], "page_id": page["page_id"],
                "revision_id": page["revision_id"],
                "url": f"https://en.wikipedia.org/w/index.php?oldid={page['revision_id']}",
                "section": section_at(text, m.start()), "index": index, "latex": m.group(1).strip(),
                "display": "display" in tag[:40] or text[max(0, m.start() - 2):m.start()].endswith(":"),
                "context_before": strip(text[max(0, m.start() - 1500):m.start()])[-400:],
                "context_after": strip(text[m.end():m.end() + 1500])[:400],
                "page_categories": [],
            }
    raise IndexError(f"{page['title']} has no <math> #{index}")


# ------------------------------------------------------------------------- parsed records

def to_srepr(s: str | None, funcs: list[str]) -> str | None:
    if s is None:
        return None
    loc = {n: sympy.Symbol(n) for n in ["e", "i", "j", "gamma", "beta", "alpha", "theta", "phi", "varphi", "zeta_s",
                                        "N", "S", "Q", "E", "C", "O", "xi", "mu", "sigma", "varepsilon", "lambda_",
                                        "E_k", "H_n", "W", "F", "L", "T", "X", "B", "u", "psi", "nu", "lambda_", "S_n", "F_n", "F_n1", "F_n2"]}
    loc.update({"Gamma": sympy.gamma, "Beta": sympy.beta, "zeta": sympy.zeta, "polygamma": sympy.polygamma,
                "binomial": sympy.binomial, "factorial": sympy.factorial, "Sum": sympy.Sum, "Product": sympy.Product,
                "Integral": sympy.Integral, "Limit": sympy.Limit, "Derivative": sympy.Derivative, "Subs": sympy.Subs,
                "oo": sympy.oo, "pi": sympy.pi, "erf": sympy.erf, "Abs": sympy.Abs, "conjugate": sympy.conjugate})
    for f in funcs:
        loc[f] = sympy.Function(f)
    return sympy.srepr(sympy.sympify(s, locals=loc, evaluate=False))


def build(cache: Path, cases=None) -> list[dict]:
    pages: dict[str, dict] = {}
    out = []
    for n, (title, idx, pieces, funcs, expect) in enumerate(CASES if cases is None else cases):
        if title not in pages:
            pages[title] = fetch(FILES[title], cache)
        f = formula_record(pages[title], idx)
        parsed = []
        for pc in pieces:
            lhs, rhs = pc[0], pc[1]
            extra = dict(pc[2]) if len(pc) > 2 else {}
            l, r = to_srepr(lhs, funcs), to_srepr(rhs, funcs)
            syms = set()
            for s in (l, r):
                if s:
                    e = eval(s, {"__builtins__": {}}, {k: getattr(sympy, k) for k in dir(sympy) if not k.startswith("_")})
                    syms |= {x.name for x in e.free_symbols}
            rec = {"formula_id": f["formula_id"], "status": extra.pop("status", "ok"),
                   "kind": extra.pop("kind", "chain" if "index_in_chain" in extra else "equation"),
                   "lhs": l, "rhs": r, "free_symbols": sorted(syms), "functions": list(funcs),
                   "translator": "fixture-hand", **extra}
            if rec["kind"] == "inequality" and not rec.get("relation"):
                rec["relation"] = "<="
            parsed.append(rec)
        exp = {"checkable": expect["checkable"], "skip_reason": expect.get("skip_reason"),
               "constants": expect.get("constants", {}), "domains": expect.get("domains", {}),
               "constraints": expect.get("constraints", [])}
        out.append({"case": f"{FILES[title]}#{idx}", "formula": f, "parsed": parsed, "expect": exp})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/tmp/formulaci-wiki-cache")
    ap.add_argument("--out", default=str(HERE / "cases.jsonl"))
    a = ap.parse_args()
    for cases, path in ((build(Path(a.cache)), Path(a.out)), (build(Path(a.cache), HOLDOUT), Path(a.out).with_name("holdout.jsonl"))):
        with open(path, "w") as fh:
            for c in cases:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"wrote {len(cases)} cases to {path}")
