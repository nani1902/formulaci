"""Unit tests for individual semantics rules (synthetic inputs, one behaviour each)."""
import sympy
from sympy import Function, Symbol, srepr, sympify

from formulaci.schemas import Formula, Parsed
from formulaci.semantics import prose
from formulaci.semantics.rules import infer

LOC = {n: Symbol(n) for n in "e i j x y z n k s b p q theta phi varphi gamma alpha beta X u v t a c m nu".split()}
LOC.update(Gamma=sympy.gamma, f=Function("f"), g=Function("g"), B=Function("B"), F=Function("F"))


def P(lhs, rhs, **kw):
    kw.setdefault("kind", "equation")
    return Parsed(formula_id="t", status=kw.pop("status", "ok"),
                  lhs=None if lhs is None else srepr(sympify(lhs, locals=LOC, evaluate=False)),
                  rhs=None if rhs is None else srepr(sympify(rhs, locals=LOC, evaluate=False)), **kw)


def F(latex="", before="", after="", title="Test page"):
    return Formula(formula_id="t", page_title=title, page_id=1, revision_id=1, url="", index=0, latex=latex,
                   context_before=before, context_after=after)


def run(lhs, rhs, latex="", before="", after="", title="Test page", **kw):
    sem, _ = infer(F(latex, before, after, title), [P(lhs, rhs, **kw)])
    return sem


def dom(sem, n):
    return sem.domains[n].type


# ------------------------------------------------------------------ constants

def test_e_power_base_is_euler():
    assert run("e**x", "exp(x)").constants == {"e": "E"}


def test_e_without_evidence_stays_variable():
    s = run("e*x", "x*e", after="where e is the eccentricity of the orbit")
    assert "e" not in s.constants


def test_e_from_context():
    assert run("log(e)", "1", before="the natural logarithm satisfies").constants == {"e": "E"}


def test_i_in_exponent_is_imaginary():
    assert run("e**(i*x)", "cos(x) + i*sin(x)").constants == {"e": "E", "i": "I"}


def test_i_with_index_usage_stays_variable():
    s = run("i + 1", "1 + i", latex=r"a_i + 1 = 1 + a_i", before="for each i = 1, ..., n we have")
    assert "i" not in s.constants
    assert dom(s, "i") == "nonneg_integer"


def test_i_from_complex_context():
    assert run("(2 + i)*(3 + i)", "5 + 5*i", before="multiplying the complex numbers").constants == {"i": "I"}


def test_j_needs_explicit_imaginary_cue():
    assert "j" not in run("j + 1", "1 + j").constants
    assert run("j**2", "-1", before="in electrical engineering the imaginary unit j satisfies").constants == {"j": "I"}


def test_gamma_only_with_euler_mascheroni():
    assert run("gamma", "1/sqrt(1 - x**2)", after="the Lorentz factor").constants == {}
    s = run("-gamma", "polygamma(0, 1)", after="where γ is the Euler–Mascheroni constant")
    assert s.constants == {"gamma": "EulerGamma"}


def test_phi_golden_ratio_only_outside_trig():
    assert run("varphi + 1", "varphi**2", before="the golden ratio satisfies").constants == {"varphi": "GoldenRatio"}
    s = run("sin(phi)**2 + cos(phi)**2", "1", before="unlike the golden ratio")
    assert s.constants == {}


def test_function_alias_needs_arity_and_cue():
    s = run("B(x, y)", "Gamma(x)*Gamma(y)/Gamma(x + y)", before="the beta function", functions=["B"])
    assert s.constants == {"B": "beta"} and s.checkable
    s3 = run("B(x, a, b)", "x", before="the incomplete beta function", functions=["B"])
    assert not s3.checkable and s3.skip_reason == "has_undefined_function"


# ------------------------------------------------------------------ domains

def test_letter_defaults():
    s = run("n + x + z + theta + epsilon + r + q", "q + r + epsilon + theta + z + x + n")
    assert dom(s, "n") == "nonneg_integer"
    assert dom(s, "x") == "real"
    assert dom(s, "z") == "complex"
    assert dom(s, "theta") == "real"          # not inside a trig function
    assert dom(s, "epsilon") == "positive"
    assert dom(s, "r") == "nonneg"
    assert dom(s, "q") == "positive"          # no convention: safe default


def test_angle_inside_trig():
    assert dom(run("sin(-theta)", "-sin(theta)"), "theta") == "angle"


def test_prose_positive_integer():
    s = run("Gamma(n)", "factorial(n - 1)", after="for every positive integer n. The gamma function")
    assert dom(s, "n") == "positive_integer"


def test_prose_bound_and_neq():
    s = run("log(x*y)/log(b)", "log(x)/log(b) + log(y)/log(b)", after="provided that b, x and y are all positive and b ≠ 1.")
    assert {dom(s, v) for v in "bxy"} == {"positive"}
    assert "Ne(b, 1)" in s.constraints
    assert s.domains["b"].exclude == [1.0]


def test_prose_unit_interval_and_abs():
    s = run("x**2", "x*x", after="for 0 ≤ x ≤ 1, one has")
    assert dom(s, "x") == "unit_interval"
    s = run("1/(1 - x)", "Sum(x**k, (k, 0, oo))", after="valid for |x| < 1.")
    assert s.domains["x"].lower == -1 and s.domains["x"].upper == 1 and "Abs(x) < 1" in s.constraints


def test_prose_real_part():
    s = run("zeta(s)", "Sum(1/n**s, (n, 1, oo))", after=r"for \mathrm{Re}(s) > 1, and its analytic continuation")
    assert "re(s) > 1" in s.constraints and dom(s, "s") == "complex"


def test_prose_membership_and_complex():
    assert dom(run("x + 0", "x", after=r"for x \in \mathbb{R}"), "x") == "real"
    assert dom(run("exp(z)*exp(-z)", "1", after="for any complex z"), "z") == "complex"


def test_widening_only_from_adjacent_text():
    far = "for all real numbers n we will later see something. " + "filler words " * 30
    s = run("n + 1", "1 + n", before=far + "and so")
    assert dom(s, "n") == "nonneg_integer"
    s = run("n + 1", "1 + n", after="for all real numbers n")
    assert dom(s, "n") == "real"


def test_tail_condition_in_latex():
    s = run("binomial(n, k)", "factorial(n)/(factorial(k)*factorial(n - k))",
            latex=r"\binom nk = \frac{n!}{k!\,(n-k)!} \quad \text{for }\ 0\leq k\leq n,")
    assert "k <= n" in s.constraints


def test_notes_condition():
    s = run("x**y", "exp(y*log(x))", notes="cond: x > 0")
    assert dom(s, "x") == "positive"


def test_prime_letter():
    s = run("p", "p", before="let p be a prime and", after="")
    assert dom(s, "p") == "positive_integer" and "Q.prime(p)" in s.constraints


def test_integer_from_tail_widens_k():
    s = run("e**(z + 2*i*k*pi)", "e**z", latex=r"e^{z+2ik\pi} =e^z \quad \text{for every } k\in \Z.")
    assert dom(s, "k") == "integer"


# ------------------------------------------------------------------ expression constraints

def test_denominator_log_sqrt_asin():
    s = run("1/x + log(y) + sqrt(t) + asin(a)", "a")
    assert "Ne(x, 0)" in s.constraints
    assert dom(s, "y") == "positive"           # bare argument of a real log
    assert "t >= 0" in s.constraints
    assert "((a) >= -1) & ((a) <= 1)" in s.constraints


def test_complex_log_only_needs_nonzero():
    assert "Ne(z, 0)" in run("e**log(z)", "z").constraints


def test_gamma_pole_and_reciprocal_gamma():
    s = run("Gamma(z + 1)", "z*Gamma(z)")
    assert any(c.startswith("Not(And(Eq(z, floor(re(z)))") for c in s.constraints)
    s = run("1/Gamma(z)", "z/Gamma(z + 1)")
    assert not any("Not(And" in c for c in s.constraints)


def test_factorial_folds_into_domain():
    s = run("factorial(n)", "n*factorial(n - 1)")
    assert dom(s, "n") == "positive_integer"


def test_trig_and_zeta_poles():
    assert "Ne(cos(theta), 0)" in run("tan(theta)**2 + 1", "sec(theta)**2").constraints
    assert "Ne(s, 1)" in run("zeta(s)", "zeta(s)").constraints


def test_sum_index_is_integer_for_powers():
    s = run("(x + y)**n", "Sum(binomial(n, k)*x**k*y**(n - k), (k, 0, n))")
    assert not any(c in s.constraints for c in ("x > 0", "y > 0"))


# ------------------------------------------------------------------ checkability

def test_skip_reasons():
    assert run("f(x)", "x**2", kind="definition_like", functions=["f"]).skip_reason == "definition"
    assert run("f(x + y)", "f(x) + f(y)", functions=["f"]).skip_reason == "functional_identity"
    assert run("F(x)", "x**2 + 1", functions=["F"]).skip_reason == "has_undefined_function"
    assert run("a**2 + b**2", "c**2").skip_reason == "statement_not_identity"
    assert run("y", "m*x + b").skip_reason == "definition"
    assert run("x**2 + y**2", "1").skip_reason == "statement_not_identity"
    assert run("Integral(log(x), x)", "x*log(x) - x + C").skip_reason == "indefinite_integral"
    assert run("x", "x", latex=r"a^p \equiv a \pmod p").skip_reason == "congruence"
    assert run("x", "x", latex=r"f(x) = O(x^2)").skip_reason == "operator_notation"
    assert run("x", "x", latex=r"\mathbb{E}[X] = \mu").skip_reason == "operator_notation"
    assert run("x", "x", latex=r"\nabla \cdot F = 0").skip_reason == "operator_notation"
    assert run("x", "x", latex=r"\mathbf{F} = m\mathbf{a}").skip_reason == "matrix_or_vector"
    assert run("x", "x", latex=r"A \cup B = B \cup A").skip_reason == "set_notation"
    assert run("x", "x", latex=r"n! \sim \sqrt{2\pi n}").skip_reason == "statement_not_identity"
    assert run("x", "x", latex=r"E = 5\,\mathrm{kg} \cdot c^2").skip_reason == "units"
    assert run(None, None, status="unparsed").skip_reason == "unparsed"
    assert run("x", "x", has_unsupported=["\\oint"]).skip_reason == "operator_notation"


def test_numeric_and_inequality_stay_checkable():
    assert run("Gamma(1/2)", "sqrt(pi)").checkable
    s = run("cosh(t)", "e**(t**2/2)", kind="inequality", relation="<=")
    assert s.checkable and "K.inequality" in s.assumptions_source


def test_definition_of_known_function_is_checked():
    s = run("Gamma(z)", "Integral(t**(z - 1)*e**(-t), (t, 0, oo))", kind="definition_like")
    assert s.checkable


def test_cancelling_symbol_is_not_one_sided():
    s = run("log(x)/log(b)", "(log(x)/log(k))/(log(b)/log(k))")
    assert s.checkable


def test_context_relation_skips_dependent_symbol():
    s = run("log(z)", "log(Abs(z)) + i*phi", before=r"one can write z = |z| e^{i \varphi} for any z ≠ 0. Taking the logarithm")
    assert s.skip_reason == "statement_not_identity"


def test_chain_is_one_record_and_strictest_piece_wins():
    pieces = [P("W", "m*a*(a*t**2/2)", index_in_chain=0), P("m*a*(a*t**2/2)", "m*(a*t)**2/2", index_in_chain=1)]
    sem, _ = infer(F(), pieces)
    assert not sem.checkable and sem.skip_reason == "definition"


# ------------------------------------------------------------------ prose helpers

def test_sym_key_and_normalize():
    assert prose.sym_key(r"\varphi_{1}") == "phi_1"
    assert prose.base_letter("x_1") == "x"
    assert "re(s) > 1" in prose.normalize_text(r"for \operatorname{Re}(s) > 1")
    assert "x <= 1" in prose.normalize_text(r"x \leq 1")
    assert "COMPLEXES" in prose.normalize_text("z ∈ ℂ")


def test_split_tail():
    main, tail = prose.split_tail(r"\Gamma(z) = \int_0^\infty t^{z-1} e^{-t}\,dt, \ \qquad \Re(z) > 0.")
    assert "Re" in tail and r"\int" in main
    assert prose.split_tail(r"x^2 = x \cdot x") == (r"x^2 = x \cdot x", "")


def test_real_data_false_checkables():
    # found by hand-reviewing a sample of real formulas the rules called checkable
    h2 = Symbol("h_prime_prime")
    sem, _ = infer(F(r"h''+h=\frac{1}{h}"), [Parsed(formula_id="t", status="ok", kind="equation",
                                                     lhs=srepr(h2 + Symbol("h")), rhs=srepr(1 / Symbol("h")))])
    assert sem.skip_reason == "differential_equation"
    assert run("2143", "12*34", latex=r"2143 = (12)(34)").skip_reason == "operator_notation"
    assert run("Abs(x)", "1", kind="inequality", relation="<").skip_reason in ("condition", "statement_not_identity")
    assert run("Abs(X)", "-X").skip_reason == "statement_not_identity"
    assert run("2*beta*e**(1 - beta)", "1").skip_reason == "statement_not_identity"
    assert run("(k_1 + k_2)**2", "2*(k_1**2 + k_2**2)").skip_reason == "statement_not_identity"
    assert "e" not in run("e**2/a**2", "m*a*(2*pi*nu)**2").constants   # e^2: squared charge, not Euler
    assert run("1 + 1", "2").checkable and run("sin(x)**2 + cos(x)**2", "1").checkable


# ------------------------------------------------------------------ second pass: reviewed real FAILs

def test_special_algebra_context():
    s = run("1 + 1", "0", before="In algebra, structures of characteristic 2 have special behavior because")
    assert s.skip_reason == "special_algebra"
    assert run("x**q", "x", title="Finite field").skip_reason == "special_algebra"
    assert run("3*3*3", "3", before=r"since in the ring $\mathbb{Z}/12\mathbb{Z}$ :").skip_reason == "special_algebra"
    assert run("aleph_0 + 1", "aleph_0", title="Cardinal number").skip_reason == "special_algebra"
    # "z/2" is not Z/2Z
    assert run("Beta(x, 1 - x)", "pi/sin(pi*x)", before="taking z/2 in the formula").checkable


def test_stated_false_context():
    assert run("1", "2", after=", a false statement. The fallacy here arises").skip_reason == "stated_false"
    assert run("pi", "25/8", before="James Smith, a merchant, who claimed that").skip_reason == "stated_false"
    # a cue about the *next* formula does not count
    assert run("1/e**x", "e**(-x)", after=". Positiveness: e^x>0 for every real number x. This results from the "
                                          "intermediate value theorem, since e^0=1 and, if one would have e^x<0").checkable


def test_defining_equations():
    assert run("x", "sqrt(2 + x)", before="which gives the equation").skip_reason == "defining_equation"
    assert run("cos(x)", "x", before="Dottie number D 0.739 Real root of").skip_reason == "defining_equation"
    assert run("2*x + 2", "3**x", after=" (where x is an unknown real number) can be solved").skip_reason == "defining_equation"
    s = run("Integral(e**(-x**2/2), (x, -z, z))/sqrt(2*pi)", "0.95", latex=r"\int_{-z}^{z} ... = 0.95",
            notes="sides: \\int_{-z}^{z} e^{-x^2/2}  ||  0.95")
    assert s.skip_reason == "defining_equation"
    # identities introduced as "obeys the equation" / "satisfying the recurrence relation" stay checkable
    assert run("Gamma(z + 1)", "z*Gamma(z)", before="The gamma function obeys the equation").checkable
    assert run("binomial(n, k)", "binomial(n - 1, k - 1) + binomial(n - 1, k)",
               before="Pascal's triangle, satisfying the recurrence relation").checkable
    assert run("Gamma(z)", "Gamma(z)", after="If the real part is an integer, this can be expressed in closed form").checkable


def test_condition_inequalities_and_index_ranges():
    s = run("4*p**3 + 27*q**2", "0", kind="inequality", relation="<", after="that is, if the polynomial has three real roots")
    assert s.skip_reason == "condition"
    assert run("i", "1", latex=r"i = 1, \ldots, n").skip_reason == "statement_not_identity"
    assert run("i", "1", latex=r"i = 1, \ldots, n").constants == {}


def test_noncommuting_and_named_constants():
    assert run("exp(X)*exp(Y)", "exp(X + Y)", before="for elements X, Y of a Lie algebra").skip_reason == "matrix_or_vector"
    assert run("Li(rho)", "pi**2/10", before=r"Define $\rho = \tfrac{1}{2} (\sqrt{5}-1)$ as the reciprocal",
               functions=["Li"]).skip_reason in ("named_constant", "has_undefined_function")
    sem, _ = infer(F(r"\frac{\varpi}{2}"), [Parsed(formula_id="t", status="ok", kind="equation",
                                                    lhs=srepr(Symbol("varpi") / 2), rhs=srepr(sympy.Rational(13, 10)))])
    assert sem.skip_reason in ("named_constant", "statement_not_identity") and "varpi" not in sem.constants
    assert run("pi", "0").skip_reason == "named_constant"
    assert run("pi", "355/113").skip_reason == "approximation"


def test_imaginary_unit_as_factor_and_golden_field():
    assert run("Abs(Gamma(a + b*i))**2", "Abs(Gamma(a))**2").constants == {"i": "I"}
    assert run("varphi**2", "varphi + 1", title="Golden field").constants == {"varphi": "GoldenRatio"}


def test_improper_integral_parameters_positive():
    s = run("Integral(x*sin(m*x)/(x**2 + a**2), (x, 0, oo))", "pi/2*e**(-m*a)")
    assert dom(s, "a") == "positive" and dom(s, "m") == "positive_integer"


def test_rational_relation_and_tolerance_hint():
    assert run("(c + a)/b", "b/(c - a)").skip_reason == "statement_not_identity"
    assert run("(a + b)**2", "a**2 + 2*a*b + b**2").checkable          # a true polynomial identity stays
    s = run("10 + 1.372*sqrt(2)/sqrt(11)", "10.585", notes="sides: 10 + 1.372\\, \\frac{\\sqrt{2}}{ \\sqrt{11} }  ||  10.585")
    assert s.checkable and "tol:3" in s.assumptions_source
