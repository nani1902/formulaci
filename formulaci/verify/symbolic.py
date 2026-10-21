"""Symbolic check. Runs inside a worker process that the supervisor kills on timeout."""
from __future__ import annotations

import sympy as sp

from formulaci.verify.reconstruct import Problem


def _is_zero(e: sp.Basic) -> bool:
    return e == 0 or (e.is_number and e.is_zero is True)


def _definitely_nonzero_constant(e: sp.Basic) -> bool:
    if not e.is_number or e.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return False
    try:
        v = sp.N(e, 30)
    except Exception:  # noqa: BLE001
        return False
    return v.is_number and abs(complex(v)) > 1e-25


def symbolic_equation(diff: sp.Basic, trace: list[str]) -> str:
    """Return 'equal' | 'not_equal' | 'unknown' for diff == 0."""
    steps = [
        ("as-is", lambda e: e),
        ("expand", sp.expand),
        ("doit", lambda e: e.doit() if e.has(sp.Sum, sp.Product, sp.Integral, sp.Derivative, sp.Limit) else e),
    ]
    cur = diff
    for name, fn in steps:
        cur = fn(cur)
        trace.append(name)
        if _is_zero(cur):
            return "equal"
    for name, fn in [("cancel", sp.cancel), ("trigsimp", sp.trigsimp), ("expand_trig", lambda e: sp.expand(sp.expand_trig(e))),
                     ("gammasimp", sp.gammasimp), ("combsimp", sp.combsimp), ("powsimp", lambda e: sp.powsimp(e, deep=True)),
                     ("expand_log", lambda e: sp.expand(sp.expand_log(e))), ("simplify", sp.simplify)]:
        try:
            out = fn(cur)
        except Exception:  # noqa: BLE001 - simplifiers occasionally raise on odd input
            continue
        trace.append(name)
        if _is_zero(out):
            return "equal"
        if name == "simplify":
            cur = out
    if cur.has(sp.Float):
        try:
            if _is_zero(sp.nsimplify(cur)):
                trace.append("nsimplify")
                return "equal"
        except Exception:  # noqa: BLE001
            pass
    if _definitely_nonzero_constant(cur):
        trace.append("nonzero-constant")
        return "not_equal"
    if not cur.has(sp.Sum, sp.Product, sp.Integral, sp.Piecewise):
        try:
            eq = cur.equals(0)
        except Exception:  # noqa: BLE001
            eq = None
        trace.append(f"equals->{eq}")
        if eq is True:
            return "equal"
        # eq is False is not trusted: sympy's random-point test ignores domain assumptions
    return "unknown"


def symbolic_inequality(p: Problem, trace: list[str]) -> str:
    """'equal' here means the ordering was proved; 'not_equal' that it is refuted outright."""
    d = p.lhs - p.rhs if p.relation in ("<", "<=") else p.rhs - p.lhs  # want d <= 0 / d < 0
    d = d.doit() if d.has(sp.Sum, sp.Product, sp.Integral) else d
    for name, fn in [("as-is", lambda e: e), ("simplify", sp.simplify), ("factor", sp.factor)]:
        try:
            e = fn(d)
        except Exception:  # noqa: BLE001
            continue
        trace.append(name)
        good = e.is_negative if p.relation in ("<", ">") else e.is_nonpositive
        if good is True:
            return "equal"
        if e.is_positive is True:
            return "not_equal"
    return "unknown"


def symbolic_check(p: Problem) -> tuple[str, list[str]]:
    trace: list[str] = []
    if p.relation == "=":
        return symbolic_equation(p.lhs - p.rhs, trace), trace
    return symbolic_inequality(p, trace), trace
