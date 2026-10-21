"""Independent reference evaluator for the bench sets.

The bench must not depend on the translate stage it measures, so it carries its own small
LaTeX -> SymPy parser. It only has to cover the dialect the bench identities are written in
(the Wikipedia subset: \\frac, \\sum, \\int ... \\,dx, \\binom, \\Gamma, \\left( \\right), trailing
\\quad conditions, ...). It is used to (a) prove every known-good identity numerically before it
enters the set and (b) prove every mutation really changes the value.

Variables are declared per identity with a sampling type (see ``SAMPLERS``); undeclared ``e``,
``i``, ``\\pi`` and ``\\gamma`` are the constants E, I, pi and EulerGamma.
"""
from __future__ import annotations

import contextlib
import random
import re
import signal
from dataclasses import dataclass, field

import mpmath
import sympy as sp

# ---------------------------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------------------------


@dataclass
class Tok:
    kind: str  # "cmd" | "num" | "letter" | "sym" | "name"
    text: str  # "\\frac", "12", "x", "+", or for "name": the wrapped name ("erf", "d", "B")
    start: int
    end: int


_WRAPPERS = ("\\mathrm", "\\operatorname", "\\mathit", "\\text", "\\textrm", "\\rm")


def tokenize(s: str) -> list[Tok]:
    toks: list[Tok] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                toks.append(Tok("cmd", "\\" + m.group(1), i, i + m.end()))
                i += m.end()
            else:
                toks.append(Tok("cmd", s[i : i + 2], i, i + 2))
                i += 2
        elif c.isdigit() or (c == "." and i + 1 < n and s[i + 1].isdigit()):
            m = re.match(r"\d*\.?\d+", s[i:])
            toks.append(Tok("num", m.group(0), i, i + m.end()))
            i += m.end()
        elif c.isalpha():
            toks.append(Tok("letter", c, i, i + 1))
            i += 1
        else:
            toks.append(Tok("sym", c, i, i + 1))
            i += 1
    # fold \mathrm{d}, \operatorname{erf}, \text{for} ... into single "name" tokens
    out: list[Tok] = []
    j = 0
    while j < len(toks):
        t = toks[j]
        if t.kind == "cmd" and t.text in _WRAPPERS and j + 1 < len(toks) and toks[j + 1].text == "{":
            k = j + 2
            while k < len(toks) and toks[k].text != "}":
                k += 1
            if k < len(toks):
                inner = s[toks[j + 1].end : toks[k].start].strip()
                kind = "text" if t.text.startswith("\\text") else "name"
                out.append(Tok(kind, inner, t.start, toks[k].end))
                j = k + 1
                continue
        out.append(t)
        j += 1
    return out


# ---------------------------------------------------------------------------------------------
# Body / condition split
# ---------------------------------------------------------------------------------------------

_COND_SEPS = ("\\quad", "\\qquad")


def split_condition(latex: str) -> tuple[str, str]:
    """Split ``body \\quad cond`` (also ``body, \\quad cond`` / ``\\text{for } ...``) at top level."""
    depth = 0
    for t in tokenize(latex):
        if t.text in ("{", "(", "[") or t.text == "\\left":
            depth += 1 if t.text != "\\left" else 0
        if t.text in ("}", ")", "]"):
            depth -= 1
        if depth == 0 and (t.text in _COND_SEPS or (t.kind == "text" and t.text.strip().lower().startswith(("for", "if", "where")))):
            body = latex[: t.start].rstrip()
            return body.rstrip(",;. "), latex[t.start :]
    return latex.rstrip().rstrip(",;. "), ""


# ---------------------------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------------------------


class ParseError(Exception):
    pass


_RELS = {"=": "==", "<": "<", ">": ">", "\\le": "<=", "\\leq": "<=", "\\leqslant": "<=",
         "\\ge": ">=", "\\geq": ">=", "\\geqslant": ">=", "\\lt": "<", "\\gt": ">", "\\ne": "!=", "\\neq": "!="}
_SKIP = {"\\,", "\\;", "\\!", "\\:", "\\ ", "\\displaystyle", "\\textstyle", "\\left", "\\right",
         "\\bigl", "\\bigr", "\\Bigl", "\\Bigr", "\\big", "\\Big", "\\biggl", "\\biggr"}
_FUNCS = {
    "\\sin": sp.sin, "\\cos": sp.cos, "\\tan": sp.tan, "\\cot": sp.cot, "\\sec": sp.sec, "\\csc": sp.csc,
    "\\sinh": sp.sinh, "\\cosh": sp.cosh, "\\tanh": sp.tanh, "\\coth": sp.coth,
    "\\arcsin": sp.asin, "\\arccos": sp.acos, "\\arctan": sp.atan,
    "\\exp": sp.exp, "\\ln": sp.log, "\\log": sp.log,
    "sech": sp.sech, "csch": sp.csch, "arsinh": sp.asinh, "arcosh": sp.acosh, "artanh": sp.atanh,
    "erf": sp.erf, "erfc": sp.erfc, "sgn": sp.sign, "Re": sp.re, "Im": sp.im,
}
# functions that need parenthesised (possibly multi-) arguments
_PFUNCS = {"\\Gamma": sp.gamma, "\\zeta": sp.zeta, "\\psi": sp.digamma, "B": sp.beta, "\\Beta": sp.beta}
_GREEK = {"alpha", "beta", "delta", "epsilon", "varepsilon", "eta", "theta", "vartheta", "kappa",
          "lambda", "mu", "nu", "xi", "rho", "sigma", "tau", "phi", "varphi", "chi", "omega", "gamma"}
_BIGOPS = {"\\sum", "\\prod", "\\int"}


@dataclass
class Parsed:
    sides: list[sp.Expr]
    rels: list[str]  # python relation symbols between consecutive sides
    cond: str = ""


@dataclass
class _P:
    toks: list[Tok]
    vars: dict[str, str]
    pos: int = 0
    bound: list[str] = field(default_factory=list)
    abs_depth: int = 0
    int_depth: int = 0

    # -- token helpers ---------------------------------------------------------------------
    def peek(self, k: int = 0) -> Tok | None:
        p = self.pos
        while p < len(self.toks) and self.toks[p].text in _SKIP:
            p += 1
        while k:
            p += 1
            while p < len(self.toks) and self.toks[p].text in _SKIP:
                p += 1
            k -= 1
        return self.toks[p] if p < len(self.toks) else None

    def next(self) -> Tok:
        while self.pos < len(self.toks) and self.toks[self.pos].text in _SKIP:
            self.pos += 1
        if self.pos >= len(self.toks):
            raise ParseError("unexpected end")
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def expect(self, text: str) -> None:
        t = self.next()
        if t.text != text:
            raise ParseError(f"expected {text!r}, got {t.text!r} at {t.start}")

    def at(self, *texts: str) -> bool:
        t = self.peek()
        return t is not None and t.text in texts

    # -- symbols -----------------------------------------------------------------------------
    def symbol(self, name: str) -> sp.Expr:
        if name in self.bound:
            return _sym(name, "int_bound")
        if name in self.vars:
            return _sym(name, self.vars[name])
        const = {"e": sp.E, "i": sp.I, "pi": sp.pi, "gamma": sp.EulerGamma}.get(name)
        if const is not None:
            return const
        return _sym(name, "real")

    # -- grammar -----------------------------------------------------------------------------
    def relation(self) -> Parsed:
        sides = [self.expr()]
        rels: list[str] = []
        while (t := self.peek()) is not None and t.text in _RELS:
            self.next()
            rels.append(_RELS[t.text])
            sides.append(self.expr())
        if self.peek() is not None:
            raise ParseError(f"trailing input at {self.peek().start}: {self.peek().text!r}")
        return Parsed(sides, rels)

    def expr(self) -> sp.Expr:
        if self.at("-", "+"):
            sign = -1 if self.next().text == "-" else 1
            acc = sign * self.term()
        else:
            acc = self.term()
        while self.at("+", "-", "\\pm"):
            op = self.next().text
            rhs = self.term()
            acc = acc + rhs if op == "+" else acc - rhs
        return acc

    def _starts_factor(self) -> bool:
        t = self.peek()
        if t is None:
            return False
        if t.kind in ("num", "letter"):
            if self.int_depth and t.text == "d" and (n := self.peek(1)) is not None and n.kind == "letter":
                return False
            return True
        if t.kind == "name":
            return not (self.int_depth and t.text == "d")
        if t.kind == "text":
            return False
        if t.text in ("(", "[", "{"):
            return True
        if t.text == "|":
            return self.abs_depth == 0
        if t.kind == "cmd":
            return t.text not in _RELS and t.text not in ("\\cdot", "\\times", "\\quad", "\\qquad", "\\pm", "\\to", "\\right")
        return False

    def term(self, stop_at_func: bool = False) -> sp.Expr:
        acc = self.unary()
        while True:
            if self.at("\\cdot", "\\times", "*"):
                if stop_at_func:
                    break
                self.next()
                acc = acc * self.unary()
            elif self.at("/"):
                self.next()
                acc = acc / self.unary()
            elif self._starts_factor():
                t = self.peek()
                if stop_at_func and (t.text in _FUNCS or t.text in _PFUNCS or t.text in _BIGOPS):
                    break
                acc = acc * self.unary()
            else:
                break
        return acc

    def unary(self) -> sp.Expr:
        if self.at("-"):
            self.next()
            return -self.unary()
        if self.at("+"):
            self.next()
            return self.unary()
        return self.postfix()

    def postfix(self) -> sp.Expr:
        base = self.primary()
        while True:
            if self.at("^"):
                self.next()
                base = base ** self.script_arg()
            elif self.at("!"):
                self.next()
                if self.at("!") and self.peek().start == self.toks[self.pos - 1].end:
                    self.next()
                    base = sp.factorial2(base)
                else:
                    base = sp.factorial(base)
            else:
                return base

    def script_arg(self) -> sp.Expr:
        """Argument of ^ or _: a braced group, or a single token (first digit of a number)."""
        t = self.peek()
        if t is None:
            raise ParseError("missing script")
        if t.text == "{":
            return self.group()
        if t.kind == "num" and len(t.text) > 1:
            self.next()
            # LaTeX takes one char: x^23 == x^2 * 3; we never write that, so refuse
            raise ParseError("ambiguous multi-digit script")
        if t.text == "-":
            self.next()
            return -self.script_arg()
        return self.primary()

    def group(self) -> sp.Expr:
        self.expect("{")
        e = self.expr()
        self.expect("}")
        return e

    def raw_group(self) -> list[Tok]:
        """Return the tokens inside the next {...} without parsing."""
        self.expect("{")
        start, depth = self.pos, 1
        while self.pos < len(self.toks):
            tx = self.toks[self.pos].text
            depth += tx == "{"
            depth -= tx == "}"
            if depth == 0:
                inner = self.toks[start : self.pos]
                self.pos += 1
                return inner
            self.pos += 1
        raise ParseError("unbalanced braces")

    def sub(self, toks: list[Tok]) -> "_P":
        return _P(toks, self.vars, 0, list(self.bound), 0, self.int_depth)

    def parse_toks(self, toks: list[Tok]) -> sp.Expr:
        p = self.sub(toks)
        e = p.expr()
        if p.peek() is not None:
            raise ParseError(f"trailing input in group: {p.peek().text!r}")
        return e

    def primary(self) -> sp.Expr:
        t = self.next()
        k, x = t.kind, t.text
        if k == "num":
            return sp.Rational(x) if "." in x else sp.Integer(x)
        if k == "letter" or (k == "name" and len(x) == 1 and x not in _PFUNCS):
            return self.with_subscript(x)
        if x == "(" or x == "[":
            close = ")" if x == "(" else "]"
            save_abs, self.abs_depth = self.abs_depth, 0
            e = self.expr()
            self.abs_depth = save_abs
            self.expect(close)
            return e
        if x == "{":
            self.pos -= 1
            return self.group()
        if x == "|":
            self.abs_depth += 1
            e = self.expr()
            self.abs_depth -= 1
            self.expect("|")
            return sp.Abs(e)
        if x in ("\\lfloor", "\\lceil"):
            e = self.expr()
            self.expect("\\rfloor" if x == "\\lfloor" else "\\rceil")
            return sp.floor(e) if x == "\\lfloor" else sp.ceiling(e)
        if x in ("\\frac", "\\dfrac", "\\tfrac"):
            return self.frac()
        if x == "\\sqrt":
            idx = None
            if self.at("["):
                self.next()
                idx = self.expr()
                self.expect("]")
            arg = self.group()
            return sp.sqrt(arg) if idx is None else sp.root(arg, idx)
        if x in ("\\binom", "\\tbinom", "\\dbinom"):
            a = self.group()
            b = self.group()
            return sp.binomial(a, b)
        if x == "\\infty":
            return sp.oo
        if x == "\\pi":
            return sp.pi if "pi" not in self.vars else self.symbol("pi")
        if x in ("\\sum", "\\prod"):
            return self.bigop(x)
        if x == "\\int":
            return self.integral()
        if x in _FUNCS or (k == "name" and x in _FUNCS):
            return self.func(x)
        if x in _PFUNCS or (k == "name" and x in _PFUNCS):
            return self.pfunc(x)
        if k == "cmd" and x[1:] in _GREEK:
            return self.with_subscript(x[1:])
        raise ParseError(f"unsupported token {x!r} at {t.start}")

    def with_subscript(self, name: str) -> sp.Expr:
        if self.at("_"):
            self.next()
            t = self.peek()
            if t.text == "{":
                inner = self.raw_group()
                sub = "".join(tt.text for tt in inner)
            else:
                sub = self.next().text
            name = f"{name}_{sub}"
        return self.symbol(name)

    def frac(self) -> sp.Expr:
        num_t = self._frac_arg()
        den_t = self._frac_arg()
        d = _derivative_op(num_t, den_t)
        if d is not None:
            var, order = d
            operand = self.term()
            return sp.diff(operand, self.symbol(var), order)
        return self.parse_toks(num_t) / self.parse_toks(den_t)

    def _frac_arg(self) -> list[Tok]:
        t = self.peek()
        if t is not None and t.text == "{":
            return self.raw_group()
        return [self.next()]  # \tfrac12 style

    def func(self, x: str) -> sp.Expr:
        f = _FUNCS[x]
        power = None
        base = None
        if self.at("^"):
            self.next()
            power = self.script_arg()
        if x == "\\log" and self.at("_"):
            self.next()
            base = self.script_arg()
        if self.at("(") or self.at("["):
            # parenthesised argument, but "\\sin (x) y" style is rare; keep postfix ^ on the call
            arg = self.primary()
        else:
            arg = self.term(stop_at_func=True)
        val = f(arg) if base is None else sp.log(arg, base)
        if self.at("^") and power is None:
            self.next()
            power = self.script_arg()
        return val if power is None else val**power

    def pfunc(self, x: str) -> sp.Expr:
        f = _PFUNCS[x]
        if not self.at("("):
            raise ParseError(f"{x} needs (...)")
        self.next()
        args = [self.expr()]
        while self.at(","):
            self.next()
            args.append(self.expr())
        self.expect(")")
        return f(*args)

    def _bounds(self) -> tuple[list[Tok] | None, sp.Expr | None]:
        lo_t, hi = None, None
        for _ in range(2):
            if self.at("_"):
                self.next()
                lo_t = self.raw_group() if self.at("{") else [self.next()]
            elif self.at("^"):
                self.next()
                hi = self.script_arg()
        return lo_t, hi

    def bigop(self, x: str) -> sp.Expr:
        lo_t, hi = self._bounds()
        if lo_t is None or hi is None:
            raise ParseError(f"{x} needs both bounds")
        eq = [i for i, t in enumerate(lo_t) if t.text == "="]
        if not eq or lo_t[0].kind != "letter":
            raise ParseError(f"{x} lower bound must be var=value")
        var = lo_t[0].text
        lo = self.parse_toks(lo_t[eq[0] + 1 :])
        self.bound.append(var)
        try:
            body = self.term()
        finally:
            self.bound.pop()
        v = _sym(var, "int_bound")
        return (sp.Sum if x == "\\sum" else sp.Product)(body, (v, lo, hi))

    def integral(self) -> sp.Expr:
        lo_t, hi = self._bounds()
        if lo_t is None or hi is None:
            raise ParseError("only definite integrals are supported")
        lo = self.parse_toks(lo_t)
        self.int_depth += 1
        try:
            body = self.expr()
        finally:
            self.int_depth -= 1
        t = self.next()
        if t.text != "d":
            raise ParseError("integral without differential")
        var = self.next()
        if var.kind != "letter":
            raise ParseError("bad differential")
        return sp.Integral(body, (_sym(var.text, "int_var"), lo, hi))


def _derivative_op(num: list[Tok], den: list[Tok]) -> tuple[str, int] | None:
    """Recognise d/dx, d^n/dx^n (also \\mathrm{d}, \\partial)."""
    nt = [t.text for t in num if t.text not in _SKIP]
    dt = [t.text for t in den if t.text not in _SKIP]
    if not nt or nt[0] not in ("d", "\\partial"):
        return None
    order = 1
    if len(nt) > 1 and nt[1] == "^":
        digits = [s for s in nt[2:] if s.isdigit()]
        if not digits:
            return None
        order = int(digits[0])
    elif len(nt) != 1:
        return None
    if len(dt) < 2 or dt[0] not in ("d", "\\partial") or not dt[1].isalpha():
        return None
    return dt[1], order


_SYMCACHE: dict[tuple[str, str], sp.Symbol] = {}

_ASSUME = {
    "real": dict(real=True), "pos": dict(positive=True), "pos1": dict(positive=True),
    "gt1": dict(positive=True), "unit": dict(positive=True), "sym1": dict(real=True),
    "gtm1": dict(real=True), "posint": dict(integer=True, positive=True),
    "nonnegint": dict(integer=True, nonnegative=True), "int": dict(integer=True),
    "complex": dict(), "int_bound": dict(integer=True), "int_var": dict(real=True),
}


def _sym(name: str, typ: str) -> sp.Symbol:
    key = (name, typ)
    if key not in _SYMCACHE:
        _SYMCACHE[key] = sp.Symbol(name, **_ASSUME.get(typ, {}))
    return _SYMCACHE[key]


def parse(latex: str, vars: dict[str, str] | None = None) -> Parsed:
    """Parse a (Wikipedia-dialect) LaTeX relation. Raises ParseError."""
    body, cond = split_condition(latex)
    p = _P(tokenize(body), dict(vars or {}))
    try:
        out = p.relation()
    except (ParseError, sp.SympifyError) as e:
        raise ParseError(str(e)) from e
    except (TypeError, ValueError, AttributeError, IndexError) as e:
        raise ParseError(f"{type(e).__name__}: {e}") from e
    out.cond = cond
    return out


# ---------------------------------------------------------------------------------------------
# Numeric checking
# ---------------------------------------------------------------------------------------------

SAMPLERS = {
    "real": lambda r: r.uniform(-3, 3),
    "pos": lambda r: r.uniform(0.2, 4),
    "pos1": lambda r: r.uniform(1, 4),
    "gt1": lambda r: r.uniform(1.5, 4),
    "unit": lambda r: r.uniform(0.05, 0.95),
    "sym1": lambda r: r.uniform(-0.9, 0.9),
    "gtm1": lambda r: r.uniform(-1, 3),
    "posint": lambda r: r.randint(1, 8),
    "nonnegint": lambda r: r.randint(0, 8),
    "int": lambda r: r.randint(-5, 5),
    "complex": lambda r: complex(r.uniform(-2, 2), r.uniform(-2, 2)),
}


class _Timeout(Exception):  # noqa: N818
    pass


@contextlib.contextmanager
def _time_limit(seconds: float):
    if seconds <= 0 or not hasattr(signal, "setitimer"):
        yield
        return

    def handler(signum, frame):
        raise _Timeout()

    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def sample_points(vars: dict[str, str], cond: str | None, n: int, seed: int) -> list[dict[str, object]]:
    """Draw up to n assignments (rejection sampling on the Python-expression ``cond``)."""
    rng = random.Random(seed)
    pts: list[dict[str, object]] = []
    tries = 0
    while len(pts) < n and tries < 200 * n:
        tries += 1
        pt = {v: SAMPLERS[t](rng) for v, t in vars.items()}
        env = {**pt, "abs": abs, "min": min, "max": max}
        if cond and not eval(cond, {"__builtins__": {}}, env):  # noqa: S307 - our own data
            continue
        if pt in pts and vars:
            continue
        pts.append(pt)
        if not vars:
            break
    return pts


def _subs_value(v: object, typ: str) -> sp.Expr:
    if isinstance(v, complex):
        return sp.Float(v.real, 30) + sp.I * sp.Float(v.imag, 30)
    if isinstance(v, int):
        return sp.Integer(v)
    return sp.Float(v, 30)


_BIG = (sp.Sum, sp.Product, sp.Integral)


def _outermost_big(e: sp.Basic):
    if isinstance(e, _BIG):
        yield e
        return
    for a in e.args:
        yield from _outermost_big(a)


def _num(e: sp.Expr) -> sp.Expr:
    """N(e) with every Sum/Product/Integral evaluated by mpmath (sympy's Sum.evalf is unreliable
    for parametric infinite series)."""
    sub = {n: _eval_big(n) for n in set(_outermost_big(e))}
    return sp.N(e.xreplace(sub) if sub else e, 30)


def _eval_big(node) -> sp.Expr:
    body, lim = node.function, node.limits[0]
    if len(node.limits) != 1 or len(lim) != 3:
        raise ValueError("unsupported limits")
    v, a, b = lim
    integer = not isinstance(node, sp.Integral)

    def bound(x):
        if x in (sp.oo, -sp.oo):
            return mpmath.inf if x == sp.oo else -mpmath.inf
        val = _num(x)
        if val.free_symbols:
            raise ValueError("symbolic bound")
        return mpmath.mpmathify(complex(val)) if not val.is_real else mpmath.mpf(str(val))

    if body.has(*_BIG):
        def f(t):
            tt = sp.Integer(int(t)) if integer else sp.Float(str(t), 30)
            return mpmath.mpmathify(complex(_num(body.xreplace({v: tt}))))
    else:
        g = sp.lambdify(v, body, modules="mpmath")

        def f(t):
            return g(mpmath.mpf(t))  # Euler-Maclaurin samples non-integer t, so no rounding

    lo, hi = bound(a), bound(b)
    with mpmath.workdps(30):
        if isinstance(node, sp.Integral):
            val = mpmath.quad(f, [lo, hi])
        elif hi == mpmath.inf:
            if isinstance(node, sp.Sum):
                val = mpmath.nsum(f, [lo, mpmath.inf])
                try:
                    alt = mpmath.nsum(f, [lo, mpmath.inf], method="levin")
                except Exception:  # noqa: BLE001 - Levin is only a cross-check
                    alt = val
                if abs(alt - val) > 1e-20 * max(1, abs(val)):  # slow (e.g. n^-s): Euler-Maclaurin
                    val = mpmath.nsum(f, [lo, mpmath.inf], method="e")
            else:
                val = mpmath.nprod(f, [lo, mpmath.inf])
        else:
            lo_i, hi_i = int(lo), int(hi)
            if hi_i - lo_i > 100000:
                raise ValueError("finite range too long")
            terms = [f(k) for k in range(lo_i, hi_i + 1)]
            val = mpmath.fsum(terms) if isinstance(node, sp.Sum) else mpmath.fprod(terms)
    c = complex(val)
    return sp.Float(c.real, 30) + sp.I * sp.Float(c.imag, 30) if c.imag else sp.Float(str(val.real if hasattr(val, "real") else val), 30)


def evaluate(expr: sp.Expr, vars: dict[str, str], pt: dict[str, object], timeout: float = 8.0):
    sub = {_sym(name, typ): _subs_value(pt[name], typ) for name, typ in vars.items()}
    # symbols created with a different assumption set (e.g. undeclared) are left alone -> error
    with _time_limit(timeout):
        val = _num(expr.xreplace(sub))
    if val.free_symbols:
        raise ValueError(f"unbound symbols {val.free_symbols}")
    c = complex(val)
    if c != c or abs(c) == float("inf"):
        raise ValueError("non-finite")
    return c


def _holds(rel: str, a: complex, b: complex, rtol: float) -> bool:
    scale = max(abs(a), abs(b), 1.0)
    if rel == "==":
        return abs(a - b) <= rtol * scale
    if rel == "!=":
        return abs(a - b) > rtol * scale
    if abs(a.imag) > 1e-12 * scale or abs(b.imag) > 1e-12 * scale:
        raise ValueError("complex value in inequality")
    x, y, tol = a.real, b.real, rtol * scale
    return {"<": x < y + tol, "<=": x <= y + tol, ">": x > y - tol, ">=": x >= y - tol}[rel]


@dataclass
class CheckResult:
    n_points: int
    n_eval: int
    n_fail: int
    errors: list[str]
    example: dict | None = None

    @property
    def holds(self) -> bool:
        return self.n_eval >= 1 and self.n_fail == 0

    @property
    def majority_fails(self) -> bool:
        return self.n_eval >= 1 and 2 * self.n_fail > self.n_eval


def check(parsed: Parsed, vars: dict[str, str], cond: str | None = None, n: int = 6, seed: int = 0,
          rtol: float = 1e-10, timeout: float = 20.0, stop_after_fails: int | None = None) -> CheckResult:
    pts = sample_points(vars, cond, n, seed)
    n_eval = n_fail = 0
    errors: list[str] = []
    example = None
    for pt in pts:
        try:
            vals = [evaluate(s, vars, pt, timeout) for s in parsed.sides]
            ok = all(_holds(r, vals[i], vals[i + 1], rtol) for i, r in enumerate(parsed.rels))
        except Exception as e:  # noqa: BLE001 - any evaluation failure (zoo, nan, timeouts) = not evaluable
            if isinstance(e, KeyboardInterrupt):
                raise
            errors.append(f"{type(e).__name__}: {str(e)[:80]}")
            continue
        n_eval += 1
        if not ok:
            n_fail += 1
            if example is None:
                example = {"point": {k: str(v) for k, v in pt.items()}, "values": [str(v) for v in vals]}
            if stop_after_fails and n_fail >= stop_after_fails:
                break
    return CheckResult(len(pts), n_eval, n_fail, errors, example)
