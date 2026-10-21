"""Regression tests from the human review of real FAILs (data/findings/reviews.jsonl, 2026-10-21).

`fixtures/review_false_positives.jsonl` holds the 110 formulas whose false FAIL was blamed on the
translator ([translator_misread_other], [superscript_is_label], [mixed_number_or_juxtaposition]).
Each must now be refused (no ok record for the reviewed relation) or read exactly as recorded in
`check_reviews.ACCEPTED_READINGS` (readings checked by hand against the reviewer's note).
"""
import json
from collections import Counter
from pathlib import Path

import sympy as sp

from formulaci.schemas import Formula
from formulaci.translate.check_reviews import classify

from .conftest import sides, tr

FIXTURE = Path(__file__).parent / "fixtures" / "review_false_positives.jsonl"
# |cd| = |cs| + |sd| (segment lengths between points c, s, d): indistinguishable from |c*d|; known gap.
KNOWN_UNRESOLVED = {"wiki:en:17553:1380896199:115"}


def test_all_reviewed_translator_false_positives_resolved():
    outcomes = Counter()
    bad = []
    for line in FIXTURE.read_text().splitlines():
        item = json.loads(line)
        f = Formula.model_validate(item["formula"])
        outcome, detail = classify({"formula_id": f.formula_id, "index_in_chain": item["index_in_chain"]}, f)
        outcomes[outcome] += 1
        if outcome not in ("refused", "fixed") and f.formula_id not in KNOWN_UNRESOLVED:
            bad.append((f.formula_id, f.latex[:80], detail[:120]))
    assert sum(outcomes.values()) == 110
    assert not bad, bad
    assert outcomes["refused"] + outcomes["fixed"] >= 109


def unsup(latex, **kw):
    return {u for r in tr(latex, **kw) for u in r.has_unsupported}


def test_named_operators_and_word_symbols():
    assert "named_operator" in unsup(r"\operatorname{vers}\theta = 1 - \cos\theta")
    assert "named_operator" in unsup(r"\operatorname{cis} \theta = e^{i\theta}")
    assert "word_symbol" in unsup(r"\lim_{\beta \to 0} \text{median} = 1")
    L, R, _ = sides(r"{\rm cas}(x)=\cos(x)+\sin(x)")
    assert L == sp.Function("cas")(sp.Symbol("x"))
    L, _, _ = sides(r"\mathrm{log1p}(x) = \log(1+x)")
    assert L == sp.Function("log1p")(sp.Symbol("x"))
    L, _, _ = sides(r"\text{Ti}_{2}(x) = 0")
    assert L == sp.Function("Ti_2")(sp.Symbol("x"))


def test_function_application_variants():
    x, T = sp.symbols("x T")
    L, _, _ = sides(r"e_s(T)= 6.1094 \exp(T)")
    assert L == sp.Function("e_s")(T)
    L, _, _ = sides(r"\theta_4\bigl[\exp(-\pi)\bigr] = 1")
    assert L == sp.Function("theta_4")(sp.exp(-sp.pi))
    L, _, _ = sides(r"\tau[A] < 0")
    assert L == sp.Function("tau")(sp.Symbol("A"))
    assert "ambiguous_application" in unsup(r"p(2n+1) = \sum_{k=0}^{n} p(n - k)q(2k + 1)")
    assert "ambiguous_application" in unsup(r"E = E(R/\mathfrak{p})")
    L, _, _ = sides(r"\gcd(a,b,c) = 3")  # sympy's gcd of symbols would collapse to 1
    assert L == sp.Function("gcd")(*sp.symbols("a b c"))
    L, _, _ = sides(r"q\gamma(a,q) = 1")  # Euler-Lehmer constant, not the incomplete gamma function
    assert L == sp.Symbol("q") * sp.Function("gamma")(*sp.symbols("a q"))
    L, _, _ = sides(r"\gamma(s,x) = 1", before="the lower incomplete gamma function")
    assert L == sp.lowergamma(*sp.symbols("s x"))


def test_conjugates():
    z, c = sp.symbols("z c")
    L, R, _ = sides(r"|z|^2 = z\overline{z}")
    assert R == z * sp.conjugate(z)
    L, R, _ = sides(r"\mathrm{Re}(z)=\frac{z+\bar z}{2}")
    assert R == (z + sp.conjugate(z)) / 2
    L, R, _ = sides(r"|z - c|^2 = z\overline{z} - \overline{c}z - c\overline{z} + c\overline{c}", before="complex numbers")
    assert R.has(sp.conjugate(c))
    # a bar next to a plain x without complex context: a mean or a conjugate? refuse
    assert "ambiguous_bar" in unsup(r"\bar x - x = 0")
    # a bar alone is just a named symbol (sample mean)
    L, _, _ = sides(r"\bar x = 2")
    assert L == sp.Symbol("x_bar")


def test_residue_symbols_and_multisets():
    assert "residue_symbol" in unsup(r"\left(\frac {7}{11}\right) = -1", before="the Legendre symbol")
    assert "residue_symbol" in unsup(r"\Bigg[\frac{\pi}{\theta}\Bigg] = 1")
    assert "multiset_coefficient" in unsup(r"\left(\!\!\binom{4}{3}\!\!\right) = 20")
    L, _, _ = sides(r"\left(\frac{1}{2}\right)^2 = \frac14", before="the Legendre symbol")  # a power: a fraction
    assert L == sp.Rational(1, 4)


def test_differentials_and_increments():
    assert "differential_form" in unsup(r"\frac{dc}{c} = \frac{dy ds}{rdx}")
    assert "differential_form" in unsup(r"\frac{dM^2}{M^2} = \frac{1 + \gamma M^2}{1 - M^2}\frac{dT_0}{T_0}")
    L, R, _ = sides(r"\frac{\Delta f}{f} = \frac{\Delta a}{a}")
    assert L == sp.Symbol("Delta_f") / sp.Symbol("f")


def test_function_argument_scope_review():
    th, ph, al, k = sp.symbols("theta phi alpha k")
    L, R, _ = sides(r"\sin \theta + \sin \varphi = 2 \sin \tfrac12 (\theta + \varphi)\, \cos\tfrac12(\theta - \varphi)")
    assert R == 2 * sp.sin((th + ph) / 2) * sp.cos((th - ph) / 2)
    assert "ambiguous_function_argument" in unsup(r"\sum_{k=1}^n \cos (2k -1)\alpha = 1")
    L, R, _ = sides(r"\cos(a x) = \tfrac{e^{i a x} + e^{-i a x} }{2}")
    e, i, a, x = sp.symbols("e i a x")
    assert R == (e ** (i * a * x) + e ** (-i * a * x)) / 2


def test_superscript_labels():
    for latex in [r"X^{(0)} = 0", r"F = F^H + F^D", r"A^\mathrm{g} A A^\mathrm{g}= A^\mathrm{g}",
                  r"\frac{G}{N} = \frac{G^\circ}{N}", r"(fg)^{(n)}=\sum_{k=0}^n {n \choose k} f^{(n-k)} g^{(k)}",
                  r"h^{i}_{k} = h^{i-1}_{k} - h^{i-1}_{k-1}", r"C_3^0 = 3", r"E^{\infty} = E^2", r"a^\omega b=a^\omega",
                  r"H_{\rm v}^{px} = \frac{p}{x}", r"{\beta_j}^{k+1} = {\beta_j}^k+\Delta \beta_j"]:
        assert "superscript_label" in unsup(latex), latex
    assert "inverse_or_reciprocal" in unsup(r"U^{-1} = U")
    # ordinary powers stay powers
    x, n = sp.symbols("x n")
    for latex, want in [(r"x^n = 1", x**n), (r"x^0 = 1", sp.Integer(1)), (r"2^n = 1", 2**n),
                        (r"30^\circ = 1", sp.pi / 6), (r"(x+1)^2 = 1", (x + 1) ** 2)]:
        L, _, r = sides(latex)
        assert r.status == "ok" and L == want, latex


def test_mixed_numbers_and_juxtaposition():
    assert "mixed_number" in unsup(r"3\frac{1}{2}=3+\frac{1}{2}")
    assert "mixed_number" in unsup(r"{}314\frac{64}{625}<100 \times \pi")
    assert "p_function" in unsup(r"\mathrm{p} K = -\log_{10} K")
    assert "juxtaposition_application" in unsup(r"\operatorname{exp} \ b\ n\ f\ x = n\ b\ f\ x")
    assert "letter_digit" in unsup(r"h2<h1")
    L, _, _ = sides(r"2\frac{\pi}{3} = 1")  # not a mixed number: a product
    assert L == 2 * sp.pi / 3
    L, _, _ = sides(r"\sum_{k=0}^{n} (-1)^k 2^{-n} = 1")  # digit after a superscript letter is fine
    assert isinstance(L, sp.Sum)


def test_lists_with_ellipsis_are_not_equations():
    rs = tr(r"i=1,\dots,n")
    assert all(r.status != "ok" for r in rs)


def test_second_pass_keeps_ordinary_math():
    """Readings that the second-pass guards must NOT refuse (found by sampling real data)."""
    s, t, k, c, n, x, N, L, i, p = sp.symbols("s t k c n x N L i p")
    a = sp.Function("a")
    cases = [
        (r"v = s(1-t)", s * (1 - t)),                                     # one bracket after a letter: product
        (r"q = 1+k_3(c-1)", 1 + sp.Symbol("k_3") * (c - 1)),              # subscripted coefficient
        (r"y = \sum_{n=0}^{3} a_n(x-c)^n", sp.Sum(a(n) * (x - c) ** n, (n, 0, 3))),  # Taylor coefficients
        (r"t = N\left(\frac{1}{s+1}+1\right) + \frac{N}{s+1}", N * (1 + 1 / (s + 1)) + N / (s + 1)),
        (r"y = n 2^{n-1}", n * 2 ** (n - 1)),                             # spaced letter and digit
        (r"y = \hat x^n", sp.Symbol("x_hat") ** n),                        # styled name is not "subscripted"
        (r"y = \sum_{i=1}^p L^i", sp.Sum(L**i, (i, 1, p))),               # lag operator powers
        (r"y = \int \cos (\ln x)\,dx", sp.Integral(sp.cos(sp.log(x)), x)),  # differential after trig(...)
        (r"y = V_{w2} - V_{w1}", sp.Symbol("V_w2") - sp.Symbol("V_w1")),     # letter+digit subscripts are labels
        (r"y = U_\mathrm{el}(x)", sp.Function("U_el")(x)),                  # roman-subscripted name applied
        (r"y = Q_j, \quad j = 1, \ldots, m", sp.Symbol("Q_j")),              # index range is a condition
        (r"y = {\exp}\bigl(2\pi/5 \bigr)", sp.exp(2 * sp.pi / 5)),
        (r"y = \operatorname{sech} (t) e^{t}", sp.sech(t) * sp.Symbol("e") ** t),
    ]
    for latex, want in cases:
        _, R, r = sides(latex)
        assert r.status == "ok" and R == want, (latex, r.has_unsupported, R)
    assert "superscript_label" in unsup(r"Y_{7}^{-7}(\theta,\varphi) = 1")  # index, not a power


def test_equation_numbers_and_variational_derivatives():
    L, _, r = sides(r"(16)\quad B_{21} = 2")
    assert L == sp.Symbol("B_21") and "pre:equation_number" in (r.notes or "")
    L, _, _ = sides(r"(2)(3) = 6")  # not followed by spacing: arithmetic
    assert L == 6
    assert "variational_derivative" in unsup(r"\frac{\delta^2 u}{\delta \theta^2} = 1")
