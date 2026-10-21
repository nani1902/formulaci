"""Recursive-descent translator: one side of a relation (a token list) -> a SymPy expression.

Design rule: when the notation is ambiguous between a checkable and an uncheckable reading,
prefer the reading that downstream stages will *skip* over one that could produce a false
FAIL. Concretely: `f(x)` with an unknown `f` becomes an undefined function (semantics skips
it), never `f*x`; vectors, ellipses, `\\pm`, operators and set notation raise `Unsupported`.
Every heuristic decision is recorded in `ctx.notes`.
"""
from __future__ import annotations

import re
from contextlib import contextmanager
from dataclasses import dataclass, field

import sympy as sp
from sympy.core.function import AppliedUndef

from .lexer import Tok
from .preprocess import RELATION_CMDS, is_relation


class ParseError(ValueError):
    pass


class Unsupported(Exception):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name


GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "omicron", "rho", "sigma", "tau", "upsilon", "phi", "chi",
    "psi", "omega", "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi",
    "Psi", "Omega", "varpi", "ell", "hbar", "aleph", "varkappa", "digamma", "Alpha", "Beta",
    "Epsilon", "Zeta", "Eta", "Iota", "Kappa", "Mu", "Nu", "Omicron", "Rho", "Tau", "Chi",
}
GREEK_ALIAS = {"varepsilon": "epsilon", "vartheta": "theta", "varphi": "phi", "varrho": "rho",
               "varsigma": "sigma", "imath": "i", "jmath": "j", "varGamma": "Gamma"}

_TRIG = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
    "cosec": sp.csc, "ctg": sp.cot, "tg": sp.tan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "coth": sp.coth, "sech": sp.sech, "csch": sp.csch,
    "cosech": sp.csch,
}
_INV = {
    "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan, "arccot": sp.acot, "arcsec": sp.asec,
    "arccsc": sp.acsc, "arccosec": sp.acsc, "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "arsinh": sp.asinh, "arcsinh": sp.asinh, "asinh": sp.asinh, "arsh": sp.asinh,
    "arcosh": sp.acosh, "arccosh": sp.acosh, "acosh": sp.acosh, "arch": sp.acosh,
    "artanh": sp.atanh, "arctanh": sp.atanh, "atanh": sp.atanh, "arth": sp.atanh,
    "arcoth": sp.acoth, "arccoth": sp.acoth, "acoth": sp.acoth,
    "arsech": sp.asech, "arcsech": sp.asech, "asech": sp.asech,
    "arcsch": sp.acsch, "arccsch": sp.acsch, "acsch": sp.acsch, "arcosech": sp.acsch,
}
INVERSE_OF = {sp.sin: sp.asin, sp.cos: sp.acos, sp.tan: sp.atan, sp.cot: sp.acot, sp.sec: sp.asec,
              sp.csc: sp.acsc, sp.sinh: sp.asinh, sp.cosh: sp.acosh, sp.tanh: sp.atanh,
              sp.coth: sp.acoth, sp.sech: sp.asech, sp.csch: sp.acsch}
_OTHER = {
    "exp": sp.exp, "ln": sp.log, "log": sp.log, "erf": sp.erf, "erfc": sp.erfc, "erfi": sp.erfi,
    "sgn": sp.sign, "sign": sp.sign, "signum": sp.sign, "arg": sp.arg, "Arg": sp.arg, "Re": sp.re,
    "Im": sp.im, "gcd": sp.gcd, "lcm": sp.lcm, "max": sp.Max, "min": sp.Min, "Ei": sp.Ei,
    "Si": sp.Si, "Ci": sp.Ci, "Shi": sp.Shi, "Chi": sp.Chi, "li": sp.li, "Li": sp.Li,
    "Ai": sp.airyai, "Bi": sp.airybi, "Gamma": sp.gamma, "zeta": sp.zeta, "Beta": sp.beta,
    "B": sp.beta, "digamma": sp.digamma, "erfinv": sp.erfinv, "erfcinv": sp.erfcinv,
    "Res": None, "sinc": None, "gd": None, "versin": None, "Log": None,
}
KNOWN_FUNCS: dict[str, object] = {**_TRIG, **_INV, **_OTHER}
# Names that are functions only when written as commands/operatorname, never as bare letters.
BARE_WORD_FUNCS = sorted(
    ["sin", "cos", "tan", "cot", "sec", "csc", "sinh", "cosh", "tanh", "coth", "sech", "csch",
     "arcsin", "arccos", "arctan", "exp", "log", "ln", "erf", "erfc", "sgn", "max", "min", "gcd",
     "arsinh", "arcosh", "artanh", "arcsinh", "arccosh", "arctanh", "lim", "det", "mod", "Re", "Im"],
    key=len, reverse=True)
UNSUPPORTED_WORDS = {
    "det": "determinant", "tr": "trace", "Tr": "trace", "rank": "matrix", "diag": "matrix",
    "Var": "probability", "Cov": "probability", "E": "probability", "Pr": "probability",
    "P": None, "mod": "modular", "bmod": "modular", "pmod": "modular", "deg": "degree_of",
    "dim": "dimension", "ker": "kernel", "hom": "hom", "sup": "sup_inf", "inf": "sup_inf",
    "liminf": "sup_inf", "limsup": "sup_inf", "argmax": "argmax", "argmin": "argmax",
    "lg": "log_base_ambiguous", "Ln": "multivalued_log", "curl": "vector_calculus",
    "div": "vector_calculus", "grad": "vector_calculus", "sn": "elliptic", "cn": "elliptic",
    "dn": "elliptic", "am": "elliptic", "cis": None, "PV": "principal_value", "vol": "measure",
    "var": "probability", "cov": "probability", "corr": "probability", "Corr": "probability",
    "Cor": "probability", "Prob": "probability", "Ex": "probability", "Std": "probability", "SD": "probability",
}
INDEX_LETTERS = set("ijklmnpqrst")
GREEK_FUNCS = {"Gamma", "zeta", "Beta"}
ALWAYS_FUNC = {"f", "g", "h", "F", "G", "H", "phi", "psi", "Phi", "Psi", "chi", "o", "O"}
TENSOR_INDEX = {"mu", "nu", "alpha", "beta", "rho", "sigma", "kappa", "lambda", "tau"}
NEVER_FUNC = {"e", "i"}
ACCENTS = {
    "hat": "hat", "widehat": "hat", "tilde": "tilde", "widetilde": "tilde", "bar": "bar",
    "overline": "bar", "dot": "dot", "ddot": "ddot", "check": "check", "breve": "breve",
    "acute": "acute", "grave": "grave", "mathring": "ring", "dddot": "dddot",
}
SCRIPT_STYLE = {"mathcal": "cal", "mathscr": "scr", "mathfrak": "frak", "mathsf": "sf", "mathtt": "tt"}
VECTOR_STYLE = {"vec", "mathbf", "boldsymbol", "bm", "bold", "pmb", "overrightarrow", "vb", "textbf", "mathbfit"}
SET_CMDS = {"R", "Z", "N", "Q", "C", "Complex", "Reals", "Naturals", "Integers", "Rationals",
            "emptyset", "varnothing", "cup", "cap", "setminus", "bigcup", "bigcap", "mid", "subset",
            "backslash", "complement"}
ELLIPSIS = {"dots", "cdots", "ldots", "ddots", "vdots", "dotsb", "dotsc", "dotsm", "dotsi", "dotso", "hdots"}
UNSUPPORTED_CMDS = {
    "iint": "multiple_integral", "iiint": "multiple_integral", "iiiint": "multiple_integral",
    "oint": "contour_integral", "oiint": "contour_integral", "nabla": "vector_calculus",
    "langle": "inner_product", "rangle": "inner_product", "lVert": "norm", "rVert": "norm",
    "|": "norm", "Vert": "norm", "otimes": "tensor", "oplus": "direct_sum", "wedge": "wedge",
    "vee": "logic", "land": "logic", "lor": "logic", "lnot": "logic", "neg": "logic",
    "neg": "logic", "star": "convolution", "ast": "convolution", "circ": "composition",
    "bmod": "modular", "pmod": "modular", "mod": "modular", "pod": "modular", "dagger": "adjoint",
    "top": "transpose", "intercal": "transpose", "mathcal": "operator", "mathscr": "operator",
    "mathfrak": "operator", "Box": "operator", "square": "operator", "triangle": "operator",
    "underline": "falling_factorial", "overbrace": None, "underbrace": None, "not": "negation",
    "bigoplus": "direct_sum", "bigotimes": "tensor", "coprod": "coproduct", "Pr": "probability",
    "det": "determinant", "sup": "sup_inf", "inf": "sup_inf", "liminf": "sup_inf",
    "limsup": "sup_inf", "deg": "degree_of", "dim": "dimension", "ker": "kernel", "hom": "hom",
    "lg": "log_base_ambiguous", "atopfrac": "atop", "operatorname": "operator", "stackrel": "stackrel",
    "overset": "overset", "underset": "underset", "sideset": "sideset", "prescript": "prescript",
    "cancelto": "cancel", "bra": "bra_ket", "ket": "bra_ket", "braket": "bra_ket",
    "hookrightarrow": "map", "uparrow": "knuth_arrow", "downarrow": "knuth_arrow",
    "Uparrow": "knuth_arrow", "binom": None, "aleph": "cardinal", "infin": None, "propto": "proportional",
    "pm": "pm", "mp": "mp", "partial": "partial_operator", "emptygroup": "hypergeometric",
    "Re": None, "Im": None, "Diamond": "operator", "triangledown": "operator",
    "sum": None, "prod": None, "lfloor": None, "lceil": None, "lvert": None,
    "perp_sup": "orthogonal_complement", "exists": "quantifier", "nexists": "quantifier",
    "forall": "quantifier", "angle": "geometry", "measuredangle": "geometry", "triangle": "geometry",
    "bigwedge": "wedge", "bigvee": "logic", "odot": "hadamard", "oslash": "operator", "ominus": "operator",
    "models": "logic", "vdash": "logic", "land": "logic", "lor": "logic", "Box": "operator",
    "langle": "inner_product", "sharp": "music", "flat": "music", "natural": "music", "$": "currency",
}


@dataclass
class Ctx:
    """Per-formula state shared by all sides."""
    notes: list[str] = field(default_factory=list)
    funcs: set[str] = field(default_factory=set)
    functions_used: set[str] = field(default_factory=set)
    vector_syms: set[str] = field(default_factory=set)
    # letters used as ordinary symbols somewhere in the formula (outside subscripts)
    main_letters: set[str] = field(default_factory=set)
    # bases written with an expression subscript somewhere (`x_{n-1}`): a sequence, not symbols
    indexed_bases: set[str] = field(default_factory=set)
    # f(a+b) where f is also used bare and is not clearly a coefficient: refuse to guess
    ambiguous_funcs: set[str] = field(default_factory=set)
    # names indexed with square brackets somewhere (`x[n]`)
    bracket_funcs: set[str] = field(default_factory=set)
    # prose around the formula talks about complex numbers / conjugates
    complex_context: bool = False
    # prose mentions Legendre/Jacobi/residue symbols
    residue_context: bool = False
    # prose mentions the incomplete gamma function
    incomplete_gamma_context: bool = False
    # letters used on their own, without a subscript (`z` in `z \bar z`, not `X` in `X_i`)
    plain_letters: set[str] = field(default_factory=set)
    # symbol names built from a base plus a written subscript (`x_1`, `B_{1,2}`), as opposed to styled names
    subscripted_names: set[str] = field(default_factory=set)

    def note(self, s: str) -> None:
        if s not in self.notes:
            self.notes.append(s)


OPEN = {"(": ")", "[": "]", "{": "}"}
MAX_INT_POW = 2000
MAX_FACTORIAL = 2000


def _is_char(t: Tok | None, v: str) -> bool:
    return t is not None and t.kind == "CHAR" and t.value == v


def _is_cmd(t: Tok | None, *v: str) -> bool:
    return t is not None and t.kind == "CMD" and t.value in v


def _sym_cmd_name(t: Tok) -> str | None:
    """Name of a symbol-like command (greek letter), else None."""
    if t.kind != "CMD":
        return None
    if t.value in GREEK:
        return t.value
    return GREEK_ALIAS.get(t.value)


def group_end(toks: list[Tok], i: int) -> int:
    """toks[i] is an opener; return index of its matching closer."""
    depth = 0
    for j in range(i, len(toks)):
        t = toks[j]
        if t.kind == "CHAR" and t.value in "([{":
            depth += 1
        elif t.kind == "CHAR" and t.value in ")]}":
            depth -= 1
            if depth == 0:
                return j
        elif t.kind == "BEGIN":
            depth += 1
        elif t.kind == "END":
            depth -= 1
            if depth == 0:
                return j
    raise ParseError("unbalanced group")


def _check_pow(base, exp):
    if base.is_Number and exp.is_Number and exp.is_Integer and abs(exp) > MAX_INT_POW and abs(base) != 1:
        raise Unsupported("huge_number")
    if base.is_Number and exp.is_Number and not exp.is_Integer and abs(base) > 10**50:
        raise Unsupported("huge_number")
    return sp.Pow(base, exp)


class Parser:
    def __init__(self, toks: list[Tok], ctx: Ctx):
        self.toks = [t for t in toks if t.kind != "SPACE" and not (t.kind == "TEXT" and not t.value.strip())]
        self.pos = 0
        self.ctx = ctx
        self.abs_depth = 0
        self.integrals: list[dict] = []
        self.depth = 0
        self.bound: list[str] = []
        self.level = 0  # sub-parse nesting (brace groups, parens, fraction parts)

    # ---------------------------------------------------------------- token helpers
    def peek(self, k: int = 0) -> Tok | None:
        j = self.pos + k
        return self.toks[j] if j < len(self.toks) else None

    def next(self) -> Tok:
        t = self.peek()
        if t is None:
            raise ParseError("unexpected end of input")
        self.pos += 1
        return t

    def expect_char(self, v: str) -> Tok:
        t = self.next()
        if not _is_char(t, v):
            raise ParseError(f"expected '{v}', got {t.value!r}")
        return t

    def at_end(self) -> bool:
        return self.pos >= len(self.toks)

    def sub(self, toks: list[Tok], fn=None):
        """Parse a token sub-list with the same state; it must be consumed completely."""
        saved = (self.toks, self.pos, self.abs_depth)
        self.toks, self.pos, self.abs_depth = toks, 0, 0
        self.level += 1
        try:
            e = (fn or self.parse_expr)()
            if not self.at_end():
                raise ParseError(f"unexpected {self.peek().value!r}")
            return e
        finally:
            self.toks, self.pos, self.abs_depth = saved
            self.level -= 1

    def read_arg(self) -> list[Tok]:
        """A macro argument: a brace group's contents, or a single token (with its own args)."""
        t = self.peek()
        if t is None:
            raise ParseError("missing argument")
        if _is_char(t, "{"):
            e = group_end(self.toks, self.pos)
            out = self.toks[self.pos + 1:e]
            self.pos = e + 1
            return out
        start = self.pos
        self.pos += 1
        if t.kind == "CMD":
            nargs = {"frac": 2, "tfrac": 2, "dfrac": 2, "binom": 2, "tbinom": 2, "sqrt": 1, "mathrm": 1,
                     "mathbf": 1, "vec": 1, "hat": 1, "bar": 1, "tilde": 1, "boldsymbol": 1, "mathit": 1,
                     "dot": 1, "ddot": 1, "mathbb": 1, "mathcal": 1, "mathfrak": 1, "mathscr": 1,
                     "mathsf": 1, "overline": 1, "underline": 1, "widehat": 1, "widetilde": 1, "bm": 1,
                     "check": 1, "breve": 1}.get(t.value, 0)
            for _ in range(nargs):
                self.read_arg()
        return self.toks[start:self.pos]

    def read_scripts(self) -> tuple[list[Tok] | None, list[Tok] | None]:
        sub = sup = None
        while True:
            t = self.peek()
            if _is_char(t, "_") and sub is None:
                self.pos += 1
                sub = self.read_arg()
            elif _is_char(t, "^") and sup is None:
                self.pos += 1
                sup = self.read_arg()
            else:
                return sub, sup

    # ---------------------------------------------------------------- grammar
    def parse_side(self):
        if not self.toks:
            raise Unsupported("empty_side")
        e = self.parse_expr()
        if not self.at_end():
            t = self.peek()
            if _is_char(t, ",") or _is_char(t, ";"):
                raise Unsupported("list")
            if _is_cmd(t, "rvert") and (_is_char(self.peek(1), "_") or _is_char(self.peek(1), "^")):
                raise Unsupported("evaluation_bar")
            raise ParseError(f"unexpected {t.value!r}")
        return e

    def parse_expr(self):
        self.depth += 1
        try:
            my_int = self.integrals[-1] if self.integrals and self.integrals[-1]["depth"] == self.depth else None
            t = self.peek()
            sign = 1
            if _is_char(t, "-"):
                self.pos += 1
                sign = -1
            elif _is_char(t, "+"):
                self.pos += 1
            elif _is_cmd(t, "pm", "mp"):
                raise Unsupported("pm")
            terms = [sign * self.parse_term()]
            while True:
                if my_int is not None and my_int["var"] is not None:
                    break
                t = self.peek()
                if _is_char(t, "+"):
                    self.pos += 1
                    terms.append(self.parse_term())
                elif _is_char(t, "-"):
                    self.pos += 1
                    terms.append(-self.parse_term())
                elif _is_cmd(t, "pm", "mp"):
                    raise Unsupported("pm")
                else:
                    break
            return sp.Add(*terms)
        finally:
            self.depth -= 1

    def _vector_count(self, e) -> bool:
        return bool(self.ctx.vector_syms) and any(s.name in self.ctx.vector_syms for s in e.free_symbols)

    def parse_term(self):
        factors = []
        nvec = 0
        after_div = False
        integral = self.integrals[-1] if self.integrals else None
        while True:
            t = self.peek()
            if t is None:
                break
            if integral is not None and integral["var"] is None and self.is_differential():
                integral["var"] = self.consume_differential()
                if factors:
                    break
                continue
            if not factors:
                f = self.parse_factor()
            elif _is_cmd(t, "cdot", "times", "centerdot", "bullet"):
                after_div = False
                self.pos += 1
                if _is_cmd(t, "times"):
                    self.ctx.note("op:times")
                f = self.parse_factor()
            elif _is_char(t, "*"):
                raise Unsupported("asterisk_op")
            elif _is_char(t, "/") or _is_cmd(t, "div"):
                self.pos += 1
                f = self.parse_factor()
                if self._vector_count(f):
                    raise Unsupported("vector_division")
                factors.append(sp.Pow(f, -1))
                after_div = True
                continue
            elif self.can_start_factor(t):
                if after_div:
                    # `x/2\lambda`, `1/2\pi`: (x/2)*lambda or x/(2*lambda)? both readings are common
                    raise Unsupported("ambiguous_division")
                before = self.toks[self.pos - 1] if self.pos > 0 else None
                if (_is_cmd(t, "frac", "tfrac", "dfrac") and factors[-1].is_Integer and before is not None
                        and before.kind == "DIGIT" and _numeric_frac_follows(self.toks, self.pos)):
                    raise Unsupported("mixed_number")  # 3\frac12 = 3 + 1/2, not 3 * 1/2
                before2 = self.toks[self.pos - 2] if self.pos > 1 else None
                if t.kind == "DIGIT" and before is not None and before.kind == "LETTER" and before.end == t.start \
                        and before.value not in ("i", "j") \
                        and not (before2 is not None and before2.kind == "CHAR" and before2.value in "^_") \
                        and not _symbolic_power_follows(self.toks, self.pos):
                    raise Unsupported("letter_digit")  # h2 < h1: h_2, not 2h  (but (-1)^k 2^n and n2^{n-1} are fine)
                if _is_char(t, "(") and before is not None and before.kind == "CHAR" and before.value in ")]}" and (
                        before.value != "}" or _standalone_group_before(self.toks, self.pos - 1)):
                    e_ = group_end(self.toks, self.pos)
                    inner_ = self.toks[self.pos + 1:e_]
                    if not all(x.kind == "DIGIT" for x in inner_) and (
                            _is_single_atom(inner_) or (inner_ and _is_char(inner_[0], "-") and _is_single_atom(inner_[1:]))):
                        # `(f*g)(t)`, `[L f](y)`: an operator expression applied to an argument
                        raise Unsupported("operator_application")
                f = self.parse_factor()
                prev = factors[-1]
                if (isinstance(f, sp.Symbol) and isinstance(prev, sp.Symbol) and f.name.startswith("e_")
                        and prev.name.startswith("e_")):
                    # `e_1 e_2`: basis elements of a (possibly non-commutative) algebra
                    raise Unsupported("basis_product")
                if (isinstance(f, sp.Symbol) and isinstance(prev, sp.Symbol) and len(f.name) == 1
                        and len(prev.name) == 1 and f.name.isupper() and prev.name.isupper()):
                    # `AB`, `OA + OB`: matrix products or geometric segments, not scalars
                    raise Unsupported("uppercase_juxtaposition")
            else:
                break
            if self._vector_count(f):
                nvec += 1
                if nvec >= 2:
                    raise Unsupported("vector_product")
            factors.append(f)
        if not factors:
            if integral is not None and integral["var"] is not None:
                return sp.Integer(1)
            t = self.peek()
            raise ParseError(f"expected operand, got {t.value if t else 'end'!r}")
        return sp.Mul(*factors)

    def can_start_factor(self, t: Tok) -> bool:
        if t.kind in ("LETTER", "DIGIT", "OPNAME", "BEGIN"):
            return True
        if t.kind == "TEXT":
            return True
        if t.kind == "CHAR":
            if t.value in "([{":
                return True
            if t.value == "|":
                return self.abs_depth == 0
            if t.value == ".":
                nxt = self.peek(1)
                return nxt is not None and nxt.kind == "DIGIT"
            return False
        if t.kind == "CMD":
            if t.value in RELATION_CMDS or t.value in ("cdot", "times", "div", "pm", "mp", "rvert",
                                                          "rfloor", "rceil", "rangle", "rVert", "}", "%"):
                return False
            if t.value == "lvert":
                return True
            return True
        return False

    def parse_factor(self):
        t = self.peek()
        if _is_char(t, "-"):
            self.pos += 1
            return -self.parse_factor()
        if _is_char(t, "+"):
            self.pos += 1
            return self.parse_factor()
        return self.parse_postfix(self.parse_primary())

    def parse_postfix(self, e):
        while True:
            t = self.peek()
            if _is_char(t, "^"):
                self.pos += 1
                arg = self.read_arg()
                e = self.apply_superscript(e, arg)
            elif _is_char(t, "!"):
                self.pos += 1
                if _is_char(self.peek(), "!"):
                    self.pos += 1
                    e = sp.factorial2(e)
                else:
                    if e.is_Integer and e > MAX_FACTORIAL:
                        raise Unsupported("huge_number")
                    e = sp.factorial(e)
            elif _is_char(t, "_"):
                raise Unsupported("subscript_on_expression")
            elif _is_char(t, "'"):
                raise Unsupported("prime_on_expression")
            elif _is_cmd(t, "%"):
                self.pos += 1
                e = e / 100
                self.ctx.note("percent")
            else:
                return e

    def apply_superscript(self, base, arg: list[Tok]):
        if len(arg) >= 1 and all(_is_cmd(a, "prime") or _is_char(a, "'") for a in arg):
            raise Unsupported("prime_on_expression")
        if len(arg) == 1 and _is_cmd(arg[0], "circ"):
            if not base.is_Number:
                raise Unsupported("superscript_label")  # G^\circ: standard state, not degrees
            self.ctx.note("degrees")
            return base * sp.pi / 180
        if len(arg) == 1 and (_is_char(arg[0], "*") or _is_cmd(arg[0], "ast")):
            raise Unsupported("conjugate_star")
        if len(arg) == 1 and (_is_cmd(arg[0], "top", "intercal", "dagger") or _is_char(arg[0], "T") and False):
            raise Unsupported("transpose")
        if len(arg) == 1 and arg[0].kind == "CHAR" and arg[0].value in "+-":
            raise Unsupported("one_sided_superscript")
        word = _roman_word(arg)
        plain = base.is_Number or base == sp.Symbol("e")
        if word == "T" and not plain:
            raise Unsupported("transpose")  # A^T, A^\mathsf{T}, u^\textsf{T}
        if not plain:
            label = _superscript_label(base, arg, word, self.ctx.subscripted_names)
            if label:
                # X^{(0)}, f^{(n)}, F^H, M^X, A^\mathrm{g}, G^\circ, E^\infty, a^\omega, h^i_k, C_3^0
                raise Unsupported("superscript_label")
        if not plain and _tensor_indices(arg):
            raise Unsupported("tensor_index")  # \gamma^\mu, B^{i\alpha}
        exp = self.sub(arg)
        if exp == -1 and isinstance(base, sp.Symbol) and base.name[:1].isupper() and len(base.name) == 1:
            raise Unsupported("inverse_or_reciprocal")  # U^{-1}, H^{-1}: inverse map, matrix inverse
        if self._vector_count(base):
            raise Unsupported("vector_power")
        return _check_pow(base, exp)

    # ---------------------------------------------------------------- primaries
    def parse_primary(self):
        t = self.peek()
        if t is None:
            raise ParseError("unexpected end of input")
        k, v = t.kind, t.value
        if k == "DIGIT" or (k == "CHAR" and v == "."):
            return self.parse_number()
        if k == "LETTER":
            return self.parse_letter()
        if k == "CHAR":
            if v in "([":
                return self.parse_paren()
            if v == "{":
                e = group_end(self.toks, self.pos)
                inner = self.toks[self.pos + 1:e]
                self.pos = e + 1
                # `\int {f(x)\,dx}`: a brace group around the integrand is transparent
                with self.transparent_for_differential():
                    return self.sub(inner)
            if v == "|":
                return self.parse_abs_bar()
            raise ParseError(f"unexpected {v!r}")
        if k == "TEXT":
            return self.parse_text()
        if k == "OPNAME":
            self.pos += 1
            return self.parse_named(v, t)
        if k == "BEGIN":
            return self.parse_env()
        if k == "CMD":
            return self.parse_command()
        raise ParseError(f"unexpected token {v!r}")

    def parse_number(self):
        digits = ""
        while True:
            t = self.peek()
            if t is not None and t.kind == "DIGIT":
                digits += t.value
                self.pos += 1
            elif _is_char(t, ".") and "." not in digits and _peek_kind(self, 1) == "DIGIT":
                digits += "."
                self.pos += 1
            elif (_is_char(t, "{") and _is_char(self.peek(1), ",") and _is_char(self.peek(2), "}")
                  and _peek_kind(self, 3) == "DIGIT"):
                self.pos += 3  # 1{,}000 thousands separator
                self.ctx.note("pre:thousands_sep")
            elif (_is_char(t, "{") and _is_char(self.peek(1), ".") and _is_char(self.peek(2), "}")
                  and _peek_kind(self, 3) == "DIGIT" and "." not in digits):
                self.pos += 3  # 1{.}67 decimal point
                digits += "."
            else:
                break
        if digits.startswith("."):
            digits = "0" + digits
        if "." in digits:
            return sp.Rational(digits)
        return sp.Integer(digits)

    def parse_paren(self):
        open_ = self.next().value
        close = OPEN[open_]
        start = self.pos - 1
        e = group_end(self.toks, start)
        closer = self.toks[e]
        if closer.value != close and not (open_ == "[" and closer.value == ")") and not (open_ == "(" and closer.value == "]"):
            raise ParseError("mismatched brackets")
        if closer.value != close:
            raise Unsupported("interval")
        inner = self.toks[self.pos:e]
        self.pos = e + 1
        if _is_lone_cmd(inner, ("binom", "tbinom", "dbinom"), 2):
            raise Unsupported("multiset_coefficient")  # \left(\!\binom{n}{k}\!\right)
        if _is_lone_cmd(inner, ("frac", "dfrac", "tfrac"), 2) and not _is_char(self.peek(), "^") and (
                open_ == "[" or self.ctx.residue_context):
            raise Unsupported("residue_symbol")  # Legendre/Jacobi (a/p), quartic [a/p]
        parts = _split_top(inner, ",")
        if len(parts) > 1:
            raise Unsupported("tuple")
        if any(is_relation(x) for x in _top_level(inner)):
            raise Unsupported("relation_in_parens")
        return self.sub(inner)

    def parse_abs_bar(self):
        self.next()
        self.abs_depth += 1
        saved_int = self.integrals
        try:
            e = self.parse_expr()
        finally:
            self.abs_depth -= 1
        t = self.next()
        if not _is_char(t, "|"):
            raise ParseError("unclosed |")
        if _is_char(self.peek(), "_") or _is_char(self.peek(), "^") and False:
            raise Unsupported("evaluation_bar")
        del saved_int
        return sp.Abs(e)

    def parse_delimited(self, closer: str):
        """Parse up to a closing command token (rvert/rfloor/rceil)."""
        depth0 = self.abs_depth
        self.abs_depth = 0
        try:
            e = self.parse_expr()
        finally:
            self.abs_depth = depth0
        t = self.next()
        if not _is_cmd(t, closer):
            if closer == "rvert" and _is_char(t, "|"):
                return e
            raise ParseError(f"expected \\{closer}")
        return e

    def parse_text(self):
        t = self.next()
        w = t.value.strip()
        if w == "d" or w == "d}":
            raise Unsupported("differential_form")
        if w in KNOWN_FUNCS or w in UNSUPPORTED_WORDS:
            return self.parse_named(w, t)
        if " " in w or not w.isalpha():
            raise Unsupported("prose")
        if len(w) == 1:
            self.ctx.note(f"text_symbol:{w}")
            return self.finish_symbol(w, t)
        # `\text{rpi}(x)` is a named function; `\text{median}`, `\text{kg}` alone are words
        return self.parse_named(w, t)

    def parse_command(self):
        t = self.next()
        v = t.value
        g = _sym_cmd_name(t)
        if v == "pi":
            if "pi" in self.ctx.funcs and _is_char(self.peek(), "("):
                self.ctx.note("ambig:pi_as_function")
                return self.parse_symbol_from("pi", t)
            return sp.pi
        if v in ("infty", "infin"):
            return sp.oo
        if g is not None:
            nxt = self.peek()
            if g in ("Delta", "delta") and nxt is not None and (nxt.kind == "LETTER" or (
                    _sym_cmd_name(nxt) is not None and nxt.value not in GREEK_FUNCS)) and not _is_char(self.peek(1), "("):
                # `\Delta f`, `\Delta\epsilon`, `\delta y`: one increment quantity, not Delta*f
                self.pos += 1
                inner = nxt.value if nxt.kind == "LETTER" else _sym_cmd_name(nxt)
                self.ctx.note(f"increment:{g}{inner}")
                return self.parse_symbol_from(f"{g}_{inner}", nxt)
            if g in ("Gamma", "zeta", "Beta") and self.function_follows():
                return self.parse_named(g, t)
            if g == "gamma" and self._paren_arity() == 2:
                if self.ctx.incomplete_gamma_context:
                    return self.apply_known("lowergamma", sp.lowergamma)
                # \gamma(a, q) is also the Euler-Lehmer constant, Stieltjes constants, ...
                self.ctx.funcs.add("gamma")
                return self.parse_symbol_from("gamma", t)
            return self.parse_symbol_from(g, t)
        if v in ("frac", "dfrac", "tfrac", "cfrac"):
            return self.parse_frac()
        if v in ("binom", "tbinom", "dbinom"):
            a = self.sub(self.read_arg())
            b = self.sub(self.read_arg())
            return sp.binomial(a, b)
        if v == "sqrt":
            idx = None
            if _is_char(self.peek(), "["):
                e = group_end(self.toks, self.pos)
                idx = self.sub(self.toks[self.pos + 1:e])
                self.pos = e + 1
            arg = self.sub(self.read_arg())
            if idx is None:
                return sp.sqrt(arg)
            self.ctx.note("nth_root")
            return _check_pow(arg, 1 / idx) if not idx.is_Number else sp.Pow(arg, sp.Integer(1) / idx)
        if v in ("sum", "prod"):
            return self.parse_bigop(v)
        if v == "int":
            return self.parse_integral()
        if v == "lim":
            return self.parse_limit()
        if v in ("lvert", "vert"):
            return sp.Abs(self.parse_delimited("rvert"))
        if v == "lfloor":
            return sp.floor(self.parse_delimited("rfloor"))
        if v == "lceil":
            return sp.ceiling(self.parse_delimited("rceil"))
        if v in ("{", "lbrace", "}", "rbrace"):
            raise Unsupported("set_notation")
        if v in ELLIPSIS:
            raise Unsupported("ellipsis")
        if v in SET_CMDS:
            raise Unsupported("set_notation")
        if v in ("mathrm", "rm", "mathup", "textrm", "mathop"):
            return self.parse_roman()
        if v == "mathbb":
            arg = self.read_arg()
            name = "".join(a.value for a in arg)
            if name in ("E",):
                raise Unsupported("expectation")
            if name in ("1", "I"):
                raise Unsupported("indicator")
            raise Unsupported("set_notation")
        if v in VECTOR_STYLE:
            return self.parse_styled_symbol(v)
        if v in SCRIPT_STYLE:
            arg = self.read_arg()
            if len(arg) == 1 and arg[0].kind == "LETTER":
                name = f"{SCRIPT_STYLE[v]}_{arg[0].value}"
                nxt = self.peek()
                if (v == "mathcal" and nxt is not None and not _is_char(nxt, "(") and not _is_char(nxt, "_")
                        and not _is_char(nxt, "^") and self.can_start_factor(nxt)):
                    # `\mathcal{F} f`, `\mathcal{L}\{f\}`: a transform applied by juxtaposition
                    raise Unsupported("operator")
                self.ctx.note(f"styled_symbol:{name}")
                return self.parse_symbol_from(name, arg[0])
            raise Unsupported("operator")
        if v in ACCENTS:
            return self.parse_accent(v)
        if v in ("overbrace", "underbrace"):
            e = self.sub(self.read_arg())
            if _is_char(self.peek(), "_") or _is_char(self.peek(), "^"):
                self.pos += 1
                self.read_arg()
            self.ctx.note("brace_annotation")
            return e
        if v in KNOWN_FUNCS:
            return self.parse_named(v, t)
        if v in ("hbar",):
            return self.parse_symbol_from("hbar", t)
        if v in UNSUPPORTED_CMDS and UNSUPPORTED_CMDS[v]:
            raise Unsupported(UNSUPPORTED_CMDS[v])
        if v in UNSUPPORTED_WORDS and UNSUPPORTED_WORDS[v]:
            raise Unsupported(UNSUPPORTED_WORDS[v])
        if v == "prime":
            raise Unsupported("prime_on_expression")
        if v == "#":
            raise Unsupported("primorial")
        if v in ("cdot", "times"):
            raise Unsupported("dangling_operator")
        raise ParseError(f"unknown command \\{v}")

    # ---------------------------------------------------------------- symbols & functions
    def function_follows(self) -> bool:
        """After a name: is the next thing `(`, possibly after scripts?"""
        j = self.pos
        while j < len(self.toks) and (_is_char(self.toks[j], "_") or _is_char(self.toks[j], "^")
                                      or _is_char(self.toks[j], "'")):
            if _is_char(self.toks[j], "'"):
                j += 1
                continue
            j += 1
            if j < len(self.toks) and _is_char(self.toks[j], "{"):
                j = group_end(self.toks, j) + 1
            else:
                j += 1
        return j < len(self.toks) and _is_char(self.toks[j], "(")

    def _paren_arity(self) -> int:
        if not _is_char(self.peek(), "("):
            return 0
        e = group_end(self.toks, self.pos)
        return len(_split_top(self.toks[self.pos + 1:e], ","))

    def parse_letter(self):
        # multi-letter function word written without a backslash (`sin x`)
        word = ""
        j = self.pos
        while j < len(self.toks) and self.toks[j].kind == "LETTER":
            word += self.toks[j].value
            j += 1
        prev = self.toks[self.pos - 1] if self.pos > 0 else None
        if len(word) >= 2 and not (prev is not None and prev.kind == "LETTER"):
            for w in BARE_WORD_FUNCS:
                if word.startswith(w):
                    t = self.toks[self.pos]
                    self.pos += len(w)
                    self.ctx.note(f"bare_function_name:{w}")
                    if w == "lim":
                        return self.parse_limit()
                    return self.parse_named(w, t)
        t = self.next()
        return self.parse_symbol_from(t.value, t)

    def parse_symbol_from(self, base: str, t: Tok, vector: bool = False):
        """Symbol-like base already consumed; handle subscripts, primes and application."""
        sub = None
        sup = None
        primes = 0
        while True:
            u = self.peek()
            if _is_char(u, "_") and sub is None:
                self.pos += 1
                sub = self.read_arg()
            elif _is_char(u, "'"):
                self.pos += 1
                primes += 1
            elif _is_char(u, "^") and sup is None:
                self.pos += 1
                arg = self.read_arg()
                if arg and all(_is_cmd(a, "prime") or _is_char(a, "'") for a in arg):
                    primes += len(arg)
                else:
                    sup = arg
            else:
                break
        name = base
        indexed_arg = None
        if sub is not None:
            sname, simple = _script_name(sub)
            letters = _script_letters(sub)
            word_sub = (sum(1 for x in sub if x.kind == "LETTER") >= 2 and all(x.kind == "LETTER" for x in sub)) or any(
                x.kind in ("TEXT", "OPNAME") or _is_cmd(x, "mathrm", "rm", "text", "textrm", "mathit", "mathsf") for x in sub
            ) or _label_subscript(sub)
            indexed = (self.bound and any(x in self.bound for x in letters)) or (
                not word_sub and any(x in self.ctx.main_letters for x in letters)) or (
                base in self.ctx.indexed_bases and letters and not word_sub)
            if indexed and not (base in self.ctx.funcs and _is_char(self.peek(), "(")):
                indexed_arg = sub
            elif (word_sub and len(sub) <= 3 and all(x.value in INDEX_LETTERS for x in sub)
                  and not (base in self.ctx.funcs and _is_char(self.peek(), "("))):
                # a_{ij}: a matrix/tensor entry, i.e. a function of its indices
                indexed_arg = [y for x in sub for y in (x, Tok("CHAR", ",", 0, 0))][:-1]
            else:
                name = f"{base}_{sname}"
                self.ctx.subscripted_names.add(name)
                if not simple:
                    self.ctx.note(f"subscript_expr:{name}")
        if vector:
            self.ctx.vector_syms.add(name)
        if _is_char(self.peek(), "(") and base in self.ctx.ambiguous_funcs and primes == 0:
            raise Unsupported("ambiguous_application")
        greek_base = base in GREEK or base in GREEK_ALIAS.values()
        if _is_char(self.peek(), "[") and base not in NEVER_FUNC and (
                base in self.ctx.bracket_funcs or sub is not None or greek_base):
            # x[n], u[1]: sequence indexing (signal processing), an undefined function of the index
            e_ = group_end(self.toks, self.pos)
            inner = self.toks[self.pos + 1:e_]
            self.pos = e_ + 1
            self.ctx.note(f"bracket_index:{name}")
            self.ctx.functions_used.add(name)
            res = sp.Function(name)(*[self.sub(p) for p in _split_top(inner, ",")])
            return self.apply_superscript(res, sup) if sup is not None else res
        is_app = _is_char(self.peek(), "(") and (base not in NEVER_FUNC or sub is not None) and (
            base in self.ctx.funcs or name in self.ctx.funcs or primes > 0)
        if is_app:
            if sup is not None:
                sup_text = "".join(x.value for x in sup)
                if sup_text in ("-1",):
                    raise Unsupported("inverse_function")
                if sup and _is_char(sup[0], "("):
                    raise Unsupported("nth_derivative")
            args = self.parse_call_args()
            if name == "B" and len(args) == 2 and sub is None and primes == 0:
                self.ctx.note("funcapp:B:beta")  # B(x, y): the Beta function, as for \mathrm{B}
                res = sp.beta(*args)
                return self.apply_superscript(res, sup) if sup is not None else res
            f = sp.Function(name)
            self.ctx.functions_used.add(name)
            if name in self.ctx.funcs or base in self.ctx.funcs:
                self.ctx.note(f"funcapp:{name}")
            e = f(*args)
            if primes:
                if len(args) == 1 and args[0].is_Symbol:
                    e = sp.Derivative(e, (args[0], primes))
                else:
                    raise Unsupported("prime_at_point")
            if sup is not None:
                if sub is not None:
                    raise Unsupported("superscript_label")  # Y_7^{-7}(theta, phi), P_l^m(x): an index
                self.ctx.note(f"power_of_function:{name}")
                e = self.apply_superscript(e, sup)
            return e
        if primes:
            name = name + "_prime" * primes
            self.ctx.note(f"primed_symbol:{name}")
        if indexed_arg is not None:
            try:
                idx = [self.sub(p) for p in _split_top(indexed_arg, ",")]
            except (ParseError, Unsupported):
                raise Unsupported("complex_subscript")
            self.ctx.note(f"indexed:{base}")
            self.ctx.functions_used.add(base)
            e = sp.Function(base)(*idx)
        else:
            e = sp.Symbol(name)
            if base in ("e", "i"):
                pass
        if sup is not None:
            e = self.apply_superscript(e, sup)
        return e

    def finish_symbol(self, name: str, t: Tok):
        return self.parse_symbol_from(name, t)

    def parse_call_args(self) -> list:
        if not _is_char(self.peek(), "("):
            raise ParseError("expected (")
        e = group_end(self.toks, self.pos)
        inner = self.toks[self.pos + 1:e]
        self.pos = e + 1
        if any(_is_char(x, ";") or _is_char(x, "|") and False for x in _top_level(inner)):
            raise Unsupported("semicolon_args")
        if any(_is_cmd(x, "mid") for x in _top_level(inner)) or sum(_is_char(x, "|") for x in inner) % 2 == 1:
            raise Unsupported("conditional_probability")
        if any(is_relation(x) for x in _top_level(inner)):
            raise Unsupported("relation_in_args")
        parts = _split_top(inner, ",")
        if not parts or any(not p for p in parts):
            raise ParseError("empty argument")
        return [self.sub(p) for p in parts]

    def parse_named(self, name: str, t: Tok):
        """A named operator: \\sin, \\operatorname{arsinh}, \\mathrm{erf}, `\\text{sinc}` ..."""
        if name in UNSUPPORTED_WORDS and UNSUPPORTED_WORDS[name]:
            raise Unsupported(UNSUPPORTED_WORDS[name])
        if name == "lim":
            return self.parse_limit()
        if name in ("sum", "prod"):
            return self.parse_bigop(name)
        func = KNOWN_FUNCS.get(name, "unknown")
        if func is None or func == "unknown":
            # undefined (or deliberately not mapped) named function
            if self.function_follows() or _is_char(self.peek(), "("):
                sub, sup = self.read_scripts()
                fname = name if sub is None else f"{name}_{_script_name(sub)[0]}"
                if sup is not None:
                    raise Unsupported("power_of_named_function")
                args = self.parse_call_args()
                self.ctx.functions_used.add(fname)
                self.ctx.note(f"named_function:{fname}")
                return sp.Function(fname)(*args)
            if func is None:
                raise Unsupported(f"function:{name}")
            if len(name) > 1:
                nxt = self.peek()
                if nxt is not None and self.can_start_factor(nxt) and not _is_char(nxt, "^"):
                    # `\operatorname{vers}\theta`, `\operatorname{cis} x`: an operator we do not know
                    raise Unsupported("named_operator")
                # `\text{median}`, `\mathrm{Re}`, `\text{kg}`: a word, not a variable we can sample
                raise Unsupported("word_symbol")
            return self.parse_symbol_from(name, t)
        return self.apply_known(name, func)

    def apply_known(self, name: str, func):
        nxt = self.peek()
        if len(name) > 1 and (nxt is None or (not self.can_start_factor(nxt) and not _is_char(nxt, "^")
                                              and not _is_char(nxt, "_") and not _is_char(nxt, "'"))):
            # `\mathrm{Re} = U l/\nu` (Reynolds number): a function name used as a word
            raise Unsupported("word_symbol")
        sub, sup = self.read_scripts()
        inverse = False
        power = None
        primes = 0
        if sup is not None:
            txt = "".join(x.value for x in sup)
            if all(_is_cmd(a, "prime") or _is_char(a, "'") for a in sup):
                primes = len(sup)
            elif txt == "-1" and func in INVERSE_OF:
                inverse = True
                self.ctx.note(f"ambig:{name}^-1_as_inverse")
            elif txt == "-1":
                raise Unsupported("inverse_function")
            else:
                power = self.sub(sup)
        while _is_char(self.peek(), "'"):
            self.pos += 1
            primes += 1
        base = None
        order = None
        if sub is not None:
            if name == "log":
                base = self.sub(sub)
                self.ctx.note("log_base_given")
            elif name in ("Li",):
                order = self.sub(sub)
            elif name in ("ln",):
                raise Unsupported("ln_with_subscript")
            elif func in (sp.Max, sp.Min):
                raise Unsupported("sup_inf")
            else:
                raise Unsupported(f"subscript_on_function:{name}")
        if _is_char(self.peek(), "(") or _is_char(self.peek(), "["):
            if _is_char(self.peek(), "["):
                e = group_end(self.toks, self.pos)
                if self.toks[e].value != "]":
                    raise ParseError("mismatched brackets")
                self.toks = self.toks[:self.pos] + [Tok("CHAR", "(", 0, 0)] + self.toks[self.pos + 1:e] + [Tok("CHAR", ")", 0, 0)] + self.toks[e + 1:]
            args = self.parse_call_args()
            nxt = self.peek()
            if (func in _TRIG.values() or func in _INV.values()) and not (self.integrals and self.is_differential()):
                after = self.peek(1)
                bare_atom = nxt is not None and (
                    (nxt.kind == "LETTER" and nxt.value not in ("e", "d")) or (
                        _sym_cmd_name(nxt) is not None and nxt.value not in GREEK_FUNCS)) and not (
                    after is not None and after.kind == "CHAR" and after.value in "^_({")
                if bare_atom:
                    # `\cos(2k-1)\alpha`, `\sin(k+1)x`: cos((2k-1)alpha) or cos(2k-1)*alpha?
                    raise Unsupported("ambiguous_function_argument")
        else:
            if name in ("max", "min", "gcd", "lcm", "Beta", "B"):
                raise Unsupported(f"function_without_parens:{name}")
            args = [self.parse_implicit_arg()]
        if name == "log" and base is None:
            self.ctx.note("log:unspecified_base")
        if name == "Li":
            if order is None:
                fn = sp.Li
            else:
                if len(args) != 1:
                    raise ParseError("polylog arity")
                e = sp.polylog(order, args[0])
                return self._finish_known(e, power, primes, args)
        if inverse:
            func = INVERSE_OF[func]
        if name == "log" and base is not None:
            if len(args) != 1:
                raise ParseError("log arity")
            e = sp.log(args[0], base)
            return self._finish_known(e, power, primes, args)
        if name == "Gamma" and len(args) == 2:
            func = sp.uppergamma
        if func in (sp.gcd, sp.lcm) and not all(a.is_Integer for a in args):
            # sympy's gcd of symbols is a polynomial gcd (gcd(a, b, c) -> 1)
            self.ctx.functions_used.add(name)
            return self._finish_known(sp.Function(name)(*args), power, primes, args)
        try:
            e = func(*args)
        except TypeError as ex:
            raise ParseError(f"bad arity for {name}: {ex}")
        return self._finish_known(e, power, primes, args)

    def _finish_known(self, e, power, primes, args):
        if primes:
            if len(args) == 1 and args[0].is_Symbol:
                e = sp.Derivative(e, (args[0], primes))
            else:
                raise Unsupported("prime_at_point")
        if power is not None:
            e = _check_pow(e, power)
        return e

    def parse_implicit_arg(self):
        """Argument of `\\sin 2x`: one factor, then further simple atoms (letters, digits after
        none, greek symbols), stopping at operators, other functions, brackets and fractions."""
        factors = [self.parse_factor()]
        if factors[0].is_Number and _is_char(self.peek(), "("):
            # `\sin\tfrac12(\theta+\varphi)` = sin((theta+phi)/2)
            factors.append(self.parse_factor())
            self.ctx.note("numeric_coefficient_function_arg")
        integral = self.integrals[-1] if self.integrals else None
        while True:
            t = self.peek()
            if t is None:
                break
            if integral is not None and integral["var"] is None and self.is_differential():
                break
            if t.kind == "LETTER":
                if t.value in self.ctx.funcs and _is_char(self.peek(1), "("):
                    break
                factors.append(self.parse_factor())
            elif t.kind == "CMD" and (_sym_cmd_name(t) is not None or t.value in ("pi", "infty")) and not (
                    t.value in ("Gamma", "zeta") and self.function_follows_at(self.pos + 1)):
                if (_sym_cmd_name(t) or "") in self.ctx.funcs and _is_char(self.peek(1), "("):
                    break
                factors.append(self.parse_factor())
            elif t.kind == "CMD" and t.value in (set(ACCENTS) | VECTOR_STYLE):
                factors.append(self.parse_factor())
            else:
                break
        if len(factors) > 1:
            self.ctx.note("implicit_function_arg")
        return sp.Mul(*factors)

    def function_follows_at(self, j: int) -> bool:
        saved = self.pos
        self.pos = j
        try:
            return self.function_follows()
        finally:
            self.pos = saved

    def parse_roman(self):
        arg = self.read_arg()
        word = "".join(a.value for a in arg if a.kind in ("LETTER", "DIGIT"))
        if not word or len(word) != sum(1 for a in arg if a.kind in ("LETTER", "DIGIT")) or len(arg) != len(word):
            # \mathrm{} around something that is not a plain word: just parse it
            return self.sub(arg)
        if word == "d":
            raise Unsupported("differential_form")
        if word in ("e", "i"):
            self.ctx.note(f"{word}:roman")
            return self.parse_symbol_from(word, arg[0])
        if word in KNOWN_FUNCS or word in UNSUPPORTED_WORDS:
            return self.parse_named(word, arg[0])
        if len(word) == 1:
            nxt = self.peek()
            if word == "p" and nxt is not None and (nxt.kind == "LETTER" or nxt.kind == "CMD"):
                raise Unsupported("p_function")  # pK = -log10 K, pH
            if word in ("B",) and _is_char(self.peek(), "("):
                return self.parse_named("Beta", arg[0])
            if word == "E" and (_is_char(self.peek(), "[") or _is_char(self.peek(), "(")):
                raise Unsupported("expectation")
            return self.parse_symbol_from(word, arg[0])
        if word.isdigit():
            return sp.Integer(word)
        return self.parse_named(word, arg[0])

    def parse_styled_symbol(self, style: str):
        arg = self.read_arg()
        if len(arg) == 1 and (arg[0].kind == "LETTER" or _sym_cmd_name(arg[0])):
            base = arg[0].value if arg[0].kind == "LETTER" else _sym_cmd_name(arg[0])
            name = ("vec_" if style in ("vec", "overrightarrow") or base.islower() else "bf_") + base
            self.ctx.note(f"vector_symbol:{name}")
            return self.parse_symbol_from(name, arg[0], vector=True)
        if len(arg) == 1 and arg[0].kind == "DIGIT":
            raise Unsupported("bold_number")
        raise Unsupported("styled_expression")

    def parse_accent(self, cmd: str):
        acc = ACCENTS[cmd]
        arg = self.read_arg()
        if len(arg) == 1 and (arg[0].kind == "LETTER" or _sym_cmd_name(arg[0])):
            base = arg[0].value if arg[0].kind == "LETTER" else _sym_cmd_name(arg[0])
            name = f"{base}_{acc}"
            if acc == "bar" and base in self.ctx.plain_letters and not _is_char(self.peek(), "_") \
                    and not _is_char(self.peek(), "("):
                # \bar z next to a plain z: complex conjugate (or a mean of z?)
                if self.ctx.complex_context or base in ("z", "w", "zeta"):
                    self.ctx.note(f"conjugate:{base}")
                    e = sp.conjugate(sp.Symbol(base))
                    sup = None
                    if _is_char(self.peek(), "^"):
                        self.pos += 1
                        return self.apply_superscript(e, self.read_arg())
                    return e
                raise Unsupported("ambiguous_bar")
            if acc in ("bar",):
                self.ctx.note(f"ambig:bar:{name}")
            if acc in ("dot", "ddot", "dddot"):
                self.ctx.note(f"ambig:time_derivative:{name}")
            if base in self.ctx.funcs:
                self.ctx.funcs.add(name)
            return self.parse_symbol_from(name, arg[0])
        if acc == "bar":
            raise Unsupported("overline_expression")
        raise Unsupported("accent_expression")

    # ---------------------------------------------------------------- fractions & derivatives
    def parse_frac(self):
        num = self.read_arg()
        den = self.read_arg()
        if num and den and _is_cmd(num[0], "delta") and _is_cmd(den[0], "delta"):
            raise Unsupported("variational_derivative")  # \frac{\delta^2 u}{\delta\theta^2}, \frac{\delta F}{\delta f}
        d = _match_derivative(num, den)
        if d is not None:
            n_order, rest, dvars = d
            if not rest:
                nxt = self.peek()
                if nxt is None or not self.can_start_factor(nxt):
                    raise Unsupported("derivative_operator")
                # d/dx [ ... ] applies to the bracket only; d/dx x^n sin x to the whole term
                operand = self.parse_factor() if (_is_char(nxt, "(") or _is_char(nxt, "[")) else self.parse_term()
                self.ctx.note("derivative_operator")
            else:
                operand = self.sub(rest)
            vars_ = []
            for vtoks, k in dvars:
                v = self.sub(vtoks)
                if not v.is_Symbol:
                    raise ParseError("derivative variable is not a symbol")
                kk = self.sub(k) if k else sp.Integer(1)
                vars_.append((v, kk))
            if operand.is_Symbol and operand not in [v for v, _ in vars_]:
                self.ctx.note(f"leibniz_function:{operand.name}")
                self.ctx.functions_used.add(operand.name)
                operand = sp.Function(operand.name)(*[v for v, _ in vars_])
            return sp.Derivative(operand, *vars_)
        with self.transparent_for_differential():
            a = self.sub(num) if num else None
        b = self.sub(den)
        if a is None:
            raise ParseError("empty numerator")
        if self._vector_count(b):
            raise Unsupported("vector_division")
        return sp.Mul(a, sp.Pow(b, -1))

    # ---------------------------------------------------------------- big operators
    def parse_bigop(self, kind: str):
        sub, sup = self.read_scripts()
        if sub is None:
            raise Unsupported(f"{kind}_without_bounds")
        vars_, lo, hi = self.parse_index(sub, sup, kind)
        self.bound.extend(v.name for v in vars_)
        try:
            t = self.peek()
            if _is_char(t, "-"):
                self.pos += 1
                body = -self.parse_term()
            else:
                body = self.parse_term()
        finally:
            for _ in vars_:
                self.bound.pop()
        cls = sp.Sum if kind == "sum" else sp.Product
        for v in reversed(vars_):
            body = cls(body, (v, lo, hi))
        return body

    def parse_index(self, sub: list[Tok], sup: list[Tok] | None, kind: str):
        top = _top_level_idx(sub)
        eqs = [i for i in top if _is_char(sub[i], "=")]
        if len(eqs) == 1:
            i = eqs[0]
            names = _split_top(sub[:i], ",")
            vars_ = []
            for nm in names:
                v = self.sub(nm)
                if not v.is_Symbol:
                    raise Unsupported(f"{kind}_index_not_symbol")
                vars_.append(v)
            lo = self.sub(sub[i + 1:])
            if sup is None:
                raise Unsupported(f"{kind}_without_upper_bound")
            hi = self.sub(sup)
            return vars_, lo, hi
        rels = [i for i in top if is_relation(sub[i])]
        if rels and sup is None:
            # 0 \le k \le n  /  k \ge 1  /  1 \le k < n
            parts = []
            ops = []
            last = 0
            for i in rels:
                parts.append(sub[last:i])
                ops.append(sub[i])
                last = i + 1
            parts.append(sub[last:])
            exprs = [self.sub(p) for p in parts]
            opv = [_rel_name(o) for o in ops]
            if len(exprs) == 3 and exprs[1].is_Symbol and opv[0] in ("<", "<=") and opv[1] in ("<", "<="):
                v = exprs[1]
                lo = exprs[0] + (1 if opv[0] == "<" else 0)
                hi = exprs[2] - (1 if opv[1] == "<" else 0)
                self.ctx.note("index_range_from_inequality")
                return [v], lo, hi
            if len(exprs) == 2 and exprs[0].is_Symbol and opv[0] in (">=", ">"):
                self.ctx.note("index_range_from_inequality")
                return [exprs[0]], exprs[1] + (1 if opv[0] == ">" else 0), sp.oo
        raise Unsupported(f"{kind}_index_set")

    def parse_limit(self):
        sub, sup = self.read_scripts()
        if sub is None or sup is not None:
            raise Unsupported("limit_form")
        top = _top_level_idx(sub)
        arrows = [i for i in top if _is_cmd(sub[i], "to", "rightarrow", "searrow", "nearrow", "longrightarrow")]
        if len(arrows) != 1:
            raise Unsupported("limit_form")
        i = arrows[0]
        var = self.sub(sub[:i])
        if not var.is_Symbol:
            raise Unsupported("limit_form")
        tgt = sub[i + 1:]
        direction = "+-"
        if len(tgt) >= 2 and _is_char(tgt[-2], "^") and tgt[-1].kind == "CHAR" and tgt[-1].value in "+-":
            direction = tgt[-1].value
            tgt = tgt[:-2]
        elif (len(tgt) >= 4 and _is_char(tgt[-4], "^") and _is_char(tgt[-3], "{")
              and tgt[-2].kind == "CHAR" and tgt[-2].value in "+-" and _is_char(tgt[-1], "}")):
            direction = tgt[-2].value
            tgt = tgt[:-4]
        target = self.sub(tgt)
        self.bound.append(var.name)
        try:
            body = self.parse_term()
        finally:
            self.bound.pop()
        names = {s.name for s in body.free_symbols} | {type(fn).__name__ for fn in body.atoms(AppliedUndef)}
        if var not in body.free_symbols and not any(var.name in nm.split("_")[1:] for nm in names):
            # `\lim_{\beta\to 0}\mu`: mu depends on beta only through prose
            raise Unsupported("limit_of_unrelated_symbol")
        if target in (sp.oo, -sp.oo):
            return sp.Limit(body, var, target)
        return sp.Limit(body, var, target, dir=direction)

    def parse_integral(self):
        sub, sup = self.read_scripts()
        if (sub is None) != (sup is None):
            raise Unsupported("integral_domain")
        named = None
        if sub is not None:
            eqs = [i for i in _top_level_idx(sub) if _is_char(sub[i], "=")]
            if len(eqs) == 1:
                named = self.sub(sub[:eqs[0]])
                if not named.is_Symbol:
                    raise Unsupported("integral_domain")
                sub = sub[eqs[0] + 1:]
        lo = self.sub(sub) if sub is not None else None
        hi = self.sub(sup) if sup is not None else None
        state = {"var": None, "depth": self.depth + 1, "levels": {self.level}}
        self.integrals.append(state)
        try:
            body = self.parse_expr()
        finally:
            self.integrals.pop()
        var = state["var"]
        if var is None:
            raise Unsupported("integral_without_differential")
        if named is not None and named != var:
            raise ParseError("integral variable in bounds does not match differential")
        if lo is None:
            self.ctx.note("indefinite_integral")
            return sp.Integral(body, var)
        return sp.Integral(body, (var, lo, hi))

    @contextmanager
    def transparent_for_differential(self):
        """Let the next sub-parse see the enclosing integral's differential."""
        state = self.integrals[-1] if self.integrals else None
        added = state is not None and state["var"] is None and self.level in state["levels"]
        if added:
            state["levels"].add(self.level + 1)
        try:
            yield
        finally:
            if added:
                state["levels"].discard(self.level + 1)

    def is_differential(self) -> bool:
        # Only at the integrand's own level, or directly in a fraction numerator (`\frac{dx}{x}`);
        # never inside brackets, where `(a\,d\,f + b)` is a product of coefficients.
        state = self.integrals[-1]
        if self.level not in state["levels"]:
            return False
        j = self._diff_marker_end(self.pos)
        if j is None:
            return False
        if j == self.pos:
            return True  # \text{dx}
        t = self.toks[j] if j < len(self.toks) else None
        if t is None:
            return False
        return t.kind == "LETTER" or _sym_cmd_name(t) is not None

    def _diff_marker_end(self, i: int) -> int | None:
        t = self.toks[i] if i < len(self.toks) else None
        if t is None:
            return None
        if t.kind == "LETTER" and t.value == "d":
            return i + 1
        if (t.kind == "OPNAME" or t.kind == "TEXT") and t.value.strip() == "d":
            return i + 1
        if t.kind == "TEXT" and re.fullmatch(r"d[a-zA-Z]", t.value.strip()):
            return i
        if _is_cmd(t, "mathrm", "rm", "mathop") and i + 3 < len(self.toks) + 1:
            if (i + 3 <= len(self.toks) - 1 and _is_char(self.toks[i + 1], "{") and self.toks[i + 2].is_("LETTER", "d")
                    and _is_char(self.toks[i + 3], "}")):
                return i + 4
            if i + 1 < len(self.toks) and self.toks[i + 1].is_("LETTER", "d"):
                return i + 2
        return None

    def consume_differential(self):
        j = self._diff_marker_end(self.pos)
        if j == self.pos:
            t = self.next()
            return sp.Symbol(t.value.strip()[1])
        self.pos = j
        t = self.next()
        base = t.value if t.kind == "LETTER" else _sym_cmd_name(t)
        sub = None
        if _is_char(self.peek(), "_"):
            self.pos += 1
            sub = self.read_arg()
        if _is_char(self.peek(), "^"):
            raise Unsupported("volume_element")
        name = base if sub is None else f"{base}_{_script_name(sub)[0]}"
        return sp.Symbol(name)

    # ---------------------------------------------------------------- environments
    def parse_env(self):
        t = self.peek()
        name = t.value
        e = group_end(self.toks, self.pos)
        inner = self.toks[self.pos + 1:e]
        self.pos = e + 1
        if name in ("cases", "dcases", "rcases"):
            return self.parse_cases(inner)
        if name in ("pmatrix", "matrix", "bmatrix", "vmatrix", "Vmatrix", "array", "smallmatrix", "Bmatrix"):
            raise Unsupported("matrix")
        raise Unsupported(f"env:{name}")

    def parse_cases(self, inner: list[Tok]):
        rows = []
        cur: list[Tok] = []
        depth = 0
        for t in inner:
            if t.kind == "ROWSEP" and depth == 0:
                rows.append(cur)
                cur = []
                continue
            if t.kind == "CHAR" and t.value in "([{" or t.kind == "BEGIN":
                depth += 1
            elif t.kind == "CHAR" and t.value in ")]}" or t.kind == "END":
                depth -= 1
            cur.append(t)
        rows.append(cur)
        pieces = []
        for r in rows:
            r = [x for x in r if x.kind != "SPACE"]
            if not r:
                continue
            amp = [i for i in _top_level_idx(r) if _is_char(r[i], "&")]
            if len(amp) != 1:
                raise Unsupported("cases")
            val, cond = r[:amp[0]], r[amp[0] + 1:]
            while val and (_is_char(val[-1], ",") or _is_char(val[-1], ".")):
                val = val[:-1]
            if any(is_relation(x) for x in _top_level(val)):
                raise Unsupported("cases_chain")
            v = self.sub(val)
            try:
                c = self.parse_condition(cond)
            except ParseError:
                raise Unsupported("cases_condition")
            pieces.append((v, c))
        if not pieces:
            raise ParseError("empty cases")
        self.ctx.note("piecewise")
        return sp.Piecewise(*pieces)

    def parse_condition(self, toks: list[Tok]):
        toks = [t for t in toks if t.kind != "SPACE"]
        while toks and (_is_char(toks[-1], ".") or _is_char(toks[-1], ",")):
            toks = toks[:-1]
        if toks and _is_char(toks[0], "(") and group_end(toks, 0) == len(toks) - 1:
            toks = toks[1:-1]
        # leading prose: "if", "for", "(for "
        while toks and toks[0].kind == "TEXT" and toks[0].value.strip().lower().strip("( ") in ("if", "for", "when", "where", ""):
            toks = toks[1:]
        if not toks:
            raise Unsupported("cases_condition")
        if len(toks) == 1 and toks[0].kind == "TEXT":
            w = toks[0].value.strip().lower().strip("(),. ")
            if w in ("otherwise", "else", "elsewhere", "for all other values", "in all other cases",
                     "if otherwise", "for other values"):
                return sp.true
            raise Unsupported("cases_condition")
        # `n>-1,\ a>0` and `x>0 \text{ and } y>0` are conjunctions: split before parsing
        parts: list[list[Tok]] = [[]]
        for i in _top_level_idx(toks):
            t = toks[i]
            if _is_char(t, ",") or (t.kind == "TEXT" and t.value.strip().lower() in ("and", ",")):
                parts.append([])
            else:
                parts[-1].append(t)
        conds = []
        for part in parts:
            if not part:
                continue
            words = " ".join(t.value for t in part if t.kind == "TEXT").strip().lower()
            core = [t for t in part if t.kind != "TEXT"]
            if not core:
                raise Unsupported("cases_condition")
            if words in ("odd", "even", "is odd", "is even"):
                conds.append(sp.Eq(sp.Mod(self.sub(core), 2), 1 if words.endswith("odd") else 0))
            elif words:
                raise Unsupported("cases_condition")
            else:
                conds.append(self.parse_relational(core))
        if not conds:
            raise Unsupported("cases_condition")
        return sp.And(*conds) if len(conds) > 1 else conds[0]

    def parse_relational(self, toks: list[Tok]):
        top = _top_level_idx(toks)
        rels = [i for i in top if is_relation(toks[i])]
        if not rels:
            raise Unsupported("cases_condition")
        parts, ops, last = [], [], 0
        for i in rels:
            parts.append(toks[last:i])
            ops.append(_rel_name(toks[i]))
            last = i + 1
        parts.append(toks[last:])
        exprs = [self.sub(p) for p in parts]
        out = []
        for a, op, b in zip(exprs, ops, exprs[1:]):
            fn = {"<": sp.Lt, "<=": sp.Le, ">": sp.Gt, ">=": sp.Ge, "!=": sp.Ne, "=": sp.Eq}.get(op)
            if fn is None:
                raise Unsupported("cases_condition")
            out.append(fn(a, b, evaluate=False))
        return sp.And(*out) if len(out) > 1 else out[0]


def _peek_kind(p: Parser, k: int) -> str | None:
    t = p.peek(k)
    return t.kind if t is not None else None


def _top_level_idx(toks: list[Tok]) -> list[int]:
    out = []
    depth = 0
    for i, t in enumerate(toks):
        if t.kind == "CHAR" and t.value in "([{" or t.kind == "BEGIN" or _is_cmd(t, "lvert", "lfloor", "lceil", "langle", "lVert"):
            depth += 1
            continue
        if t.kind == "CHAR" and t.value in ")]}" or t.kind == "END" or _is_cmd(t, "rvert", "rfloor", "rceil", "rangle", "rVert"):
            depth -= 1
            continue
        if depth == 0:
            out.append(i)
    return out


def _top_level(toks: list[Tok]) -> list[Tok]:
    return [toks[i] for i in _top_level_idx(toks)]


def _split_top(toks: list[Tok], sep: str) -> list[list[Tok]]:
    idx = [i for i in _top_level_idx(toks) if _is_char(toks[i], sep)]
    parts, last = [], 0
    for i in idx:
        parts.append(toks[last:i])
        last = i + 1
    parts.append(toks[last:])
    return parts


def _rel_name(t: Tok) -> str:
    v = t.value
    return {
        "=": "=", ":=": ":=", "=:": "=:", "<": "<", ">": ">", "le": "<=", "leq": "<=",
        "leqslant": "<=", "leqq": "<=", "ge": ">=", "geq": ">=", "geqslant": ">=", "geqq": ">=",
        "ne": "!=", "neq": "!=", "equiv": "equiv", "approx": "approx", "simeq": "approx",
        "sim": "sim", "cong": "approx", "approxeq": "approx", "doteq": "approx",
        "propto": "propto", "to": "to", "rightarrow": "to", "longrightarrow": "to",
        "mapsto": "to", "in": "in", "notin": "in", "subset": "subset", "subseteq": "subset",
        "ll": "ll", "gg": "gg",
    }.get(v, v)


def _script_name(toks: list[Tok]) -> tuple[str, bool]:
    """Name fragment for a subscript; (text, is_simple)."""
    parts = []
    simple = True
    for t in toks:
        if t.kind in ("LETTER", "DIGIT"):
            parts.append(t.value)
        elif t.kind == "TEXT":
            parts.append(t.value.strip().replace(" ", ""))
        elif t.kind == "OPNAME":
            parts.append(t.value)
        elif _sym_cmd_name(t):
            parts.append(_sym_cmd_name(t))
        elif _is_cmd(t, "mathrm", "rm", "text", "mathit", "mathbf", "textrm") or _is_char(t, "{") or _is_char(t, "}"):
            continue
        elif _is_cmd(t, "infty"):
            parts.append("inf")
        elif _is_cmd(t, "pi"):
            parts.append("pi")
        else:
            simple = False
            parts.append(t.value if t.kind != "CMD" else "\\" + t.value)
    s = "".join(parts)
    if not simple:
        return "{" + s + "}", False
    return s, True


def _label_subscript(sub: list[Tok]) -> bool:
    """`V_{w2}`, `N_{A0}`, `\\rho_{de0}`, `\\delta_{k0}`: letters followed by digits label a quantity;
    `x_{2k}` (digit before letter) is index arithmetic."""
    if not sub or not all(t.kind in ("LETTER", "DIGIT") for t in sub) or sub[0].kind != "LETTER":
        return False
    kinds = "".join("L" if t.kind == "LETTER" else "D" for t in sub)
    return "D" in kinds and "DL" not in kinds


def _script_letters(toks: list[Tok]) -> set[str]:
    out = set()
    for t in toks:
        if t.kind == "LETTER":
            out.add(t.value)
        elif _sym_cmd_name(t):
            out.add(_sym_cmd_name(t))
    return out


def _is_dmark(toks: list[Tok], i: int) -> int | None:
    """If toks[i:] starts with a differential marker (d, \\partial, \\mathrm{d}), return end index."""
    if i >= len(toks):
        return None
    t = toks[i]
    if t.kind == "LETTER" and t.value == "d":
        return i + 1
    if _is_cmd(t, "partial"):
        return i + 1
    if (t.kind in ("OPNAME", "TEXT")) and t.value.strip() == "d":
        return i + 1
    if _is_cmd(t, "mathrm", "rm") and i + 3 < len(toks) + 0 and _is_char(toks[i + 1], "{") and toks[i + 2].is_("LETTER", "d") and _is_char(toks[i + 3], "}"):
        return i + 4
    if _is_cmd(t, "mathrm", "rm") and i + 1 < len(toks) and toks[i + 1].is_("LETTER", "d"):
        return i + 2
    return None


ONE_ARG_CMDS = {"mathrm", "rm", "mathit", "mathbf", "mathsf", "mathtt", "mathcal", "mathscr", "mathfrak", "mathbb",
                "boldsymbol", "bm", "vec", "hat", "widehat", "bar", "overline", "tilde", "widetilde", "dot", "ddot",
                "check", "breve", "textbf"}


def _read_script_toks(toks: list[Tok], i: int) -> tuple[list[Tok], int]:
    if i < len(toks) and _is_char(toks[i], "{"):
        e = group_end(toks, i)
        return toks[i + 1:e], e + 1
    if i + 1 < len(toks) and toks[i].kind == "CMD" and toks[i].value in ONE_ARG_CMDS and _is_char(toks[i + 1], "{"):
        e = group_end(toks, i + 1)  # `_\mathrm{el}`: the command with its argument
        return toks[i:e + 1], e + 1
    return toks[i:i + 1], i + 1


def _match_derivative(num: list[Tok], den: list[Tok]):
    """Leibniz notation: num = d[^n] rest, den = (d var [^k])+. Returns (n, rest, [(var, k)])."""
    j = _is_dmark(num, 0)
    if j is None:
        return None
    n_toks = None
    if j < len(num) and _is_char(num[j], "^"):
        n_toks, j = _read_script_toks(num, j + 1)
    rest = num[j:]
    # the numerator `d` must be followed by nothing, a symbol or a group, not by an operator
    if rest and rest[0].kind == "CHAR" and rest[0].value in "+-=)":
        return None
    dvars = []
    i = 0
    while i < len(den):
        k = _is_dmark(den, i)
        if k is None or k >= len(den):
            return None
        v = den[k]
        if not (v.kind == "LETTER" or _sym_cmd_name(v)):
            return None
        vt = [v]
        k += 1
        if k < len(den) and _is_char(den[k], "_"):
            s, k2 = _read_script_toks(den, k + 1)
            vt = den[k - 1:k2]
            k = k2
        order = None
        if k < len(den) and _is_char(den[k], "^"):
            order, k = _read_script_toks(den, k + 1)
        dvars.append((vt, order))
        i = k
    if not dvars:
        return None
    return n_toks, rest, dvars


def prescan_brackets(toks: list[Tok]) -> set[str]:
    """Letters indexed with square brackets and a single-atom index somewhere (`x[n]`, `u[1]`)."""
    out = set()
    for i, t in enumerate(toks[:-1]):
        if t.kind == "LETTER" and t.value not in ("e", "i", "d") and _is_char(toks[i + 1], "[") and not (
                i > 0 and toks[i - 1].kind == "LETTER"):
            try:
                e = group_end(toks, i + 1)
            except ParseError:
                continue
            if toks[e].value == "]" and _is_single_atom(toks[i + 2:e]):
                out.add(t.value)
    return out


def _symbolic_power_follows(toks: list[Tok], pos: int) -> bool:
    """`n2^{n-1}`, `n2^n`: the digit at `pos` is the base of a power whose exponent names a symbol,
    so it is a juxtaposed factor, not a subscript (`h2` alone stays `h_2`)."""
    t = toks[pos]
    if t.kind != "DIGIT" or pos + 2 >= len(toks) or not _is_char(toks[pos + 1], "^"):
        return False
    nxt = toks[pos + 2]
    if nxt.kind == "LETTER":
        return True
    if _is_char(nxt, "{"):
        end = group_end(toks, pos + 2)
        return any(x.kind == "LETTER" for x in toks[pos + 3:end])
    return False


def prescan_functions(toks: list[Tok]) -> tuple[set[str], list[str], set[str]]:
    """Decide which single-letter / greek names are applied as functions in this formula.

    `name(args)` is function application when the argument list is *structurally* a call: a
    top-level comma (`B(x,y)`) or a single atom (`y(t)`, `a(2)`), or the name is primed (`f'(x)`).
    With a compound argument (`a(b+c)`) it is a call only if the name is conventionally a
    function (f, g, h, F, G, H, phi, psi, chi, an uppercase Latin letter, any greek letter) *and*
    the name is never used bare elsewhere in the formula: in `(e+f x)^p ... f(m+n+1)` the `f`
    is a coefficient. A name applied anywhere in the formula is a function everywhere in it.
    """
    funcs: set[str] = set()
    notes: list[str] = []
    ambiguous: set[str] = set()
    n_apps: dict[str, int] = {}
    applied: dict[str, tuple[str, bool]] = {}  # name -> (reason, strong)
    bare: set[str] = set()
    n = len(toks)
    skip_to = 0
    for i, t in enumerate(toks):
        if i < skip_to:
            continue  # inside \\mathrm{N}, \\hat{f}, ...: already handled with the command
        j = i + 1
        if t.kind == "LETTER":
            name = t.value
        elif _sym_cmd_name(t) or _is_cmd(t, "pi"):
            name = _sym_cmd_name(t) or "pi"
            if name in ("Gamma", "zeta", "Beta"):
                continue
        elif t.kind == "CMD" and (t.value in ACCENTS or t.value in SCRIPT_STYLE or t.value in VECTOR_STYLE
                                  or t.value in ("mathrm", "rm", "mathit")) and i + 1 < n:
            # \hat f(\xi), \mathcal{O}(h), \mathbf{F}(x): decided like the bare letter, under the styled name
            arg, j = _read_script_toks(toks, i + 1)
            if not (len(arg) == 1 and (arg[0].kind == "LETTER" or _sym_cmd_name(arg[0]))):
                continue
            skip_to = j
            base = arg[0].value if arg[0].kind == "LETTER" else _sym_cmd_name(arg[0])
            if t.value in ACCENTS:
                name = f"{base}_{ACCENTS[t.value]}"
                if base in ALWAYS_FUNC and j < n and _is_char(toks[j], "("):
                    funcs.add(base)
                    funcs.add(name)
            elif t.value in SCRIPT_STYLE:
                name = f"{SCRIPT_STYLE[t.value]}_{base}"
            elif t.value in ("mathrm", "rm", "mathit"):
                name = base
            else:
                name = ("vec_" if t.value in ("vec", "overrightarrow") or base.islower() else "bf_") + base
        else:
            continue
        if name in NEVER_FUNC and not (i + 1 < n and _is_char(toks[i + 1], "_")):
            continue
        primed = False
        had_sub = False
        while j < n and (_is_char(toks[j], "_") or _is_char(toks[j], "^") or _is_char(toks[j], "'")):
            if _is_char(toks[j], "'"):
                primed = True
                j += 1
                continue
            had_sub = had_sub or _is_char(toks[j], "_")
            is_sup = _is_char(toks[j], "^")
            arg, j = _read_script_toks(toks, j + 1)
            if is_sup and arg and all(_is_cmd(a, "prime") or _is_char(a, "'") for a in arg):
                primed = True
        if j >= n or not _is_char(toks[j], "("):
            if not primed:
                bare.add(name)
            continue
        try:
            e = group_end(toks, j)
        except ParseError:
            continue
        inner = toks[j + 1:e]
        reason, strong = None, False
        if name == "d" and not (_is_single_atom(inner) or any(_is_char(x, ",") for x in _top_level(inner))):
            continue
        if name == "pi":
            if len(inner) == 1 and inner[0].kind == "LETTER":
                reason, strong = "pi_single_letter_arg", True
        elif primed:
            reason, strong = "primed", True
        elif any(_is_char(x, ",") or _is_char(x, ";") for x in _top_level(inner)):
            reason, strong = "comma_args", True
        elif _is_single_atom(inner):
            reason, strong = "single_atom_arg", True
        elif name in ALWAYS_FUNC or name.split("_")[0] in ALWAYS_FUNC:
            reason = "conventional_name"
        elif t.kind == "CMD":
            reason = "greek_or_styled_name"
        elif name.isupper():
            reason = "uppercase"
        if reason is None and had_sub:
            continue  # k_3(c-1), a_n(x-c)^n: a subscripted coefficient times a bracket
        n_apps[name] = n_apps.get(name, 0) + 1
        if name not in applied or strong or (applied[name][0] is None and reason is not None):
            applied[name] = (reason, strong or applied.get(name, ("", False))[1])
    coefficient_run = len(bare & set("abcde")) >= 3  # integral tables: (a+bx)...(e+fx)
    whole_side = _whole_side_names(toks)  # `E = E(R/p)`: the bare name is an entire side
    for name, (reason, strong) in applied.items():
        if reason is None and name == "pi":
            continue  # 2\pi(r+h)
        if reason is None:
            # lowercase letter with a compound argument: `s(1-t)` once is a product; the same letter
            # applied again and never used plainly, `p(2n+1) = \sum p(n-k) q(2k+1)`, is a function
            if name not in bare and not coefficient_run and n_apps.get(name, 0) >= 2:
                ambiguous.add(name)
                notes.append(f"ambiguous_application:{name}")
            continue
        if strong or name not in bare:
            funcs.add(name)
            notes.append(f"funcapp_rule:{name}:{reason}")
        elif coefficient_run and reason == "conventional_name":
            notes.append(f"mult_not_call:{name}")
        elif reason != "conventional_name" and name not in whole_side:
            # N(1/(s+1) + ...) with N also inside a fraction: a product, as written
            notes.append(f"mult_not_call:{name}")
        else:
            # `E = E(R/p)`, `\mathcal{L}_T f ... f(y/2)`: the same name bare and applied
            ambiguous.add(name)
            notes.append(f"ambiguous_application:{name}")
    return funcs, notes, ambiguous


def indexed_bases(toks: list[Tok]) -> set[str]:
    """Bases carrying a subscript with arithmetic and a letter (`a_{n+1}`, `x_{2k}`)."""
    out: set[str] = set()
    for i, t in enumerate(toks[:-1]):
        if not _is_char(toks[i + 1], "_"):
            continue
        base = t.value if t.kind == "LETTER" else _sym_cmd_name(t)
        if base is None:
            continue
        sub, _ = _read_script_toks(toks, i + 2)
        has_letter = any(x.kind == "LETTER" or _sym_cmd_name(x) for x in sub)
        has_arith = any(x.kind == "CHAR" and x.value in "+-" for x in sub) or (
            any(x.kind == "DIGIT" for x in sub) and has_letter and not _label_subscript(sub))
        if has_letter and has_arith:
            out.add(base)
    return out


def _roman_word(arg: list[Tok]) -> str | None:
    r"""`\mathrm{qc}`, `\text{in}`, `\mathsf{T}`, a bare `T` -> the word; else None."""
    if len(arg) == 1 and arg[0].kind in ("TEXT", "OPNAME"):
        w = arg[0].value.strip()
        return w if w.isalnum() and w else None
    if len(arg) == 1 and arg[0].kind == "LETTER" and arg[0].value == "T":
        return "T"
    if len(arg) >= 4 and arg[0].kind == "CMD" and arg[0].value in ("mathrm", "rm", "mathsf", "textsf", "mathit", "mathbf") \
            and _is_char(arg[1], "{") and _is_char(arg[-1], "}") and all(a.kind in ("LETTER", "DIGIT") for a in arg[2:-1]):
        return "".join(a.value for a in arg[2:-1])
    if len(arg) == 2 and arg[0].kind == "CMD" and arg[0].value in ("mathrm", "rm", "mathsf", "textsf") and arg[1].kind == "LETTER":
        return arg[1].value
    return None


EXPONENT_LETTERS = set("nkmpqrjxyztil")


def _superscript_label(base, arg: list[Tok], word: str | None, subscripted: set[str] = frozenset()) -> bool:
    """Is this superscript a label/index rather than an exponent? (base is not a number or e)"""
    if not arg:
        return False
    if _is_char(arg[0], "(") and _is_char(arg[-1], ")"):
        return True  # X^{(0)}, f^{(n)}, w^{(i)}_k: iterate / derivative order / index
    if word is not None and word != "T":
        return True  # A^\mathrm{g}, H^\text{cp}, \operatorname{Ric}^g
    names = [a.value if a.kind in ("LETTER", "DIGIT") else (_sym_cmd_name(a) or ("infty" if _is_cmd(a, "infty") else None))
             for a in arg]
    if any(nm in ("infty", "omega", "Omega") for nm in names):
        return True  # E^\infty (spectral sequence page), a^\omega (idempotent power)
    if len(arg) == 1 and arg[0].kind == "DIGIT" and arg[0].value == "0" and (
            isinstance(base, AppliedUndef) or (isinstance(base, sp.Symbol) and base.name in subscripted)):
        return True  # C_3^0, g_i^0, Y_0^0(theta, phi): an index on an indexed name
    has_letter = any(a.kind == "LETTER" or _sym_cmd_name(a) for a in arg)
    if has_letter and ((isinstance(base, sp.Symbol) and base.name in subscripted) or isinstance(base, AppliedUndef)):
        return True  # h^i_k, B_{1,2}^s, \nu_k^{ij}, {\beta_j}^{k+1}, H_{\rm v}^{px}: indices on an indexed name
    if isinstance(base, sp.Symbol) and base.name[:1].isupper() and len(base.name) == 1 and len(arg) == 1 \
            and arg[0].kind == "LETTER" and arg[0].value not in EXPONENT_LETTERS:
        return True  # F^H, M^X, T^a, A^g: a label on a capital
    return False


def _numeric_frac_follows(toks: list[Tok], i: int) -> bool:
    """toks[i] is \\frac; are both arguments plain integers?"""
    j = i + 1
    for _ in range(2):
        if j >= len(toks):
            return False
        if _is_char(toks[j], "{"):
            e = group_end(toks, j)
            if not all(t.kind == "DIGIT" for t in toks[j + 1:e]) or e == j + 1:
                return False
            j = e + 1
        elif toks[j].kind == "DIGIT":
            j += 1
        else:
            return False
    return True


def _standalone_group_before(toks: list[Tok], close: int) -> bool:
    """toks[close] is `}`: is its group a free-standing `{...}` (like `{\\mathcal P}`), not an argument
    of `_`, `^`, `\\frac`, `\\mathbf`, ...?"""
    depth = 0
    for j in range(close, -1, -1):
        t = toks[j]
        if _is_char(t, "}"):
            depth += 1
        elif _is_char(t, "{"):
            depth -= 1
            if depth == 0:
                prev = toks[j - 1] if j > 0 else None
                return not (prev is not None and (prev.kind == "CMD" or _is_char(prev, "_") or _is_char(prev, "^")
                                                   or _is_char(prev, "}")))
    return False


def _is_lone_cmd(toks: list[Tok], names: tuple[str, ...], nargs: int) -> bool:
    """toks is exactly `\\cmd{..}{..}` (or single-token arguments)."""
    toks = [t for t in toks if t.kind != "SPACE"]
    if not toks or not (toks[0].kind == "CMD" and toks[0].value in names):
        return False
    i = 1
    for _ in range(nargs):
        if i >= len(toks):
            return False
        if _is_char(toks[i], "{"):
            i = group_end(toks, i) + 1
        else:
            i += 1
    return i == len(toks)


def _plain_word(arg: list[Tok], n: int) -> bool:
    return len(arg) >= n and all(a.kind == "LETTER" for a in arg)


def _tensor_indices(arg: list[Tok]) -> bool:
    """`\\gamma^\\mu`, `\\eta^{\\mu\\nu}`, `B^{i\\alpha}`: index letters only, at least one greek index."""
    names = [a.value if a.kind == "LETTER" else _sym_cmd_name(a) for a in arg]
    if any(nm is None for nm in names):
        return False
    if len(names) == 1:
        return names[0] in ("mu", "nu")
    return all(nm in TENSOR_INDEX or nm in INDEX_LETTERS for nm in names) and any(nm in TENSOR_INDEX for nm in names)


def plain_letters(toks: list[Tok]) -> set[str]:
    """Letters used without a subscript (and outside subscripts and accent arguments)."""
    out: set[str] = set()
    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if _is_char(t, "_") or (t.kind == "CMD" and (t.value in ACCENTS or t.value in VECTOR_STYLE or t.value in SCRIPT_STYLE)):
            _, i = _read_script_toks(toks, i + 1)
            continue
        nm = t.value if t.kind == "LETTER" else _sym_cmd_name(t)
        if nm and not (i + 1 < n and _is_char(toks[i + 1], "_")):
            out.add(nm)
        i += 1
    return out


def main_letters(toks: list[Tok]) -> set[str]:
    """Single-letter / greek names used as symbols outside of subscripts and bigop limits."""
    out: set[str] = set()
    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if _is_char(t, "_") or (t.kind == "CMD" and (t.value in ACCENTS or t.value in VECTOR_STYLE or t.value in SCRIPT_STYLE)):
            _, i = _read_script_toks(toks, i + 1)  # subscripts and accent/style arguments are not plain uses
            continue
        if t.kind == "LETTER":
            out.add(t.value)
        elif _sym_cmd_name(t):
            out.add(_sym_cmd_name(t))
        i += 1
    return out - {"d", "e", "i"}


def _whole_side_names(toks: list[Tok]) -> set[str]:
    """Names that make up an entire side of a relation on their own (`E` in `E = E(R/p)`)."""
    out = set()
    side: list[Tok] = []
    depth = 0
    for t in toks + [Tok("CHAR", "=", 0, 0)]:
        if depth == 0 and is_relation(t):
            core = [x for x in side if x.kind != "SPACE"]
            if len(core) == 1:
                nm = core[0].value if core[0].kind == "LETTER" else _sym_cmd_name(core[0])
                if nm:
                    out.add(nm)
            side = []
            continue
        if t.kind == "CHAR" and t.value in "([{":
            depth += 1
        elif t.kind == "CHAR" and t.value in ")]}":
            depth -= 1
        side.append(t)
    return out


def _is_single_atom(inner: list[Tok]) -> bool:
    if not inner:
        return False
    if all(t.kind == "DIGIT" for t in inner):
        return True
    t = inner[0]
    if t.kind == "CMD" and (t.value in VECTOR_STYLE or t.value in ACCENTS or t.value in SCRIPT_STYLE) and len(inner) > 1:
        arg, k = _read_script_toks(inner, 1)  # n(\mathbf r), f(\hat x)
        return len(arg) == 1 and (arg[0].kind == "LETTER" or bool(_sym_cmd_name(arg[0]))) and k == len(inner)
    if not (t.kind == "LETTER" or _sym_cmd_name(t)):
        return False
    rest = inner[1:]
    if not rest:
        return True
    if _is_char(rest[0], "_"):
        _, k = _read_script_toks(rest, 1)
        return k == len(rest)
    return False


def parse_side(toks: list[Tok], ctx: Ctx):
    return Parser(toks, ctx).parse_side()
