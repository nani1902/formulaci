"""Build tests/verify/fixtures/corpus.jsonl: Parsed + Semantics pairs with an expected verdict.

    uv run python tests/verify/fixtures/build_corpus.py

Categories: `true` (must PASS), `mutated` (must FAIL; tagged with the mutation and the true
identity it came from), `branch` (branch-cut traps, must be INCONCLUSIVE), `special` (other
policy rules: definitions, integer-only identities, measure-zero failures, SKIPs).
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp
from sympy import (Abs, Derivative, Integral, Product, Rational, Sum, atan, acos, asin, beta, binomial, cos, cosh,
                   cot, csc, exp, factorial, floor, gamma, log, oo, pi, sec, sin, sinh, sqrt, tan, tanh)

OUT = Path(__file__).resolve().parent / "corpus.jsonl"

a, b, c, d, n, k, m, r, t, x, y, z, C = sp.symbols("a b c d n k m r t x y z C")
e_, i_ = sp.Symbol("e"), sp.Symbol("i")
f = sp.Function("f")

ROWS: list[dict] = []


def add(cid, category, lhs, rhs, expected, *, domains=None, constants=None, constraints=None,
        relation=None, kind=None, mutation=None, source=None, checkable=True, skip_reason=None, note="",
        notes=None, hints=None):
    kind = kind or ("inequality" if relation not in (None, "=") else "equation")
    fid = f"fixture:verify:{cid}"
    ROWS.append({
        "id": cid, "category": category, "expected": expected, "mutation": mutation, "source": source,
        "note": note,
        "parsed": {"formula_id": fid, "status": "ok", "kind": kind, "relation": relation,
                   "lhs": sp.srepr(lhs), "rhs": sp.srepr(rhs),
                   "free_symbols": sorted(s.name for s in (sp.sympify(lhs).free_symbols | sp.sympify(rhs).free_symbols)),
                   "translator": "fixture", "notes": notes},
        "semantics": {"formula_id": fid, "checkable": checkable, "skip_reason": skip_reason,
                      "domains": {k_: (v if isinstance(v, dict) else {"type": v}) for k_, v in (domains or {}).items()},
                      "constants": constants or {}, "constraints": constraints or [],
                      "assumptions_source": ["fixture"] + list(hints or [])},
    })


def pair(cid, lhs, rhs, mlhs, mrhs, mutation, **kw):
    """A true identity and its mutated twin with the same semantics."""
    add(cid, "true", lhs, rhs, "PASS", **kw)
    add(f"{cid}__{mutation}", "mutated", mlhs, mrhs, "FAIL", mutation=mutation, source=cid, **kw)


def known_miss(why: str) -> None:
    """Mark the last mutated row as a documented miss: the policy correctly refuses to FAIL it."""
    ROWS[-1]["expected"] = "INCONCLUSIVE"
    ROWS[-1]["note"] = f"known miss: {why}"


E_CONST = {"e": "E"}
POS2 = {"x": "positive", "y": "positive"}
NN = {"n": "nonneg_integer"}

# ---- trigonometric
pair("pythagorean", sin(x)**2 + cos(x)**2, 1, sin(x)**2 + cos(x)**2, 2, "wrong_constant")
pair("sin_double", sin(2*x), 2*sin(x)*cos(x), sin(2*x), -2*sin(x)*cos(x), "sign_flip")
pair("cos_double", cos(2*x), cos(x)**2 - sin(x)**2, cos(2*x), cos(x)**2 + sin(x)**2, "sign_flip")
pair("tan_sum", tan(x + y), (tan(x) + tan(y))/(1 - tan(x)*tan(y)),
     tan(x + y), (tan(x) + tan(y))/(1 + tan(x)*tan(y)), "sign_flip")
pair("sin_sum", sin(x + y), sin(x)*cos(y) + cos(x)*sin(y),
     sin(x + y), sin(x)*cos(y) - cos(x)*sin(y), "sign_flip")
pair("cot_csc", 1 + cot(x)**2, csc(x)**2, 1 + cot(x)**2, sec(x)**2, "wrong_function")
pair("sin_triple", sin(3*x), 3*sin(x) - 4*sin(x)**3, sin(3*x), 3*sin(x) - 4*sin(x)**2, "exponent_off_by_one")
pair("cos_diff", cos(x) - cos(y), -2*sin((x + y)/2)*sin((x - y)/2),
     cos(x) - cos(y), -2*sin((x + y)/2)*cos((x - y)/2), "wrong_function")
pair("product_to_sum", sin(x)*cos(y), (sin(x + y) + sin(x - y))/2,
     sin(x)*cos(y), (sin(x + y) + sin(y - x))/2, "swapped_symbols")

# ---- hyperbolic
pair("hyp_pythagorean", cosh(x)**2 - sinh(x)**2, 1, cosh(x)**2 + sinh(x)**2, 1, "sign_flip")
pair("sinh_double", sinh(2*x), 2*sinh(x)*cosh(x), sinh(2*x), sinh(x)*cosh(x), "dropped_factor")
pair("cosh_sum", cosh(x + y), cosh(x)*cosh(y) + sinh(x)*sinh(y),
     cosh(x + y), cosh(x)*cosh(y) - sinh(x)*sinh(y), "sign_flip")
pair("tanh_exp", tanh(x), (e_**(2*x) - 1)/(e_**(2*x) + 1),
     tanh(x), (e_**x - 1)/(e_**x + 1), "dropped_factor", constants=E_CONST)
known_miss("both sides tend to 1: the `large` regime agrees to 1e-8, so not every regime fails")
pair("hyp_complex", cosh(z)**2 - sinh(z)**2, 1, cosh(z)**2 - sinh(z)**2, -1, "wrong_constant",
     domains={"z": "complex"})

# ---- log / exp / powers
pair("log_product", log(x*y), log(x) + log(y), log(x*y), log(x) - log(y), "sign_flip", domains=POS2)
pair("exp_sum", exp(x + y), exp(x)*exp(y), exp(x + y), exp(x) + exp(y), "wrong_operator")
pair("log_power", log(x**y), y*log(x), log(x**y), (y + 1)*log(x), "off_by_one",
     domains={"x": "positive", "y": "real"})
pair("euler_formula", e_**(i_*x), cos(x) + i_*sin(x), e_**(i_*x), cos(x) - i_*sin(x), "sign_flip",
     constants={"e": "E", "i": "I"})
pair("power_product", x**y*x**z, x**(y + z), x**y*x**z, y**(x + z), "swapped_symbols",
     domains={"x": "positive", "y": "positive", "z": "real"})
pair("power_exp_log", x**y, exp(y*log(x)), x**y, exp(x*log(y)), "swapped_symbols", domains=POS2)

# ---- gamma / beta
pair("gamma_recurrence", gamma(x + 1), x*gamma(x), gamma(x + 1), (x + 1)*gamma(x), "off_by_one")
pair("gamma_reflection", gamma(x)*gamma(1 - x), pi/sin(pi*x), gamma(x)*gamma(1 - x), pi/cos(pi*x),
     "wrong_function")
pair("gamma_duplication", gamma(x)*gamma(x + Rational(1, 2)), 2**(1 - 2*x)*sqrt(pi)*gamma(2*x),
     gamma(x)*gamma(x + Rational(1, 2)), 2**(1 - x)*sqrt(pi)*gamma(2*x), "dropped_factor",
     domains={"x": "positive"})
pair("beta_gamma", beta(x, y), gamma(x)*gamma(y)/gamma(x + y), beta(x, y), gamma(x)*gamma(y)/gamma(x + y + 1),
     "off_by_one", domains=POS2)
pair("factorial_gamma", factorial(n), gamma(n + 1), factorial(n), gamma(n), "off_by_one", domains=NN)

# ---- binomial / finite sums
pair("binomial_row_sum", Sum(binomial(n, k), (k, 0, n)), 2**n, Sum(binomial(n, k), (k, 0, n)), 2**(n + 1),
     "exponent_off_by_one", domains=NN)
pair("sum_integers", Sum(k, (k, 1, n)), n*(n + 1)/2, Sum(k, (k, 1, n)), n*(n - 1)/2 + 1, "sign_flip",
     domains=NN)
pair("sum_squares", Sum(k**2, (k, 1, n)), n*(n + 1)*(2*n + 1)/6, Sum(k**2, (k, 1, n)), n*(n + 1)*(2*n + 3)/6,
     "wrong_constant", domains=NN)
pair("sum_cubes", Sum(k**3, (k, 1, n)), (n*(n + 1)/2)**2, Sum(k**3, (k, 1, n)), (n*(n + 1)/2)**3,
     "exponent_off_by_one", domains=NN)
pair("sum_k_binomial", Sum(k*binomial(n, k), (k, 0, n)), n*2**(n - 1), Sum(k*binomial(n, k), (k, 0, n)),
     n*2**n, "exponent_off_by_one", domains={"n": "positive_integer"})
pair("vandermonde", Sum(binomial(m, k)*binomial(n, r - k), (k, 0, r)), binomial(m + n, r),
     Sum(binomial(m, k)*binomial(n, r - k), (k, 0, r)), binomial(m + n, r + 1), "off_by_one",
     domains={"m": "positive_integer", "n": "positive_integer", "r": "positive_integer"},
     constraints=["r <= m + n - 1"])
pair("pascal", binomial(n, k), binomial(n - 1, k - 1) + binomial(n - 1, k),
     binomial(n, k), binomial(n - 1, k - 1) + binomial(n - 1, k + 1), "off_by_one",
     domains={"n": "positive_integer", "k": "positive_integer"}, constraints=["k <= n - 1"])
pair("geometric_finite", Sum(x**k, (k, 0, n)), (1 - x**(n + 1))/(1 - x),
     Sum(x**k, (k, 0, n - 1)), (1 - x**(n + 1))/(1 - x), "off_by_one_bound",
     domains={"n": "nonneg_integer", "x": "real"}, constraints=["Ne(x, 1)"])
pair("telescoping", Sum(1/(k*(k + 1)), (k, 1, n)), 1 - 1/(n + 1), Sum(1/(k*(k + 1)), (k, 1, n)), 1 - 1/n,
     "off_by_one", domains={"n": "positive_integer"})
pair("finite_product_factorial", Product(k, (k, 1, n)), factorial(n), Product(k, (k, 1, n)), factorial(n + 1),
     "off_by_one", domains=NN)

# ---- infinite series / products (constants and functions)
pair("geometric_series", Sum(x**k, (k, 0, oo)), 1/(1 - x), Sum(x**k, (k, 0, oo)), 1/(1 + x), "sign_flip",
     constraints=["Abs(x) < 1"])
pair("exp_series", Sum(x**k/factorial(k), (k, 0, oo)), exp(x), Sum(x**k/factorial(k), (k, 1, oo)), exp(x),
     "off_by_one_bound")
known_miss("exp(x) - 1 vs exp(x): relative difference e^-x passes in the `large` regime")
pair("basel", Sum(1/k**2, (k, 1, oo)), pi**2/6, Sum(1/k**2, (k, 1, oo)), pi**2/8, "wrong_constant")
pair("leibniz", Sum((-1)**k/(2*k + 1), (k, 0, oo)), pi/4, Sum((-1)**k/(2*k + 1), (k, 0, oo)), pi/2,
     "wrong_constant")
pair("wallis_like_product", Product(1 - 1/k**2, (k, 2, oo)), Rational(1, 2),
     Product(1 - 1/k**2, (k, 2, oo)), Rational(1, 3), "wrong_constant")

# ---- integrals
pair("gaussian_integral", Integral(exp(-t**2), (t, -oo, oo)), sqrt(pi),
     Integral(exp(-t**2), (t, -oo, oo)), pi, "dropped_factor")
pair("gamma_integral", Integral(t**(x - 1)*exp(-t), (t, 0, oo)), gamma(x),
     Integral(t**x*exp(-t), (t, 0, oo)), gamma(x), "exponent_off_by_one", domains={"x": "positive"})
pair("atan_integral", Integral(1/(1 + t**2), (t, 0, x)), atan(x), Integral(1/(1 + t**2), (t, 0, x)), 2*atan(x),
     "wrong_constant")
pair("power_integral", Integral(t**x, (t, 0, 1)), 1/(x + 1), Integral(t**x, (t, 0, 1)), 1/x, "off_by_one",
     domains={"x": "positive"})
pair("log_integral", Integral(log(t), (t, 1, x)), x*log(x) - x + 1, Integral(log(t), (t, 1, x)), x*log(x) - x,
     "dropped_term", domains={"x": "positive"})
pair("indefinite_cos", Integral(cos(x), x), sin(x) + C, Integral(cos(x), x), -sin(x) + C, "sign_flip")

# ---- derivatives
pair("derivative_sin_squared", Derivative(sin(x)**2, x), sin(2*x), Derivative(sin(x)**2, x), cos(2*x),
     "wrong_function")
pair("derivative_x_to_x", Derivative(x**x, x), x**x*(log(x) + 1), Derivative(x**x, x), x**x*log(x),
     "dropped_term", domains={"x": "positive"})
pair("derivative_atan", Derivative(atan(x), x), 1/(1 + x**2), Derivative(atan(x), x), 1/(1 - x**2), "sign_flip")
pair("atan_reciprocal", atan(x) + atan(1/x), pi/2, atan(x) + atan(1/x), pi, "wrong_constant",
     domains={"x": "positive"})

# ---- inequalities (checked directionally)
pair("am_gm", (a + b)/2, sqrt(a*b), (a + b)/2, sqrt(a*b), "flipped_direction",
     domains={"a": "positive", "b": "positive"}, relation=">=")
ROWS[-1]["parsed"]["relation"] = "<="  # the mutated twin flips the direction
pair("bernoulli", (1 + x)**n, 1 + n*x, (1 + x)**n, 1 + n*x, "flipped_direction",
     domains={"x": {"type": "real", "lower": -1}, "n": {"type": "positive_integer", "lower": 2}}, relation=">=")
ROWS[-1]["parsed"]["relation"] = "<="
ROWS[-1]["semantics"]["constraints"] = ["Ne(x, 0)"]
ROWS[-2]["semantics"]["constraints"] = ["Ne(x, 0)"]
pair("cauchy_schwarz_2d", (a*c + b*d)**2, (a**2 + b**2)*(c**2 + d**2), (a*c + b*d)**2,
     (a**2 + b**2)*(c**2 + d**2), "flipped_direction", relation="<=")
ROWS[-1]["parsed"]["relation"] = ">="
pair("exp_tangent_line", exp(x), 1 + x, exp(x), 1 + x, "flipped_direction", relation=">=")
ROWS[-1]["parsed"]["relation"] = "<="
pair("log_tangent_line", log(x), x - 1, log(x), x - 1, "flipped_direction", relation="<=",
     domains={"x": "positive"})
ROWS[-1]["parsed"]["relation"] = ">="
add("triangle_inequality", "true", Abs(x + y), Abs(x) + Abs(y), "PASS", relation="<=")

# ---- branch-cut traps: true on the principal branch for positive reals, fail off it
add("trap_sqrt_product", "branch", sqrt(x*y), sqrt(x)*sqrt(y), "INCONCLUSIVE")
add("trap_sqrt_square", "branch", sqrt(x**2), x, "INCONCLUSIVE")
add("trap_atan_reciprocal", "branch", atan(x) + atan(1/x), pi/2, "INCONCLUSIVE")
add("trap_asin_sin", "branch", asin(sin(x)), x, "INCONCLUSIVE")
add("trap_acos_cos", "branch", acos(cos(x)), x, "INCONCLUSIVE")
add("trap_atan_tan", "branch", atan(tan(x)), x, "INCONCLUSIVE")
add("trap_sqrt_perfect_square", "branch", sqrt(x**2 + 2*x + 1), x + 1, "INCONCLUSIVE")
add("trap_log_product_complex", "branch", log(x*y), log(x) + log(y), "INCONCLUSIVE",
    domains={"x": "complex", "y": "complex"})
add("trap_log_quotient_complex", "branch", log(x/y), log(x) - log(y), "INCONCLUSIVE",
    domains={"x": "complex", "y": "complex"})
add("trap_log_square_complex", "branch", log(z**2), 2*log(z), "INCONCLUSIVE", domains={"z": "complex"})
add("trap_cube_root_complex", "branch", (z**3)**Rational(1, 3), z, "INCONCLUSIVE", domains={"z": "complex"})
add("trap_sqrt_quotient_complex", "branch", sqrt(x)/sqrt(y), sqrt(x/y), "INCONCLUSIVE",
    domains={"x": "complex", "y": "complex"})
add("trap_power_product_complex", "branch", (x*y)**a, x**a*y**a, "INCONCLUSIVE",
    domains={"x": "complex", "y": "complex", "a": "real"})
add("trap_power_of_power_complex", "branch", z**(a*b), (z**a)**b, "INCONCLUSIVE",
    domains={"z": "complex", "a": "real", "b": "real"})

# ---- other policy rules
add("special_solves_for_symbol", "special", y, x**2 + 1, "INCONCLUSIVE", kind="definition_like",
    note="bare symbol on one side: a definition, not an identity")
add("special_integer_only", "special", sin(pi*n), 0, "PASS",
    note="no integer domain given; holds only at integers -> resample as integers")
add("special_measure_zero", "special", floor(x) + floor(-x), -1, "INCONCLUSIVE",
    note="true except at integers; failures confined to integers_small")
add("special_undefined_function", "special", f(x), x**2, "SKIP", note="defines f")
add("special_not_checkable", "special", x, x, "SKIP", checkable=False, skip_reason="statement_not_identity")
add("special_constant_e_i_pi", "special", e_**(i_*pi) + 1, 0, "PASS", constants={"e": "E", "i": "I"})


# ---- rounded decimals and approximations (the side's LaTeX comes from the translator's `sides:` note)
def sides(lhs_tex, rhs_tex):
    return f"sides: {lhs_tex}  ||  {rhs_tex}"


Fr = sp.Rational
add("decimal_rounded_5", "approx", pi/(3*sqrt(2)), Fr("0.74048"), "PASS",
    notes=sides(r"\frac{\pi}{3\sqrt{2}}", "0.74048"), note="Kepler conjecture density, rounded to 5 places")
add("decimal_rounded_2", "approx", Fr(2, 3), Fr("0.67"), "PASS", notes=sides(r"\frac{2}{3}", "0.67"))
add("decimal_rounded_sum", "approx", 10 + Fr("1.372")*sqrt(2)/sqrt(11), Fr("10.585"), "PASS",
    notes=sides(r"10 + 1.372\, \frac{\sqrt{2}}{ \sqrt{11} }", "10.585."))
add("decimal_truncated_ellipsis", "approx", sqrt(3), Fr("1.7320"), "PASS",
    notes=sides(r"\sqrt{3}", r"1.7320\ldots"), note="truncated digits marked by an ellipsis")
add("decimal_truncated_unmarked", "mutated", sqrt(3), Fr("1.7320"), "FAIL", mutation="truncated_not_rounded",
    notes=sides(r"\sqrt{3}", "1.7320"), note="1.73205... rounds to 1.7321 and no ellipsis marks truncation")
add("decimal_wrong_digit", "mutated", pi/(3*sqrt(2)), Fr("0.74084"), "FAIL", mutation="swapped_digits",
    source="decimal_rounded_5", notes=sides(r"\frac{\pi}{3\sqrt{2}}", "0.74084"))
add("decimal_wrong_rounding", "mutated", sp.E, Fr("2.7183"), "FAIL", mutation="wrong_last_digit",
    notes=sides("e", "2.7183"), note="e = 2.718281..., so 2.7183 is correctly rounded: expect PASS",)
ROWS[-1]["expected"], ROWS[-1]["category"], ROWS[-1]["mutation"] = "PASS", "approx", None
add("decimal_wrong_rounding_2", "mutated", sp.E, Fr("2.7186"), "FAIL", mutation="wrong_last_digit",
    notes=sides("e", "2.7186"))
add("pi_rational_355_113", "approx", pi, Fr(355, 113), "INCONCLUSIVE", notes=sides(r"\pi", "355/113"),
    note="'Taking pi = 355/113': a working approximation")
add("pi_rational_3927_1250", "approx", pi, Fr(3927, 1250), "INCONCLUSIVE",
    notes=sides(r"\pi", r"\frac{3927}{1250}"))
add("stirling_with_tolerance_hint", "approx", gamma(x + 1), sqrt(2*pi*x)*(x/sp.E)**x, "PASS",
    domains={"x": {"type": "positive", "lower": 2000}}, hints=["tol:rel=1e-3"],
    note="Stirling's approximation, relative error 1/(12x) < 1e-3 here")
add("stirling_approx_hint", "approx", gamma(x + 1), sqrt(2*pi*x)*(x/sp.E)**x, "INCONCLUSIVE",
    domains={"x": {"type": "positive", "lower": 2000}}, hints=["tol:approx"])
add("stirling_no_hint", "mutated", gamma(x + 1), sqrt(2*pi*x)*(x/sp.E)**x, "FAIL", mutation="approximation_as_identity",
    domains={"x": {"type": "positive", "lower": 2000}}, note="without a hint an approximation is not an identity")

# ---- superscripts that are labels, not powers (FAIL would be a translation artefact)
B12 = sp.Symbol("B_{1,2}")
s_, F_, D_, H_, Hs, p_, w_ = sp.symbols("s F D H H_s p omega")
add("label_bayes_factor", "label", B12, B12**s_, "INCONCLUSIVE",
    domains={"B_{1,2}": "positive", "s": "complex"}, notes=sides("B_{1,2}", "B_{1,2}^s"))
add("label_force_parts", "label", F_, F_**D_ + F_**H_, "INCONCLUSIVE",
    domains={"F": "positive", "D": "positive", "H": "positive"}, notes=sides("F", "F^H + F^D"))
add("label_idempotent_power", "label", a*a**w_, a**w_, "INCONCLUSIVE",
    domains={"a": "real", "omega": "positive"}, notes=sides(r"aa^\omega", r"a^\omega"))
add("label_multiletter", "label", Hs**(x*p_), x/p_, "INCONCLUSIVE",
    domains={"H_s": "positive", "p": "positive", "x": "real"}, notes=sides(r"H_\text{s}^{xp}", r"\frac{x}{p}"))
add("label_parenthesised_zero", "label", sp.Integer(1), sp.Integer(0), "INCONCLUSIVE",
    notes=sides("X^{(0)}", "0"), note="the translator collapsed X^{(0)} to 1")
add("label_superscript_zero", "label", sp.Integer(1), sp.Integer(3), "INCONCLUSIVE", notes=sides("C_3^0", "3"))
add("label_translator_note", "label", cos(a*x), sp.Symbol("e^iax")/2 + exp(-i_*a*x)/2, "INCONCLUSIVE",
    domains={"a": "real", "x": "real", "e^iax": "positive"}, constants={"i": "I"},
    notes="superscript_label:e^iax\n" + sides(r"\cos(a x)", r"\tfrac{e^{i a x} + e^{-i a x} }{2}"))
# exponents that take part in arithmetic are real powers: these mutations must still FAIL
pair("exponent_sum", x**(a + b)*x**c, x**(a + b + c), x**(a + b)*x**c, x**(a + b - c), "sign_flip",
     domains={"x": "positive", "a": "real", "b": "real", "c": "real"})
pair("exponent_scaling", (x**2)**a, x**(2*a), (x**2)**a, x**(2*a + 1), "exponent_off_by_one",
     domains={"x": "positive", "a": "real"})


def main() -> None:
    with OUT.open("w") as fh:
        for row in ROWS:
            fh.write(json.dumps(row) + "\n")
    cats: dict[str, int] = {}
    for row in ROWS:
        cats[row["category"]] = cats.get(row["category"], 0) + 1
    print(f"wrote {len(ROWS)} rows to {OUT}: {cats}")


if __name__ == "__main__":
    main()
