"""Score the rules against hand-labeled fixtures (tests/semantics/fixtures/cases.jsonl).

Domains and constraints are compared *semantically*: both the labeled and the inferred
(domains + constraints) are evaluated on a fixed grid of sample points (integers, rationals of
both signs, complex numbers). For each checkable case:

- unsafe:            the rules admit a sample point the label forbids (risk of a false FAIL)
- over-restrictive:  the rules exclude a point the label allows (costs coverage only)
"""
from __future__ import annotations

import itertools
import json
import random
from collections import defaultdict
from pathlib import Path

import sympy
from sympy import I, Rational

from formulaci.schemas import Domain, Formula, Parsed
from formulaci.semantics.rules import infer

POOL_REAL = [Rational(v) for v in range(-3, 7)] + [Rational(-5, 2), Rational(-3, 2), Rational(-7, 10), Rational(-3, 10),
                                                    Rational(1, 5), Rational(1, 2), Rational(9, 10), Rational(3, 2),
                                                    Rational(5, 2), Rational(37, 10)]
POOL_COMPLEX = [Rational(1, 2) + I / 2, Rational(-6, 5) + 7 * I / 10, 2 - 3 * I / 2, Rational(3, 10) - 2 * I, I, -1 + I]
MAX_POINTS = 400

CONSTANT_RULES = ("C.e_", "C.i_", "C.j_", "C.gamma_", "C.phi_", "C.pi_", "C.function_alias")


def in_domain(d: Domain, v) -> bool:
    if v.is_real and float(v) in d.exclude:
        return False
    if d.type == "complex":
        return True
    if not v.is_real:
        return False
    if d.type in ("integer", "nonneg_integer", "positive_integer") and not v.is_integer:
        return False
    if d.type in ("nonneg_integer", "nonneg", "unit_interval") and v < 0:
        return False
    if d.type in ("positive_integer", "positive") and v <= 0:
        return False
    if d.type == "unit_interval" and v > 1:
        return False
    if d.lower is not None and v < d.lower:
        return False
    if d.upper is not None and v > d.upper:
        return False
    return True


_cache: dict = {}


def _parse_constraint(c: str, names):
    key = (c, tuple(sorted(names)))
    if key not in _cache:
        loc = {n: sympy.Symbol(n) for n in names}
        from formulaci.safeload import parse_constraint
        try:
            _cache[key] = parse_constraint(c, loc)
        except Exception:
            _cache[key] = None
    return _cache[key]


def holds(c: str, names, point: dict) -> bool:
    e = _parse_constraint(c, names)
    if e is None:
        return True   # unparseable constraint: cannot exclude anything
    try:
        v = e.xreplace({sympy.Symbol(k): val for k, val in point.items()})
        if isinstance(v, sympy.logic.boolalg.Boolean) and v not in (sympy.true, sympy.false):
            v = v.doit() if hasattr(v, "doit") else v
            if isinstance(v, sympy.assumptions.assume.AppliedPredicate):
                v = sympy.ask(v)
            else:
                v = sympy.simplify(v)
        return bool(v is sympy.true or v is True)
    except Exception:
        return False


def region(points, names, domains: dict[str, Domain], constraints: list[str]):
    out = set()
    for i, pt in enumerate(points):
        if all(n not in domains or in_domain(domains[n], pt[n]) for n in names) and all(holds(c, names, pt) for c in constraints):
            out.add(i)
    return out


def sample_points(names, complex_names, seed=0):
    pools = [POOL_REAL + (POOL_COMPLEX if n in complex_names else []) for n in names]
    total = 1
    for p in pools:
        total *= len(p)
    if total <= MAX_POINTS:
        return [dict(zip(names, combo)) for combo in itertools.product(*pools)]
    rng = random.Random(seed)
    return [{n: rng.choice(p) for n, p in zip(names, pools)} for _ in range(MAX_POINTS)]


def score_case(case: dict) -> dict:
    f = Formula.model_validate(case["formula"])
    pieces = [Parsed.model_validate(p) for p in case["parsed"]]
    sem, tr = infer(f, pieces)
    exp = case["expect"]
    r = {"case": case["case"], "latex": f.latex, "expected": exp, "got": sem.model_dump(), "rules": sem.assumptions_source}
    r["checkable_ok"] = sem.checkable == exp["checkable"]
    r["skip_ok"] = r["checkable_ok"] and (sem.checkable or sem.skip_reason == exp["skip_reason"])
    r["constants_ok"] = None
    r["domain_results"] = {}
    r["unsafe"] = r["over_restrictive"] = None
    r["bad_constraints"] = []
    r["missed_constraints"] = []
    if exp["checkable"] and sem.checkable:
        r["constants_ok"] = sem.constants == exp["constants"]
        got_types = {k: v.type for k, v in sem.domains.items()}
        for n, t in exp["domains"].items():
            r["domain_results"][n] = (t, got_types.get(n))
        names = sorted(set(exp["domains"]) | set(sem.domains))
        exp_domains = {n: Domain(type=t) for n, t in exp["domains"].items()}
        complex_names = {n for n in names if exp["domains"].get(n) == "complex" or got_types.get(n) == "complex"}
        pts = sample_points(names, complex_names)
        r_exp = region(pts, names, exp_domains, exp["constraints"])
        r_got = region(pts, names, sem.domains, sem.constraints)
        unsafe = r_got - r_exp
        over = r_exp - r_got
        r["unsafe"] = bool(unsafe)
        r["over_restrictive"] = bool(over)
        if unsafe:
            r["unsafe_example"] = {k: str(v) for k, v in pts[min(unsafe)].items()}
            for c in exp["constraints"]:
                if any(not holds(c, names, pts[i]) for i in unsafe):
                    r["missed_constraints"].append(c)
        if over:
            r["over_example"] = {k: str(v) for k, v in pts[min(over)].items()}
            for c in sem.constraints:
                if any(not holds(c, names, pts[i]) for i in r_exp):
                    r["bad_constraints"].append(c)
        # per-rule attribution for constraint rules
        r["constraint_rule_bad"] = sorted({rule for rule, why in tr.entries
                                           if why.startswith("[") and why[1:].split("] ")[0] in r["bad_constraints"]})
    r["fully_correct"] = bool(r["skip_ok"] and (not exp["checkable"] or (
        r["constants_ok"] and all(a == b for a, b in r["domain_results"].values()) and not r["unsafe"] and not r["over_restrictive"])))
    r["safe"] = bool(r["checkable_ok"] and (not exp["checkable"] or (r["constants_ok"] and not r["unsafe"])))
    return r


def score_file(path) -> dict:
    cases = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    results = [score_case(c) for c in cases]
    rep = {"n": len(results), "results": results}
    both_check = [r for r in results if r["expected"]["checkable"] and r["got"]["checkable"]]
    n_exp_check = sum(r["expected"]["checkable"] for r in results)
    n_exp_skip = len(results) - n_exp_check
    rep["checkability_accuracy"] = sum(r["checkable_ok"] for r in results) / len(results)
    rep["checkable_recall"] = sum(r["got"]["checkable"] for r in results if r["expected"]["checkable"]) / max(1, n_exp_check)
    got_check = [r for r in results if r["got"]["checkable"]]
    rep["checkable_precision"] = sum(r["expected"]["checkable"] for r in got_check) / max(1, len(got_check))
    skips = [r for r in results if not r["expected"]["checkable"] and not r["got"]["checkable"]]
    rep["skip_reason_accuracy"] = sum(r["skip_ok"] for r in skips) / max(1, len(skips))
    rep["n_expected_checkable"], rep["n_expected_skip"] = n_exp_check, n_exp_skip
    rep["constants_accuracy"] = sum(bool(r["constants_ok"]) for r in both_check) / max(1, len(both_check))
    doms = [v for r in both_check for v in r["domain_results"].values()]
    rep["domain_type_accuracy"] = sum(a == b for a, b in doms) / max(1, len(doms))
    rep["n_domain_symbols"] = len(doms)
    rep["unsafe_cases"] = sum(bool(r["unsafe"]) for r in both_check)
    rep["over_restrictive_cases"] = sum(bool(r["over_restrictive"]) for r in both_check)
    rep["n_both_checkable"] = len(both_check)
    rep["fully_correct"] = sum(r["fully_correct"] for r in results) / len(results)
    rep["false_checkable"] = [r["case"] for r in results if r["got"]["checkable"] and not r["expected"]["checkable"]]

    per_rule = defaultdict(lambda: [0, 0])     # rule -> [fired, correct]
    for r in results:
        exp = r["expected"]
        for tag in r["rules"]:
            rule, _, sym = tag.partition(":")
            if rule.startswith("K."):
                ok = r["skip_ok"]
            elif rule.startswith(CONSTANT_RULES):
                if not (exp["checkable"] and r["got"]["checkable"]):
                    continue
                ok = exp["constants"].get(sym) == r["got"]["constants"].get(sym)
            elif rule.startswith(("D.", "P.")) and sym:
                if not (exp["checkable"] and r["got"]["checkable"]) or sym not in exp["domains"]:
                    continue
                ok = exp["domains"][sym] == r["got"]["domains"].get(sym, {}).get("type")
            elif rule.startswith("C."):
                if not (exp["checkable"] and r["got"]["checkable"]):
                    continue
                ok = rule not in r.get("constraint_rule_bad", [])
            else:
                continue
            per_rule[rule][0] += 1
            per_rule[rule][1] += int(ok)
    rep["per_rule"] = {k: {"fired": v[0], "correct": v[1], "accuracy": v[1] / v[0]} for k, v in sorted(per_rule.items())}
    return rep


def format_report(rep: dict, verbose: bool = False) -> str:
    L = [f"cases: {rep['n']}  (expected checkable {rep['n_expected_checkable']}, expected skip {rep['n_expected_skip']})",
         f"checkability accuracy:        {rep['checkability_accuracy']:.1%}",
         f"  checkable precision:        {rep['checkable_precision']:.1%}  (of formulas we call checkable, label agrees)",
         f"  checkable recall:           {rep['checkable_recall']:.1%}",
         f"skip_reason accuracy:         {rep['skip_reason_accuracy']:.1%}  (both skipped)",
         f"constants exact match:        {rep['constants_accuracy']:.1%}  (both checkable, n={rep['n_both_checkable']})",
         f"domain type accuracy:         {rep['domain_type_accuracy']:.1%}  (n={rep['n_domain_symbols']} symbols)",
         f"unsafe cases (admit points the label forbids): {rep['unsafe_cases']}/{rep['n_both_checkable']}",
         f"over-restrictive cases (exclude allowed points): {rep['over_restrictive_cases']}/{rep['n_both_checkable']}",
         f"fully correct cases:          {rep['fully_correct']:.1%}",
         f"called checkable but label says skip: {rep['false_checkable']}",
         "", "per-rule accuracy (fired / correct):"]
    for k, v in rep["per_rule"].items():
        L.append(f"  {k:30s} {v['fired']:4d} {v['correct']:4d}  {v['accuracy']:.0%}")
    bad = [r for r in rep["results"] if not r["fully_correct"]]
    L.append("")
    L.append(f"not fully correct: {len(bad)}")
    for r in bad:
        e, g = r["expected"], r["got"]
        why = []
        if not r["checkable_ok"]:
            why.append(f"checkable got {g['checkable']} ({g['skip_reason']}) want {e['checkable']} ({e['skip_reason']})")
        elif not r["skip_ok"]:
            why.append(f"skip_reason got {g['skip_reason']} want {e['skip_reason']}")
        if r["constants_ok"] is False:
            why.append(f"constants got {g['constants']} want {e['constants']}")
        for n, (a, b) in r["domain_results"].items():
            if a != b:
                why.append(f"{n}: got {b} want {a}")
        if r["unsafe"]:
            why.append(f"UNSAFE e.g. {r.get('unsafe_example')} missed {r['missed_constraints']}")
        if r["over_restrictive"]:
            why.append(f"over-restrictive e.g. {r.get('over_example')} by {r['bad_constraints']}")
        L.append(f"  {r['case']}: " + "; ".join(why))
        if verbose:
            L.append(f"      rules: {r['rules']}")
            L.append(f"      constraints: {g['constraints']}")
    return "\n".join(L)
