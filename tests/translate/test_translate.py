"""Translation rules, classification, and the guards against silent mis-translation."""
import sympy as sp

from .conftest import sides, tr

x, y, z, a, b, n, k, s, t = sp.symbols("x y z a b n k s t")
e, i = sp.Symbol("e"), sp.Symbol("i")
f = sp.Function("f")


def notes_of(r):
    return (r.notes or "").splitlines()


# ------------------------------------------------------------------ operators and functions
def test_big_operators():
    L, R, _ = sides(r"\sum_{k=0}^{n} \binom{n}{k} = 2^n")
    assert L == sp.Sum(sp.binomial(n, k), (k, 0, n)) and R == 2**n
    L, _, _ = sides(r"\prod_{k=1}^n k = n!")
    assert L == sp.Product(k, (k, 1, n))
    L, _, _ = sides(r"\sum_{n,m=0}^\infty a = 1")
    assert isinstance(L, sp.Sum) and len(L.limits) == 2
    L, _, _ = sides(r"\sum_{k \ge 1} x^k = 1")
    assert L == sp.Sum(x**k, (k, 1, sp.oo))
    r = tr(r"\sum_{d|n} d = \sigma(n)")[0]
    assert r.status == "not_checkable" and "sum_index_set" in r.has_unsupported


def test_definite_and_indefinite_integrals():
    L, R, _ = sides(r"\int_a^b x^2 \, dx = \frac{b^3-a^3}{3}")
    assert L == sp.Integral(x**2, (x, a, b))
    L, _, _ = sides(r"\int_0^\infty e^{-t} t^{z-1}\,\mathrm{d}t = \Gamma(z)")
    assert L == sp.Integral(e ** (-t) * t ** (z - 1), (t, 0, sp.oo))
    L, R, r = sides(r"\int \frac{dx}{x} = \ln|x| + C")
    assert L == sp.Integral(1 / x, x) and R == sp.log(sp.Abs(x)) + sp.Symbol("C")
    L, _, _ = sides(r"\int \frac{(\ln x)^n\,dx}{x} = 1")
    assert L == sp.Integral(sp.log(x) ** n / x, x)
    L, _, _ = sides(r"\int {\frac{1}{\sqrt{a^2 + u^2}}\,du} = 1")
    assert L.limits[0][0] == sp.Symbol("u")
    L, _, _ = sides(r"\int_{u=0}^\infty e^{-u}\,du = 1")
    assert L == sp.Integral(e ** (-sp.Symbol("u")), (sp.Symbol("u"), 0, sp.oo))


def test_integral_dx_and_coefficient_d():
    # `d` as a coefficient next to letters inside brackets is not a differential
    L, R, _ = sides(r"\int (d+e\,x)^m dx = \frac{1}{d\,f(m+2)} \int (a\,d\,f - b) x\, dx")
    d_, f_, m_ = sp.symbols("d f m")
    assert L == sp.Integral((d_ + e * x) ** m_, x)
    assert R.has(sp.Integral((a * d_ * f_ - b) * x, x))
    # body stops at the differential; the trailing + C is outside
    L, R, _ = sides(r"\int \cos x \, dx + C = \sin x")
    assert L == sp.Integral(sp.cos(x), x) + sp.Symbol("C")
    r = tr(r"\int_a^b f = F(b) - F(a)")[0]  # Lebesgue-style, no differential: not guessed
    assert r.status == "not_checkable" and "integral_without_differential" in r.has_unsupported


def test_double_integral_order():
    L, _, _ = sides(r"\int_0^1\int_0^2 x y \,dy\,dx = 1")
    assert L == sp.Integral(sp.Integral(x * y, (y, 0, 2)), (x, 0, 1))


def test_limits():
    L, R, _ = sides(r"\lim_{x\to 0}\frac{\sin x}{x} = 1")
    assert L == sp.Limit(sp.sin(x) / x, x, 0, dir="+-")
    L, _, _ = sides(r"\lim_{n\to\infty}\left(1+\frac1n\right)^n = e")
    assert L == sp.Limit((1 + 1 / n) ** n, n, sp.oo)
    L, _, _ = sides(r"\lim_{x\to 0^+} x^x = 1")
    assert L == sp.Limit(x**x, x, 0, dir="+")


def test_binomials_roots_exp_ln_log():
    L, R, _ = sides(r"\binom{n}{k} = \tbinom nk")
    assert L == R == sp.binomial(n, k)
    L, R, _ = sides(r"\sqrt[3]{x} = \sqrt{y}")
    assert L == x ** sp.Rational(1, 3) and R == sp.sqrt(y)
    L, R, _ = sides(r"\exp(x) = \ln y")
    assert L == sp.exp(x) and R == sp.log(y)
    L, R, r = sides(r"\log_b x = \log x")
    assert L == sp.log(x) / sp.log(b) and R == sp.log(x)
    assert "log:unspecified_base" in notes_of(r)


def test_trig_hyperbolic_inverse_and_powers():
    L, R, _ = sides(r"\sin^2 x + \cos^2 x = 1")
    assert L == sp.sin(x) ** 2 + sp.cos(x) ** 2
    L, R, _ = sides(r"\sinh x \cosh y = \tanh 2x")
    assert L == sp.sinh(x) * sp.cosh(y) and R == sp.tanh(2 * x)
    L, R, r = sides(r"\arcsin x = \sin^{-1} x")
    assert L == R == sp.asin(x)
    assert any(nt.startswith("ambig:sin^-1") for nt in notes_of(r))
    L, _, _ = sides(r"\operatorname{arcsinh} x = 0")
    assert L == sp.asinh(x)


def test_function_argument_scope():
    L, R, _ = sides(r"\sin 2x \cos y = \sin x^2")
    assert L == sp.sin(2 * x) * sp.cos(y) and R == sp.sin(x**2)
    L, _, _ = sides(r"\sin \frac{\pi}{2} x = 0")
    assert L == sp.sin(sp.pi * x / 2)  # following letters are absorbed into the argument
    L, _, _ = sides(r"\ln|x| = 0")
    assert L == sp.log(sp.Abs(x))


def test_special_functions():
    L, R, _ = sides(r"\Gamma(z+1) = z\Gamma(z)")
    assert L == sp.gamma(z + 1) and R == z * sp.gamma(z)
    L, _, _ = sides(r"\Gamma^2(z) = 1")
    assert L == sp.gamma(z) ** 2
    L, R, _ = sides(r"\zeta(s) = \Beta(x, y)")
    assert L == sp.zeta(s) and R == sp.beta(x, y)
    L, _, _ = sides(r"\mathrm{B}(x,y) = 1")
    assert L == sp.beta(x, y)
    L, _, _ = sides(r"\Gamma(s, x) = \gamma(s, x)")
    assert L == sp.uppergamma(s, x)


def test_accents_and_subscripts():
    L, R, _ = sides(r"\hat{x} + \bar y + \tilde z + \dot w = x_1 + a_{ij} + \alpha_n")
    assert {str(q) for q in L.free_symbols} == {"x_hat", "y_bar", "z_tilde", "w_dot"}
    assert sp.Symbol("x_1") in R.free_symbols and sp.Symbol("alpha_n") in R.free_symbols
    L, _, r = sides(r"\vec v = 0")
    assert L == sp.Symbol("vec_v")


def test_primes():
    L, R, _ = sides(r"f'(x) = f''(x)")
    assert L == sp.Derivative(f(x), x) and R == sp.Derivative(f(x), (x, 2))
    L, _, _ = sides(r"\Gamma'(z) = 1")
    assert L == sp.Derivative(sp.gamma(z), z)
    L, _, r = sides(r"y' = 1")
    assert L == sp.Symbol("y_prime")


def test_e_and_i_stay_symbols():
    L, R, r = sides(r"e^{i\pi} = -1")
    assert L == e ** (i * sp.pi)
    assert "hint:e_only_as_exp_base" in notes_of(r) and "hint:i_present" in notes_of(r)


def test_derivatives():
    L, R, _ = sides(r"\frac{d}{dx} x^n = n x^{n-1}")
    assert L == sp.Derivative(x**n, x)
    L, _, _ = sides(r"\frac{\partial^2 u}{\partial x \partial y} = 0")
    assert L == sp.Derivative(sp.Function("u")(x, y), x, y)  # Leibniz: u depends on x, y
    L, _, r = sides(r"\frac{dy}{dx} = y")
    assert L == sp.Derivative(sp.Function("y")(x), x)  # Leibniz: y depends on x
    # d/dx [ ... ] applies to the bracket only
    L, _, _ = sides(r"\frac{d}{dx}\left[x^2\right](1+x) = 0")
    assert L == (1 + x) * sp.Derivative(x**2, x)


def test_numbers():
    L, R, _ = sides(r"0.5 = 1{,}000")
    assert L == sp.Rational(1, 2) and R == 1000


# ------------------------------------------------------------------ application vs multiplication
def test_conventional_function_names_are_applied():
    L, R, r = sides(r"f(x+y) = f(x)f(y)")
    assert L == f(x + y) and R == f(x) * f(y)
    assert r.functions == ["f"]


def test_compound_argument_is_multiplication():
    L, R, _ = sides(r"a(b+c) = ab + ac")
    assert L == a * (b + sp.Symbol("c"))


def test_single_atom_argument_is_application():
    L, _, r = sides(r"y(t) = A\cos(\omega t)")
    assert L == sp.Function("y")(t)


def test_coefficient_named_f_is_multiplication():
    # integral-table style: a..f are coefficients, so f(m+1) is f*(m+1), not a call
    L, R, r = sides(r"(a+b\,x)^m (c+d\,x)^n (e+f\,x)^p = f(m+1)")
    assert R == sp.Symbol("f") * (sp.Symbol("m") + 1)
    assert "mult_not_call:f" in notes_of(r)
    # otherwise a bare f next to f(compound) is ambiguous: refuse rather than guess
    r = tr(r"[\mathcal{L}_T f](y) = \frac{1}{2}f\left(\frac{y}{2}\right)")[0]
    assert r.status == "not_checkable"


def test_greek_letter_applied_is_function():
    L, _, _ = sides(r"\theta(it) - 1 = 0")
    assert L == sp.Function("theta")(i * t) - 1
    L, _, _ = sides(r"\Phi{\left(\frac{x}{2}\right)} = 0")
    assert L == sp.Function("Phi")(x / 2)


def test_pi_of_letter_is_prime_counting_like_function():
    L, _, r = sides(r"\pi(x) = 2\pi(r+h)")
    assert L == sp.Function("pi")(x)
    assert "ambig:pi_as_function" in notes_of(r)


def test_uppercase_juxtaposition_unsupported():
    r = tr(r"AB = BA")[0]
    assert r.status == "not_checkable" and "uppercase_juxtaposition" in r.has_unsupported


def test_index_dependent_subscripts_become_sequences():
    L, R, _ = sides(r"x_n = x_{n-1} - 1")
    xs = sp.Function("x")
    assert L == xs(n) and R == xs(n - 1) - 1
    L, _, _ = sides(r"\sum_{n=0}^\infty a_n x^n = 1")
    assert L == sp.Sum(sp.Function("a")(n) * x**n, (n, 0, sp.oo))
    L, R, _ = sides(r"a_{ij} = a_{ji}")
    assert L == sp.Function("a")(i, sp.Symbol("j"))
    L, _, _ = sides(r"v_{max} = 1")
    assert L == sp.Symbol("v_max")


# ------------------------------------------------------------------ unsupported constructs
def test_ellipsis_unsupported_and_chain_bridged():
    rs = tr(r"\sum_{k=0}^n x^k = 1 + x + \cdots + x^n = \frac{1-x^{n+1}}{1-x}")
    assert rs[0].status == "not_checkable" and "ellipsis" in rs[0].has_unsupported
    bridge = [r for r in rs if any(nt.startswith("bridge:") for nt in notes_of(r))]
    assert len(bridge) == 1 and bridge[0].status == "ok"
    assert sp.sympify(bridge[0].rhs) == (1 - x ** (n + 1)) / (1 - x)


def test_pm_coupled_split_and_lone_pm_unsupported():
    rs = tr(r"\sin(a \pm b) = \sin a \cos b \pm \cos a \sin b")
    assert len(rs) == 2 and all(r.status == "ok" for r in rs)
    assert sp.sympify(rs[1].lhs) == sp.sin(a - b)
    r = tr(r"\sin\frac{x}{2} = \pm\sqrt{\frac{1-\cos x}{2}}")[0]
    assert r.status == "not_checkable" and "pm" in r.has_unsupported


def test_differential_forms_unsupported():
    r = tr(r"dx = \frac{2}{t^2-1}\,dt")[0]
    assert r.status == "not_checkable" and "differential_form" in r.has_unsupported


def test_other_unsupported():
    for latex, name in [
        (r"\oint_C f\,dz = 0", "contour_integral"),
        (r"\|x\| = 1", "norm"),
        (r"(f*g)(t) = 1", "asterisk_op"),
        (r"\nabla\cdot F = 0", "vector_calculus"),
        (r"{}_2F_1(a,b;c;z) = 1", "hypergeometric"),
        (r"a \equiv b \pmod n", "modular"),
    ]:
        r = tr(latex)[0]
        assert r.status in ("not_checkable", "unparsed"), latex
        assert name in r.has_unsupported, (latex, r.has_unsupported, r.error)


def test_huge_numbers_guarded():
    r = tr(r"10^{10^{10}} = x")[0]
    assert r.status == "not_checkable" and "huge_number" in r.has_unsupported


# ------------------------------------------------------------------ classification
def test_chain_split_pairwise():
    rs = tr(r"\cosh^2 x - \sinh^2 x = 1 = \cos^2 x + \sin^2 x")
    assert [r.kind for r in rs] == ["chain", "chain"]
    assert [r.index_in_chain for r in rs] == [0, 1]
    assert sp.sympify(rs[1].lhs) == 1


def test_inequalities_have_relation():
    r = tr(r"|\sin x| \le 1")[0]
    assert r.kind == "inequality" and r.relation == "<=" and r.status == "ok"
    rs = tr(r"0 < x < 1")
    assert [r.relation for r in rs] == ["<", "<"]


def test_definition_markers():
    for latex in [r"c_k := \sum_{j=0}^k j", r"f(x) \equiv x^2 + 1", r"\phi \triangleq 2", r"x^2 =: g"]:
        r = tr(latex)[0]
        assert r.kind == "definition_like", latex
    r = tr(r"g(x) = x^2", before="The function g is defined as")[0]
    assert r.kind == "definition_like" and "definition_from_prose" in notes_of(r)
    r = tr(r"\Gamma(z+1) = z\Gamma(z)", before="We define")[0]
    assert r.kind == "equation"  # Gamma is a known function, not a name being defined
    r = tr(r"\sin^2 x + \cos^2 x \equiv 1")[0]
    assert r.kind == "equation" and "equiv_as_identity" in notes_of(r)


def test_expression_without_relation_not_checkable():
    r = tr(r"\frac{\pi}{4}")[0]
    assert r.kind == "other" and r.status == "not_checkable" and r.lhs is not None


def test_approx_and_membership_are_other():
    for latex in [r"\pi \approx 3.14", r"x \in [0,1]", r"n! \sim \sqrt{2\pi n}"]:
        r = tr(latex)[0]
        assert r.kind == "other" and r.status == "not_checkable", latex


def test_srepr_round_trip_and_fields():
    r = tr(r"\int_0^1 f(x)^2 \,dx = \sum_{n=1}^\infty \frac{1}{n^2}")[0]
    for side in (r.lhs, r.rhs):
        expr = sp.sympify(side)
        assert sp.srepr(expr) == side
        assert eval(side, vars(sp)) == expr
    assert r.functions == ["f"] and r.free_symbols == []
    assert r.translator.startswith("formulaci-rd")


def test_errors_never_raise():
    for junk in ["!!", "\\frac{", "}{", "\\begin{align} x &= \\end{align}", "", "\\unknowncmd x = 1", "x^"]:
        rs = tr(junk)
        assert rs and all(r.status in ("unparsed", "not_checkable", "ok") for r in rs)


def test_lark_fallback_only_accepts_unambiguous_parses():
    # our parser rejects \unknowncmd; lark rejects it too -> stays unparsed
    r = tr(r"\foo x = 1", lark=True)[0]
    assert r.status == "unparsed"


# ------------------------------------------------------------------ rules added after the first real-data run
def test_real_data_rules():
    L, R, r = sides(r"\mathrm{Re}=U l/\nu_\infty")  # a known function name with no argument is a symbol
    assert L == sp.Symbol("Re") and R == sp.Symbol("U") * sp.Symbol("l") / sp.Symbol("nu_inf")
    L, R, _ = sides(r"L = rmv_\perp")  # relation symbols as subscript labels
    assert sp.Symbol("v_perp") in R.free_symbols
    L, R, _ = sides(r"d(x,y)=d(y,x)")  # metric
    assert L == sp.Function("d")(x, y)
    L, R, _ = sides(r"f(n) = \mathcal{O}(n^2) + \mathcal{L}")
    assert R == sp.Function("cal_O")(n**2) + sp.Symbol("cal_L")
    L, R, _ = sides(r"m = 1{.}5 \times 10^{-2}")
    assert R == sp.Rational(3, 200)
    for latex, name in [
        (r"N = f_1 + f_2 + ... + f_n", "ellipsis"),
        (r"P(A|B) = \frac{P(B|A)P(A)}{P(B)}", "conditional_probability"),
        (r"\mathrm{d}U = T\,\mathrm{d}S - P\,\mathrm{d}V", "differential_form"),
        (r"2 = \{0,1\}", "set_notation"),
        (r"U = W^\perp", "orthogonal_complement"),
    ]:
        r = tr(latex)[0]
        assert r.status == "not_checkable" and name in r.has_unsupported, (latex, r.has_unsupported, r.error)


def test_srepr_fixpoint_after_reevaluation():
    r = tr(r"1-(1/2)^{1-\frac{1}{\alpha}}=0")[0]
    assert r.status == "ok"
    assert sp.srepr(sp.sympify(r.lhs)) == r.lhs


def test_real_data_guards_second_round():
    for latex, name in [
        (r"e^{- i \pi Sx/2 \lambda } = 2 \cos \frac{\pi S x}{2 \lambda}", "ambiguous_division"),
        (r"ds^2 = E \, dx^2 + 2F \, dx \, dy + G \, dy^2", "differential_form"),
        (r"e_2 e_3 e_1 e_3 = -e_2 e_3 e_3 e_1", "basis_product"),
        (r"\textbf{a}\cdot A \textbf{b} = \textbf{b} \cdot A^\mathsf{T} \textbf{a}", "transpose"),
        (r"\gamma^\mu \gamma^\nu + \gamma^\nu\gamma^\mu = 2 \eta^{\mu\nu}", "tensor_index"),
        (r"\operatorname{var}[X] = \sigma^2", "probability"),
        (r"\begin{align} \arccos(z) & z & & \sqrt{1 - z^2} & & -i\ln(z) = 0 \end{align}", "table_row"),
    ]:
        rs = tr(latex)
        assert any(name in r.has_unsupported for r in rs), (latex, [(r.has_unsupported, r.error) for r in rs])
        assert not any(r.status == "ok" and name in r.has_unsupported for r in rs)
    L, _, _ = sides(r"a e^{\lambda x} = 0")  # a power, not an index
    assert L == sp.Symbol("a") * e ** (sp.Symbol("lambda") * x)
    r = tr(r"x^{\alpha\beta} = 1")[0]  # only index letters: read as tensor indices (documented)
    assert "tensor_index" in r.has_unsupported
    L, R, _ = sides(r"X^{\mathrm{qc}}_0 = z^{ideal}")
    assert L == sp.Symbol("X_0^qc") and R == sp.Symbol("z^ideal")
    L, R, _ = sides(r"y[n] = x[n] + x[n-1]")
    assert L == sp.Function("y")(n) and R == sp.Function("x")(n) + sp.Function("x")(n - 1)
    L, R, _ = sides(r"d(k) = k + o(k)")
    assert L == sp.Function("d")(k) and R == k + sp.Function("o")(k)
    L, _, _ = sides(r"x/2 \cdot y = 1")  # explicit operator after the divisor is unambiguous
    assert L == x * y / 2
    rs = tr(r"\begin{align} a &= b \\ -c &= d \end{align}")  # new row starting with a minus
    assert len(rs) == 2 and sp.sympify(rs[1].lhs) == -sp.Symbol("c")


def test_real_data_guards_third_round():
    L, _, _ = sides(r"|\mathrm{N}(\alpha_1)| = 1")  # roman letter applied to an atom is a call
    assert L == sp.Abs(sp.Function("N")(sp.Symbol("alpha_1")))
    r = tr(r"\left\{\mathcal{F} f\right\}(-s) = 1")[0]  # transform applied by juxtaposition
    assert "operator" in r.has_unsupported
    r = tr(r"\frac{1}{2} r^2 d\theta_2 = \frac{1}{2} r^2 k d\theta_1")[0]
    assert "differential_form" in r.has_unsupported
    L, _, _ = sides(r"\frac{d\theta}{dt} = \omega")  # a derivative is not a differential form
    assert L == sp.Derivative(sp.Function("theta")(t), t)
