"""Task functions executed inside worker processes. Inputs and outputs are plain dicts.

Three tasks per formula link, each under its own supervisor timeout:
  prepare  -> rebuild the problem, return metadata or a SKIP reason
  symbolic -> symbolic check
  numeric  -> sampled evaluation per regime (cooperative deadline; hard kill as backstop)
"""
from __future__ import annotations

import random
import time

import mpmath as mp
import sympy as sp

from formulaci.schemas import Parsed, Semantics
from formulaci.verify import guards
from formulaci.verify import numeric as num
from formulaci.verify.reconstruct import (NotCheckable, Problem, bare_symbol_side, build_problem,
                                          has_branch_cut)
from formulaci.verify.sampler import (BASE_REGIMES, INTEGER_RESAMPLE_REGIMES, REGIMES, in_domain,
                                      sample_value, seed_for)

POINTS_PER_REGIME = 12
CONSTANT_LIKE = {"e", "i", "j", "pi", "π"}  # usually Euler's number / the imaginary unit / pi
POINTS_PER_REGIME_SLOW = 6  # integrals and infinite series cost ~0.1-0.5 s per point
MAX_ATTEMPTS = 40


def _problem(payload: dict) -> Problem:
    p = build_problem(Parsed.model_validate(payload["parsed"]),
                      Semantics.model_validate(payload["semantics"]))
    return _indefinite_to_derivative(p)


def _indefinite_to_derivative(p: Problem) -> Problem:
    """An identity between antiderivatives holds up to a constant: compare derivatives instead."""
    indef = [i for side in (p.lhs, p.rhs) for i in side.atoms(sp.Integral)
             if any(len(lim) == 1 for lim in i.limits)]
    if not indef:
        return p
    var = next(lim[0] for lim in indef[0].limits if len(lim) == 1)
    syms = {s.name: s.symbol for s in p.syms}
    x = syms.get(var.name, var)
    if x not in (p.lhs.free_symbols | p.rhs.free_symbols):
        raise NotCheckable("indefinite integral in a variable that is not free")
    if p.relation != "=":
        raise NotCheckable("indefinite integral inside an inequality")
    p.lhs, p.rhs = sp.diff(p.lhs, x), sp.diff(p.rhs, x)
    p.notes.append(f"indefinite integral: compared d/d{x.name} of both sides (constant of integration ignored)")
    return p


def task_prepare(payload: dict) -> dict:
    notes = payload["parsed"].get("notes")
    try:
        p = _problem(payload)
    except NotCheckable as e:
        return {"skip": str(e)}
    return {
        "relation": p.relation,
        "branch": has_branch_cut(p.lhs) or has_branch_cut(p.rhs),
        "slow": num.is_slow(p),
        "bare_symbol": bare_symbol_side(p),
        # guards against statements mistaken for identities (see policy.decide)
        "zero_side": bool(p.syms) and p.relation == "=" and (p.lhs == 0 or p.rhs == 0),
        "unmapped_constants": sorted(s.name for s in p.syms if s.name in CONSTANT_LIKE
                                     and s.name not in payload["semantics"].get("domains", {})),
        "decimal_sides": guards.decimal_sides(p, notes),
        "rational_approx": guards.rational_approximation(p),
        "label": guards.label_superscript(p, notes),
        "tol": guards.tolerance_hints(payload["semantics"].get("assumptions_source", [])),
        "symbols": {s.name: s.type for s in p.syms},
        "notes": p.notes,
        "constraint_errors": p.constraint_errors,
        "lhs": sp.sstr(p.lhs)[:300],
        "rhs": sp.sstr(p.rhs)[:300],
    }


def task_symbolic(payload: dict) -> dict:
    from formulaci.verify.symbolic import symbolic_check

    p = _problem(payload)
    result, trace = symbolic_check(p)
    out = {"symbolic": result, "trace": trace}
    if not p.syms and result == "not_equal":
        out["closed"] = _closed_form_values(p)
    return out


def _closed_form_values(p) -> dict | None:
    """For a constant identity: SymPy's closed forms of both sides and their values at two precisions.
    Used only when numeric quadrature/summation fails to converge (oscillatory integrals)."""
    import sympy as sp
    try:
        sides = [e.doit() for e in (p.lhs, p.rhs)]
        if any(e.has(sp.Integral, sp.Sum, sp.Product, sp.Limit) or e.free_symbols or not e.is_number for e in sides):
            return None
        vals = [[sp.N(e, d) for e in sides] for d in (50, 100)]
        if any(not v.is_number or v.has(sp.nan, sp.zoo, sp.oo) for row in vals for v in row):
            return None
        for v50, v100 in zip(*vals):
            if abs(v50 - v100) > sp.Float(10) ** -40 * max(1, abs(v100)):
                return None
        l, r = vals[1]
        diff = abs(l - r)
        rel = diff / max(abs(l), abs(r), sp.Integer(1))
        if rel < sp.Float(10) ** -8:
            return None
        return {"lhs": sp.sstr(sides[0]), "rhs": sp.sstr(sides[1]), "lhs_val": sp.sstr(sp.N(l, 50)),
                "rhs_val": sp.sstr(sp.N(r, 50)), "abs_diff": sp.sstr(sp.N(diff, 20)), "rel_diff": sp.sstr(sp.N(rel, 20))}
    except Exception:  # noqa: BLE001
        return None


def _point_dict(r: num.PointResult) -> dict:
    return {
        "point": r.point, "status": r.status, "error": r.error,
        "lhs": num.fmt_num(r.lhs), "rhs": num.fmt_num(r.rhs),
        "abs_diff": num.fmt_num(r.abs_diff), "rel_diff": num.fmt_num(r.rel_diff),
        "rel": float(r.rel_diff) if r.rel_diff is not None else None,
    }


def _regime_points(ev: num.Evaluator, p: Problem, formula_id: str, name: str):
    """Generator: evaluate up to POINTS_PER_REGIME evaluable points, yielding after each attempt."""
    regime = REGIMES[name]
    rng = random.Random(seed_for(formula_id, name))
    seen, n_eval = set(), 0
    target = POINTS_PER_REGIME_SLOW if ev.slow else POINTS_PER_REGIME
    for _ in range(MAX_ATTEMPTS):
        if n_eval >= target:
            return
        point = {s.name: sample_value(s, regime, rng) for s in p.syms}
        key = tuple(sorted(point.items()))
        if key in seen:
            continue
        seen.add(key)
        if not all(in_domain(s, point[s.name]) for s in p.syms) or not ev.satisfies(point):
            continue
        r = ev.evaluate(point, name == "complex")
        n_eval += r.status != "error"
        yield _point_dict(r)


def _run_regimes(ev: num.Evaluator, p: Problem, formula_id: str, names: list[str], deadline: float) -> list[dict]:
    """Round-robin over regimes so that a deadline leaves every regime with a similar sample."""
    gens = {n: _regime_points(ev, p, formula_id, n) for n in names}
    points: dict[str, list] = {n: [] for n in names}
    while gens and time.monotonic() < deadline:
        for n in list(gens):
            try:
                points[n].append(next(gens[n]))
            except StopIteration:
                del gens[n]
            if time.monotonic() >= deadline:
                break
    return [{"name": n, "n_points": len(pts), "n_fail": sum(pt["status"] == "fail" for pt in pts),
             "n_error": sum(pt["status"] == "error" for pt in pts), "points": pts}
            for n, pts in points.items()]


def task_numeric(payload: dict) -> dict:
    budget = float(payload.get("budget", 10.0))
    start = time.monotonic()
    p = _problem(payload)
    fid = payload["parsed"]["formula_id"] + f"#{payload['parsed'].get('index_in_chain') or 0}"
    ev = num.Evaluator.build(p)
    tol = guards.tolerance_hints(payload["semantics"].get("assumptions_source", []))
    if tol.get("rel"):
        ev.rel_tol = max(ev.rel_tol, mp.mpf(tol["rel"]))
    if tol.get("abs"):
        ev.abs_tol = mp.mpf(tol["abs"])
    # the supervisor kills us at `budget`; finish (and reply) comfortably before that
    ev.hard_deadline = start + max(budget - 0.7, 0.3)
    deadline = ev.hard_deadline - 0.1
    out = {"regimes": [], "constant": not p.syms, "integer_resampled": False,
           "eval_error": ev.error, "timed_out": False}
    if ev.error:
        return out
    if not p.syms:
        r = ev.evaluate({}, complex_regime=True)
        pts = [_point_dict(r)]
        out["regimes"].append({"name": "constant", "n_points": 1, "n_fail": int(r.status == "fail"),
                               "n_error": int(r.status == "error"), "points": pts})
        return out
    names = list(BASE_REGIMES)
    if p.relation == "=" and any(s.is_complex for s in p.syms):
        names.insert(4, "complex")
    out["regimes"] = _run_regimes(ev, p, fid, names, deadline)
    regs = {r["name"]: r for r in out["regimes"]}
    ints = regs["integers_small"]
    # failures at non-integer positive points (not just off-branch ones) suggest an integer-only identity
    others_fail = any(r["n_fail"] for r in out["regimes"]
                      if r["name"] in ("small_positive", "unit_interval", "large"))
    # ... unless the prose stated a real (non-integer) domain: then failing at non-integers is a FAIL
    stated = guards.stated_type_symbols(payload["semantics"].get("assumptions_source", []))
    stated_real = any(s.name in stated and not s.is_integer for s in p.syms)
    # "holds at the integers" means nothing when a bound such as |x| < 1 leaves a single admissible
    # integer (x = 0): every non-integer symbol must take at least 3 distinct values at evaluable points
    seen: dict[str, set] = {}
    for pt in ints["points"]:
        if pt["status"] != "error":
            for name_, val in pt["point"].items():
                seen.setdefault(name_, set()).add(str(val))
    diverse = all(len(seen.get(s.name, ())) >= 3 for s in p.syms if not s.is_integer)
    if ints["n_points"] - ints["n_error"] >= 5 and ints["n_fail"] == 0 and others_fail \
            and not all(s.is_integer for s in p.syms) and not stated_real and diverse:
        out["integer_resampled"] = True
        out["regimes"] += _run_regimes(ev, p, fid, INTEGER_RESAMPLE_REGIMES, deadline)
    out["timed_out"] = time.monotonic() > deadline
    return out


def task_sleep(payload: dict) -> dict:
    """Diagnostic: simulate a computation that never returns (used by the pool tests)."""
    time.sleep(float(payload["seconds"]))
    return {"slept": payload["seconds"]}


TASKS = {"prepare": task_prepare, "symbolic": task_symbolic, "numeric": task_numeric, "sleep": task_sleep}


def worker_main(conn) -> None:
    """Loop: receive (task, payload), reply ("ok", result) or ("err", message)."""
    import traceback

    import mpmath as mp

    mp.mp.dps = num.DPS
    while True:
        try:
            msg = conn.recv()
        except EOFError:
            return
        if msg is None:
            return
        task, payload = msg
        try:
            conn.send(("ok", TASKS[task](payload)))
        except Exception as e:  # noqa: BLE001
            conn.send(("err", f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}"))
