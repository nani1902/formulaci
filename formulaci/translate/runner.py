"""Stage driver: formulas.jsonl -> parsed.jsonl with hard per-formula timeouts.

Each formula is translated in a worker process. Inside the worker a SIGALRM soft timeout turns
a slow translation into a clean `error`; if the worker still does not answer (a hang inside C
code, e.g. a giant integer power), the parent kills and restarts it. Either way the formula
gets an `unparsed` record with `error="timeout ..."` and the run continues.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import queue
import signal
import threading
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from formulaci.schemas import Formula, Parsed, read_jsonl

from .core import TRANSLATOR, translate
from .stats import summarize


class _SoftTimeout(Exception):
    pass


def _on_alarm(signum, frame):
    raise _SoftTimeout()


def _failure(fid: str, msg: str) -> list[Parsed]:
    return [Parsed(formula_id=fid, status="unparsed", kind="other", error=msg[:300], translator=TRANSLATOR)]


def translate_guarded(f: Formula, use_lark: bool, soft_timeout: float) -> list[Parsed]:
    """translate() with a SIGALRM timeout and a catch-all; only call from a main thread."""
    old = signal.signal(signal.SIGALRM, _on_alarm)
    signal.setitimer(signal.ITIMER_REAL, soft_timeout)
    try:
        return translate(f, use_lark=use_lark)
    except _SoftTimeout:
        return _failure(f.formula_id, f"timeout after {soft_timeout:g}s (soft)")
    except RecursionError:
        return _failure(f.formula_id, "RecursionError: formula nested too deeply")
    except Exception as ex:  # noqa: BLE001 - every failure becomes a record
        return _failure(f.formula_id, f"internal: {type(ex).__name__}: {ex}")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _worker_main(conn, use_lark: bool, soft_timeout: float) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    while True:
        try:
            msg = conn.recv()
        except EOFError:
            return
        if msg is None:
            return
        f = Formula.model_validate_json(msg)
        recs = translate_guarded(f, use_lark, soft_timeout)
        conn.send([r.model_dump_json() for r in recs])


class _Worker:
    def __init__(self, ctx, use_lark: bool, soft_timeout: float):
        self.ctx, self.use_lark, self.soft_timeout = ctx, use_lark, soft_timeout
        self._start()

    def _start(self):
        self.conn, child = self.ctx.Pipe()
        self.proc = self.ctx.Process(target=_worker_main, args=(child, self.use_lark, self.soft_timeout), daemon=True)
        self.proc.start()
        child.close()

    def run(self, f: Formula, hard_timeout: float) -> list[Parsed]:
        try:
            self.conn.send(f.model_dump_json())
            if self.conn.poll(hard_timeout):
                return [Parsed.model_validate_json(s) for s in self.conn.recv()]
            err = f"timeout after {hard_timeout:g}s (worker killed)"
        except (EOFError, BrokenPipeError, ConnectionResetError, OSError) as ex:
            err = f"worker crashed: {type(ex).__name__}"
        self.kill()
        self._start()
        return _failure(f.formula_id, err)

    def kill(self):
        if self.proc.is_alive():
            self.proc.kill()
        self.proc.join(timeout=5)
        self.conn.close()

    def close(self):
        try:
            self.conn.send(None)
        except (BrokenPipeError, OSError):
            pass
        self.proc.join(timeout=5)
        if self.proc.is_alive():
            self.proc.kill()


def translate_many(formulas: Iterable[Formula], *, workers: int = 4, timeout: float = 20.0, use_lark: bool = False,
                   on_result: Callable[[Formula, list[Parsed]], None] | None = None) -> None:
    """Translate formulas, calling on_result(formula, records) as each finishes (any order).

    workers=0 runs in-process with only the soft (SIGALRM) timeout; use it for debugging.
    """
    soft = max(1.0, timeout * 0.75)
    if workers <= 0:
        for f in formulas:
            on_result(f, translate_guarded(f, use_lark, soft))
        return
    ctx = mp.get_context("spawn")
    jobs: queue.Queue = queue.Queue(maxsize=workers * 4)
    results: queue.Queue = queue.Queue()
    DONE = object()

    def drive():
        w = _Worker(ctx, use_lark, soft)
        try:
            while True:
                f = jobs.get()
                if f is DONE:
                    return
                results.put((f, w.run(f, timeout)))
        finally:
            w.close()

    threads = [threading.Thread(target=drive, daemon=True) for _ in range(workers)]
    for t in threads:
        t.start()

    def feed():
        for f in formulas:
            jobs.put(f)
        for _ in threads:
            jobs.put(DONE)

    feeder = threading.Thread(target=feed, daemon=True)
    feeder.start()
    while any(t.is_alive() for t in threads) or not results.empty():
        try:
            f, recs = results.get(timeout=0.2)
        except queue.Empty:
            continue
        on_result(f, recs)
    feeder.join(timeout=1)


def run(in_path: str | Path = "data/raw/formulas.jsonl", out_path: str | Path = "data/parsed/parsed.jsonl", *,
        limit: int | None = None, force: bool = False, workers: int = 4, timeout: float = 20.0,
        use_lark: bool = False, progress: bool = False) -> dict:
    """Stage entry point (SPEC: `run(in_path, out_path, **opts)`). Resumable: formula ids already
    present in out_path are skipped unless force=True. Returns the summary over the whole output."""
    in_path, out_path = Path(in_path), Path(out_path)
    if not in_path.exists():
        raise FileNotFoundError(f"input not found: {in_path}")
    if force and out_path.exists():
        out_path.unlink()
    done = {r.formula_id for r in read_jsonl(out_path, Parsed)}
    todo: list[Formula] = []
    for f in read_jsonl(in_path, Formula):
        if f.formula_id in done:
            continue
        done.add(f.formula_id)  # also dedupes repeated ids in the input
        todo.append(f)
        if limit is not None and len(todo) >= limit:
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bar = None
    if progress and todo:
        from rich.progress import BarColumn, MofNCompleteColumn, Progress, TimeRemainingColumn
        bar = Progress("[progress.description]{task.description}", BarColumn(), MofNCompleteColumn(),
                       TimeRemainingColumn())
        bar.start()
        task = bar.add_task("translate", total=len(todo))
    t0 = time.time()
    with out_path.open("a") as out:
        def on_result(f, recs):
            out.write("".join(r.model_dump_json() + "\n" for r in recs))
            out.flush()
            if bar is not None:
                bar.advance(task)
        try:
            translate_many(todo, workers=workers if len(todo) > 1 else 0, timeout=timeout,
                           use_lark=use_lark, on_result=on_result)
        finally:
            if bar is not None:
                bar.stop()
    summary = summarize(list(read_jsonl(out_path, Parsed)))
    summary["new_formulas"] = len(todo)
    summary["seconds"] = round(time.time() - t0, 1)
    summary["translator"] = TRANSLATOR
    Path(str(out_path) + ".summary.json").write_text(json.dumps(summary, indent=1))
    return summary


__all__ = ["run", "translate_many", "translate_guarded"]
