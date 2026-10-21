"""Run translate -> semantics -> verify over the bench sets and measure them.

Stages are imported lazily (``formulaci.<stage>.run``); a stage that is missing or still the
skeleton stub is reported as unavailable and everything downstream of it is not measured.
Stage outputs go to ``data/bench/runs/<set>/`` so the bench never touches other stages' data.

Positive class = "formula is wrong". A prediction is positive iff the verdict is FAIL.
- precision = FAIL on mutated / (FAIL on mutated + FAIL on known-good)
- recall    = FAIL on mutated / all mutated (end to end: untranslated counts as missed)
- recall | verified = same, restricted to mutated formulas that got PASS/FAIL/INCONCLUSIVE
"""
from __future__ import annotations

import importlib
import inspect
import json
import shutil
import time
import traceback
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

from .sets import read_jsonl, write_jsonl

STAGES = ["translate", "semantics", "verify"]
SET_FILES = {"known_good": "known_good.jsonl", "mutated": "mutated.jsonl", "lacast": "lacast_benchmark.jsonl"}
VERDICTS = ["PASS", "FAIL", "INCONCLUSIVE", "SKIP", "MISSING"]


# --- stage discovery and invocation -------------------------------------------------------------

def find_stage(name: str) -> tuple[Callable | None, str]:
    """Return (run function, where) or (None, reason)."""
    candidates = [f"formulaci.{name}", f"formulaci.{name}.run", f"formulaci.{name}.stage",
                  f"formulaci.{name}.pipeline", f"formulaci.{name}.core", f"formulaci.{name}.{name}"]
    errors = []
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
        except ModuleNotFoundError as e:
            if e.name and modname.startswith(e.name):
                continue
            errors.append(f"{modname}: {e}")
            continue
        except Exception as e:  # noqa: BLE001 - a half-written stage must not break the bench
            errors.append(f"{modname}: {type(e).__name__}: {e}")
            continue
        fn = getattr(mod, "run", None)
        if inspect.ismodule(fn):
            fn = getattr(fn, "run", None)
        if callable(fn):
            return fn, f"{modname}.run"
    return None, "; ".join(errors) or f"no run() in formulaci.{name}"


def _call(fn: Callable, stage: str, paths: dict[str, Path], opts: dict) -> None:
    """Call a stage's run() mapping our paths onto its parameter names."""
    natural_in = {"translate": "formulas", "semantics": "parsed", "verify": "semantics"}[stage]
    natural_out = {"translate": "parsed", "semantics": "semantics", "verify": "verdicts"}[stage]
    sig = inspect.signature(fn)
    kwargs: dict = {}
    aliases = {
        "formulas": ("formulas", "formula", "formulas_path", "formula_path", "extract_path", "raw_path", "source_path"),
        "parsed": ("parsed", "parsed_path", "parse_path", "translate_path", "translated_path"),
        "semantics": ("semantics", "semantics_path", "sem_path", "domains_path"),
    }
    # verify.run(in_path=parsed, semantics_path=...): in_path is the parsed file when semantics has its own param
    if stage == "verify" and any(p in aliases["semantics"] for p in sig.parameters):
        natural_in = "parsed"
    positional = []
    for pname, p in sig.parameters.items():
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        value = None
        if pname in ("in_path", "input", "input_path", "inp", "src"):
            value = paths[natural_in]
        elif pname in ("out_path", "output", "output_path", "out", "dst"):
            value = paths[natural_out]
        else:
            for key, names in aliases.items():
                if pname in names:
                    value = paths[key]
            if pname == "force":
                value = True
            elif pname == "progress":
                value = False
            if pname in opts:
                value = opts[pname]
        if value is None:
            continue
        if p.kind == p.POSITIONAL_ONLY:
            positional.append(str(value) if isinstance(value, Path) else value)
        else:
            kwargs[pname] = str(value) if isinstance(value, Path) else value
    fn(*positional, **kwargs)


def run_pipeline(formulas: Path, workdir: Path, stages: list[str], opts: dict | None = None) -> dict:
    """Run the requested stages on ``formulas``; returns per-stage status and runtime."""
    workdir.mkdir(parents=True, exist_ok=True)
    paths = {"formulas": formulas, "parsed": workdir / "parsed.jsonl",
             "semantics": workdir / "semantics.jsonl", "verdicts": workdir / "verdicts.jsonl"}
    status: dict = {}
    upstream_ok = True
    for stage in STAGES:
        out = paths[{"translate": "parsed", "semantics": "semantics", "verify": "verdicts"}[stage]]
        if stage not in stages:
            status[stage] = {"status": "not_requested", "reused": out.exists()}
            continue
        if not upstream_ok:
            status[stage] = {"status": "skipped_upstream_unavailable"}
            continue
        fn, where = find_stage(stage)
        if fn is None:
            status[stage] = {"status": "unavailable", "detail": where}
            upstream_ok = False
            continue
        if out.exists():
            out.unlink()
        t0 = time.time()
        try:
            _call(fn, stage, paths, (opts or {}).get(stage, {}))
            status[stage] = {"status": "ok", "where": where, "seconds": round(time.time() - t0, 2)}
        except BaseException as e:  # noqa: BLE001 - typer.Exit/SystemExit from a stub counts as unavailable
            if isinstance(e, KeyboardInterrupt):
                raise
            status[stage] = {"status": "error", "where": where, "seconds": round(time.time() - t0, 2),
                             "detail": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-2000:]}
            upstream_ok = False
            continue
        if not out.exists() or (out.stat().st_size == 0 and formulas.stat().st_size > 0):
            status[stage] = {**status[stage], "status": "error",
                             "detail": f"{stage} wrote no records to {out.name}"}
            upstream_ok = False
    return {"paths": {k: str(v) for k, v in paths.items()}, "stages": status}


# --- joining ------------------------------------------------------------------------------------

def _base_id(fid: str, known: set[str]) -> str | None:
    if fid in known:
        return fid
    for sep in ("#", "|", "@", "~", "/"):
        if sep in fid and fid.split(sep)[0] in known:
            return fid.split(sep)[0]
    head = fid
    while ":" in head:
        head = head.rsplit(":", 1)[0]
        if head in known:
            return head
    return None


def _group(path: Path, known: set[str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in read_jsonl(path):
        base = _base_id(str(r.get("formula_id", "")), known)
        if base is not None:
            out[base].append(r)
    return out


def aggregate_verdict(rs: list[dict]) -> str:
    vs = [r.get("verdict") for r in rs]
    if not vs:
        return "MISSING"
    if "FAIL" in vs:
        return "FAIL"
    if all(v == "PASS" for v in vs):
        return "PASS"
    if "INCONCLUSIVE" in vs:
        return "INCONCLUSIVE"
    if "PASS" in vs:
        return "PASS"
    return "SKIP"


def join(records: list[dict], run: dict) -> list[dict]:
    """One row per formula with its labels and the pipeline's outcome at each stage."""
    known = {r["formula_id"] for r in records}
    p = run["paths"]
    parsed = _group(Path(p["parsed"]), known)
    sem = _group(Path(p["semantics"]), known)
    ver = _group(Path(p["verdicts"]), known)
    st = run["stages"]
    have = {s: st.get(s, {}).get("status") == "ok" or (st.get(s, {}).get("status") == "not_requested"
                                                     and st[s].get("reused")) for s in STAGES}
    rows = []
    for r in records:
        fid, b = r["formula_id"], r["bench"]
        prs = parsed.get(fid, [])
        statuses = [x.get("status") for x in prs]
        tstatus = None
        if have["translate"]:
            tstatus = "missing" if not prs else ("ok" if all(s == "ok" for s in statuses) else
                                                 ("partial" if "ok" in statuses else statuses[0]))
        checkable = None
        if have["semantics"]:
            sr = sem.get(fid, [])
            checkable = bool(sr) and any(x.get("checkable") for x in sr)
            skip_reasons = sorted({x.get("skip_reason") for x in sr if x.get("skip_reason")})
        else:
            skip_reasons = []
        vrs = ver.get(fid, [])
        verdict = aggregate_verdict(vrs) if have["verify"] else None
        cex = next((v.get("counterexample") for v in vrs if v.get("verdict") == "FAIL"), None)
        reason = "; ".join(sorted({v.get("reason", "") for v in vrs if v.get("reason")}))[:300]
        rows.append({
            "formula_id": fid, "set": b["set"], "label": b["label"], "category": b["category"],
            "mutation": b.get("mutation"), "detail": b.get("mutation_detail"), "source_id": b.get("source_id"),
            "name": b.get("name"), "latex": r["latex"], "translate": tstatus,
            "translate_errors": sorted({x.get("error") for x in prs if x.get("error")})[:3],
            "unsupported": sorted({u for x in prs for u in x.get("has_unsupported", [])}),
            "checkable": checkable, "skip_reasons": skip_reasons, "verdict": verdict,
            "reason": reason, "counterexample": cex, "lacast": b.get("lacast", {}).get("human"),
        })
    return rows


# --- metrics ------------------------------------------------------------------------------------

def _rate(n: int, d: int) -> float | None:
    return round(n / d, 4) if d else None


def _block(rows: list[dict]) -> dict:
    n = len(rows)
    out: dict = {"n": n}
    tr = [r for r in rows if r["translate"] is not None]
    if tr:
        ok = sum(r["translate"] == "ok" for r in tr)
        out["translate_ok"] = ok
        out["translate_ok_rate"] = _rate(ok, len(tr))
    sm = [r for r in rows if r["checkable"] is not None and r["translate"] == "ok"]
    if any(r["checkable"] is not None for r in rows):
        out["checkable"] = sum(r["checkable"] for r in sm)
        out["checkable_rate_given_translated"] = _rate(out["checkable"], len(sm))
        out["checkable_rate_end_to_end"] = _rate(sum(bool(r["checkable"]) for r in rows), n)
    vr = [r for r in rows if r["verdict"] is not None]
    if vr:
        c = Counter(r["verdict"] for r in vr)
        out["verdicts"] = {v: c.get(v, 0) for v in VERDICTS}
        decided = c["PASS"] + c["FAIL"] + c["INCONCLUSIVE"]
        out["fail_rate"] = _rate(c["FAIL"], n)
        out["inconclusive_rate"] = _rate(c["INCONCLUSIVE"], n)
        out["inconclusive_rate_given_verified"] = _rate(c["INCONCLUSIVE"], decided)
        out["fail_rate_given_verified"] = _rate(c["FAIL"], decided)
        out["pass_rate_given_verified"] = _rate(c["PASS"], decided)
    return out


def _pr(good: list[dict], mut: list[dict]) -> dict:
    if not good and not mut or (good and good[0]["verdict"] is None) or (mut and mut[0]["verdict"] is None):
        return {}
    tp = sum(r["verdict"] == "FAIL" for r in mut)
    fp = sum(r["verdict"] == "FAIL" for r in good)
    verified = [r for r in mut if r["verdict"] in ("PASS", "FAIL", "INCONCLUSIVE")]
    return {"tp": tp, "fp": fp, "n_mutated": len(mut), "n_known_good": len(good),
            "precision": _rate(tp, tp + fp), "recall": _rate(tp, len(mut)),
            "recall_given_verified": _rate(tp, len(verified)),
            "false_positive_rate": _rate(fp, len(good))}


def compute_metrics(rows: list[dict]) -> dict:
    good = [r for r in rows if r["set"] == "known_good"]
    mut = [r for r in rows if r["set"] == "mutated"]
    lac = [r for r in rows if r["set"] == "lacast"]
    m: dict = {"synthetic": {}, "lacast": {}}
    if good or mut:
        syn = m["synthetic"]
        syn["overall"] = {"known_good": _block(good), "mutated": _block(mut), **_pr(good, mut)}
        # paired: mutations of identities whose known-good version PASSed
        passed = {r["formula_id"] for r in good if r["verdict"] == "PASS"}
        paired = [r for r in mut if r["source_id"] in passed]
        if good and good[0]["verdict"] is not None:
            syn["overall"]["recall_on_mutations_of_passing_identities"] = _rate(
                sum(r["verdict"] == "FAIL" for r in paired), len(paired))
            syn["overall"]["n_mutations_of_passing_identities"] = len(paired)
        syn["per_category"] = {}
        for cat in sorted({r["category"] for r in good + mut}):
            g = [r for r in good if r["category"] == cat]
            mm = [r for r in mut if r["category"] == cat]
            syn["per_category"][cat] = {"known_good": _block(g), "mutated": _block(mm), **_pr(g, mm)}
        syn["per_mutation"] = {}
        for mt in sorted({r["mutation"] for r in mut}):
            mm = [r for r in mut if r["mutation"] == mt]
            blk = _block(mm)
            if mm and mm[0]["verdict"] is not None:
                tp = sum(r["verdict"] == "FAIL" for r in mm)
                ver = [r for r in mm if r["verdict"] in ("PASS", "FAIL", "INCONCLUSIVE")]
                blk.update({"recall": _rate(tp, len(mm)), "recall_given_verified": _rate(tp, len(ver)),
                            "missed_as_pass": sum(r["verdict"] == "PASS" for r in mm)})
            syn["per_mutation"][mt] = blk
        if rows and rows[0]["translate"] is not None:
            per_t: dict = {}
            for st in sorted({str(r["translate"]) for r in good + mut}):
                sub = [r for r in good + mut if str(r["translate"]) == st]
                per_t[st] = {"known_good": _block([r for r in sub if r["set"] == "known_good"]),
                             "mutated": _block([r for r in sub if r["set"] == "mutated"])}
            syn["per_translator_status"] = per_t
        syn["false_positives"] = [_brief(r) for r in good if r["verdict"] == "FAIL"]
        syn["missed_mutations"] = [_brief(r) for r in mut if r["verdict"] is not None and r["verdict"] != "FAIL"]
        syn["translate_failures_known_good"] = [_brief(r) for r in good if r["translate"] not in (None, "ok")]
    if lac:
        L = m["lacast"]
        L["overall"] = _block(lac)
        if lac[0]["translate"] is not None:
            xt: dict = defaultdict(Counter)
            for r in lac:
                xt[f"human_semantic_latex={r['lacast']['semantic_latex']}"][r["translate"]] += 1
                xt[f"human_mathematica={r['lacast']['mathematica']}"][r["translate"]] += 1
            L["translate_vs_human_labels"] = {k: dict(v) for k, v in sorted(xt.items())}
        L["fails_for_review"] = [_brief(r) for r in lac if r["verdict"] == "FAIL"]
    return m


def _brief(r: dict) -> dict:
    return {k: r[k] for k in ("formula_id", "category", "mutation", "detail", "name", "latex", "translate",
                               "checkable", "skip_reasons", "verdict", "reason", "counterexample") if k in r}


# --- driver -------------------------------------------------------------------------------------

def load_sets(bench_dir: Path, sets: list[str]) -> dict[str, list[dict]]:
    out = {}
    if "synthetic" in sets:
        out["synthetic"] = read_jsonl(bench_dir / SET_FILES["known_good"]) + read_jsonl(bench_dir / SET_FILES["mutated"])
    if "lacast" in sets:
        out["lacast"] = read_jsonl(bench_dir / SET_FILES["lacast"])
    return out


def _subsample(records: list[dict], limit: int | None) -> list[dict]:
    """Keep the first ``limit`` known-good identities and all their mutations (paired sample)."""
    if not limit:
        return records
    good = [r for r in records if r["bench"]["set"] == "known_good"][:limit]
    keep = {r["formula_id"] for r in good}
    other = [r for r in records if r["bench"]["set"] != "known_good"]
    if other and other[0]["bench"]["set"] == "lacast":
        return other[:limit]
    return good + [r for r in other if r["bench"]["source_id"] in keep]


def measure(bench_dir: str | Path = "data/bench", stages: list[str] | None = None,
            sets: list[str] | None = None, limit: int | None = None, opts: dict | None = None) -> dict:
    bench_dir = Path(bench_dir)
    stages = stages or STAGES
    sets = sets or ["synthetic", "lacast"]
    t0 = time.time()
    all_rows: list[dict] = []
    runs = {}
    for name, records in load_sets(bench_dir, sets).items():
        records = _subsample(records, limit)
        if not records:
            runs[name] = {"status": "empty set (run `formulaci bench build` first)"}
            continue
        workdir = bench_dir / "runs" / name
        formulas = workdir / "formulas.jsonl"
        workdir.mkdir(parents=True, exist_ok=True)
        write_jsonl(formulas, records)
        t1 = time.time()
        run = run_pipeline(formulas, workdir, stages, opts)
        run["n_formulas"] = len(records)
        run["seconds"] = round(time.time() - t1, 2)
        runs[name] = run
        all_rows += join(records, run)
    metrics = compute_metrics(all_rows)
    metrics["runs"] = {k: {kk: vv for kk, vv in v.items() if kk != "paths"} for k, v in runs.items()}
    metrics["stages_requested"] = stages
    metrics["limit"] = limit
    metrics["total_seconds"] = round(time.time() - t0, 2)
    metrics["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    bench_dir.mkdir(parents=True, exist_ok=True)
    (bench_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False) + "\n")
    write_jsonl(bench_dir / "rows.jsonl", all_rows)
    from .report import render

    (bench_dir / "REPORT.md").write_text(render(metrics))
    return metrics


def clean_runs(bench_dir: Path) -> None:
    shutil.rmtree(bench_dir / "runs", ignore_errors=True)
