"""MCP server: lets a language model check a formula before it shows it to a user.

Run with ``formulaci-mcp`` (stdio transport). Tools: ``verify_formula``, ``verify_text``,
``explain_verdict``; resource ``formulaci://policy``. Every tool returns a result, never an
error: an exception or a timeout becomes ``{"verdict": "INCONCLUSIVE", "reason": ...}``.
stdout is the protocol channel, so logging goes to stderr only.
"""

from __future__ import annotations

import contextlib
import logging
import os
import re
import sys
from typing import Any

import anyio
import anyio.to_thread

try:  # mcp >= 2: FastMCP was renamed MCPServer
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

log = logging.getLogger("formulaci.mcp")

MAX_TIMEOUT_S = 60.0
DEFAULT_TIMEOUT_S = 20.0
# Extra wall-clock time on top of the per-formula budget before the server gives up waiting.
_GRACE_S = 15.0


# The API is imported lazily so the server starts (and lists its tools) even if importing
# the pipeline fails; tests monkeypatch these three names.
def check(*args: Any, **kwargs: Any):
    from formulaci.api import check as _check

    return _check(*args, **kwargs)


def check_many(*args: Any, **kwargs: Any):
    from formulaci.api import check_many as _check_many

    return _check_many(*args, **kwargs)


def extract_formulas(*args: Any, **kwargs: Any):
    from formulaci.api import extract_formulas as _extract

    return _extract(*args, **kwargs)


POLICY = """\
formulaci verification policy (read before acting on a verdict)

What is checked: identities, i.e. a relation (=, <, <=, >, >=) that should hold for every
admissible value of its free variables: algebraic identities, series, integrals, special
function relations, closed forms, numeric constants. Equations to solve (x^2 - 2 = 0),
laws between measured quantities (F = ma), definitions (f(x) := ...) and prose are not
identities; they come back SKIP or INCONCLUSIVE.

Verdicts:
- PASS: symbolic and/or numeric agreement at high precision in every sampled regime.
- FAIL: precision-first. Reported only when the two sides disagree at 50 and 65+ digits in at
  least two independent sampling regimes (or for a constant, stably at both precisions) and
  SymPy does not prove them equal. A counterexample is attached. Treat FAIL as "this formula,
  as written and as read, is wrong": do not present it; fix it or say it could not be verified.
- INCONCLUSIVE: no decision (timeout, ambiguous notation, branch cuts, too few valid points,
  an approximation). Not evidence either way.
- SKIP: not a checkable identity, or notation the translator refuses.

Limits:
- The verdict is about the LaTeX as read. Check `translation` (lhs/rhs) and `assumptions`
  (inferred domains and constants): a FAIL can come from a misreading, e.g. e or i read as
  variables, a superscript that is a label, or a log with a different base.
- On real Wikipedia pages roughly one in ten FAIL flags was a true error before human review;
  most of the rest were statements or notation that is not an identity. On formulas you wrote
  as identities, a FAIL is much more likely to be real, but read the counterexample.
- Each formula has a time budget (default 20 s, at most 60 s). Hard integrals and slowly
  converging series can time out and come back INCONCLUSIVE.
- Context text helps: it is used to infer variable domains (n integer, x > 0, |x| < 1).
"""

_ADVICE_PASS = "Verified numerically and symbolically; you may present this formula."
_ADVICE_UNSURE = "Could not verify; say so or rephrase as a checkable identity."

_INSTRUCTIONS = (
    "formulaci machine-checks mathematical identities written in LaTeX. Call verify_formula "
    "(or verify_text for a draft with several formulas) before presenting any non-trivial "
    "identity, series, integral, or closed form to a user. Never present a formula that came "
    "back FAIL. Read formulaci://policy for what the verdicts mean."
)

mcp = _Server("formulaci", instructions=_INSTRUCTIONS)


def _clamp_timeout(timeout: float | None) -> float:
    try:
        t = float(timeout) if timeout is not None else DEFAULT_TIMEOUT_S
    except (TypeError, ValueError):
        t = DEFAULT_TIMEOUT_S
    if t != t or t <= 0:  # NaN or non-positive
        t = DEFAULT_TIMEOUT_S
    return min(t, MAX_TIMEOUT_S)


def _error_result(reason: str, latex: str | None = None) -> dict:
    out: dict[str, Any] = {"verdict": "INCONCLUSIVE", "reason": reason, "advice": _ADVICE_UNSURE}
    if latex is not None:
        out = {"latex": latex, **out}
    return out


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


_SREPR = re.compile(r"^[A-Z][A-Za-z]*\(")


def _readable(expr: Any) -> Any:
    """sympy srepr string -> plain expression string; anything else (already readable) unchanged."""
    if not isinstance(expr, str) or not _SREPR.match(expr):
        return expr
    try:
        import sympy

        return sympy.sstr(sympy.sympify(expr))
    except Exception:
        return expr


def _compact_translation(pieces: Any) -> list[dict]:
    out = []
    for piece in pieces or []:
        if not isinstance(piece, dict):
            piece = _get(piece, "model_dump", lambda: {"value": str(piece)})()
        item: dict[str, Any] = {}
        for key in ("index_in_chain", "lhs", "relation", "rhs", "status", "unsupported", "error"):
            if piece.get(key) not in (None, [], ""):
                item[key] = _readable(piece[key]) if key in ("lhs", "rhs") else piece[key]
        if not item:
            item = {k: v for k, v in piece.items() if isinstance(v, (str, int, float, bool))}
        out.append(item)
    return out


def _compact_counterexample(ce: Any) -> dict | None:
    if ce is None:
        return None
    if not isinstance(ce, dict):
        ce = _get(ce, "model_dump", lambda: {"value": str(ce)})()
    return dict(ce) or None


def _short(value: Any) -> Any:
    """'1.000000000000000000000' -> '1.0'; integers and non-decimals stay as given."""
    if not isinstance(value, str) or not re.fullmatch(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?", value.strip()):
        return value
    try:
        import mpmath

        return mpmath.nstr(mpmath.mpf(str(value)), 12)
    except Exception:
        return value


def _fail_advice(counterexample: dict | None, reason: str) -> str:
    if counterexample:
        at = counterexample.get("assignments")
        where = ", ".join(f"{k} = {_short(v)}" for k, v in at.items()) if isinstance(at, dict) and at else ""
        lhs, rhs = _short(counterexample.get("lhs")), _short(counterexample.get("rhs"))
        if where and lhs is not None and rhs is not None:
            return (
                f"Do not present this formula; the identity fails at {where}, "
                f"where the left side is {lhs} and the right side is {rhs}."
            )
        if lhs is not None and rhs is not None:
            return f"Do not present this formula; the left side is {lhs} but the right side is {rhs}."
    detail = f" ({reason})" if reason else ""
    return f"Do not present this formula; the identity fails{detail}."


def _advice(verdict: str, counterexample: dict | None, reason: str) -> str:
    if verdict == "FAIL":
        return _fail_advice(counterexample, reason)
    if verdict == "PASS":
        return _ADVICE_PASS
    return _ADVICE_UNSURE


def _compact(result: Any) -> dict:
    """CheckResult -> small JSON-able dict for a calling model."""
    verdict = str(_get(result, "verdict", "INCONCLUSIVE"))
    reason = _get(result, "reason", "") or ""
    counterexample = _compact_counterexample(_get(result, "counterexample"))
    out: dict[str, Any] = {
        "latex": _get(result, "latex"),
        "verdict": verdict,
        "reason": reason,
        "advice": _advice(verdict, counterexample, reason),
    }
    if counterexample:
        out["counterexample"] = counterexample
    symbolic = _get(result, "symbolic")
    if symbolic and symbolic != "unknown":
        out["symbolic"] = symbolic
    translation = _compact_translation(_get(result, "translation"))
    if translation:
        out["translation"] = translation
    assumptions = _get(result, "assumptions")
    if assumptions:
        out["assumptions"] = assumptions
    skip_reason = _get(result, "skip_reason")
    if skip_reason:
        out["skip_reason"] = skip_reason
    elapsed = _get(result, "elapsed_s")
    if isinstance(elapsed, (int, float)):
        out["elapsed_s"] = round(float(elapsed), 2)
    return out


async def _run_blocking(fn, *args: Any, wall_s: float, **kwargs: Any):
    """Run a pipeline call in a worker thread; give up waiting after wall_s seconds.

    The pipeline has its own per-formula timeout; this is the backstop if it overruns. Stray
    prints from the pipeline go to stderr so they can never reach the protocol channel.
    """

    def call():
        with contextlib.redirect_stdout(sys.stderr):
            return fn(*args, **kwargs)

    with anyio.fail_after(wall_s):
        return await anyio.to_thread.run_sync(call, abandon_on_cancel=True)


@mcp.tool()
async def verify_formula(latex: str, context: str = "", timeout: float = DEFAULT_TIMEOUT_S) -> dict:
    """Machine-check one mathematical identity written in LaTeX before you present it.

    Call this before showing a user any non-trivial identity, series, integral, closed form,
    special-function relation or numeric constant that you derived or recalled, e.g.
    r"\\sum_{k=1}^\\infty 1/k^2 = \\pi^2/6" or r"\\int_0^1 x^n\\,dx = \\frac{1}{n+1}".
    Pass one relation (=, <, <=, >, >=) without surrounding $...$. Put the sentence around it
    in `context` (it is used to infer domains such as "n a positive integer", "|x| < 1").

    Returns {verdict: PASS|FAIL|INCONCLUSIVE|SKIP, reason, advice, counterexample?,
    translation (how the LaTeX was read, as lhs/rhs), assumptions (inferred domains),
    skip_reason?}. Follow `advice`: never present a FAIL formula; fix it and check again.
    INCONCLUSIVE/SKIP means unverified, not wrong. `timeout` is seconds, capped at 60.
    """
    try:
        t = _clamp_timeout(timeout)
        result = await _run_blocking(check, latex, context, timeout=t, wall_s=t + _GRACE_S)
        return _compact(result)
    except TimeoutError:
        log.warning("verify_formula timed out: %r", latex)
        return _error_result(f"timeout after {_clamp_timeout(timeout):g} s", latex)
    except Exception as exc:
        log.exception("verify_formula failed: %r", latex)
        return _error_result(f"{type(exc).__name__}: {exc}", latex)


@mcp.tool()
async def verify_text(text: str, max_formulas: int = 50, timeout: float = DEFAULT_TIMEOUT_S) -> dict:
    """Check every formula in a draft answer (Markdown/LaTeX or wiki text) before you send it.

    Call this on a draft that contains several displayed or inline formulas ($...$, $$...$$,
    \\[...\\], \\(...\\), <math>...</math>): each identity, series, integral or closed form is
    extracted with its surrounding sentence and checked. Prose, definitions and equations to
    solve are skipped. At most `max_formulas` (cap 200) are checked; `timeout` is seconds per
    formula, capped at 60.

    Returns {summary: {total, PASS, FAIL, INCONCLUSIVE, SKIP}, results: [per-formula dicts as
    from verify_formula], advice}. `advice` lists the formulas that must be fixed (FAIL) before
    the text is shown; fix them and call again.
    """
    try:
        t = _clamp_timeout(timeout)
        n = max(1, min(int(max_formulas), 200))
        formulas = await _run_blocking(extract_formulas, text, wall_s=60.0)
        found = len(formulas)
        formulas = list(formulas)[:n]
        results = []
        if formulas:
            # check_many runs in parallel workers; allow every formula its full budget as backstop.
            wall = t * len(formulas) + _GRACE_S
            raw = await _run_blocking(check_many, formulas, timeout=t, wall_s=wall)
            results = [_compact(r) for r in raw]
        summary = {"total": len(results), "PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0, "SKIP": 0}
        for r in results:
            summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
        out: dict[str, Any] = {"summary": summary, "results": results, "advice": _text_advice(results)}
        if found > len(formulas):
            out["truncated"] = f"{found} formulas found, only the first {len(formulas)} were checked"
        return out
    except TimeoutError:
        log.warning("verify_text timed out")
        return _error_result("timeout while checking the text")
    except Exception as exc:
        log.exception("verify_text failed")
        return _error_result(f"{type(exc).__name__}: {exc}")


def _text_advice(results: list[dict]) -> str:
    if not results:
        return "No checkable formulas found in the text."
    fails = [(i, r) for i, r in enumerate(results, 1) if r["verdict"] == "FAIL"]
    unsure = sum(r["verdict"] in ("INCONCLUSIVE", "SKIP") for r in results)
    parts = []
    if fails:
        listed = "; ".join(f"#{i} {r.get('latex')}: {r['advice']}" for i, r in fails)
        n = len(fails)
        parts.append(f"Fix {n} formula{'s' if n > 1 else ''} before presenting the text: {listed}")
    else:
        parts.append("No formula failed.")
    if unsure:
        parts.append(f"{unsure} formula(s) could not be verified; do not claim they were checked.")
    return " ".join(parts)


@mcp.tool()
async def explain_verdict(latex: str, context: str = "", timeout: float = DEFAULT_TIMEOUT_S) -> str:
    """Check one LaTeX identity and return a human-readable explanation of the verdict.

    Use after verify_formula when you need to show the user why a formula fails (how it was
    read, inferred domains, regimes sampled, the counterexample) or to debug a misreading.
    For the decision itself prefer verify_formula, which returns structured JSON.
    """
    try:
        t = _clamp_timeout(timeout)
        result = await _run_blocking(check, latex, context, timeout=t, wall_s=t + _GRACE_S)
        return str(result.explain())
    except TimeoutError:
        log.warning("explain_verdict timed out: %r", latex)
        return f"INCONCLUSIVE: timeout after {_clamp_timeout(timeout):g} s"
    except Exception as exc:
        log.exception("explain_verdict failed: %r", latex)
        return f"INCONCLUSIVE: {type(exc).__name__}: {exc}"


@mcp.resource("formulaci://policy", name="policy", mime_type="text/plain",
              description="What formulaci verdicts mean, the FAIL policy, and its limits.")
def policy() -> str:
    return POLICY


def main() -> None:
    # The SDK configures a stderr handler when the server object is built; this only adds one
    # if it did not, and sets the level (FORMULACI_MCP_LOG=DEBUG|INFO|WARNING|ERROR).
    logging.basicConfig(stream=sys.stderr, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    logging.getLogger().setLevel(os.environ.get("FORMULACI_MCP_LOG", "WARNING").upper())
    log.info("formulaci MCP server starting (stdio)")
    mcp.run("stdio")


if __name__ == "__main__":
    main()
