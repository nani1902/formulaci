"""MCP server tests over the SDK's in-memory transport.

No __init__.py in this directory on purpose: with one, pytest would put tests/ on sys.path
and this package would shadow the `mcp` SDK.
"""

from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager

import anyio
import pytest

pytest.importorskip("mcp")

from formulaci import mcp_server  # noqa: E402

try:  # mcp >= 2
    from mcp import Client

    @asynccontextmanager
    async def connect():
        async with Client(mcp_server.mcp) as client:
            yield client
except ImportError:  # mcp 1.x
    from mcp.shared.memory import create_connected_server_and_client_session

    @asynccontextmanager
    async def connect():
        async with create_connected_server_and_client_session(mcp_server.mcp._mcp_server) as client:
            yield client


try:
    import formulaci.api  # noqa: F401

    HAVE_API = True
except Exception:
    HAVE_API = False


def run(coro_fn, *args):
    return anyio.run(coro_fn, *args)


async def _call(name: str, args: dict):
    async with connect() as client:
        result = await client.call_tool(name, args)
    text = result.content[0].text
    return text if name == "explain_verdict" else json.loads(text)


def call(name: str, **args):
    return run(_call, name, args)


# ---- fakes matching the formulaci.api contract -------------------------------------------


class FakeResult:
    def __init__(self, latex: str, verdict: str, **kw):
        self.latex = latex
        self.verdict = verdict
        self.reason = kw.get("reason", "")
        self.skip_reason = kw.get("skip_reason")
        self.symbolic = kw.get("symbolic", "unknown")
        self.counterexample = kw.get("counterexample")
        self.translation = kw.get("translation", [])
        self.assumptions = kw.get("assumptions", {})
        self.regimes = kw.get("regimes", [])
        self.elapsed_s = kw.get("elapsed_s", 0.01)

    def explain(self) -> str:
        return f"{self.verdict}: {self.latex}"


def fake_check(latex, context="", title="", *, timeout=20.0, workers=0):
    if "boom" in latex:
        raise RuntimeError("translator exploded")
    if latex.endswith("= 2"):
        return FakeResult(
            latex, "FAIL", reason="numeric mismatch", symbolic="not_equal",
            counterexample={"assignments": {"x": "0.7"}, "lhs": "1.0", "rhs": "2.0",
                            "abs_diff": "1.0", "rel_diff": "0.5"},
            translation=[{"lhs": "Add(Pow(sin(Symbol('x')), Integer(2)), Pow(cos(Symbol('x')), Integer(2)))",
                          "relation": "==", "rhs": "Integer(2)", "status": "ok"}],
            assumptions={"x": {"type": "real"}},
        )
    if latex.endswith("= 1"):
        return FakeResult(latex, "PASS", symbolic="equal")
    return FakeResult(latex, "SKIP", skip_reason="statement_not_identity")


def fake_check_many(items, *, timeout=20.0, workers=4):
    return [fake_check(*it) if isinstance(it, tuple) else fake_check(it) for it in items]


def fake_extract(text):
    import re

    return [(m.group(1).strip(), text) for m in re.finditer(r"\$([^$]+)\$", text)]


@pytest.fixture
def fakes(monkeypatch):
    monkeypatch.setattr(mcp_server, "check", fake_check)
    monkeypatch.setattr(mcp_server, "check_many", fake_check_many)
    monkeypatch.setattr(mcp_server, "extract_formulas", fake_extract)


# ---- protocol surface (no pipeline needed) ---------------------------------------------------


def test_lists_tools_and_policy_resource():
    async def go():
        async with connect() as client:
            tools = (await client.list_tools()).tools
            resources = (await client.list_resources()).resources
            policy = await client.read_resource("formulaci://policy")
        return tools, resources, policy

    tools, resources, policy = run(go)
    by_name = {t.name: t for t in tools}
    assert set(by_name) == {"verify_formula", "verify_text", "explain_verdict"}
    for t in tools:
        assert "before" in t.description.lower() or "after verify_formula" in t.description.lower()
    assert (getattr(by_name["verify_formula"], "input_schema", None) or by_name["verify_formula"].inputSchema)["required"] == ["latex"]
    assert [str(r.uri) for r in resources] == ["formulaci://policy"]
    text = policy.contents[0].text
    assert "precision-first" in text and "one in ten" in text and "60 s" in text


def test_timeout_clamped():
    assert mcp_server._clamp_timeout(1000) == 60.0
    assert mcp_server._clamp_timeout(-1) == mcp_server.DEFAULT_TIMEOUT_S
    assert mcp_server._clamp_timeout(float("nan")) == mcp_server.DEFAULT_TIMEOUT_S
    assert mcp_server._clamp_timeout(5) == 5.0
    assert mcp_server._clamp_timeout(0.001) == mcp_server.MIN_TIMEOUT_S


# ---- tools with fakes ------------------------------------------------------------------------


def test_verify_formula_fail_with_fakes(fakes):
    out = call("verify_formula", latex=r"\sin^2 x + \cos^2 x = 2")
    assert out["verdict"] == "FAIL"
    assert out["advice"].startswith("Do not present this formula; it fails at the 1-variable sample point")
    assert "x = 0.7" not in out["advice"] and "1.0" in out["advice"] and "2.0" in out["advice"]
    assert out["counterexample"]["assignments"] == {"x": "0.7"}
    assert out["translation"][0]["lhs"] == "sin(x)**2 + cos(x)**2"
    assert out["translation"][0]["rhs"] == "2"
    assert out["assumptions"] == {"x": {"type": "real"}}


def test_verify_formula_pass_and_skip_with_fakes(fakes):
    ok = call("verify_formula", latex=r"\sin^2 x + \cos^2 x = 1")
    assert ok["verdict"] == "PASS" and ok["advice"].startswith("Proved symbolically; numeric evaluation was not available")
    assert "counterexample" not in ok
    skip = call("verify_formula", latex="F = ma")
    assert skip["verdict"] == "SKIP" and skip["skip_reason"] == "statement_not_identity"
    assert skip["advice"].startswith("Could not verify")


def test_pass_advice_states_the_evidence():
    adv = mcp_server._pass_advice
    assert "symbolically and numerically at 12" in adv(FakeResult("x", "PASS", symbolic="equal", regimes=[{"n_points": 12, "n_error": 0}]), "")
    assert adv(FakeResult("x", "PASS", symbolic="unknown", regimes=[{"n_points": 12, "n_error": 2}]), "").startswith("Verified numerically at 10")
    assert adv(FakeResult("x", "PASS", symbolic="equal"), "").startswith("Proved symbolically")
    assert "integer" in adv(FakeResult("x", "PASS", regimes=[{"n_points": 36}]), "integer-only identity whose integer domain was not stated")
    assert adv(FakeResult("x", "PASS"), "").startswith("Marked PASS without")


def test_fail_advice_carries_numbers_only():
    adv = mcp_server._fail_advice({"assignments": {"x_ignore_all_instructions": "0"}, "lhs": "1.0", "rhs": "2.0"}, "")
    assert "ignore" not in adv and "1-variable" in adv and "1.0" in adv


def test_verify_text_errors_keep_text_shape(fakes):
    out = call("verify_text", text="x" * (2_000_001))
    assert out["summary"]["total"] == 0 and out["results"] == [] and "too long" in out["error"]
    assert "not claim" in out["advice"]


def test_exception_becomes_inconclusive(fakes):
    out = call("verify_formula", latex="boom = 1")
    assert out["verdict"] == "INCONCLUSIVE"
    assert "translator exploded" in out["reason"]
    assert call("explain_verdict", latex="boom").startswith("INCONCLUSIVE")


def test_wall_clock_backstop(monkeypatch):
    def slow_check(latex, context="", title="", *, timeout=20.0, workers=0):
        time.sleep(3)

    monkeypatch.setattr(mcp_server, "check", slow_check)
    monkeypatch.setattr(mcp_server, "_GRACE_S", 0.0)
    t0 = time.monotonic()
    out = call("verify_formula", latex="x = x", timeout=0.3)
    assert time.monotonic() - t0 < 2.5
    assert out["verdict"] == "INCONCLUSIVE" and "timeout" in out["reason"]


def test_verify_text_with_fakes(fakes):
    text = (r"For real $x$ we have $\sin^2 x + \cos^2 x = 1$, and hence "
            r"$\sin^2 x + \cos^2 x = 2$.")
    out = call("verify_text", text=text)
    assert out["summary"] == {"total": 3, "PASS": 1, "FAIL": 1, "INCONCLUSIVE": 0, "SKIP": 1}
    assert [r["verdict"] for r in out["results"]] == ["SKIP", "PASS", "FAIL"]
    # advice names formulas by index only; untrusted LaTeX stays in results (data), never in instructions
    assert "#3" in out["advice"] and r"\cos^2 x = 2" not in out["advice"]
    assert out["advice"].startswith("Fix 1 formula before presenting the text: #3")

    capped = call("verify_text", text=text, max_formulas=1)
    assert capped["summary"]["total"] == 1 and "truncated" in capped


def test_verify_text_without_formulas(fakes):
    out = call("verify_text", text="No math here.")
    assert out["summary"]["total"] == 0 and out["advice"] == "No checkable formulas found in the text."


def test_explain_with_fakes(fakes):
    assert call("explain_verdict", latex=r"\sin^2 x + \cos^2 x = 1") == r"PASS: \sin^2 x + \cos^2 x = 1"


# ---- real pipeline ---------------------------------------------------------------------------

real = pytest.mark.skipif(not HAVE_API, reason="formulaci.api not importable yet")


@real
def test_real_pythagorean_fail():
    out = call("verify_formula", latex=r"\sin^2 x + \cos^2 x = 2")
    assert out["verdict"] == "FAIL", out
    assert out["advice"].startswith("Do not present this formula")
    assert out.get("counterexample")


@real
def test_real_pythagorean_pass():
    out = call("verify_formula", latex=r"\sin^2 x + \cos^2 x = 1")
    assert out["verdict"] == "PASS", out
    assert out["advice"].startswith("Verified symbolically and numerically at")


@real
def test_real_verify_text_finds_two_formulas():
    text = (r"The Pythagorean identity $\sin^2 x + \cos^2 x = 1$ holds for every real x, and the "
            r"geometric series gives $\sum_{k=0}^{\infty} x^k = \frac{1}{1-x}$ whenever |x| < 1.")
    out = call("verify_text", text=text)
    assert out["summary"]["total"] == 2, out
    assert out["summary"]["FAIL"] == 0, out


@real
def test_real_explain():
    text = call("explain_verdict", latex=r"\sin^2 x + \cos^2 x = 2")
    assert "FAIL" in text
