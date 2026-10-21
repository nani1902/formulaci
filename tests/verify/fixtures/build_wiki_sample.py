"""Build tests/verify/fixtures/wiki_sample.jsonl: real Wikipedia formulas (ids and LaTeX from
tests/translate/fixtures/formulas.jsonl), hand-translated to Parsed + Semantics the way the
translate and semantics stages are expected to emit them.

    uv run python tests/verify/fixtures/build_wiki_sample.py
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp
from sympy import Abs, Integral, Product, Rational, Sum, beta, binomial, factorial, gamma, oo, pi, sin, sinh, sqrt

OUT = Path(__file__).resolve().parent / "wiki_sample.jsonl"
a, b, k, n, t, x, y, z = sp.symbols("a b k n t x y z")
i_ = sp.Symbol("i")
f = sp.Function("f")
ROWS = []


def add(fid, latex, links, expected, *, domains=None, constants=None, constraints=None, kind="equation",
        checkable=True, skip_reason=None, note=""):
    """links: list of (lhs, rhs) pairs; more than one makes a chain."""
    parsed = []
    for idx, (lhs, rhs) in enumerate(links):
        parsed.append({
            "formula_id": fid, "status": "ok", "kind": "chain" if len(links) > 1 else kind,
            "index_in_chain": idx if len(links) > 1 else None,
            "lhs": sp.srepr(lhs), "rhs": sp.srepr(rhs), "translator": "hand", "notes": latex,
        })
    ROWS.append({"formula_id": fid, "latex": latex, "expected": expected, "note": note, "parsed": parsed,
                 "semantics": {"formula_id": fid, "checkable": checkable, "skip_reason": skip_reason,
                               "domains": {k_: {"type": v} for k_, v in (domains or {}).items()},
                               "constants": constants or {}, "constraints": constraints or [],
                               "assumptions_source": ["hand"]}})


U = Rational(1, 2)
add("wiki:en:25804104:1379178075:0", r"1 + \cot^2\theta = \csc^2\theta",
    [(1 + sp.cot(x)**2, sp.csc(x)**2)], "PASS")
add("wiki:en:12316:1381182218:2", r"\Gamma(n) = (n-1)!", [(gamma(n), factorial(n - 1))], "PASS",
    domains={"n": "positive_integer"})
add("wiki:en:12316:1381182218:19", r"\Gamma(z) = \int_0^\infty t^{z-1} e^{-t}\, dt",
    [(gamma(z), Integral(t**(z - 1)*sp.exp(-t), (t, 0, oo)))], "PASS", domains={"z": "positive"})
add("wiki:en:12316:1381182218:59", r"\Gamma(1-z) \Gamma(z) = \frac{\pi}{\sin \pi z}, \qquad z \not\in \Z",
    [(gamma(1 - z)*gamma(z), pi/sin(pi*z))], "PASS")
add("wiki:en:12316:1381182218:61", r"\Gamma(z) \Gamma\left(z + \frac12\right) = 2^{1-2z} \, \sqrt{\pi} \, \Gamma(2z).",
    [(gamma(z)*gamma(z + U), 2**(1 - 2*z)*sqrt(pi)*gamma(2*z))], "PASS", domains={"z": "positive"})
add("wiki:en:12316:1381182218:62", r"\Gamma(z) = \frac1z \prod_{n=1}^{\infty} \frac{(1+1/n)^z}{1 + z/n}",
    [(gamma(z), Product((1 + 1/n)**z/(1 + z/n), (n, 1, oo))/z)], "PASS", domains={"z": "positive"})
add("wiki:en:12316:1381182218:86", r"\frac{\Gamma^2(z)}{\Gamma (2z)}=\int_0^1 t^{z-1}(1-t)^{z-1} \, dt.",
    [(gamma(z)**2/gamma(2*z), Integral(t**(z - 1)*(1 - t)**(z - 1), (t, 0, 1)))], "PASS", domains={"z": "positive"})
add("wiki:en:12316:1381182218:92", r"2^{2z-1}\Gamma^2(z)=\Gamma (2z)\Beta \left(\frac{1}{2},z\right).",
    [(2**(2*z - 1)*gamma(z)**2, gamma(2*z)*beta(U, z))], "PASS", domains={"z": "positive"})
add("wiki:en:12316:1381182218:97", r"|\Gamma(a+bi)|^2 = |\Gamma(a)|^2 \prod_{k=0}^\infty \frac{1}{1+\frac{b^2}{(a+k)^2}}",
    [(Abs(gamma(a + b*i_))**2, Abs(gamma(a))**2*Product(1/(1 + b**2/(a + k)**2), (k, 0, oo)))], "PASS",
    domains={"a": "positive", "b": "real"}, constants={"i": "I"})
add("wiki:en:12316:1381182218:101", r"\Gamma(bi)\Gamma(-bi)=\frac{\pi}{-bi\sin \pi bi}=\frac{\pi}{b\sinh \pi b}",
    [(gamma(b*i_)*gamma(-b*i_), pi/(-b*i_*sin(pi*b*i_))), (pi/(-b*i_*sin(pi*b*i_)), pi/(b*sinh(pi*b)))],
    "PASS", domains={"b": "real"}, constants={"i": "I"})
add("wiki:en:12316:1381182218:104", r"\Gamma\left(\tfrac12\right)=\sqrt{\pi},", [(gamma(U, evaluate=False), sqrt(pi))], "PASS")
add("wiki:en:4668:1376065730:4", r"\tbinom{4}{2} =\tfrac{4\times 3}{2\times1} = \tfrac{4!}{2!2!} = 6",
    [(binomial(4, 2, evaluate=False), Rational(12, 2)), (Rational(12, 2), factorial(4)/(factorial(2)*factorial(2))),
     (factorial(4)/(factorial(2)*factorial(2)), sp.Integer(6))], "PASS")
add("wiki:en:4668:1376065730:6", r"\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k} .",
    [(binomial(n, k), binomial(n - 1, k - 1) + binomial(n - 1, k))], "PASS",
    domains={"n": "positive_integer", "k": "positive_integer"})
add("wiki:en:4668:1376065730:12", r"(x+y)^n=\sum_{k=0}^n\binom nk x^ky^{n-k}",
    [((x + y)**n, Sum(binomial(n, k)*x**k*y**(n - k), (k, 0, n)))], "PASS", domains={"n": "nonneg_integer"})
add("wiki:en:25804104:1379178075:75", r"\alpha = \frac{\pi}{4}", [(a, pi/4)], "INCONCLUSIVE",
    note="assignment of a symbol, not an identity")
add("wiki:en:12316:1381182218:16", r"y = \log f(x)", [(y, sp.log(f(x)))], "SKIP")
add("wiki:en:12316:1381182218:68", r"\int_{C_R}\frac{e^{az}}{1+e^z}\, dz=-2\pi ie^{a\pi i}.", [(a, a)], "SKIP",
    checkable=False, skip_reason="operator_notation", note="contour integral")


def main() -> None:
    with OUT.open("w") as fh:
        for row in ROWS:
            fh.write(json.dumps(row) + "\n")
    print(f"wrote {len(ROWS)} rows to {OUT}")


if __name__ == "__main__":
    main()
