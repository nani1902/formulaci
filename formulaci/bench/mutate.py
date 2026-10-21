"""Mutation engine: known-good identities -> labelled wrong formulas.

For every known-good record and every mutation type, candidate edits are generated on the LaTeX
text (never touching the trailing ``\\quad`` condition, sum indices or differentials), tried in a
seeded random order, and the first candidate that (1) still parses with the oracle and (2) fails
at a strict majority of the oracle's sample points is kept. Candidates that preserve the value,
change it only at a minority of points, do not parse, or cannot be evaluated are dropped and
counted in the returned stats.
"""
from __future__ import annotations

import os
import random
import re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from . import oracle
from .sets import N_POINTS, read_jsonl, write_jsonl
from .structure import Scan, balanced, scan

MUTATION_TYPES = [
    "sign_flip", "exponent_pm1", "dropped_factor", "wrong_constant",
    "swapped_symbols", "off_by_one", "num_den_swap", "missing_term",
]
MAX_TRIES = 8
_INTLIKE = {"posint", "nonnegint", "int"}
_FUNC_SWAPS = {"\\sin": "\\cos", "\\cos": "\\sin", "\\sinh": "\\cosh", "\\cosh": "\\sinh",
               "\\tan": "\\cot", "\\cot": "\\tan", "\\arcsin": "\\arccos", "\\arccos": "\\arcsin",
               "erf": "erfc", "erfc": "erf", "sech": "csch", "csch": "sech"}


def _replace(sc: Scan, a: int, b: int, new: str) -> str:
    s, e = sc.span(a, b)
    return sc.text[:s] + new + sc.text[e:]


def _remove(sc: Scan, a: int, b: int) -> str:
    s, e = sc.span(a, b)
    return (sc.text[:s].rstrip() + " " + sc.text[e:].lstrip()).strip()


def _bound_toks(sc: Scan) -> set[int]:
    out: set[int] = set()
    for b in sc.bigops:
        for key in ("lower", "upper"):
            if key in b:
                out.update(range(*b[key]))
    return out


def _bump(src: str, delta: int) -> str:
    s = src.strip()
    if re.fullmatch(r"-?\d+", s):
        return str(int(s) + delta)
    return f"{s} {'+' if delta > 0 else '-'} 1"


# --- candidate generators: each returns [(detail, new_body)] -----------------------------------

def c_sign_flip(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    bound = _bound_toks(sc)
    out = []
    for i, t in enumerate(sc.toks):
        if t.text in ("+", "-") and i not in bound and i not in sc.protected:
            new = "-" if t.text == "+" else "+"
            out.append((f"'{t.text}'->'{new}' at {t.start}", _replace(sc, i, i + 1, new)))
    for k, (a, b) in enumerate(sc.sides):
        if b > a:
            out.append((f"negate side {k}", _replace(sc, a, b, f"-\\left({sc.src(a, b)}\\right)"), 1))
    return out


def c_exponent_pm1(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    for at in sc.atoms:
        if at.kind != "exponent" or at.a in sc.protected:
            continue
        a, b = at.extra["arg"]
        if b <= a:
            continue
        old = sc.src(a, b)
        delta = rng.choice((1, -1))
        new = _bump(old, delta)
        out.append((f"^{{{old}}}->^{{{new}}}", _replace(sc, at.a, at.b, f"^{{{new}}}")))
    return out


def c_dropped_factor(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    for g in sc.groups:
        if g.ctx == "bound":
            continue
        for prod in g.products:
            for at in prod:
                if at.kind == "deriv" or any(i in sc.protected for i in range(at.a, at.b) if at.kind != "bigop"):
                    continue
                out.append((f"drop {sc.src(at.a, at.b)!r}", _remove(sc, at.a, at.b)))
    return out


def c_wrong_constant(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    bound = _bound_toks(sc)
    pref, fallback = [], []
    toks = sc.toks
    for i, t in enumerate(toks):
        if i in bound or i in sc.protected:
            continue
        if t.kind == "num" and t.text in ("2", "3"):
            new = "3" if t.text == "2" else "2"
            pref.append((f"{t.text}->{new}", _replace(sc, i, i + 1, new)))
        elif t.kind == "num" and t.text == "1":
            pref.append(("1->e", _replace(sc, i, i + 1, "e")))
        elif t.kind == "num" and re.fullmatch(r"\d+", t.text):
            fallback.append((f"{t.text}->{int(t.text) + 1}", _replace(sc, i, i + 1, str(int(t.text) + 1))))
        elif t.text == "\\pi" and "pi" not in vars:
            if i > 0 and toks[i - 1].kind == "num" and toks[i - 1].text == "2" and i - 1 not in bound:
                pref.append(("2\\pi->\\pi", _replace(sc, i - 1, i + 1, "\\pi")))
            else:
                pref.append(("\\pi->2\\pi", _replace(sc, i, i + 1, "2\\pi")))
        elif t.text == "e" and t.kind in ("letter", "name") and "e" not in vars:
            nxt = toks[i + 1].text if i + 1 < len(toks) else ""
            if nxt != "^":
                pref.append(("e->1", _replace(sc, i, i + 1, "1")))
    return pref + [(d, b, 1) for d, b in fallback]


def c_swapped_symbols(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    names = list(vars)
    for k, (a, b) in enumerate(sc.sides):
        occ: dict[str, list[int]] = {}
        for i in range(a, b):
            t = sc.toks[i]
            nm = t.text[1:] if t.kind == "cmd" else t.text
            if nm in vars and (t.kind in ("letter", "name") or t.kind == "cmd") and i not in sc.protected:
                occ.setdefault(nm, []).append(i)
        present = [n for n in names if n in occ]
        for x in range(len(present)):
            for y in range(x + 1, len(present)):
                u, v = present[x], present[y]
                if (vars[u] in _INTLIKE) != (vars[v] in _INTLIKE):
                    continue
                pieces, last = [], 0
                for i in sorted(occ[u] + occ[v]):
                    s, e = sc.toks[i].start, sc.toks[i].end
                    t = sc.toks[i]
                    other = v if (t.text[1:] if t.kind == "cmd" else t.text) == u else u
                    rep = ("\\" + other) if len(other) > 1 else other
                    if t.kind == "name":  # \mathrm{x} style: keep a plain letter
                        rep = other
                    pieces.append(sc.text[last:s] + rep)
                    last = e
                out.append((f"swap {u}<->{v} in side {k}", "".join(pieces) + sc.text[last:]))
    for i, t in enumerate(sc.toks):
        key = t.text
        if key in _FUNC_SWAPS and i not in sc.protected:
            new = _FUNC_SWAPS[key]
            src = sc.src(i, i + 1)
            rep = src.replace(key, new) if t.kind == "name" else new
            if t.kind == "name":
                rep = src[: src.rfind("{") + 1] + new + "}"
            out.append((f"{key}->{new}", _replace(sc, i, i + 1, rep)))
    for at in sc.atoms:
        if at.kind == "binom":
            (a1, b1), (a2, b2) = at.extra["args"]
            s1, s2 = sc.src(a1, b1), sc.src(a2, b2)
            if s1 != s2:
                new = sc.text[: sc.toks[a1].start] + s2 + sc.text[sc.toks[b1 - 1].end : sc.toks[a2].start] + s1 \
                    + sc.text[sc.toks[b2 - 1].end :]
                out.append((f"binom args {s1}<->{s2}", new))
    return out


def c_off_by_one(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    for b in sc.bigops:
        for key in ("lower", "upper"):
            if key not in b:
                continue
            a0, b0 = b[key]
            if key == "lower" and "var" in b:
                a0 += 2  # skip "k ="
            if b0 <= a0:
                continue
            old = sc.src(a0, b0)
            if "\\infty" in old:
                continue
            delta = 1 if key == "lower" and old.strip() == "0" else rng.choice((1, -1))
            new = _bump(old, delta)
            braced = sc.toks[b[key][0] - 1].text == "{"
            rep = new if braced or re.fullmatch(r"\d", new) else f"{{{new}}}"
            out.append((f"{b['op']} {key} {old}->{new}", _replace(sc, a0, b0, rep)))
    return out


def c_num_den_swap(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    for at in sc.atoms:
        if at.kind != "frac":
            continue
        (na, nb), (da, db) = at.extra["num"], at.extra["den"]
        if nb <= na or db <= da:
            continue
        sn, sd = sc.src(na, nb), sc.src(da, db)
        if sn.strip() == sd.strip():
            continue
        s0, e0 = sc.toks[na].start, sc.toks[nb - 1].end
        s1, e1 = sc.toks[da].start, sc.toks[db - 1].end
        new = sc.text[:s0] + sd + sc.text[e0:s1] + sn + sc.text[e1:]
        out.append((f"\\frac{{{sn}}}{{{sd}}} swapped", new))
    return out


def c_missing_term(sc: Scan, vars, rng) -> list[tuple[str, str]]:
    out = []
    bound = _bound_toks(sc)
    for g in sc.groups:
        if len(g.terms) < 2 or g.a in bound:
            continue
        for k, (a, b, sign) in enumerate(g.terms):
            if k == 0:
                na, nb, nsign = g.terms[1]
                end = nsign + 1 if nsign is not None and sc.toks[nsign].text == "+" else na
                new = _remove(sc, a, end)
            else:
                new = _remove(sc, a, b)
            out.append((f"remove term {sc.src(a, b).strip()!r}", new))
    return out


GENERATORS = {
    "sign_flip": c_sign_flip, "exponent_pm1": c_exponent_pm1, "dropped_factor": c_dropped_factor,
    "wrong_constant": c_wrong_constant, "swapped_symbols": c_swapped_symbols, "off_by_one": c_off_by_one,
    "num_den_swap": c_num_den_swap, "missing_term": c_missing_term,
}


# --- driver ----------------------------------------------------------------------------------

def mutate_record(rec: dict, mtype: str, seed: int = 0, max_tries: int = MAX_TRIES) -> tuple[dict | None, Counter]:
    """Return (mutated record or None, Counter of dropped-candidate reasons)."""
    stats: Counter = Counter()
    b = rec["bench"]
    vars, cond = b["vars"], b.get("cond")
    latex = rec["latex"]
    body, _ = oracle.split_condition(latex)
    suffix = latex[len(body):]
    sc = scan(body)
    rng = random.Random(f"{rec['formula_id']}:{mtype}:{seed}")
    cands = GENERATORS[mtype](sc, vars, rng)
    rng.shuffle(cands)
    cands.sort(key=lambda c: c[2] if len(c) > 2 else 0)  # preferred sites first, fallbacks after
    seen = {body.strip()}
    cands = [c for c in cands if c[1].strip() not in seen and not seen.add(c[1].strip())]
    if not cands:
        stats["no_site"] += 1
        return None, stats
    num = int(rec["formula_id"].rsplit(":", 1)[1])
    for detail, new_body, *_ in cands[:max_tries]:
        new_latex = new_body + suffix
        if not balanced(new_latex):
            stats["unparseable"] += 1
            continue
        try:
            p = oracle.parse(new_latex, vars)
        except Exception:  # noqa: BLE001 - ParseError or a sympy constructor rejecting the result
            stats["unparseable"] += 1
            continue
        try:
            r = oracle.check(p, vars, cond, n=N_POINTS, seed=num, stop_after_fails=N_POINTS // 2 + 1)
        except Exception:  # noqa: BLE001
            stats["unevaluable"] += 1
            continue
        if r.n_eval == 0:
            stats["unevaluable"] += 1
            continue
        if r.n_fail == 0:
            stats["preserved"] += 1
            continue
        if not r.majority_fails:
            stats["weak"] += 1
            continue
        out = {k: v for k, v in rec.items() if k != "bench"}
        out["formula_id"] = f"bench:mut:{num:04d}:{mtype}"
        out["latex"] = new_latex
        out["url"] = f"bench://mutated/{num:04d}/{mtype}"
        out["page_categories"] = [c for c in rec["page_categories"] if not c.startswith("bench-label")] + [
            "bench-label:false", f"bench-mutation:{mtype}"]
        out["bench"] = {**b, "set": "mutated", "label": "false", "mutation": mtype, "mutation_detail": detail,
                        "source_id": rec["formula_id"], "source_latex": latex,
                        "oracle": {"n_eval": r.n_eval, "n_fail": r.n_fail, "example": r.example}}
        return out, stats
    stats["exhausted"] += 1
    return None, stats


def _work(args):
    rec, mtype, seed = args
    return mtype, *mutate_record(rec, mtype, seed)


def run(in_path: str | Path, out_path: str | Path, types: list[str] | None = None, seed: int = 0,
        jobs: int | None = None) -> dict:
    """Mutate every record of ``in_path`` with every type; write ``out_path``; return stats."""
    recs = read_jsonl(in_path)
    types = types or MUTATION_TYPES
    work = [(r, t, seed) for r in recs for t in types]
    kept: list[dict] = []
    per_type: dict[str, Counter] = {t: Counter() for t in types}
    with ProcessPoolExecutor(max_workers=jobs or os.cpu_count()) as ex:
        for mtype, rec, st in ex.map(_work, work, chunksize=4):
            per_type[mtype].update(st)
            if rec is not None:
                kept.append(rec)
                per_type[mtype]["kept"] += 1
    kept.sort(key=lambda r: r["formula_id"])
    write_jsonl(out_path, kept)
    dropped = {t: sum(v for k, v in c.items() if k in ("preserved", "weak", "unparseable", "unevaluable"))
               for t, c in per_type.items()}
    return {"n_source": len(recs), "n_kept": len(kept), "per_type": {t: dict(c) for t, c in per_type.items()},
            "dropped_candidates": dropped,
            "dropped_preserving_identity": sum(c["preserved"] for c in per_type.values())}
