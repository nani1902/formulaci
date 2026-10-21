"""Playwright harness: drive calculator pages with reference inputs and compare to formulas.py.

Safety: by default every target URL must resolve to a local host (127.0.0.1 / localhost / ::1).
Anything else raises :class:`LiveSiteRefused` before a browser is started, unless
``allow_live=True`` (CLI ``--allow-live``), which needs the user's explicit go-ahead. Even in live
mode the harness aborts every non-GET request the page tries to make to a non-local host, so
reference inputs are only typed into client-side calculators, never posted to a server.
"""
from __future__ import annotations

import ipaddress
import json
import math
import re
import time
from pathlib import Path
from typing import Any, Literal, Optional
from urllib.parse import urljoin, urlparse

import yaml
from pydantic import BaseModel, ConfigDict, Field

from . import formulas as F

VECTORS_PATH = Path(__file__).with_name("vectors.json")
LIVE_TARGETS = Path(__file__).with_name("targets.yaml")
USER_AGENT = "formulaci-clinical-audit/0.1 (+research; reference-formula accuracy audit)"
DEFAULT_REL_TOL = 0.005


# ---------------------------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------------------------
class ResultSpec(BaseModel):
    model_config = ConfigDict(extra="allow")
    selector: str
    regex: str = r"(-?[0-9]+(?:\.[0-9]+)?)"
    unit: Optional[str] = None


class Tol(BaseModel):
    rel: float = DEFAULT_REL_TOL
    abs: float = 0.0


class Target(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    url: str
    formula: str
    site: str = ""
    title: str = ""
    claimed_version: str = ""
    recipe: list[dict[str, Any]] = Field(default_factory=list)
    result: Optional[ResultSpec] = None
    cases: Optional[list[dict[str, Any]]] = None
    tolerance: Tol = Field(default_factory=Tol)
    selectors_verified: Optional[bool] = None
    iframe_src: Optional[str] = None  # calculator lives in an iframe: drive that document directly
    notes: str = ""

    def drive_url(self, base_url: str | None) -> str:
        url = resolve_url(self.url, base_url)
        return urljoin(url, self.iframe_src) if self.iframe_src else url


class AuditRecord(BaseModel):
    target: str
    formula: str
    inputs: dict[str, Any]
    site_output: Optional[float]
    reference_output: Optional[float]
    status: Literal["match", "mismatch", "unreadable"]
    notes: str = ""
    url: str = ""
    claimed_version: str = ""
    site_text: Optional[str] = None
    tolerance: Optional[float] = None
    diagnosis: list[str] = Field(default_factory=list)


class LiveSiteRefused(RuntimeError):
    pass


# ---------------------------------------------------------------------------------------------
# Targets, hosts, cases
# ---------------------------------------------------------------------------------------------
def load_targets(path: str | Path) -> list[Target]:
    data = yaml.safe_load(Path(path).read_text())
    items = data["targets"] if isinstance(data, dict) else data
    return [Target.model_validate(t) for t in items]


def resolve_url(url: str, base_url: str | None) -> str:
    if urlparse(url).scheme:
        return url
    if not base_url:
        raise ValueError(f"relative target URL {url!r} needs --base-url")
    return urljoin(base_url.rstrip("/") + "/", url)


def is_local(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_hosts(urls: list[str], allow_live: bool) -> None:
    remote = sorted({urlparse(u).hostname or u for u in urls if not is_local(u)})
    if remote and not allow_live:
        raise LiveSiteRefused(
            f"refusing to drive non-local hosts without --allow-live: {', '.join(remote)}")


def default_cases(formula: str, n: int) -> list[dict]:
    """Typical-tagged reference vectors already in canonical units."""
    vecs = json.loads(VECTORS_PATH.read_text())["vectors"]
    picked = [v["inputs"] for v in vecs
              if v["formula"] == formula and "typical" in v["tags"] and not v["units"]]
    return picked[:n]


def _fmt(x: float, nd: int = 3) -> str:
    if isinstance(x, bool):
        return str(x).lower()
    if isinstance(x, int) or float(x).is_integer():
        return str(int(x))
    return f"{x:.{nd}f}".rstrip("0").rstrip(".")


def template_vars(inputs: dict) -> dict[str, Any]:
    """Inputs plus derived unit conversions, as strings for typing into pages."""
    v: dict[str, Any] = {k: (_fmt(x) if isinstance(x, (int, float)) and not isinstance(x, bool)
                             else x) for k, x in inputs.items()}
    g = inputs.get
    if g("scr") is not None:
        v["scr_umol"] = _fmt(g("scr") * F.CREATININE_UMOL_PER_MG_DL, 1)
    if g("height") is not None:
        h_in = g("height") / F.CM_PER_IN
        v.update(height_in=_fmt(h_in, 2), height_m=_fmt(g("height") / 100, 3),
                 height_ft=str(int(h_in // 12)), height_in_rem=_fmt(h_in - 12 * (h_in // 12), 2))
    if g("weight") is not None:
        v["weight_lb"] = _fmt(g("weight") / F.KG_PER_LB, 2)
    if g("hr") is not None:
        v.update(rr_s=_fmt(60 / g("hr"), 3), rr_ms=_fmt(60000 / g("hr"), 0))
    if g("glucose") is not None:
        v["glucose_mmol"] = _fmt(g("glucose") / F.GLUCOSE_MG_DL_PER_MMOL, 2)
    if g("ca") is not None:
        v["ca_mmol"] = _fmt(g("ca") / F.CALCIUM_MG_DL_PER_MMOL, 3)
    if g("albumin") is not None:
        v["albumin_g_l"] = _fmt(g("albumin") * 10, 1)
    for name in ("tc", "hdl"):
        if g(name) is not None:
            v[f"{name}_mmol"] = _fmt(g(name) / F.CHOLESTEROL_MG_DL_PER_MMOL, 2)
    if g("tg") is not None:
        v["tg_mmol"] = _fmt(g("tg") / F.TRIGLYCERIDE_MG_DL_PER_MMOL, 2)
    if g("sex") is not None:
        s = str(g("sex")).lower()
        v.update(sex_title=s.title(), sex_initial=s[:1].upper())
    return v


def _when(step: dict, inputs: dict) -> bool:
    cond = step.get("when")
    return not cond or all(inputs.get(k) == want for k, want in cond.items())


# ---------------------------------------------------------------------------------------------
# Comparison and diagnosis
# ---------------------------------------------------------------------------------------------
def parse_value(text: str | None, regex: str) -> tuple[Optional[float], int]:
    """Return (value, decimals shown) from the result text, or (None, 0)."""
    if not text:
        return None, 0
    m = re.search(regex, text.replace(",", "").replace("−", "-"))
    if not m:
        return None, 0
    s = m.group(1)
    try:
        val = float(s)
    except ValueError:
        return None, 0
    return val, (len(s.split(".")[1]) if "." in s else 0)


def tolerance(ref: float, decimals: int, tol: Tol) -> float:
    """Half a unit in the last displayed place, plus a relative allowance for constants."""
    return max(tol.abs, 0.5 * 10 ** -decimals + tol.rel * abs(ref))


def _candidates(key: str, inputs: dict):
    """Yield (description, value) for plausible wrong implementations of formula ``key``."""
    spec = F.REGISTRY[key]
    # 1. another registered formula / version computed on the same inputs
    for other in F.REGISTRY.values():
        if other.key == key:
            continue
        missing = [n for n in other.inputs if n not in inputs]
        if missing and missing != ["black"]:
            continue
        for black in ([False, True] if missing else [None]):
            args = dict(inputs) if black is None else {**inputs, "black": black}
            try:
                val = F.evaluate(other.key, args)
            except Exception:
                continue
            extra = "" if black is None else f" with black={black}"
            yield f"matches {other.key}{extra} ({other.citation.split('.')[0]})", val
    # 2. unit mix-ups on each dimensioned input
    for name in spec.inputs:
        q = F.QUANTITY.get(name)
        if q is None or not isinstance(inputs.get(name), (int, float)):
            continue
        canon = spec.inputs[name]
        for unit, factor in F.CONVERSIONS[q].items():
            if factor == 1.0 or unit == "µmol/L":
                continue
            as_entered = {**inputs, name: inputs[name] / factor}
            as_other = {**inputs, name: inputs[name] * factor}
            for desc, args in ((f"{name} entered in {unit} but used as {canon}", as_entered),
                               (f"{name} in {canon} treated as {unit}", as_other)):
                try:
                    yield f"unit mix-up: {desc}", spec.func(**args)
                except Exception:
                    continue
    # 3. RR in milliseconds instead of seconds for rate corrections
    if key.startswith("qtc_") and "hr" in inputs:
        yield "RR interval used in ms instead of s", spec.func(**{**inputs, "hr": inputs["hr"] / 1000})


def diagnose(key: str, inputs: dict, site: float, tol_abs: float) -> list[str]:
    hits = []
    for desc, val in _candidates(key, inputs):
        if isinstance(val, (int, float)) and math.isfinite(val) and abs(val - site) <= tol_abs:
            hits.append(f"{desc}: {val:.4g}")
    return hits


# ---------------------------------------------------------------------------------------------
# Browser driving
# ---------------------------------------------------------------------------------------------
def _do_step(page, step: dict, vars_: dict, timeout_ms: int) -> None:
    def fmt(s):
        return str(s).format(**vars_)
    if "fill" in step:
        page.fill(fmt(step["fill"]), fmt(step["value"]), timeout=timeout_ms)
    elif "select" in step:
        sel, val = fmt(step["select"]), fmt(step["value"])
        try:
            page.select_option(sel, value=val, timeout=timeout_ms)
        except Exception:
            page.select_option(sel, label=val, timeout=timeout_ms)
    elif "click" in step:
        page.click(fmt(step["click"]), timeout=timeout_ms)
    elif "check" in step:
        page.check(fmt(step["check"]), timeout=timeout_ms)
    elif "uncheck" in step:
        page.uncheck(fmt(step["uncheck"]), timeout=timeout_ms)
    elif "press" in step:
        page.keyboard.press(fmt(step["press"]))
    elif "wait" in step:
        page.wait_for_timeout(int(step["wait"]))
    else:
        raise ValueError(f"unknown recipe step {step}")


def _read(page, spec: ResultSpec, timeout_ms: int) -> tuple[Optional[str], Optional[float], int]:
    """Poll the result element until its text parses as a number or the timeout passes."""
    deadline = time.monotonic() + timeout_ms / 1000
    text = None
    while True:
        loc = page.locator(spec.selector).first
        try:
            if loc.count():
                tag = loc.evaluate("e => e.tagName")
                text = (loc.input_value(timeout=500) if tag in ("INPUT", "TEXTAREA")
                        else loc.inner_text(timeout=500))
        except Exception:
            pass
        val, dec = parse_value(text, spec.regex)
        if val is not None or time.monotonic() > deadline:
            return text, val, dec
        page.wait_for_timeout(100)


def audit_target(page, target: Target, url: str, inputs: dict, timeout_ms: int) -> AuditRecord:
    try:
        ref = F.evaluate(target.formula, inputs)
    except Exception as e:  # e.g. Martin-Hopkins table unavailable
        return AuditRecord(target=target.id, formula=target.formula, inputs=inputs, url=url,
                           site_output=None, reference_output=None, status="unreadable",
                           claimed_version=target.claimed_version,
                           notes=f"reference unavailable: {e}")
    base = dict(target=target.id, formula=target.formula, inputs=inputs, url=url,
                reference_output=ref, claimed_version=target.claimed_version)
    if target.result is None:
        return AuditRecord(**base, site_output=None, status="unreadable",
                           notes="target has no result selector")
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    vars_ = template_vars(inputs)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms * 4)
        for step in target.recipe:
            if _when(step, inputs):
                _do_step(page, step, vars_, timeout_ms)
        text, val, dec = _read(page, target.result, timeout_ms)
    except Exception as e:
        return AuditRecord(**base, site_output=None, status="unreadable",
                           notes=f"driving failed: {type(e).__name__}: {str(e).splitlines()[0]}")
    js = f"; page errors: {'; '.join(errors)[:300]}" if errors else ""
    if val is None:
        return AuditRecord(**base, site_output=None, site_text=text, status="unreadable",
                           notes=f"no number matching {target.result.regex!r} in result{js}")
    tol = tolerance(ref, dec, target.tolerance)
    ok = abs(val - ref) <= tol
    diag = [] if ok else diagnose(target.formula, inputs, val, tol)
    rel = abs(val - ref) / abs(ref) if ref else float("inf")
    note = (f"|site-ref|={abs(val - ref):.4g} ({rel:.2%}) vs tol {tol:.3g}" + js)
    return AuditRecord(**base, site_output=val, site_text=text, tolerance=tol,
                       status="match" if ok else "mismatch", notes=note, diagnosis=diag)


def _record_key(target: str, inputs: dict) -> str:
    return target + "|" + json.dumps(inputs, sort_keys=True)


def run(in_path: str | Path, out_path: str | Path, *, base_url: str | None = None,
        allow_live: bool = False, force: bool = False, max_cases: int = 3,
        only: list[str] | None = None, timeout_ms: int = 3000, delay_s: float | None = None,
        headless: bool = True) -> list[AuditRecord]:
    """Audit every target in ``in_path``; append records to ``out_path`` (JSONL); return them."""
    targets = load_targets(in_path)
    if only:
        targets = [t for t in targets if t.id in set(only)]
    urls = {t.id: t.drive_url(base_url) for t in targets}
    check_hosts(list(urls.values()), allow_live)  # before any browser starts
    live = any(not is_local(u) for u in urls.values())
    delay = delay_s if delay_s is not None else (3.0 if live else 0.0)

    out = Path(out_path)
    done = set()
    if out.exists() and not force:
        for line in out.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add(_record_key(r["target"], r["inputs"]))
    elif out.exists() and force:
        out.unlink()
    out.parent.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    records: list[AuditRecord] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(user_agent=USER_AGENT)

        def guard(route):
            req = route.request
            if req.method != "GET" and not is_local(req.url):
                return route.abort()
            return route.continue_()
        ctx.route("**/*", guard)
        try:
            for t in targets:
                cases = t.cases or default_cases(t.formula, max_cases)
                for inputs in cases:
                    if _record_key(t.id, inputs) in done:
                        continue
                    page = ctx.new_page()
                    try:
                        rec = audit_target(page, t, urls[t.id], inputs, timeout_ms)
                    finally:
                        page.close()
                    records.append(rec)
                    with out.open("a") as f:
                        f.write(rec.model_dump_json() + "\n")
                    if delay:
                        time.sleep(delay)
        finally:
            browser.close()
    return records


def summarize(records: list[AuditRecord]) -> dict[str, dict[str, int]]:
    s: dict[str, dict[str, int]] = {}
    for r in records:
        s.setdefault(r.target, {"match": 0, "mismatch": 0, "unreadable": 0})[r.status] += 1
    return s


def target_status(counts: dict[str, int]) -> str:
    """One word per target: any mismatch wins, then all-unreadable, else match."""
    if counts["mismatch"]:
        return "mismatch"
    if counts["match"] == 0:
        return "unreadable"
    return "match"
