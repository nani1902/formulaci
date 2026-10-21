"""Second-pass checkability rules, driven by review of real FAILs (data/findings/reviews.jsonl).

Each function looks at the page title, section, the prose around the formula and the LaTeX,
and returns the matched evidence (a short string) or None. They only ever *skip* formulas or add
hints, so they cannot create FAILs; their cost is recall, measured on the fixtures.
"""
from __future__ import annotations

import re

# --------------------------------------------------------------------------- special algebra
# The arithmetic is not ordinary: finite fields, modular rings, ordinals/cardinals, quaternions,
# semigroups, Boolean/tropical algebra, other bases, floating point.
SPECIAL_ALGEBRA = re.compile(
    r"\bmodulo\b|\bmod\s+\d|\\pmod|\\bmod|characteristic\s*(?:2|p|two|\$?\s*p\s*\$?)\b|finite fields?|galois fields?"
    r"|(?-i:\bGF\s*\()|\\mathrm\s*\{\s*GF\s*\}|\\mathbb\s*\{?\s*F\s*\}?\s*_|(?-i:\bF_(?:2|q|p)\b)|\\mathbb\s*\{?\s*Z\s*\}?\s*/|(?-i:\bZ\s*/\s*\d+\s*Z\b)|ℤ\s*/"
    r"|\bordinals?\b|\bcardinals?\b|cardinality of the continuum|\\aleph|ℵ|\baleph\b|transfinite"
    r"|\b(?:bi)?quaternions?\b|split-complex|dual numbers?|hypercomplex|\bversors?\b"
    r"|\bsemigroups?\b|\bmonoids?\b|\bidempotent\b|\bboolean\b|\btropical\b|max-plus|min-plus"
    r"|duodecimal|dozenal|binary (?:addition|arithmetic|numbers?|numerals?|system|representation|digits?)|\bbase[- ](?:2|12|two|twelve|8|16)\b"
    r"|floating[- ]point|dirac matri|non-diophantine|trivial ring|coxeter group|\bwheel theory"
    r"|square roots? of minus one|vector algebra of (?:william rowan )?hamilton",
    re.I)


def special_algebra(title: str, section: str, before: str, after: str, latex: str) -> str | None:
    for where, text in (("title", title), ("section", section), ("context", before[-400:] + " " + after[:400]), ("latex", latex)):
        m = SPECIAL_ALGEBRA.search(text or "")
        if m:
            return f"{where}: {m.group(0)!r}"
    return None


# --------------------------------------------------------------------------- stated false
STATED_FALSE = re.compile(
    r"\bis false\b|which is false|a false (?:statement|equation)|\bincorrect(?:ly)?\b|\bnot true\b|\bcontradiction\b"
    r"|\bno solutions?\b|there is no \$?\s*\w+\s*\$?\s*such that|cannot be justified|cannot (?:hold|be true)|\bcounterexamples?\b"
    r"|\bfallac(?:y|ies|ious)\b|\bcranks?\b|\bpurported(?:ly)?\b|\berroneous(?:ly)?\b|pseudomath|invalid proof"
    r"|faulty|\bwrongly\b|redefinition of",
    re.I)
# phrases that only point forward, so they only count before the formula
STATED_FALSE_BEFORE = re.compile(r"if one would have|instead of simply|\bclaimed that\b|there is no \$?\s*\w+\s*\$?\s*such that", re.I)


def stated_false(before: str, after: str) -> str | None:
    m = STATED_FALSE.search(before[-200:]) or STATED_FALSE_BEFORE.search(before[-120:]) or STATED_FALSE.search(after[:150])
    return repr(m.group(0)) if m else None


# --------------------------------------------------------------------------- defining equations
# Prose immediately before the formula that introduces an equation to solve or a definition.
DEFINING_BEFORE = re.compile(
    r"(?<!functional )(?<!differential )\b(?:the|this|an|following|implicit|transcendental|nonlinear) equation\b(?! of)"
    r"|equations? below|gives the equation|left with the equation|\bsolv(?:e|es|ed|ing)\b|\bsolutions?\b|\broots? of\b|\bunknowns?\b"
    r"|\bdetermined by\b|\bsatisfying\W*$|\bsuch that\W*$|\bconditions?\b|\bboundary\b|\bimplicit\b|holds(?: true)? only when|only holds|\bwriting\b"
    r"|\bfor which\b|\bfixed[- ]point\b",
    re.I)
DERIVATION_CUE = re.compile(r"\bfollows?\b|\bfollow from\b|\bproof\b|\bderiv|\bobeys?\b|\bsatisfies\b|\bfulfil+s\b", re.I)
CANCELS_CUE = re.compile(r"\bthen\b|\bwe have\b|\bone has\b|\bwe get\b|\bwe obtain\b|\bit follows\b|\bimplies\b"
                         r"|can be written|is given by|as follows|\bidentity\b", re.I)
DEFINING_AFTER = re.compile(
    r"^\W{0,4}(?:if|when|for which)\b|\bsolv(?:e|es|ed|ing)\b|\bthe solution\b|\bunknowns?\b|\bnonlinear equation\b|\bimplicit\b"
    r"|\bmust lie\b|\blies on\b|\bby definition\b|\b(?:real )?roots? (?:is|are)\b",
    re.I)


def defining_cue(before: str, after: str, forms: list[str] = ()) -> str | None:
    tail = before[-80:]
    if DERIVATION_CUE.search(tail):
        tail = ""         # "the formula follows by solving for ...": a derived identity
    for m in DEFINING_BEFORE.finditer(tail):
        rest = tail[m.end():]
        if CANCELS_CUE.search(rest):
            continue          # "if a, b > 0 then log(ab) = ..." introduces an identity
        return f"before: {m.group(0)!r}"
    head = after[:150]
    m = DEFINING_AFTER.search(head)
    first_sentence = re.split(r"[.;]\s", head[m.end():], maxsplit=1)[0] if m else ""
    if m and m.group(0).strip(" ,.;:").lower() in ("if", "when", "for which"):
        if CANCELS_CUE.search(first_sentence):
            return None   # "If m is not an integer then ...": a remark, not the formula's condition
        clause = head[m.end():m.end() + 25]
        if not any(re.search(r"(?<![A-Za-z])\\?" + re.escape(f) + r"(?![A-Za-z])", clause) for f in forms):
            return None   # "If the real part is ...": about something else; "if σ is odd" names the formula's symbol
    return f"after: {m.group(0)!r}" if m else None


UNIVERSAL_CUE = re.compile(r"\bfor (?:all|every|any|each)\b|\balways\b|\bholds for\b|\bfor arbitrary\b", re.I)


def universal_cue(before: str, after: str) -> bool:
    return bool(UNIVERSAL_CUE.search(before[-80:]) or UNIVERSAL_CUE.search(after[:60]))


APPROX_CUE = re.compile(r"\\approx|≈|\btaking\b|\bapproximat(?:e|ely|ion|ions)\b|\babout\b|\broughly\b|\brounded\b|\brounding\b|\bestimat(?:e|ed)\b|\bnearly\b", re.I)


def approx_cue(before: str, after: str) -> str | None:
    m = APPROX_CUE.search(before[-150:]) or APPROX_CUE.search(after[:100])
    return repr(m.group(0)) if m else None


# --------------------------------------------------------------------------- non-commuting objects
NONCOMMUTING = re.compile(
    r"\bmatri(?:x|ces)\b|\boperators?\b|\blie (?:algebra|group|bracket)\b|\bpauli\b|\bhermitian\b|\bcommutators?\b|non-?commut"
    r"|\bsymplectic\b|\bbivector|\bendomorphism|\blinear (?:map|operator|transformation)s?\b|\bidentity matrix\b|\bspinors?\b",
    re.I)


def noncommuting(names: list[str], title: str, section: str, before: str, after: str) -> str | None:
    caps = [n for n in names if re.fullmatch(r"[A-Z](?:_\w+)?|sigma_\w+|gamma_\w+", n)]
    if not caps:
        return None
    if "I" in names and len(caps) >= 2:
        return "a free symbol `I` (identity) next to other capital letters"
    for text in (title, section, before[-250:] + " " + after[:200]):
        m = NONCOMMUTING.search(text or "")
        if m:
            return f"{m.group(0)!r} with symbols {caps}"
    return None


# --------------------------------------------------------------------------- named constants / parameters
def named_parameter(names: list[str], forms_of, before: str, after: str) -> str | None:
    """A free symbol the adjacent prose fixes to a value ("Define ρ = ...", "where q is eπ")."""
    text = before[-400:] + " \u00b6 " + after[:250]
    for n in names:
        for f in forms_of(n):
            sym = r"(?:\\?" + re.escape(f) + r")"
            pat = (rf"(?:\bdefine|\blet|\bwhere|\bwith|\bhere|\bset)\s+\$?\s*{sym}\s*(?:=|\\equiv|:=)\s*[^,;$]*?(?:\d|\\sqrt|\\pi|\\frac)"
                   rf"|\bwhere\s+\$?\s*{sym}\s*\$?\s+is\s+(?:e\s*π|e\^\\pi|e\^π|the\s+\w+(?:'s)?\s+constant|a\s+(?:fixed|given|certain)\b|(?:Gelfond|Euler|Catalan))"
                   rf"|\$?\s*{sym}\s*\$?\s+(?:is|are)\s+(?:certain|fixed|specific)\b")
            m = re.search(pat, text, re.I)
            if m:
                return f"{n}: {m.group(0)[:60]!r}"
    return None


NAMED_SYMBOLS = {"varpi": "the lemniscate constant ϖ is not π"}


def index_range(latex: str) -> bool:
    """`i = 1, \\ldots, n`, `i=1,2,3`: an index range, not an equation."""
    return bool(re.match(r"^\s*[A-Za-z](?:_\{?\w+\}?)?\s*=\s*-?\d+\s*,\s*(?:\\[,;! ]\s*)*(?:\\[lc]?dots|\\ldots|\.\.\.|\d)", latex.strip()))


def function_name_misread(latex: str) -> str | None:
    """`e(t) = ...`, `f(x) = ...` where the translator turned the call into a product."""
    m = re.match(r"^\s*([A-Za-z])\s*(?:\\left)?\(\s*([A-Za-z])\s*(?:\\right)?\)\s*=", latex.strip())
    return m.group(1) if m else None


def decimal_places(latex_side: str) -> int | None:
    """Number of decimal places of a bare decimal literal like `0.95` / `9.414` (None otherwise)."""
    m = re.fullmatch(r"\s*-?\d+\.(\d+)\s*(?:\\[,;!]|~|\.|,)*\s*", latex_side or "")
    return len(m.group(1)) if m else None
