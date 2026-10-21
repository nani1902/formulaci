"""Batch driver: join Parsed + Semantics, verify each formula under a wall-clock cap, write Verdicts."""
from __future__ import annotations

import json
import os
import queue
import threading
import time
from collections import OrderedDict
from pathlib import Path

from formulaci.schemas import Parsed, Semantics, Tolerance, Verdict, append_jsonl, read_jsonl
from formulaci.verify import policy
from formulaci.verify.pool import TaskFailed, TaskTimeout, Worker

CAP_SECONDS = 20.0
PREPARE_TIMEOUT = 4.0
SYMBOLIC_TIMEOUT = 6.0
SYMBOLIC_TIMEOUT_SLOW = 3.0  # integrals / infinite series: leave the time to the numeric phase
# abs=0: near-zero values are judged by the precision ladder (noise shrinks with dps), not a fixed floor
TOLERANCE = Tolerance(abs=0.0, rel=1e-8, dps=50)


def _skip(fid: str, reason: str) -> Verdict:
    return Verdict(formula_id=fid, verdict="SKIP", reason=reason, tolerance=TOLERANCE)


def verify_link(worker: Worker, parsed: Parsed, sem: Semantics, deadline: float) -> dict:
    """Run prepare/symbolic/numeric for one link. Returns a dict with verdict pieces and raw data."""
    payload = {"parsed": parsed.model_dump(), "semantics": sem.model_dump()}
    out = {"index": parsed.index_in_chain or 0, "meta": None, "symbolic": "unknown", "trace": [],
           "numeric": None, "notes": []}

    def left():
        return deadline - time.monotonic()

    try:
        meta = worker.call("prepare", payload, min(PREPARE_TIMEOUT, max(left(), 0.1)))
    except (TaskTimeout, TaskFailed) as e:
        return {**out, "verdict": "INCONCLUSIVE", "reason": f"Could not rebuild the expression ({str(e).splitlines()[0]})."}
    if "skip" in meta:
        return {**out, "verdict": "SKIP", "reason": f"Not checkable: {meta['skip']}."}
    out["meta"] = meta
    if meta["bare_symbol"]:
        return {**out, "verdict": "INCONCLUSIVE",
                "reason": f"The equation solves for (or defines) the symbol {meta['bare_symbol']}; it is not an identity to check."}

    try:
        cap_sym = SYMBOLIC_TIMEOUT_SLOW if meta.get("slow") else SYMBOLIC_TIMEOUT
        sym = worker.call("symbolic", payload, min(cap_sym, max(left() * 0.4, 0.5)))
        out["symbolic"], out["trace"] = sym["symbolic"], sym["trace"]
    except TaskTimeout:
        out["notes"].append("symbolic check timed out")
    except TaskFailed as e:
        out["notes"].append(f"symbolic check failed: {str(e).splitlines()[0]}")

    budget = left()
    if budget < 1.0:
        out["notes"].append("no time left for the numeric phase")
    else:
        try:
            out["numeric"] = worker.call("numeric", {**payload, "budget": budget - 0.5}, budget)
        except TaskTimeout:
            out["notes"].append(f"numeric phase exceeded the {CAP_SECONDS:.0f}s cap")
            out["numeric"] = {"eval_error": "numeric phase timed out", "regimes": []}
        except TaskFailed as e:
            out["numeric"] = {"eval_error": f"numeric phase crashed: {str(e).splitlines()[0]}", "regimes": []}
    verdict, reason, ce = policy.decide(meta, out["symbolic"], out["numeric"])
    if verdict == "FAIL" and out["notes"]:
        reason = reason.rstrip(".") + f" [{'; '.join(out['notes'])}]."
    out.update(verdict=verdict, reason=reason, counterexample=ce)
    return out


def verify_formula(worker: Worker, links: list[Parsed], sem: Semantics | None,
                   cap: float = CAP_SECONDS) -> tuple[Verdict, list[dict]]:
    fid = links[0].formula_id
    if sem is None:
        return _skip(fid, "No semantics record for this formula; domains and constants unknown."), []
    if not sem.checkable:
        return _skip(fid, f"Semantics marked it not checkable ({sem.skip_reason or 'no reason given'})."), []
    deadline = time.monotonic() + cap
    details = []
    for link in sorted(links, key=lambda p: p.index_in_chain or 0):
        if time.monotonic() > deadline - 0.5:
            details.append({"index": link.index_in_chain or 0, "verdict": "INCONCLUSIVE",
                            "reason": f"The {cap:.0f}s per-formula cap was used up by earlier chain links.",
                            "numeric": None})
            continue
        details.append(verify_link(worker, link, sem, deadline))
    combined = policy.combine_chain([
        (d["index"], d["verdict"], d["reason"], d.get("counterexample"),
         policy.regime_results(d["numeric"]) if d.get("numeric") else [])
        for d in details])
    verdict, reason, ce, regimes = combined
    sym = next((d["symbolic"] for d in details if d.get("verdict") == verdict and "symbolic" in d), "unknown")
    return Verdict(formula_id=fid, verdict=verdict, symbolic=sym, regimes=regimes, counterexample=ce,
                   tolerance=TOLERANCE, reason=reason), details


def load_inputs(parsed_path, semantics_path):
    groups: OrderedDict[str, list[Parsed]] = OrderedDict()
    for p in read_jsonl(parsed_path, Parsed):
        groups.setdefault(p.formula_id, []).append(p)
    sems = {s.formula_id: s for s in read_jsonl(semantics_path, Semantics)}
    return groups, sems


def run(in_path: str = "data/parsed/parsed.jsonl", out_path: str = "data/verdicts/verdicts.jsonl",
        semantics_path: str = "data/semantics/semantics.jsonl", limit: int | None = None,
        force: bool = False, workers: int | None = None, cap: float = CAP_SECONDS,
        progress: bool = True, only: set[str] | None = None) -> dict:
    """Verify every formula in `in_path` (joined with `semantics_path`); append Verdicts to `out_path`.

    Resumable: ids already in `out_path` are skipped unless `force`. Deterministic: sampling is
    seeded by formula id. On completion the output is rewritten in input order.
    """
    groups, sems = load_inputs(in_path, semantics_path)
    out = Path(out_path)
    if force and out.exists():
        out.unlink()
    done = {v.formula_id for v in read_jsonl(out, Verdict)}
    todo = [fid for fid in groups if fid not in done and (only is None or fid in only)]
    if limit is not None:
        todo = todo[:limit]
    workers = max(1, workers or min(4, os.cpu_count() or 1))

    jobs: queue.Queue = queue.Queue()
    for fid in todo:
        jobs.put(fid)
    results: queue.Queue = queue.Queue()

    def drive():
        w = Worker()
        try:
            w.warm()
            while True:
                try:
                    fid = jobs.get_nowait()
                except queue.Empty:
                    return
                t0 = time.monotonic()
                try:
                    v, _ = verify_formula(w, groups[fid], sems.get(fid), cap)
                except Exception as e:  # noqa: BLE001 - never let one formula stop the batch
                    v = Verdict(formula_id=fid, verdict="INCONCLUSIVE", tolerance=TOLERANCE,
                                reason=f"Internal error in the verify stage: {type(e).__name__}: {e}")
                results.put((v, time.monotonic() - t0))
        finally:
            w.close()

    threads = [threading.Thread(target=drive, daemon=True) for _ in range(min(workers, len(todo)) or 0)]
    for t in threads:
        t.start()
    counts: dict[str, int] = {}
    bar = _Progress(len(todo), progress)
    for _ in range(len(todo)):
        v, _dt = results.get()
        append_jsonl(out, [v])
        counts[v.verdict] = counts.get(v.verdict, 0) + 1
        bar.advance(counts)
    for t in threads:
        t.join()
    bar.close()
    if out.exists():
        _rewrite_in_order(out, list(groups))
    return {"processed": len(todo), "skipped_existing": len(done), **counts}


def _rewrite_in_order(out: Path, order: list[str]) -> None:
    rank = {fid: i for i, fid in enumerate(order)}
    lines = {}
    for v in read_jsonl(out, Verdict):
        lines[v.formula_id] = v.model_dump_json()
    tmp = out.with_suffix(".tmp")
    with tmp.open("w") as f:
        for fid in sorted(lines, key=lambda k: (rank.get(k, len(rank)), k)):
            f.write(lines[fid] + "\n")
    os.replace(tmp, out)


class _Progress:
    def __init__(self, total: int, enabled: bool):
        self._p = None
        if enabled and total:
            from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn

            self._p = Progress(TextColumn("verify"), BarColumn(), MofNCompleteColumn(),
                               TimeElapsedColumn(), TextColumn("{task.description}"))
            self._p.start()
            self._t = self._p.add_task("", total=total)

    def advance(self, counts):
        if self._p:
            self._p.update(self._t, advance=1, description=json.dumps(counts))

    def close(self):
        if self._p:
            self._p.stop()
