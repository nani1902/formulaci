"""Detectors for formulas whose mismatch is not an error: rounded decimals, rational approximations
of constants, tolerance hints from Semantics, and superscripts that are labels rather than powers.

They read the translator's `sides: <lhs latex> || <rhs latex>` line in `Parsed.notes`, the
reconstructed expressions, and `Semantics.assumptions_source`. All run inside the worker.
"""
from __future__ import annotations

import re
from fractions import Fraction

import sympy as sp

from formulaci.verify.reconstruct import Problem

# ---------------------------------------------------------------- translator notes


def note_lines(notes: str | None) -> list[str]:
    return [s.strip() for s in (notes or "").splitlines() if s.strip()]


def sides_latex(notes: str | None) -> tuple[str, str] | None:
    """The `sides: L || R` LaTeX the translator recorded for this record, if any."""
    for line in note_lines(notes):
        if line.startswith("sides:") and "||" in line:
            left, right = line[len("sides:"):].split("||", 1)
            return left.strip(), right.strip()
    return None


# ---------------------------------------------------------------- decimal literals

_SPACING = re.compile(r"\\[,;:!> ]|\\quad|\\qquad|~|\s|[{}]")
_TRUNC = re.compile(r"(\\l?dots|\\cdots|\.\.\.|…)$")
_DECIMAL = re.compile(r"^([+-]?)(\d*)\.(\d+)$")


def decimal_literal(latex: str) -> dict | None:
    """'0.74048' -> {'text': '0.74048', 'decimals': 5, 'value': Fraction, 'truncated': False}.

    Only a side that is *nothing but* a decimal number qualifies (trailing punctuation and an
    ellipsis are allowed; an ellipsis marks the digits as truncated, not rounded)."""
    s = _SPACING.sub("", latex)
    s = s.rstrip(".,;") if not s.endswith("...") else s
    truncated = bool(_TRUNC.search(s))
    s = _TRUNC.sub("", s).rstrip(".,;")
    m = _DECIMAL.match(s)
    if not m:
        return None
    text = f"{m.group(1)}{m.group(2) or '0'}.{m.group(3)}"
    return {"text": text, "decimals": len(m.group(3)), "value": Fraction(text), "truncated": truncated}


def decimal_sides(p: Problem, notes: str | None) -> list[dict]:
    """Decimal-literal sides whose reconstructed value equals the literal (index 0 = lhs, 1 = rhs)."""
    sides = sides_latex(notes)
    if sides is None:
        return []
    out = []
    for i, (latex, expr) in enumerate(zip(sides, (p.lhs, p.rhs))):
        lit = decimal_literal(latex)
        if lit is None or not expr.is_Rational:
            continue
        if Fraction(int(expr.p), int(expr.q)) != lit["value"]:
            continue  # the translator did something else with it
        out.append({"side": i, "text": lit["text"], "decimals": lit["decimals"], "truncated": lit["truncated"]})
    return out


def rational_approximation(p: Problem) -> bool:
    """Constant formula of the form <irrational constant expression> = <non-integer fraction>, e.g.
    pi = 355/113: usually a historical or working approximation, not a claimed identity."""
    if p.syms or p.relation != "=":
        return False
    for a, b in ((p.lhs, p.rhs), (p.rhs, p.lhs)):
        if b.is_Rational and not b.is_Integer and a.is_number and a.is_rational is False:
            return True
    return False


# ---------------------------------------------------------------- tolerance hints from Semantics

_TOL = re.compile(r"^tol:\s*(rel|abs|digits)\s*=\s*([0-9.eE+-]+)\s*$")


def tolerance_hints(assumptions_source: list[str]) -> dict:
    """`tol:rel=1e-3`, `tol:abs=0.005`, `tol:digits=3` (half a unit in the 3rd decimal), `tol:approx`
    (the context says the formula is approximate: never FAIL)."""
    out: dict = {}
    for item in assumptions_source or []:
        item = item.strip()
        if item in ("tol:approx", "tol:approximate"):
            out["approx"] = True
            continue
        m = _TOL.match(item)
        if not m:
            continue
        kind, val = m.group(1), float(m.group(2))
        if kind == "digits":
            out["abs"] = max(out.get("abs", 0.0), 0.5 * 10 ** -int(val))
        elif val > 0:
            out[kind] = max(out.get(kind, 0.0), val)
    return out


def stated_type_symbols(assumptions_source: list[str]) -> set[str]:
    """Symbols whose number type was stated in the prose (P.type_phrase:x, P.member:x, P.interval:x)."""
    out: set[str] = set()
    for item in assumptions_source or []:
        m = re.match(r"^P\.(?:type_phrase|member|interval):(.+)$", item.strip())
        if m:
            out.add(m.group(1))
    return out


# ---------------------------------------------------------------- label superscripts

# LaTeX patterns on a *letter* base (a `}` closing a name or subscript counts; a `)` does not, so
# (-1)^{(k+1)} stays a power)
_LETTER_BASE = r"(?:[A-Za-z]|(?<!\))\}|_[A-Za-z0-9])\s*\^\s*"
_LATEX_LABELS = [
    (re.compile(_LETTER_BASE + r"\{?\s*\("), "a parenthesised superscript"),           # X^{(0)}, f^{(n)}
    (re.compile(_LETTER_BASE + r"(\{\s*0\s*\}|0(?![\d.]))"), "a superscript 0"),       # C_3^0, g_i^0
    (re.compile(_LETTER_BASE + r"\{?\s*\\(text|mathrm|rm)\b"), "a text superscript"),  # A^\mathrm{g}
    (re.compile(_LETTER_BASE + r"\{?\s*\\circ\b"), "a circle superscript (standard state, not degrees)"),
    (re.compile(r"\\operatorname\s*\{[^}]*\}\s*\^"), "a superscript on an operator name"),  # Ric^g, H^{-1}
]
_UPPER = re.compile(r"^[A-Z](_.*)?$")
# limits of big operators (\sum_{k=0}^{n}, \int_0^\infty) are bounds, not superscripts
_BIG_OP_LIMITS = re.compile(
    r"\\(sum|prod|coprod|int|iint|iiint|oint|bigcup|bigcap|bigoplus|bigotimes|lim|limsup|liminf|max|min|sup|inf)"
    r"(?![A-Za-z])\s*(\\limits)?\s*(_\s*(\{[^{}]*(\{[^{}]*\}[^{}]*)*\}|\\?\w+))?\s*(\^\s*(\{[^{}]*\}|\\?\w+))?")


def _label_parts(e: sp.Basic) -> tuple[int, frozenset] | None:
    """(coefficient, symbols) if `e` is c * (a product of distinct bare symbols), else None."""
    if isinstance(e, sp.Symbol):
        return 1, frozenset([e])
    if isinstance(e, sp.Mul):
        coeff, rest = e.as_coeff_mul()
        if coeff.is_Integer and rest and all(isinstance(a, sp.Symbol) for a in rest):
            return int(coeff), frozenset(rest)
    return None


def label_superscript(p: Problem, notes: str | None) -> str | None:
    """Why a superscript in this formula is probably a label, not a power (or None).

    Fires on: translator `superscript_label:` notes; symbols whose name contains '^'; LaTeX
    superscripts on a letter that are parenthesised, 0, text, a circle or infinity, or sit on an
    operator name; a symbol raised to oo or to something involving I; an uppercase letter raised
    to an uppercase letter (M^X) or to -1 (an operator/matrix inverse); a multi-letter superscript
    (H_s^{xp} -> H_s**(p*x)); and a symbol that occurs *only* as a bare exponent of other symbols
    (B^s, F^D + F^H, a a^omega = a^omega). Exponents that take part in arithmetic (a+1) are
    treated as genuine powers, so exponent laws keep their FAILs."""
    for line in note_lines(notes):
        if line.startswith("superscript_label:"):
            return f"the translator marked {line.split(':', 1)[1].strip()} as a superscript label"
    for s in p.syms:
        if "^" in s.name:
            return f"symbol {s.name} carries a superscript in its name"
    sides = sides_latex(notes)
    if sides:
        latex = _BIG_OP_LIMITS.sub(" ", " ".join(sides))
        for rx, what in _LATEX_LABELS:
            if rx.search(latex):
                return f"the LaTeX has {what}, which usually indexes rather than exponentiates"
    free = p.lhs.free_symbols | p.rhs.free_symbols  # bound summation/integration variables are not labels
    sym_pows = [pw for side in (p.lhs, p.rhs) for pw in side.atoms(sp.Pow) if isinstance(pw.base, sp.Symbol)]
    for pw in sym_pows:
        b, e = pw.base, pw.exp
        if e.has(sp.oo, -sp.oo, sp.zoo):
            return f"{b}^oo is not a power"
        if e.has(sp.I):
            return f"{b} raised to an imaginary exponent; the superscript (often i) is probably an index"
        if _UPPER.match(b.name) and (e == -1 or (isinstance(e, sp.Symbol) and _UPPER.match(e.name))):
            return (f"{b}^{e} on an uppercase letter reads as an operator/matrix inverse" if e == -1
                    else f"{b}^{e} (an uppercase letter on an uppercase letter) reads as a label")
    pows = [pw for pw in sym_pows if not pw.exp.is_number]
    for pw in pows:
        parts = _label_parts(pw.exp)
        if parts and abs(parts[0]) == 1 and len(parts[1]) > 1 and parts[1] <= free:
            return f"the multi-letter superscript in {pw.base}^{{{pw.exp}}} reads as a label"
    if not pows:
        return None
    stripped = [side.replace(lambda e: isinstance(e, sp.Pow) and isinstance(e.base, sp.Symbol)
                             and not e.exp.is_number, lambda e: e.base) for side in (p.lhs, p.rhs)]
    outside = set().union(*(s.free_symbols for s in stripped))
    for pw in pows:
        for s in pw.exp.free_symbols:
            if s in outside or s not in free:
                continue
            uses = [q for q in pows if s in q.exp.free_symbols]
            parts = [_label_parts(q.exp) for q in uses]
            if any(pt is None for pt in parts):
                continue  # s takes part in arithmetic (a+1, ...): a genuine exponent
            # c*s is allowed only as the merge of repeated labels (J^k J^k -> J^{2k}): the same base
            # must also carry the bare label
            bare = {(q.base, pt[1]) for q, pt in zip(uses, parts) if abs(pt[0]) == 1}
            if all(abs(pt[0]) == 1 or (q.base, pt[1]) in bare for q, pt in zip(uses, parts)):
                return f"{s} occurs only as the superscript of {pw.base}, so {pw.base}^{s} is probably a label"
    return None
