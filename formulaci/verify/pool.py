"""Killable worker processes. SymPy cannot be interrupted reliably with signals, so every task runs
in a child process; on timeout the child is killed and a fresh one is forked from a preloaded
forkserver (cheap: sympy is already imported there)."""
from __future__ import annotations

import multiprocessing as mpr
import sys


class TaskTimeout(Exception):
    pass


class TaskFailed(Exception):
    pass


def _context():
    if sys.platform != "win32":
        ctx = mpr.get_context("forkserver")
        ctx.set_forkserver_preload(["sympy", "mpmath", "formulaci.verify.worker", "formulaci.verify._warm"])
        return ctx
    return mpr.get_context("spawn")


_CTX = None


MEMORY_LIMIT_BYTES = 8 * 1024 ** 3   # best effort: a runaway expression must not exhaust the machine


def _limit_memory() -> None:
    try:
        import resource
        for name in ("RLIMIT_AS", "RLIMIT_DATA"):
            lim = getattr(resource, name, None)
            if lim is None:
                continue
            soft, hard = resource.getrlimit(lim)
            cap = MEMORY_LIMIT_BYTES if hard in (resource.RLIM_INFINITY, -1) else min(MEMORY_LIMIT_BYTES, hard)
            try:
                resource.setrlimit(lim, (cap, hard))
            except (ValueError, OSError):
                pass
    except Exception:  # platform without resource limits; the supervisor's kill still bounds time
        pass


def _entry(conn):
    _limit_memory()
    from formulaci.verify.worker import worker_main

    worker_main(conn)


class Worker:
    def __init__(self):
        global _CTX
        if _CTX is None:
            _CTX = _context()
        self._ctx = _CTX
        self.proc = None
        self.conn = None
        self.restarts = 0

    def _start(self):
        parent, child = self._ctx.Pipe()
        self.proc = self._ctx.Process(target=_entry, args=(child,), daemon=True)
        self.proc.start()
        child.close()
        self.conn = parent

    def warm(self):
        """Start the process now so its startup does not count against a formula's cap."""
        if self.proc is None or not self.proc.is_alive():
            self._start()

    def call(self, task: str, payload: dict, timeout: float):
        if self.proc is None or not self.proc.is_alive():
            self._start()
        self.conn.send((task, payload))
        if not self.conn.poll(max(timeout, 0.05)):
            self.kill()
            raise TaskTimeout(f"{task} exceeded {timeout:.1f}s")
        try:
            status, result = self.conn.recv()
        except (EOFError, OSError) as e:
            self.kill()
            raise TaskFailed(f"worker died during {task}: {e}") from None
        if status != "ok":
            raise TaskFailed(result)
        return result

    def kill(self):
        if self.proc is not None:
            self.proc.kill()
            self.proc.join(timeout=5)
            self.restarts += 1
        if self.conn is not None:
            self.conn.close()
        self.proc = self.conn = None

    def close(self):
        if self.proc is not None and self.proc.is_alive():
            try:
                self.conn.send(None)
                self.proc.join(timeout=2)
            except (OSError, BrokenPipeError):
                pass
            if self.proc.is_alive():
                self.proc.kill()
        self.proc = self.conn = None
