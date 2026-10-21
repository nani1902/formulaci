"""Stage driver: join formulas with parsed records, run the rules, write semantics.jsonl."""
from __future__ import annotations

import json
import signal
import threading
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path

from formulaci.schemas import Formula, Parsed, Semantics, append_jsonl, existing_ids, read_jsonl
from formulaci.semantics.rules import infer

DEFAULT_FORMULAS = "data/raw/formulas.jsonl"
DEFAULT_PARSED = "data/parsed/parsed.jsonl"
DEFAULT_OUT = "data/semantics/semantics.jsonl"


class _Timeout(BaseException):  # not Exception: rule code has broad excepts
    pass


@contextmanager
def _time_limit(seconds: float | None):
    """SIGALRM-based limit (main thread, Unix); a no-op elsewhere."""
    if not seconds or not hasattr(signal, "setitimer") or threading.current_thread() is not threading.main_thread():
        yield
        return

    def _raise(signum, frame):
        raise _Timeout()

    old = signal.signal(signal.SIGALRM, _raise)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def group_parsed(path) -> "OrderedDict[str, list[Parsed]]":
    """Parsed records grouped by formula_id (chains contribute several pieces)."""
    groups: OrderedDict[str, list[Parsed]] = OrderedDict()
    for p in read_jsonl(path, Parsed):
        groups.setdefault(p.formula_id, []).append(p)
    for pieces in groups.values():
        pieces.sort(key=lambda p: (p.index_in_chain is None, p.index_in_chain or 0))
    return groups


def load_formulas(path, wanted: set[str] | None = None) -> dict[str, Formula]:
    out = {}
    for f in read_jsonl(path, Formula):
        if wanted is None or f.formula_id in wanted:
            out[f.formula_id] = f
    return out


def run(in_path: str = DEFAULT_PARSED, out_path: str = DEFAULT_OUT, formulas_path: str = DEFAULT_FORMULAS,
        limit: int | None = None, force: bool = False, batch: int = 200, timeout: float | None = 10.0) -> dict:
    """Infer semantics for every parsed formula. Resumable: ids already in `out_path` are skipped."""
    out = Path(out_path)
    if force and out.exists():
        out.unlink()
    done = existing_ids(out, Semantics) if out.exists() else set()
    groups = group_parsed(in_path)
    todo = [fid for fid in groups if fid not in done]
    if limit is not None:
        todo = todo[:limit]
    formulas = load_formulas(formulas_path, set(todo)) if Path(formulas_path).exists() else {}
    stats = {"seen": len(groups), "skipped_existing": len(groups) - len([f for f in groups if f not in done]),
             "written": 0, "checkable": 0, "missing_formula": 0, "skip_reasons": {}}
    buf = []
    for fid in todo:
        f = formulas.get(fid)
        if f is None:
            stats["missing_formula"] += 1
        try:
            with _time_limit(timeout):
                sem, _ = infer(f, groups[fid])
        except _Timeout:
            sem = Semantics(formula_id=fid, checkable=False, skip_reason="semantics_timeout",
                            assumptions_source=["K.internal_timeout"])
            stats["timeouts"] = stats.get("timeouts", 0) + 1
        except Exception as e:  # one malformed record must not stop the stage
            sem = Semantics(formula_id=fid, checkable=False, skip_reason="semantics_error",
                            assumptions_source=[f"K.internal_error:{type(e).__name__}"])
            stats["errors"] = stats.get("errors", 0) + 1
        buf.append(sem)
        stats["written"] += 1
        stats["checkable"] += int(sem.checkable)
        if not sem.checkable:
            stats["skip_reasons"][sem.skip_reason] = stats["skip_reasons"].get(sem.skip_reason, 0) + 1
        if len(buf) >= batch:
            append_jsonl(out, buf)
            buf = []
    if buf:
        append_jsonl(out, buf)
    return stats


def explain(formula_id: str, formulas_path: str = DEFAULT_FORMULAS, parsed_path: str = DEFAULT_PARSED,
            formula: Formula | None = None, pieces: list[Parsed] | None = None) -> str:
    """Human-readable account of which rules fired for one formula, and why."""
    if pieces is None:
        pieces = group_parsed(parsed_path).get(formula_id)
        if not pieces:
            raise KeyError(f"{formula_id} not found in {parsed_path}")
    if formula is None and Path(formulas_path).exists():
        formula = load_formulas(formulas_path, {formula_id}).get(formula_id)
    sem, tr = infer(formula, pieces)
    lines = [f"formula_id: {formula_id}"]
    if formula is not None:
        lines.append(f"page: {formula.page_title} / {formula.section}")
        lines.append(f"latex: {formula.latex}")
    else:
        lines.append("latex: (formula record not found; no context available)")
    for p in pieces:
        lines.append(f"piece {p.index_in_chain if p.index_in_chain is not None else 0}: [{p.status}/{p.kind}] lhs={p.lhs} rhs={p.rhs}"
                     + (f" relation={p.relation}" if p.relation else ""))
    lines.append("")
    lines.append("rules fired:")
    for rule, why in tr.entries:
        lines.append(f"  {rule:28s} {why}")
    lines.append("")
    lines.append("result: " + json.dumps(sem.model_dump(exclude={"formula_id", "assumptions_source"}), ensure_ascii=False))
    return "\n".join(lines)
