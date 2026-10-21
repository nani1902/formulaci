"""Public library API: check one LaTeX formula (or many) end to end.

    from formulaci.api import check
    r = check(r"\\sin^2 x + \\cos^2 x = 1")
    r.verdict      # "PASS"
    print(r.explain())

`check` runs translate -> semantics -> verify for one formula and never raises for bad input.
Verification runs in killable worker processes (see `formulaci.verify.pool`); they are started
lazily, kept for the lifetime of the process, and restarted if one dies.
"""
from __future__ import annotations

import atexit
import hashlib
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Literal

from pydantic import BaseModel, Field

from formulaci.schemas import Formula, Parsed, Semantics
from formulaci.verify.pool import Worker

__all__ = ["CheckResult", "check", "check_many", "extract_formulas"]

Verdict = Literal["PASS", "FAIL", "INCONCLUSIVE", "SKIP"]

# readable sentences for the semantics skip reasons (anything else falls back to the raw reason)
SKIP_SENTENCES = {
    "unparsed": "The LaTeX could not be parsed.",
    "definition": "It defines a symbol rather than stating an identity, so there is nothing to check.",
    "defining_equation": "It defines or solves for a symbol rather than stating an identity.",
    "statement_not_identity": "It relates particular quantities (a law, a condition or an equation to solve), "
                              "not an identity that holds for all values.",
    "operator_notation": "It uses notation the translator does not handle (operators, ellipses, undefined objects).",
    "has_undefined_function": "It uses a function whose meaning is not known.",
    "functional_identity": "It is a property of an unspecified function, which cannot be sampled.",
    "named_constant": "It gives the value of a named constant that the checker does not know.",
    "approximation": "The formula is stated as an approximation.",
    "notation_or_convention": "It is a notational convention rather than an identity.",
    "units": "It involves physical units.",
    "stated_false": "The surrounding text presents it as false.",
    "special_algebra": "The arithmetic here is not ordinary real or complex arithmetic.",
    "matrix_or_vector": "The symbols are matrices, vectors or operators, not scalars.",
    "differential_equation": "It is a differential equation to solve, not an identity.",
    "condition": "It is a condition, not an identity.",
    "no_relation": "There is no relation (=, <, ...) to check.",
    "indefinite_integral": "It contains an indefinite integral that cannot be compared.",
    "translator_not_checkable": "The translator marked it as not checkable.",
}

_LEADING_QUALIFIER = re.compile(r"^\s*(for|where|when|whenever|if|iff|with|valid|provided)\b", re.I)


class CheckResult(BaseModel):
    """Outcome of checking one formula. All fields are plain JSON-friendly values."""

    latex: str
    verdict: Verdict
    reason: str
    skip_reason: str | None = None
    symbolic: str = "unknown"
    counterexample: dict | None = None
    translation: list[dict] = Field(default_factory=list)
    assumptions: dict = Field(default_factory=dict)
    regimes: list[dict] = Field(default_factory=list)
    elapsed_s: float = 0.0
    formula_id: str = ""
    context: str = ""

    def explain(self) -> str:
        """A short multi-line human summary."""
        lines = [f"{self.verdict}: {self.latex}", f"  {self.reason}"]
        if self.context:
            lines.append(f"  context: {self.context}")
        for t in self.translation:
            if t.get("lhs") is not None and t.get("rhs") is not None:
                idx = f"[{t['index_in_chain']}] " if t.get("index_in_chain") is not None else ""
                lines.append(f"  read as: {idx}{t['lhs']} {t.get('relation') or '?'} {t['rhs']}")
        a = self.assumptions
        if a.get("domains"):
            lines.append("  domains: " + ", ".join(f"{k} {v}" for k, v in a["domains"].items()))
        if a.get("constants"):
            lines.append("  constants: " + ", ".join(f"{k} = {v}" for k, v in a["constants"].items()))
        if a.get("constraints"):
            lines.append("  constraints: " + "; ".join(a["constraints"]))
        if self.counterexample:
            ce = self.counterexample
            where = ", ".join(f"{k} = {_short(v)}" for k, v in ce.get("assignments", {}).items()) or "(no variables)"
            lines.append(f"  counterexample: {where}: lhs = {_short(ce.get('lhs'))}, rhs = {_short(ce.get('rhs'))}, "
                         f"relative difference {_short(ce.get('rel_diff'))}")
        if self.regimes:
            lines.append("  sampled: " + ", ".join(f"{r['name']} {r['n_points'] - r['n_fail']}/{r['n_points']} ok"
                                                   for r in self.regimes))
        lines.append(f"  ({self.elapsed_s:.2f}s)")
        return "\n".join(lines)


def _short(s) -> str:
    if s is None:
        return "?"
    try:
        return f"{float(s):.10g}"
    except (TypeError, ValueError):
        s = str(s)
        return s if len(s) <= 40 else s[:37] + "..."


# --------------------------------------------------------------------------- worker processes

_MAIN_LOCK = threading.Lock()


@contextmanager
def _main_hidden():
    """Hide the __main__ script from multiprocessing while a worker starts.

    The forkserver (and spawn) re-import the parent's main script in the child; an unguarded script
    (`print(check(...))` at top level, no `if __name__ == "__main__"`) would then recurse. The worker
    entry point lives in formulaci.verify.pool and does not need __main__.
    """
    main = sys.modules.get("__main__")
    with _MAIN_LOCK:
        if main is None:
            yield
            return
        saved = {k: main.__dict__[k] for k in ("__spec__", "__file__") if k in main.__dict__}
        main.__dict__.pop("__file__", None)
        main.__spec__ = None
        try:
            yield
        finally:
            main.__dict__.pop("__spec__", None)
            main.__dict__.update(saved)


class _Worker(Worker):
    def _start(self):
        with _main_hidden():
            super()._start()


class _Pool:
    """Idle workers kept for reuse. A worker is checked out by one thread at a time."""

    MAX_IDLE = 8

    def __init__(self):
        self._lock = threading.Lock()
        self._idle: list[_Worker] = []

    def acquire(self) -> _Worker:
        with self._lock:
            w = self._idle.pop() if self._idle else None
        if w is None:
            w = _Worker()
        w.warm()  # restarts a worker whose process died
        return w

    def release(self, w: _Worker) -> None:
        with self._lock:
            if len(self._idle) < self.MAX_IDLE:
                self._idle.append(w)
                return
        w.close()

    def warm(self, n: int) -> None:
        ws = [self.acquire() for _ in range(n)]
        for w in ws:
            self.release(w)

    def close(self) -> None:
        with self._lock:
            idle, self._idle = self._idle, []
        for w in idle:
            try:
                w.close()
            except Exception:  # noqa: BLE001 - shutting down
                pass


_POOL = _Pool()
atexit.register(_POOL.close)


# --------------------------------------------------------------------------- one formula

def _formula(latex: str, context: str, title: str) -> Formula:
    fid = "api:" + hashlib.sha1((latex + "\x00" + context).encode()).hexdigest()
    before, after = _split_context(latex, context)
    return Formula(formula_id=fid, source="api", page_title=title, page_id=0, revision_id=0, url="", index=0,
                   latex=latex, context_before=before, context_after=after)


def _split_context(latex: str, context: str) -> tuple[str, str]:
    """Context containing the formula is split around it; a qualifier ("for |x|<1") goes after it."""
    if not context:
        return "", ""
    # a formula of one or two characters ("x") would match inside unrelated prose
    k = context.find(latex) if len(latex.strip()) >= 3 else -1
    if k >= 0:
        return context[:k].rstrip(" $"), context[k + len(latex):].lstrip(" $")
    if _LEADING_QUALIFIER.match(context):
        return "", context
    return context, ""


def _readable(srepr: str | None) -> str | None:
    if srepr is None:
        return None
    from sympy import sstr

    from formulaci.semantics.rules import load_expr

    e = load_expr(srepr)
    return sstr(e) if e is not None else srepr


def _translation(pieces: list[Parsed]) -> list[dict]:
    return [{"index_in_chain": p.index_in_chain, "status": p.status, "kind": p.kind, "relation": p.relation,
             "lhs": _readable(p.lhs), "rhs": _readable(p.rhs), "free_symbols": p.free_symbols,
             "unsupported": p.has_unsupported, "error": p.error,
             "notes": [n for n in (p.notes or "").split("\n") if n]} for p in pieces]


def _assumptions(sem: Semantics) -> dict:
    return {"domains": {k: d.type for k, d in sem.domains.items()}, "constants": dict(sem.constants),
            "constraints": list(sem.constraints), "assumptions_source": list(sem.assumptions_source)}


def _summarize(e: BaseException) -> str:
    msg = str(e).strip().splitlines()[0] if str(e).strip() else ""
    return f"{type(e).__name__}: {msg}"[:300] if msg else type(e).__name__


def _check(latex, context="", title="", timeout: float = 20.0) -> CheckResult:
    t0 = time.monotonic()
    try:
        latex = "" if latex is None else str(latex)
        context, title = str(context or ""), str(title or "")
        timeout = float(timeout) if timeout and timeout > 0 else 20.0
    except Exception as e:  # noqa: BLE001 - never raise for bad input
        return CheckResult(latex=repr(latex), verdict="INCONCLUSIVE", reason=f"Bad input: {_summarize(e)}.")
    res = CheckResult(latex=latex, verdict="INCONCLUSIVE", reason="", context=context)

    def done(verdict: str, reason: str, **kw) -> CheckResult:
        res.verdict, res.reason = verdict, reason
        for k, v in kw.items():
            setattr(res, k, v)
        res.elapsed_s = round(time.monotonic() - t0, 3)
        return res

    stage = "input"
    try:
        from formulaci.semantics.rules import infer
        from formulaci.semantics.stage import _Timeout, _time_limit
        from formulaci.translate.core import translate
        from formulaci.verify.run import verify_formula

        if not latex.strip():
            return done("SKIP", "Empty formula.", skip_reason="unparsed")
        f = _formula(latex, context, title)
        res.formula_id = f.formula_id
        try:
            # SIGALRM-based, so it applies only when called from the main thread
            with _time_limit(timeout):
                stage = "translate"
                pieces = translate(f)
                res.translation = _translation(pieces)
                if all(p.status == "unparsed" for p in pieces):
                    errs = "; ".join(dict.fromkeys(p.error or "unknown error" for p in pieces))
                    return done("SKIP", f"Could not parse the LaTeX ({errs}).", skip_reason="unparsed")
                stage = "semantics"
                sem, _ = infer(f, pieces)
        except _Timeout:
            return done("INCONCLUSIVE", f"The {stage} stage did not finish within the {timeout:g}s timeout.")
        res.assumptions = _assumptions(sem)
        if not sem.checkable:
            why = sem.skip_reason or "not_checkable"
            sentence = SKIP_SENTENCES.get(why, f"Not checkable ({why.replace('_', ' ')}).")
            if why == "unparsed":
                errs = "; ".join(dict.fromkeys(p.error for p in pieces if p.error))
                sentence = f"Could not parse the LaTeX ({errs})." if errs else sentence
            return done("SKIP", sentence, skip_reason=why)

        stage = "verify"
        cap = max(timeout - (time.monotonic() - t0), 1.0)
        w = _POOL.acquire()
        try:
            v, _ = verify_formula(w, pieces, sem, cap)
        finally:
            _POOL.release(w)
        return done(v.verdict, v.reason, symbolic=v.symbolic,
                    skip_reason="not_checkable" if v.verdict == "SKIP" else None,
                    counterexample=v.counterexample.model_dump() if v.counterexample else None,
                    regimes=[r.model_dump() for r in v.regimes])
    except Exception as e:  # noqa: BLE001 - an internal error must not escape the API
        return done("INCONCLUSIVE", f"Internal error in the {stage} stage ({_summarize(e)}).")


def check(latex: str, context: str = "", title: str = "", *, timeout: float = 20.0,
          workers: int = 0) -> CheckResult:
    """Check one LaTeX formula. `context` is prose around it ("for |x| < 1"), `title` a page/topic name.

    `timeout` caps the whole check in seconds. `workers` is accepted for symmetry with `check_many`;
    a single check always uses one (reused) worker process. Never raises for bad input.
    """
    return _check(latex, context, title, timeout)


def _item(it) -> tuple[str, str, str]:
    if isinstance(it, dict):
        return it.get("latex", ""), it.get("context", ""), it.get("title", "")
    if isinstance(it, (tuple, list)):
        parts = list(it) + ["", "", ""]
        return parts[0], parts[1], parts[2]
    return it, "", ""


def check_many(items: list[dict] | list[tuple[str, str]], *, timeout: float = 20.0,
               workers: int = 4) -> list[CheckResult]:
    """Check many formulas in parallel; results come back in input order.

    Items are dicts with `latex` and optional `context` / `title`, or `(latex, context)` tuples.
    `timeout` applies per formula; `workers` is the number of parallel worker processes.
    """
    items = list(items or [])
    if not items:
        return []
    n = max(1, min(int(workers or 1), len(items)))
    _POOL.warm(n)

    def one(it):
        try:
            latex, context, title = _item(it)
        except Exception as e:  # noqa: BLE001
            return CheckResult(latex=repr(it), verdict="INCONCLUSIVE", reason=f"Bad input item: {_summarize(e)}.")
        return _check(latex, context, title, timeout)

    if n == 1:
        return [one(it) for it in items]
    with ThreadPoolExecutor(max_workers=n, thread_name_prefix="formulaci-check") as ex:
        return list(ex.map(one, items))


# --------------------------------------------------------------------------- formulas in free text

_MATH = re.compile(
    r"(?P<env>\\begin\{(?P<name>equation|align|gather|multline|eqnarray)\*?\}(?P<envbody>.*?)\\end\{(?P=name)\*?\})"
    r"|<math(?:\s[^>]*)?>(?P<math>.*?)</math>"
    r"|(?<!\\)\$\$(?P<dd>.+?)(?<!\\)\$\$"
    r"|\\\[(?P<br>.+?)\\\]"
    r"|\\\((?P<par>.+?)\\\)"
    r"|(?<![\\$])\$(?!\s)(?P<d>[^$\n]+?)(?<![\s\\])\$(?!\d)",
    re.S,
)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])|\n\s*\n")


def extract_formulas(text: str) -> list[tuple[str, str]]:
    """Pull formulas out of free text (Markdown, LaTeX, wikitext).

    Recognizes `$...$`, `$$...$$`, `\\(...\\)`, `\\[...\\]`, `<math>...</math>` and
    `\\begin{equation}` (also align/gather/multline/eqnarray) blocks. Returns `(latex, sentence)`
    pairs in document order; the sentence is the surrounding text with the math delimiters removed
    (formulas kept inline), which can be passed to `check` as its `context`.
    """
    if not text:
        return []
    found = []
    for m in _MATH.finditer(text):
        body = next(g for g in (m.group("envbody"), m.group("math"), m.group("dd"), m.group("br"),
                                m.group("par"), m.group("d")) if g is not None)
        body = body.strip()
        if body:
            found.append((body, m.start(), m.end()))
    if not found:
        return []
    # sentence boundaries, ignoring any that fall inside a formula
    spans = [(s, e) for _, s, e in found]
    cuts = [0] + [b.start() for b in _SENTENCE_END.finditer(text)
                  if not any(s <= b.start() < e for s, e in spans)] + [len(text)]
    out = []
    for latex, s, e in found:
        lo = max(c for c in cuts if c <= s)
        hi = min(c for c in cuts if c >= e)
        sentence = _MATH.sub(lambda m: next(g for g in (m.group("envbody"), m.group("math"), m.group("dd"),
                                                       m.group("br"), m.group("par"), m.group("d"))
                                            if g is not None).strip(), text[lo:hi])
        out.append((latex, " ".join(sentence.split())))
    return out
