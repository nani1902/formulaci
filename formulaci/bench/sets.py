"""Building the known-good set: catalogue -> oracle-proven `Formula` records.

Records are `Formula` JSON plus one extra key, ``bench``, holding the labels (set, category,
mutation, source id, oracle variables). `Formula.model_validate` ignores the extra key, so every
stage reads these files like extract output; the labels are also mirrored in
``page_categories`` (``bench-category:trig``, ``bench-mutation:sign_flip``) in case a stage
re-serialises records.
"""
from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from formulaci.schemas import Formula

from . import oracle
from .identities import E, PAGES

N_POINTS = 6

_TYPE_WORDS = {
    "real": "real", "pos": "positive real", "pos1": "positive real", "gt1": "real",
    "unit": "real", "sym1": "real", "gtm1": "real", "posint": "positive integer",
    "nonnegint": "non-negative integer", "int": "integer", "complex": "complex",
}
_GREEK_TXT = {"alpha": "α", "beta": "β", "theta": "θ", "lambda": "λ", "mu": "μ", "sigma": "σ"}


_PROPER = {"Pythagorean", "Lagrange", "Dirichlet", "Euler", "Legendre", "Pascal", "Catalan", "Nicomachus",
           "Basel", "Leibniz", "Taylor", "Gregory", "Mercator", "Wallis", "Gaussian", "Bose–Einstein",
           "Laplace", "Bernoulli", "Jordan", "Young", "Sophie", "De", "Vandermonde", "Brahmagupta–Fibonacci",
           "Cauchy–Schwarz"}


def parse_vars(spec: str) -> dict[str, str]:
    return dict(t.split(":") for t in spec.split()) if spec else {}


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def domain_phrase(vars: dict[str, str]) -> str:
    """'for all real x and y and positive integers n' etc., from the sampling types."""
    if not vars:
        return ""
    parts: list[str] = []
    by_type: dict[str, list[str]] = {}
    for v, t in vars.items():
        by_type.setdefault(t, []).append(_GREEK_TXT.get(v, v))
    for t, names in by_type.items():
        many = len(names) > 1
        if t == "unit":
            parts.append(" and ".join(f"0 < {n} < 1" for n in names))
        elif t == "sym1":
            parts.append(" and ".join(f"|{n}| < 1" for n in names))
        elif t == "gt1":
            parts.append(" and ".join(f"{n} > 1" for n in names))
        elif t == "gtm1":
            parts.append(" and ".join(f"real {n} ≥ -1" for n in names))
        elif t == "real":
            parts.append(f"all real {_join(names)}")
        else:
            word = _TYPE_WORDS[t] + ("s" if many else "")
            word = word.replace("real numbers", "reals")
            parts.append(f"{word} {_join(names)}" if t != "complex" else f"complex {_join(names)}")
    return "for " + "; ".join(parts)


def _context(name: str, vars: dict[str, str], ctx: str | None) -> str:
    phrase = ctx if ctx is not None else domain_phrase(vars)
    first = name.split()[0]
    proper = first[0].isupper() and (first.rstrip("'s") in _PROPER or "'" in first or "–" in first)
    lead = f"The {name if proper else name[0].lower() + name[1:]} states that"
    return f"{lead}, {phrase}," if phrase else f"{lead}"


def _check_one(args):
    i, (cat, name, latex, vars_s, cond, ctx) = args
    vars = parse_vars(vars_s)
    try:
        p = oracle.parse(latex, vars)
        r = oracle.check(p, vars, cond, n=N_POINTS, seed=i)
        return i, r.holds and r.n_eval >= min(3, r.n_points), {"n_eval": r.n_eval, "n_fail": r.n_fail,
                                                                "errors": r.errors[:3]}
    except Exception as e:  # noqa: BLE001
        return i, False, {"error": f"{type(e).__name__}: {e}"}


def known_good_records(jobs: int | None = None, verify: bool = True) -> tuple[list[dict], list[dict]]:
    """Return (records, rejected). Every record has been proven by the oracle when verify=True."""
    items = list(enumerate(E, start=1))
    if verify:
        with ProcessPoolExecutor(max_workers=jobs or os.cpu_count()) as ex:
            results = {i: (ok, info) for i, ok, info in ex.map(_check_one, items)}
    else:
        results = {i: (True, {}) for i, _ in items}
    records, rejected = [], []
    for i, (cat, name, latex, vars_s, cond, ctx) in items:
        ok, info = results[i]
        vars = parse_vars(vars_s)
        fid = f"bench:good:{i:04d}"
        if not ok:
            rejected.append({"formula_id": fid, "name": name, "latex": latex, **info})
            continue
        f = Formula(
            formula_id=fid, source="bench", lang="en", page_title=PAGES[cat], page_id=0, revision_id=0,
            url=f"bench://known_good/{i:04d}", section=name, index=i, latex=latex, display=True,
            context_before=_context(name, vars, ctx), context_after="",
            page_categories=["bench", f"bench-category:{cat}", "bench-label:true"],
        )
        rec = json.loads(f.model_dump_json())
        rec["bench"] = {"set": "known_good", "label": "true", "category": cat, "name": name,
                        "vars": vars, "cond": cond, "mutation": None, "source_id": fid,
                        "oracle": {k: v for k, v in info.items() if k != "errors"}}
        records.append(rec)
    return records, rejected


def write_jsonl(path: str | Path, records: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
