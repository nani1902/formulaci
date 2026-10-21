"""One test per preprocessing rule (spacing, delimiters, environments, conditions, ...)."""
import sympy as sp

from formulaci.translate.lexer import tokenize
from formulaci.translate.preprocess import normalize_source

from .conftest import sides, tr

x, y, a, b, n, k = sp.symbols("x y a b n k")


def notes_of(r):
    return (r.notes or "").splitlines()


def test_spacing_commands_are_ignored():
    L, R, r = sides(r"a\,b \; + \! c = d~e")
    assert L == a * b + sp.Symbol("c")
    assert R == sp.Symbol("d") * sp.Symbol("e")
    assert "pre:spacing" in notes_of(r)


def test_left_right_and_size_commands():
    L, R, r = sides(r"\left( x + 1 \right)^2 = \bigl[ x \bigr] \Bigg( y + 1 \Bigg)")
    assert L == (x + 1) ** 2 and R == x * (y + 1)
    assert "pre:left_right" in notes_of(r) and "pre:size" in notes_of(r)


def test_left_bar_is_abs_and_left_dot_dropped():
    L, R, _ = sides(r"\ln\left|\frac{x}{a}\right| = \left. y \right.")
    assert L == sp.log(sp.Abs(x / a)) and R == y


def test_displaystyle_textstyle_dropped():
    L, R, r = sides(r"\displaystyle \frac{1}{2} = \textstyle\tfrac12")
    assert L == R == sp.Rational(1, 2)
    assert "pre:style" in notes_of(r)


def test_operatorname_mathrm_text():
    L, R, _ = sides(r"\operatorname{arsinh} x = \mathrm{erf}(x) + \text{sgn}(x)")
    assert L == sp.asinh(x) and R == sp.erf(x) + sp.sign(x)


def test_mathbf_boldsymbol_vectors_flagged():
    L, _, r = sides(r"\mathbf{v} = \mathbf{w}")
    assert L == sp.Symbol("vec_v") and "vector_symbol:vec_v" in notes_of(r)
    r = tr(r"\boldsymbol{a}\cdot\boldsymbol{b} = \boldsymbol{b}\cdot\boldsymbol{a}")[0]
    assert r.status == "not_checkable" and "vector_product" in r.has_unsupported
    r = tr(r"\vec a \times \vec b = -\vec b \times \vec a")[0]
    assert r.status == "not_checkable"


def test_mathbb_is_unsupported():
    r = tr(r"\mathbb{E}[X] = \mu")[0]
    assert r.status == "not_checkable" and "expectation" in r.has_unsupported
    r = tr(r"x \in \mathbb{R}")[0]
    assert r.status == "not_checkable" and r.kind == "other"


def test_unicode_and_over_choose():
    assert "\\le" in normalize_source("x ≤ y", [])
    L, R, r = sides(r"{n \choose k} = {a \over b}")
    assert L == sp.binomial(n, k) and R == a / b
    assert "pre:over_choose" in notes_of(r)


def test_align_rows_split_into_records():
    rs = tr(r"\begin{align} \cos x &= \frac{e^{ix}+e^{-ix}}2 \\ \sin x &= \frac{e^{ix}-e^{-ix}}{2i} \end{align}")
    assert len(rs) == 2 and all(r.status == "ok" for r in rs)
    assert [r.index_in_chain for r in rs] == [0, 1]
    assert sp.sympify(rs[1].lhs) == sp.sin(x)


def test_aligned_continuation_rows_form_a_chain():
    rs = tr(r"\begin{aligned} (a+b)^2 &= (a+b)(a+b) \\ &= a^2 + 2ab + b^2 \end{aligned}")
    assert [r.kind for r in rs] == ["chain", "chain"]
    assert sp.sympify(rs[1].rhs) == a**2 + 2 * a * b + b**2


def test_multiline_expression_rows_and_alignat_columns():
    rs = tr(r"\begin{align} x &= a + b \\ &\qquad + c \end{align}")
    assert len(rs) == 1 and sp.sympify(rs[0].rhs) == a + b + sp.Symbol("c")
    rs = tr(r"\begin{alignat}{2} x &= 1 & \quad & y = 2 \end{alignat}")
    assert [sp.sympify(r.lhs) for r in rs] == [x, y]


def test_line_break_inside_brackets_continues():
    L, R, _ = sides("\\begin{align} x &= \\left(a + \\\\ b\\right) \\end{align}")
    assert R == a + b


def test_align_condition_column():
    rs = tr(r"\begin{align} \coth x &= -\frac{1}{\sinh^2 x} - 1 && x \neq 0 \end{align}")
    assert len(rs) == 1 and "cond: x \\neq 0" in notes_of(rs[0])
    # the condition column must not be glued into the expression (would give csch(x**2))
    assert sp.sympify(rs[0].rhs) == -1 / sp.sinh(x) ** 2 - 1


def test_cases_becomes_piecewise():
    L, R, r = sides(r"|x| = \begin{cases} x & \text{if } x \ge 0 \\ -x & \text{otherwise} \end{cases}")
    assert R == sp.Piecewise((x, x >= 0), (-x, True))
    L, R, r = sides(r"g = \begin{cases} 1 & (n>-1,\ a>0) \\ 0 & \text{otherwise} \end{cases}")
    assert R.args[0].cond == sp.And(n > -1, a > 0)


def test_cases_with_unparseable_condition_is_unsupported():
    r = tr(r"g(n) = \begin{cases} 1 & n \in \mathbb{P} \\ 0 & \text{otherwise}\end{cases}")[0]
    assert r.status == "not_checkable" and "cases_condition" in r.has_unsupported


def test_array_and_matrix_unsupported():
    r = tr(r"A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}")[0]
    assert r.status == "not_checkable" and "matrix" in r.has_unsupported


def test_trailing_conditions_recorded():
    cases = {
        r"\int_0^\infty e^{-ax}\,dx = \frac{1}{a} \quad (a>0)": "a>0",
        r"\sum_{k=0}^\infty x^k = \frac{1}{1-x}, \qquad |x|<1": "|x|<1",
        r"\Gamma(n) = (n-1)! \text{ for } n \ge 1": "n \\ge 1",
        r"\ln(xy) = \ln x + \ln y \quad \text{if } x,y > 0": "x,y > 0",
        r"x^0 = 1 \qquad\mbox{(for }x\neq 0\mbox{)}": "x\\neq 0",
    }
    for latex, cond in cases.items():
        r = tr(latex)[0]
        assert r.status == "ok", latex
        assert f"cond: {cond}" in notes_of(r), (latex, r.notes)


def test_comma_quad_separates_two_equations():
    rs = tr(r"\sin(-x) = -\sin x, \quad \cos(-x) = \cos x.")
    assert len(rs) == 2 and all(r.status == "ok" for r in rs)
    assert sp.sympify(rs[1].lhs) == sp.cos(x)


def test_trailing_punctuation_stripped():
    r = tr(r"e^{i\pi} + 1 = 0.")[0]
    assert r.status == "ok" and sp.sympify(r.rhs) == 0


def test_tag_label_color_phantom_dropped():
    L, R, _ = sides(r"x = \color{red}{y} \tag{1}\label{eq:a}\phantom{zz}")
    assert R == y


def test_stackrel_def_is_definition():
    r = tr(r"f(x) \stackrel{\text{def}}{=} x^2")[0]
    assert r.kind == "definition_like"
    r = tr(r"\phi \overset{\mathrm{def}}{=} \frac{1+\sqrt 5}{2}")[0]
    assert r.kind == "definition_like"


def test_tokenizer_keeps_spans():
    toks = tokenize(r"\frac{a}{b} \quad x")
    assert toks[0].value == "frac" and toks[0].start == 0
    assert any(t.kind == "SPACE" and t.value == "quad" for t in toks)
