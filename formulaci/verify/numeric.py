"""Compile sympy expressions to mpmath callables and evaluate identities at sample points.

Elementary and special functions go through `lambdify(..., "mpmath")`. `Sum`/`Product`/`Integral`
nodes are replaced by placeholders and evaluated by our own closures, so that symbolic bounds are
instantiated per point, infinite sums/products use `nsum`/`nprod` with a convergence check, and
integrals use `mpmath.quad` with an error estimate. `Derivative` and `Limit` are resolved
symbolically (`doit`) before compiling.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import mpmath as mp
import sympy as sp

from formulaci.verify.reconstruct import Problem
from formulaci.verify.sampler import Value, to_mp

DPS = 50
LADDER = (50, 65, 100, 200, 400, 1000)  # failing points climb this ladder until the result is trustworthy
REL_TOL = mp.mpf("1e-8")
MAX_FINITE_TERMS = 20000
DIRECT_TERMS = 3000
POINT_SECONDS = 2.0  # per-point alarm inside the worker


class EvalError(Exception):
    pass


class _MpBinomial(sp.Function):
    """binomial printed as mpmath.binomial (lambdify's default gamma-ratio form has poles)."""
    nargs = 2


_MODULES = [{"_MpBinomial": mp.binomial, "LambertW": mp.lambertw, "lambertw": mp.lambertw,
             "Abs": mp.fabs, "fabs": mp.fabs}, "mpmath"]
_AGG = (sp.Sum, sp.Product, sp.Integral)


def resolve_calculus(expr: sp.Basic) -> sp.Basic:
    """Evaluate Derivative and Limit nodes symbolically, innermost first."""
    if expr.has(sp.Derivative):
        expr = expr.replace(lambda e: isinstance(e, sp.Derivative), lambda e: e.doit())
    if expr.has(sp.Limit):
        expr = expr.replace(lambda e: isinstance(e, sp.Limit), lambda e: e.doit())
        if expr.has(sp.Limit):
            raise EvalError("limit could not be evaluated symbolically")
    if expr.has(sp.Derivative):
        raise EvalError("derivative could not be evaluated")
    return expr


def _to_mp(x):
    if isinstance(x, (mp.mpf, mp.mpc)):
        return x
    if isinstance(x, bool):
        return mp.mpf(int(x))
    if hasattr(x, "_mpf_"):  # lazy constants such as mpmath.pi
        return mp.mpf(x)
    try:
        return mp.mpmathify(x)
    except (TypeError, ValueError):
        return x


def _as_int(v) -> int:
    v = _to_mp(v)
    if isinstance(v, mp.mpc):
        if abs(v.imag) > mp.mpf("1e-20"):
            raise EvalError("complex summation bound")
        v = v.real
    if not mp.isfinite(v):
        raise EvalError("infinite bound in finite context")
    n = int(mp.nint(v))
    if abs(v - n) > mp.mpf("1e-20"):
        raise EvalError("non-integer summation bound")
    return n


def _is_inf(v) -> int:
    v = _to_mp(v)
    if isinstance(v, mp.mpf) and mp.isinf(v):
        return 1 if v > 0 else -1
    return 0


def compile_expr(expr: sp.Basic, args: list[sp.Symbol]):
    """Return f(*mp_values) -> mp number. Raises EvalError at call time on failure."""
    expr = expr.replace(lambda e: isinstance(e, sp.binomial), lambda e: _MpBinomial(*e.args))
    aggs = sorted(_top_level_aggregates(expr), key=sp.default_sort_key)
    dummies = [sp.Dummy(f"agg{i}") for i in range(len(aggs))]
    body = expr.xreplace(dict(zip(aggs, dummies))) if aggs else expr
    leftovers = body.atoms(sp.Derivative, sp.Limit, sp.Order)
    if leftovers:
        raise EvalError(f"unsupported construct {type(next(iter(leftovers))).__name__}")
    try:
        outer = sp.lambdify(list(args) + dummies, body, modules=_MODULES)
    except Exception as e:  # noqa: BLE001
        outer = _evalf_fallback(body, list(args) + dummies, e)
    agg_fns = [_compile_aggregate(a, args) for a in aggs]

    def f(*vals):
        extra = [g(*vals) for g in agg_fns]
        try:
            return _to_mp(outer(*vals, *extra))
        except (ZeroDivisionError, OverflowError, ValueError, TypeError, ArithmeticError) as e:
            raise EvalError(f"{type(e).__name__}: {e}") from None
    return f


def _evalf_fallback(body, args, err):
    def g(*vals):
        subs = {a: sp.Float(str(v), DPS) if not isinstance(v, mp.mpc)
                else sp.Float(str(v.real), DPS) + sp.I * sp.Float(str(v.imag), DPS)
                for a, v in zip(args, vals)}
        out = body.evalf(mp.mp.dps, subs=subs)
        if not out.is_number:
            raise EvalError(f"could not evaluate numerically ({err})")
        c = complex(out) if not out.is_real else None
        return mp.mpf(str(out)) if c is None else mp.mpc(str(sp.re(out)), str(sp.im(out)))
    return g


def _top_level_aggregates(expr):
    out = []
    if isinstance(expr, _AGG):
        return [expr]
    for a in expr.args:
        out.extend(_top_level_aggregates(a))
    return out


def _compile_aggregate(node, args):
    # peel multiple limits into nested single-limit nodes (innermost limit first)
    if len(node.limits) > 1:
        inner = node.func(node.function, node.limits[0])
        return _compile_aggregate(node.func(inner, *node.limits[1:]), args)
    lim = node.limits[0]
    if len(lim) != 3:
        raise EvalError(f"indefinite {type(node).__name__} cannot be evaluated numerically")
    var = sp.Dummy("k", **lim[0].assumptions0)  # the bound variable's name never reaches codegen
    fa, fb = compile_expr(lim[1], args), compile_expr(lim[2], args)
    body = compile_expr(node.function.xreplace({lim[0]: var}), list(args) + [var])

    if isinstance(node, sp.Integral):
        def integral(*vals):
            a, b = fa(*vals), fb(*vals)
            g = lambda t: body(*vals, t)  # noqa: E731
            # quad's own error estimate can be badly optimistic for sharply peaked integrands,
            # so the value must also be reproduced on a subdivided interval
            try:
                val, err = mp.quad(g, [a, b], error=True, maxdegree=8)
                # (at confirmation rungs the 50-digit value was already cross-checked)
                val2 = mp.quad(g, _subdivide(a, b), maxdegree=8) if mp.mp.dps <= DPS else val
            except EvalError:
                raise
            except Exception as e:  # noqa: BLE001
                raise EvalError(f"quad failed: {e}") from None
            scale = max(abs(val), abs(val2))
            if not mp.isfinite(scale) or err > mp.mpf("1e-15") * scale \
                    or abs(val - val2) > mp.mpf("1e-12") * scale:
                raise EvalError("integral did not converge")
            return val
        return integral

    is_sum = isinstance(node, sp.Sum)

    def aggregate(*vals):
        a_raw, b_raw = fa(*vals), fb(*vals)
        a_inf, b_inf = _is_inf(a_raw), _is_inf(b_raw)
        term = lambda k: body(*vals, mp.mpf(k) if not isinstance(k, mp.mpf) else k)  # noqa: E731
        if a_inf or b_inf:
            if a_inf == -1 or b_inf != 1:
                raise EvalError("only [a, oo) infinite ranges are supported")
            return _infinite(term, _as_int(a_raw), is_sum)
        a, b = _as_int(a_raw), _as_int(b_raw)
        if b < a - 1:
            raise EvalError("reversed summation range (convention-dependent)")
        if b - a + 1 > MAX_FINITE_TERMS:
            raise EvalError("finite range too long")
        acc = mp.mpf(0) if is_sum else mp.mpf(1)
        for k in range(a, b + 1):
            t = term(k)
            acc = acc + t if is_sum else acc * t
        return acc
    return aggregate


def _subdivide(a, b) -> list:
    ia, ib = _is_inf(a), _is_inf(b)
    if ia == 0 and ib == 0:
        return [a + (b - a) * j / 5 for j in range(6)]
    if ia == 0:
        return [a, a + 1, a + 10, b]
    if ib == 0:
        return [a, b - 10, b - 1, b]
    return [a, -3, mp.mpf("0.5"), 3, b]


def _infinite(term, a: int, is_sum: bool):
    """Sum or product over [a, oo). Direct accumulation when terms decay fast enough; otherwise
    nsum/nprod extrapolation, accepted only if two working precisions agree."""
    target = 0 if is_sum else 1
    try:
        d1, d2 = abs(term(a + 2000) - target), abs(term(a + 8000) - target)
    except EvalError:
        raise
    except Exception as e:  # noqa: BLE001
        raise EvalError(f"term evaluation failed: {e}") from None
    if not (d2 < mp.mpf("1e-3") and d2 <= d1 * 1.0001):
        raise EvalError("series terms do not tend to zero; treated as divergent")
    # 1) direct accumulation until 5 consecutive terms are negligible
    acc, small = (mp.mpf(0) if is_sum else mp.mpf(1)), 0
    eps = mp.mpf(10) ** (-(mp.mp.dps + 3))
    for k in range(a, a + DIRECT_TERMS):
        t = term(k)
        acc = acc + t if is_sum else acc * t
        dev = abs(t - target)
        small = small + 1 if dev <= eps * max(abs(acc), eps) else 0
        if small >= 5:
            return acc
        if k - a >= 100 and k % 50 == 0:  # slow (non-geometric) decay: leave it to extrapolation
            if dev > abs(term(k - 50) - target) * mp.mpf("0.2"):
                break
    # 2) extrapolation, cross-checked by restarting it SHIFT terms later at a higher precision
    #    (a wrong extrapolation rarely survives a change of starting point)
    fn = mp.nsum if is_sum else mp.nprod
    shift = 25
    try:
        v1 = fn(term, [a, mp.inf])
        with mp.extradps(10):
            head = mp.fsum(term(k) for k in range(a, a + shift)) if is_sum \
                else mp.fprod(term(k) for k in range(a, a + shift))
            tail = fn(term, [a + shift, mp.inf])
            v2 = head + tail if is_sum else head * tail
    except EvalError:
        raise
    except Exception as e:  # noqa: BLE001
        raise EvalError(f"series evaluation failed: {e}") from None
    if not mp.isfinite(abs(v2)) or abs(v1 - v2) > mp.mpf(10) ** (-(mp.mp.dps - 15)) * max(1, abs(v2)):
        raise EvalError("series extrapolation did not converge")
    return +v2


# ---------------------------------------------------------------- evaluation of an identity

def is_slow(p: Problem) -> bool:
    """Integrals and infinite sums/products cost ~0.1-1 s per point."""
    return bool(p.lhs.atoms(sp.Integral) or p.rhs.atoms(sp.Integral)) or any(
        sp.oo in (abs(lim[1]), abs(lim[2]))
        for side in (p.lhs, p.rhs) for agg in side.atoms(sp.Sum, sp.Product) for lim in agg.limits
        if len(lim) == 3)


@dataclass
class PointResult:
    point: dict[str, Value]
    status: str  # "pass" | "fail" | "error"
    lhs: object = None
    rhs: object = None
    abs_diff: object = None
    rel_diff: object = None
    error: str = ""


@dataclass
class Evaluator:
    problem: Problem
    lhs_f: object = None
    rhs_f: object = None
    names: list[str] = field(default_factory=list)
    point_seconds: float = POINT_SECONDS
    rel_tol: object = REL_TOL  # widened only by a `tol:` hint from Semantics
    abs_tol: object = mp.mpf(0)
    hard_deadline: float | None = None  # time.monotonic() value no point may run past
    slow: bool = False  # integrals or infinite sums/products: sample fewer points
    zero_sides: tuple = (False, False)  # sides that are literally 0, where an exact 0 is trustworthy
    allow_complex: bool = False  # the formula itself contains I, so complex values are expected
    error: str = ""

    @classmethod
    def build(cls, p: Problem) -> "Evaluator":
        ev = cls(p)
        ev.names = [s.name for s in p.syms]
        ev.allow_complex = bool(p.lhs.has(sp.I) or p.rhs.has(sp.I))
        ev.zero_sides = (p.lhs == 0, p.rhs == 0)
        ev.slow = is_slow(p)
        if ev.slow:
            ev.point_seconds = 2.5 * POINT_SECONDS
        if not p.syms:
            ev.point_seconds = 4 * POINT_SECONDS  # one point only: afford slow series/integrals
        # safe positional names: symbol names from Wikipedia never reach generated code
        safe = [sp.Symbol(f"v{i}", **s.symbol.assumptions0) for i, s in enumerate(p.syms)]
        repl = {s.symbol: v for s, v in zip(p.syms, safe)}
        try:
            lhs = resolve_calculus(p.lhs.xreplace(repl))
            rhs = resolve_calculus(p.rhs.xreplace(repl))
            ev.lhs_f, ev.rhs_f = compile_expr(lhs, safe), compile_expr(rhs, safe)
        except EvalError as e:
            ev.error = str(e)
        except Exception as e:  # noqa: BLE001
            ev.error = f"compile failed: {type(e).__name__}: {e}"
        ev._constraint_fns = []
        for c in p.constraints:
            try:
                ev._constraint_fns.append(sp.lambdify(safe, c.xreplace(repl), modules=_MODULES))
            except Exception:  # noqa: BLE001
                ev._constraint_fns.append(lambda *a, _c=c.xreplace(repl): bool(
                    _c.subs({s: sp.nsimplify(str(v)) for s, v in zip(safe, a)})))
        return ev

    def satisfies(self, point: dict[str, Value]) -> bool:
        if not self._constraint_fns:
            return True
        vals = [to_mp(point[n]) for n in self.names]
        for fn in self._constraint_fns:
            try:
                if not bool(fn(*vals)):
                    return False
            except Exception:  # noqa: BLE001 - e.g. comparison of complex numbers
                return False
        return True

    def _eval_sides(self, vals):
        try:
            l = self.lhs_f(*vals)
            r = self.rhs_f(*vals)
        except EvalError:
            raise
        except Exception as e:  # noqa: BLE001
            raise EvalError(f"{type(e).__name__}: {e}") from None
        for v in (l, r):
            if not isinstance(v, (mp.mpf, mp.mpc)):
                raise EvalError(f"non-numeric value {v!r}")
            if not mp.isfinite(abs(v)) or mp.isnan(abs(v)):
                raise EvalError("non-finite value (pole or overflow)")
        return l, r

    def _eval_at(self, point, dps: int):
        mp.mp.dps = dps
        return self._eval_sides([to_mp(point[n]) for n in self.names])

    def evaluate(self, point: dict[str, Value], complex_regime: bool) -> PointResult:
        """Evaluate both sides at `point`.

        A mismatch at 50 digits is only a failure once it is trustworthy: both sides must agree
        to 1e-15 with their values at the next rung of the precision ladder (otherwise
        cancellation is eating the digits and we keep climbing), and an exact 0 from a
        non-trivial expression must persist to the top rung. A difference that shrinks as the
        precision grows is rounding noise around zero, i.e. a pass.
        """
        res = PointResult(point, "error")
        if self.error:
            res.error = self.error
            return res
        old = mp.mp.dps
        budget = self.point_seconds
        if self.hard_deadline is not None:
            budget = min(budget, self.hard_deadline - time.monotonic())
        if budget <= 0.05:
            res.error = "no time left"
            return res
        with _alarm(budget):
            try:
                prev = None  # (dps, lhs, rhs, abs_diff) at the previous rung
                for i, dps in enumerate(LADDER):
                    l, r = self._eval_at(point, dps)
                    if i == 0:
                        res.lhs, res.rhs = l, r
                        if not (complex_regime or self.allow_complex) and (_nonreal(l) or _nonreal(r)):
                            res.error = "value left the real line (outside the real domain)"
                            return res
                    status, ad, rd = self._compare(l, r)
                    if status == "pass" or (
                            prev is not None and ad < prev[3] * mp.mpf(10) ** (-((dps - prev[0]) // 2))):
                        # agreement, or a difference that shrinks with precision (noise around 0)
                        res.status, res.abs_diff, res.rel_diff = "pass", ad, rd
                        return res
                    if prev is not None and _stable(l, prev[1]) and _stable(r, prev[2]):
                        # an exact 0 from a non-trivial side may be total cancellation: it must
                        # survive the whole ladder
                        exact_zero = (l == 0 and not self.zero_sides[0]) or (r == 0 and not self.zero_sides[1])
                        if not exact_zero or i == len(LADDER) - 1:
                            res.status, res.lhs, res.rhs, res.abs_diff, res.rel_diff = "fail", l, r, ad, rd
                            return res
                    prev = (dps, l, r, ad)
                res.error = f"numerically unstable up to {LADDER[-1]} digits"
                return res
            except EvalError as e:
                res.error = str(e)
                return res
            except PointTimeout:
                res.error = f"point evaluation exceeded {self.point_seconds:.0f}s"
                return res
            except Exception as e:  # noqa: BLE001
                res.error = f"{type(e).__name__}: {e}"
                return res
            finally:
                mp.mp.dps = old

    def _compare(self, l, r):
        rel = self.problem.relation
        ad = abs(l - r)
        scale = max(abs(l), abs(r))
        rd = ad / scale if scale else mp.mpf(0)
        if rel == "=":
            return ("pass" if rd <= self.rel_tol or ad <= self.abs_tol else "fail"), ad, rd
        # inequality: both sides must be real
        if _nonreal(l) or _nonreal(r):
            raise EvalError("complex value in an inequality")
        l, r = mp.re(l), mp.re(r)
        violation = l - r if rel in ("<", "<=") else r - l
        ok = violation <= max(self.rel_tol * scale, self.abs_tol)  # strict relations are accepted at equality within tolerance
        return ("pass" if ok else "fail"), ad, rd


class PointTimeout(BaseException):  # not swallowed by broad excepts inside mpmath
    pass


class _alarm:
    """SIGALRM-based per-point timeout (mpmath is pure Python, so this interrupts it)."""

    def __init__(self, seconds: float):
        self.seconds = seconds
        self.old = None

    def _handler(self, signum, frame):
        raise PointTimeout()

    def __enter__(self):
        import signal
        import threading

        if hasattr(signal, "setitimer") and threading.current_thread() is threading.main_thread():
            self.old = signal.signal(signal.SIGALRM, self._handler)
            signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc):
        import signal

        if self.old is not None:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self.old)
        return False


def _stable(a, b) -> bool:
    d = abs(a - b)
    scale = max(abs(a), abs(b))
    return d == 0 or d <= mp.mpf("1e-15") * scale


def _nonreal(v) -> bool:
    return isinstance(v, mp.mpc) and abs(v.imag) > mp.mpf("1e-30") * max(1, abs(v))


def fmt_num(v, digits: int = 40) -> str:
    if v is None:
        return ""
    if isinstance(v, mp.mpc) and not _nonreal(v):
        v = v.real
    if v == 0:
        return "0"  # exact
    return mp.nstr(v, digits, strip_zeros=False) if isinstance(v, mp.mpf) else mp.nstr(v, digits)


def deadline_left(deadline: float | None) -> float:
    return float("inf") if deadline is None else deadline - time.monotonic()
