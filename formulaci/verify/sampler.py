"""Seeded, domain-aware point sampler.

Sample values are kept as exact decimal strings (reals), ints, or (re, im) string pairs (complex),
so the same point can be re-evaluated at higher precision and reported verbatim.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass

import mpmath as mp

from formulaci.verify.reconstruct import SymSpec

# Value: int | str (decimal) | tuple[str, str] (complex re, im)
Value = int | str | tuple


@dataclass(frozen=True)
class Regime:
    name: str
    real: tuple[float, float, str]  # (lo, hi, "uniform"|"log")
    integer: tuple[int, int]
    complex_box: float | None = None  # half-width of the box for complex-typed symbols
    integer_only: bool = False  # sample every symbol as an integer


REGIMES: dict[str, Regime] = {
    "small_positive": Regime("small_positive", (0.05, 5.0, "log"), (1, 12)),
    "unit_interval": Regime("unit_interval", (0.0, 1.0, "uniform"), (0, 3)),
    "integers_small": Regime("integers_small", (0, 12, "uniform"), (0, 12), integer_only=True),
    "mixed_sign": Regime("mixed_sign", (-5.0, 5.0, "uniform"), (-8, 8)),
    "complex": Regime("complex", (-3.0, 3.0, "uniform"), (-6, 6), complex_box=3.0),
    "large": Regime("large", (10.0, 1000.0, "log"), (15, 60)),
    # used only by the integer-resampling special case
    "integers_large": Regime("integers_large", (13, 40, "uniform"), (13, 40), integer_only=True),
    "integers_mixed_sign": Regime("integers_mixed_sign", (-10, 10, "uniform"), (-10, 10),
                                  integer_only=True),
}
BASE_REGIMES = ["small_positive", "unit_interval", "integers_small", "mixed_sign", "large"]
INTEGER_RESAMPLE_REGIMES = ["integers_large", "integers_mixed_sign"]


def seed_for(formula_id: str, regime: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{formula_id}|{regime}".encode()).digest()[:8], "big")


def _decimal(rng: random.Random, lo: float, hi: float, mode: str, sig: int = 6) -> str:
    if mode == "log" and lo > 0:
        x = math.exp(rng.uniform(math.log(lo), math.log(hi)))
    else:
        x = rng.uniform(lo, hi)
    if x == 0:
        return "0"
    digits = sig - 1 - int(math.floor(math.log10(abs(x))))
    s = f"{round(x, max(digits, 0)):.{max(digits, 0)}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def _type_bounds(spec: SymSpec) -> tuple[float | None, float | None, bool, bool]:
    """(lower, upper, lower_open, upper_open) implied by type + explicit bounds."""
    lo, hi, lo_open, hi_open = None, None, False, False
    t = spec.type
    if t in ("positive", "positive_integer"):
        lo, lo_open = (0, True) if t == "positive" else (1, False)
    elif t in ("nonneg", "nonneg_integer"):
        lo = 0
    elif t == "unit_interval":
        lo, hi = 0, 1
    if spec.lower is not None and (lo is None or spec.lower >= lo):
        lo, lo_open = spec.lower, False
    if spec.upper is not None and (hi is None or spec.upper <= hi):
        hi, hi_open = spec.upper, False
    return lo, hi, lo_open, hi_open


def in_domain(spec: SymSpec, v: Value) -> bool:
    if isinstance(v, tuple):
        return spec.is_complex
    x = mp.mpf(v)
    lo, hi, lo_open, hi_open = _type_bounds(spec)
    if lo is not None and (x < lo or (lo_open and x == lo)):
        return False
    if hi is not None and (x > hi or (hi_open and x == hi)):
        return False
    if spec.is_integer and not isinstance(v, int):
        return False
    return all(abs(x - mp.mpf(e)) > mp.mpf("1e-30") for e in spec.exclude)


def sample_value(spec: SymSpec, regime: Regime, rng: random.Random) -> Value:
    lo_t, hi_t, _, _ = _type_bounds(spec)
    if spec.is_integer or regime.integer_only:
        a, b = regime.integer
        if lo_t is not None:
            a = max(a, math.ceil(lo_t))
            b = max(b, a)
        if hi_t is not None:
            b = min(b, math.floor(hi_t))
            a = min(a, b)
        return rng.randint(a, b)
    if spec.is_complex and regime.complex_box:
        w = regime.complex_box
        re_, im_ = _decimal(rng, -w, w, "uniform"), _decimal(rng, -w, w, "uniform")
        if im_ in ("0", "-0"):
            im_ = "0.5"
        return (re_, im_)
    lo, hi, mode = regime.real
    if spec.type == "unit_interval":
        lo, hi, mode = 0.0, 1.0, "uniform"
    elif lo_t is not None or hi_t is not None:
        # clamp the regime window into the domain; fall back to the domain itself
        L = max(lo, lo_t) if lo_t is not None else lo
        H = min(hi, hi_t) if hi_t is not None else hi
        if L >= H:
            L = lo_t if lo_t is not None else (hi_t - 5)
            H = hi_t if hi_t is not None else (L + 5)
            mode = "uniform"
        if mode == "log" and L <= 0:
            mode = "uniform"
        lo, hi = L, H
    return _decimal(rng, lo, hi, mode)


def to_mp(v: Value):
    if isinstance(v, tuple):
        return mp.mpc(mp.mpf(v[0]), mp.mpf(v[1]))
    return mp.mpf(v)


def fmt_value(v: Value) -> str:
    if isinstance(v, tuple):
        sign = "-" if v[1].startswith("-") else "+"
        return f"{v[0]} {sign} {v[1].lstrip('-')}*I"
    return str(v)


def magnitude(point: dict[str, Value]) -> float:
    return max((abs(complex(float(v[0]), float(v[1]))) if isinstance(v, tuple) else abs(float(v)))
               for v in point.values()) if point else 0.0
