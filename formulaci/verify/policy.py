"""The verdict policy (SPEC.md, Verdict / FAIL policy). Pure Python over the worker's dicts.

FAIL requires all of:
  (a) symbolic result is not "equal";
  (b) in every regime with >= MIN_EVAL evaluable points, at least MAJORITY of them fail with
      relative error > 1e-8 at 50 dps (each failure confirmed stable under input perturbation,
      climbing to 800 dps when cancellation makes 50 digits untrustworthy), and there are at
      least MIN_REGIMES such regimes (3 if the numeric phase hit its deadline);
  (c) no special-case rule applies (definition of a bare symbol, branch cuts, integer-only
      identities, failures confined to a measure-zero set).
Constant identities (no free symbols) are the one extension: one point, confirmed at two precisions.
Two guards (see `decide`) block FAIL for formulas that are probably statements, not identities.
"""
from __future__ import annotations

from formulaci.schemas import Counterexample, RegimeResult
from formulaci.verify.sampler import fmt_value, magnitude

MIN_EVAL = 5
MAJORITY = 0.7
MIN_REGIMES = 2
POSITIVE_REGIMES = {"small_positive", "unit_interval", "integers_small", "large"}
OFF_BRANCH_REGIMES = {"mixed_sign", "complex"}
INTEGER_REGIMES = {"integers_small", "integers_large", "integers_mixed_sign"}


def n_eval(r: dict) -> int:
    return r["n_points"] - r["n_error"]


def regime_results(numeric: dict) -> list[RegimeResult]:
    return [RegimeResult(name=r["name"], n_points=r["n_points"], n_fail=r["n_fail"],
                         n_error=r["n_error"]) for r in numeric.get("regimes", [])]


def counterexample(regimes: list[dict]) -> Counterexample | None:
    fails = [pt for r in regimes for pt in r["points"] if pt["status"] == "fail"]
    if not fails:
        return None
    best = min(fails, key=lambda pt: (magnitude(pt["point"]), -(pt["rel"] or 0)))
    return Counterexample(assignments={k: fmt_value(v) for k, v in sorted(best["point"].items())},
                          lhs=best["lhs"], rhs=best["rhs"], abs_diff=best["abs_diff"],
                          rel_diff=best["rel_diff"])


def _first_error(numeric: dict) -> str:
    for r in numeric.get("regimes", []):
        for pt in r["points"]:
            if pt["status"] == "error" and pt["error"]:
                return pt["error"]
    return numeric.get("eval_error") or "no point could be evaluated"


def _fmt_ce(ce: Counterexample | None) -> str:
    if ce is None:
        return ""
    a = ", ".join(f"{k}={v}" for k, v in ce.assignments.items())
    return f" (e.g. at {a}: lhs={ce.lhs[:14]}, rhs={ce.rhs[:14]})" if a else \
        f" (lhs={ce.lhs[:18]}, rhs={ce.rhs[:18]})"


def decide(meta: dict, symbolic: str, numeric: dict | None) -> tuple[str, str, Counterexample | None]:
    """Return (verdict, reason, counterexample).

    Two guards turn a FAIL into INCONCLUSIVE because on real Wikipedia data the formula is far more
    likely a statement than a wrong identity: a symbol named like a constant (e, i, pi) that
    Semantics neither mapped nor typed, and an equation with a literal 0 side and free variables
    (an equation to solve, e.g. ax^2+bx+c=0).
    """
    verdict, reason, ce = _decide(meta, symbolic, numeric)
    if verdict != "FAIL":
        return verdict, reason, ce
    if meta.get("unmapped_constants"):
        names = ", ".join(meta["unmapped_constants"])
        return "INCONCLUSIVE", (f"Would fail with {names} as plain variable(s), but {names} is probably a "
                                f"constant (Euler's number / imaginary unit / pi) that semantics did not map"
                                f"{_fmt_ce(ce)}."), ce
    if meta.get("zero_side"):
        return "INCONCLUSIVE", (f"Not zero at sample points, but an expression set equal to 0 usually states an "
                                f"equation to solve rather than an identity{_fmt_ce(ce)}."), ce
    return verdict, reason, ce


def _decide(meta: dict, symbolic: str, numeric: dict | None) -> tuple[str, str, Counterexample | None]:
    rel = meta.get("relation", "=")
    what = "inequality" if rel != "=" else "identity"
    sym_note = {"equal": "proved symbolically" if rel == "=" else "ordering proved symbolically",
                "not_equal": "symbolic difference is nonzero", "unknown": "symbolic check inconclusive"}[symbolic]

    if numeric is None or numeric.get("eval_error") or not numeric.get("regimes"):
        err = (numeric or {}).get("eval_error") or "numeric phase did not run"
        if symbolic == "equal":
            return "PASS", f"The {what} was {sym_note}; numeric evaluation unavailable ({err}).", None
        return "INCONCLUSIVE", f"Could not evaluate numerically ({err}); {sym_note}.", None

    regs = numeric["regimes"]
    total_eval = sum(n_eval(r) for r in regs)
    total_fail = sum(r["n_fail"] for r in regs)
    ce = counterexample(regs)

    if symbolic == "equal":
        if total_fail == 0:
            return "PASS", f"The {what} was {sym_note} and holds at all {total_eval} evaluable sample points.", None
        return "INCONCLUSIVE", (f"Symbolic simplification says the {what} holds but it fails at {total_fail} of "
                                f"{total_eval} sample points{_fmt_ce(ce)}; check the domain assumptions."), ce

    if numeric.get("constant"):
        r = regs[0]
        if n_eval(r) == 0:
            return "INCONCLUSIVE", f"The constant {what} could not be evaluated ({_first_error(numeric)}).", None
        if r["n_fail"]:
            return "FAIL", (f"The constant {what} does not hold: both sides differ beyond 1e-8 relative error, "
                            f"stably at two working precisions{_fmt_ce(ce)}."), ce
        return "PASS", f"The constant {what} holds to 50 significant digits ({sym_note}).", None

    qualified = [r for r in regs if n_eval(r) >= MIN_EVAL]
    if not qualified:
        return "INCONCLUSIVE", (f"Too few evaluable points ({total_eval}) to judge; "
                                f"typical error: {_first_error(numeric)}."), ce

    if numeric.get("integer_resampled"):
        int_q = [r for r in qualified if r["name"] in INTEGER_REGIMES]
        if len(int_q) >= 2 and all(r["n_fail"] == 0 for r in int_q):
            n = sum(n_eval(r) for r in int_q)
            return "PASS", (f"Holds at all {n} integer sample points but not at non-integers, so it is an "
                            f"integer-only {what} whose integer domain was not stated."), None
        return "INCONCLUSIVE", (f"Holds at small integers but fails elsewhere, including some integer "
                                f"resamples{_fmt_ce(ce)}; not flagged."), ce

    if total_fail == 0:
        if symbolic == "not_equal":
            return "INCONCLUSIVE", (f"Holds at all {total_eval} sample points but symbolic simplification found "
                                    f"a nonzero difference; possibly a branch or assumption issue."), None
        if total_eval >= 10:
            return "PASS", (f"The {what} holds at all {total_eval} evaluable points across {len(qualified)} "
                            f"regimes ({sym_note})."), None
        return "INCONCLUSIVE", f"Holds at the {total_eval} evaluable points, too few to call it a PASS.", None

    majority = [r for r in qualified if r["n_fail"] / n_eval(r) >= MAJORITY]
    need = 3 if numeric.get("timed_out") else MIN_REGIMES
    if len(majority) == len(qualified) and len(qualified) >= need:
        names = ", ".join(r["name"] for r in qualified)
        return "FAIL", (f"The {what} fails at {total_fail} of {total_eval} evaluable points, a clear majority "
                        f"in every regime ({names}){_fmt_ce(ce)}."), ce
    if len(majority) == len(qualified):
        return "INCONCLUSIVE", (f"Fails in every judged regime, but only {len(qualified)} regime(s) had "
                                f"{MIN_EVAL}+ evaluable points{_fmt_ce(ce)}; not enough to flag."), ce

    failing = {r["name"] for r in regs if r["n_fail"]}
    if failing <= OFF_BRANCH_REGIMES and all(r["n_fail"] == 0 for r in regs if r["name"] in POSITIVE_REGIMES):
        if meta.get("branch"):
            return "INCONCLUSIVE", (f"Holds for positive arguments and fails only in {', '.join(sorted(failing))} "
                                    f"sampling, where sqrt/log/inverse-trig branch cuts apply{_fmt_ce(ce)}."), ce
        return "INCONCLUSIVE", (f"Holds for positive arguments but fails in {', '.join(sorted(failing))} "
                                f"sampling; an unstated domain restriction is likely{_fmt_ce(ce)}."), ce
    if failing == {"integers_small"}:
        return "INCONCLUSIVE", (f"Fails only at integer points, a measure-zero set for real variables "
                                f"(removable singularity or convention){_fmt_ce(ce)}."), ce
    return "INCONCLUSIVE", (f"Fails at {total_fail} of {total_eval} evaluable points but not at a clear "
                            f"majority in every regime (failing: {', '.join(sorted(failing))}){_fmt_ce(ce)}."), ce


def combine_chain(link_results: list[tuple[int, str, str, object, list]]) -> tuple:
    """Combine per-link (index, verdict, reason, ce, regimes) for a chain a = b = c."""
    if len(link_results) == 1:
        return link_results[0][1:]
    for verdict in ("FAIL", "INCONCLUSIVE"):
        for idx, v, reason, ce, regs in link_results:
            if v == verdict:
                return v, f"Chain link {idx}: {reason}", ce, regs
    if all(v == "SKIP" for _, v, *_ in link_results):
        return "SKIP", link_results[0][2], None, []
    passes = [lr for lr in link_results if lr[1] == "PASS"]
    if len(passes) == len(link_results):
        return "PASS", f"All {len(passes)} links of the chain hold; first: {passes[0][2]}", None, passes[0][4]
    skipped = [lr for lr in link_results if lr[1] == "SKIP"]
    return ("INCONCLUSIVE", f"{len(passes)} chain links pass, {len(skipped)} skipped "
            f"(e.g. link {skipped[0][0]}: {skipped[0][2]})", None, passes[0][4])
