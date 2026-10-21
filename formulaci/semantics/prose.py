"""Prose and condition parsing for the semantics stage.

Turns plain-text context (and trailing LaTeX conditions such as `\\quad x > 0`) into
facts about the formula's free symbols: comparisons ("x > 0", "0 <= k <= n", "|x| < 1"),
type statements ("n is a positive integer", "for all real x", "z in C") and enumerations
("n = 0, 1, 2, ..."). Everything is regex based and deterministic.
"""
from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field

import sympy

UNICODE_GREEK = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "ϵ": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ϑ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "π": "pi", "ρ": "rho", "σ": "sigma",
    "τ": "tau", "υ": "upsilon", "φ": "phi", "ϕ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda", "Ξ": "Xi", "Π": "Pi",
    "Σ": "Sigma", "Φ": "Phi", "Ψ": "Psi", "Ω": "Omega",
}
GREEK_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta",
    "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "varpi", "rho",
    "varrho", "sigma", "varsigma", "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega",
]
VAR_VARIANTS = {"varphi": "phi", "vartheta": "theta", "varepsilon": "epsilon", "varrho": "rho",
                "varsigma": "sigma", "lamda": "lambda"}   # varpi is the lemniscate constant, not pi


def sym_key(name: str) -> str:
    """Canonical key for a symbol name: `\\varphi_{1}` -> `phi_1`, `θ` -> `theta`."""
    s = name.strip()
    for u, g in UNICODE_GREEK.items():
        s = s.replace(u, g)
    s = re.sub(r"\\(?:mathrm|text|mathit|operatorname|textrm|rm)\s*", "", s)
    s = s.replace("\\", "").replace("{", "").replace("}", "").replace(" ", "")
    head, sep, tail = s.partition("_")
    head = VAR_VARIANTS.get(head, head)
    return head + (sep + tail if sep else "")


def base_letter(name: str) -> str:
    """The letter a symbol is named after: `x_1` -> `x`, `phi'` -> `phi`."""
    return sym_key(name).split("_")[0].rstrip("'").rstrip("′")


# --------------------------------------------------------------------------- normalization

_SET_WORDS = {"R": "REALS", "C": "COMPLEXES", "Z": "INTEGERS", "N": "NATURALS", "Q": "RATIONALS"}


def normalize_text(t: str) -> str:
    """Map LaTeX/Unicode/wiki prose to a small ASCII vocabulary the extractors understand."""
    if not t:
        return ""
    t = t.replace("−", "-").replace("\u2009", " ").replace("\xa0", " ").replace("…", " ... ")
    t = t.replace("’", "'").replace("$", " ")   # extract marks neighbouring formulas as $latex$
    for u, g in UNICODE_GREEK.items():
        t = t.replace(u, f" {g} ")
    # real / imaginary parts
    t = re.sub(r"(?:\\operatorname\s*\{\s*Re\s*\}|\\mathrm\s*\{\s*Re\s*\}|\\text\s*\{\s*Re\s*\}|\\Re(?![a-zA-Z])|ℜ|(?<![A-Za-z])Re(?=\s*[({]))"
               r"\s*(?:\\left)?\s*[({]?\s*([A-Za-z\\][A-Za-z_{}0-9\\]*)\s*(?:\\right)?\s*[)}]?",
               lambda m: f" re({sym_key(m.group(1))}) ", t)
    t = re.sub(r"(?:\\operatorname\s*\{\s*Im\s*\}|\\mathrm\s*\{\s*Im\s*\}|\\Im(?![a-zA-Z])|ℑ|(?<![A-Za-z])Im(?=\s*[({]))"
               r"\s*(?:\\left)?\s*[({]?\s*([A-Za-z\\][A-Za-z_{}0-9\\]*)\s*(?:\\right)?\s*[)}]?",
               lambda m: f" im({sym_key(m.group(1))}) ", t)
    # comparison operators
    t = re.sub(r"\\(?:leqslant|leq|le)(?![a-zA-Z])|≤|⩽", " <= ", t)
    t = re.sub(r"\\(?:geqslant|geq|ge)(?![a-zA-Z])|≥|⩾", " >= ", t)
    t = re.sub(r"\\(?:neq|ne)(?![a-zA-Z])|≠", " != ", t)
    t = re.sub(r"\\lt(?![a-zA-Z])", " < ", t)
    t = re.sub(r"\\gt(?![a-zA-Z])", " > ", t)
    t = re.sub(r"\\not\s*\\in(?![a-zA-Z])|\\notin(?![a-zA-Z])|∉", " notin ", t)
    t = re.sub(r"\\in(?![a-zA-Z])|∈", " in ", t)
    # number sets
    t = re.sub(r"\\mathbb\s*\{?\s*([RCZNQ])\s*\}?", lambda m: f" {_SET_WORDS[m.group(1)]} ", t)
    t = re.sub(r"\\(R|C|Z|N|Q)(?![A-Za-z])", lambda m: f" {_SET_WORDS[m.group(1)]} ", t)
    t = re.sub(r"\\(Reals|Complexes|Integers|Naturals|Rationals)(?![A-Za-z])",
               lambda m: f" {m.group(1).upper()} ", t)
    for u, w in {"ℝ": "REALS", "ℂ": "COMPLEXES", "ℤ": "INTEGERS", "ℕ": "NATURALS", "ℚ": "RATIONALS"}.items():
        t = t.replace(u, f" {w} ")
    t = re.sub(r"REALS\s*(?:_\s*\{?\s*>\s*0\s*\}?|\^\s*\{?\s*\+\s*\}?|_\s*\{?\s*\+\s*\}?)", "POSREALS", t)
    t = re.sub(r"REALS\s*_\s*\{?\s*>=\s*0\s*\}?", "NONNEGREALS", t)
    t = re.sub(r"INTEGERS\s*(?:_\s*\{?\s*>\s*0\s*\}?|\^\s*\{?\s*\+\s*\}?|_\s*\{?\s*\+\s*\}?)", "POSINTEGERS", t)
    t = re.sub(r"INTEGERS\s*_\s*\{?\s*>=\s*0\s*\}?", "NONNEGINTEGERS", t)
    t = re.sub(r"NATURALS\s*_\s*\{?\s*0\s*\}?", "NONNEGINTEGERS", t)
    t = re.sub(r"NATURALS\s*_\s*\{?\s*(?:>\s*0|1|\+)\s*\}?", "POSINTEGERS", t)
    # layout commands
    t = re.sub(r"\\(?:left|right|bigl|bigr|Bigl|Bigr|biggl|biggr|big|Big|bigg|Bigg)(?![a-zA-Z])", "", t)
    t = re.sub(r"\\(?:lvert|rvert|vert)(?![a-zA-Z])", "|", t)
    t = re.sub(r"\\(?:qquad|quad|displaystyle|textstyle|scriptstyle)(?![a-zA-Z])|\\[,;:! ]|~", " ", t)
    t = re.sub(r"\\(?:text|mathrm|mbox|textrm|operatorname|mathit|textit|rm)\s*\{([^{}]*)\}", r" \1 ", t)
    for _ in range(3):
        t = re.sub(r"\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)", t)
    t = re.sub(r"\\[dt]?frac\s*(\d)\s*(\d)", r"(\1)/(\2)", t)
    t = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", t)
    t = re.sub(r"\\(?:cdot|times)(?![a-zA-Z])", "*", t)
    t = re.sub(r"\\infty(?![a-zA-Z])|∞", " oo ", t)
    t = re.sub(r"\\(?:ldots|cdots|dots|dotsb|dotsc)(?![a-zA-Z])", " ... ", t)
    t = re.sub(r"\\(" + "|".join(GREEK_NAMES) + r")(?![a-zA-Z])", lambda m: f" {VAR_VARIANTS.get(m.group(1), m.group(1))} ", t)
    t = re.sub(r"(?<![A-Za-z])var(phi|theta|epsilon|rho|sigma)(?![A-Za-z])", r"\1", t)
    t = re.sub(r"_\s*\{\s*([A-Za-z0-9]+)\s*\}", r"_\1", t)
    t = t.replace("{", " ").replace("}", " ")
    t = re.sub(r"\\([A-Za-z]+)", r" \1 ", t)
    t = re.sub(r"[ \t\r\n]+", " ", t)
    return t.strip()


# --------------------------------------------------------------------------- facts


@dataclass
class Fact:
    """One statement about a symbol (or a free-standing constraint) found in text."""
    kind: str                 # "type" | "bound" | "constraint"
    rule: str                 # stable rule id
    sym: str | None           # formula symbol name, or None for multi-symbol constraints
    value: str = ""           # type name (for kind=type) / relation text
    rel: object = None        # sympy relational for bounds/constraints
    local: bool = True        # found in the formula itself or right next to it
    source: str = ""          # "tail" | "notes" | "context"
    evidence: str = ""        # the matched text
    same_sentence: bool = True  # no sentence break between the match and the formula
    foreign: bool = False     # the phrase also names symbols the formula does not have


@dataclass
class SymbolForms:
    """Prose spellings of the formula's free symbols."""
    by_form: dict[str, str] = field(default_factory=dict)   # prose form -> formula symbol name

    @classmethod
    def build(cls, names):
        sf = cls()
        for n in names:
            k = sym_key(n)
            forms = {k, n}
            head, _, tail = k.partition("_")
            if tail and len(head) == 1 and tail.isalnum():
                forms.add(head + tail)          # wiki "x1" for x_1
            for f in forms:
                if f and re.fullmatch(r"[A-Za-z][A-Za-z0-9_']*", f):
                    sf.by_form.setdefault(f, n)
        return sf

    def regex(self):
        if not self.by_form:
            return None
        alts = sorted(self.by_form, key=len, reverse=True)
        return r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(a) for a in alts) + r")(?![A-Za-z0-9_(])"


# Patterns use a generic identifier and matches are filtered against the formula's symbols
# afterwards, so every regex is compiled once rather than once per symbol set.
GENERIC_SYM = r"(?<![A-Za-z0-9_\\])[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)?'?(?![A-Za-z0-9_(])"
_rc = functools.lru_cache(maxsize=None)(re.compile)
_CONNECTORS = {"and", "or", "all", "any", "every", "each", "the", "for", "with", "both", "some", "a", "an", "fixed", "distinct"}

_NUM = r"(?:\d+(?:\.\d+)?|\(\s*-?\d+(?:\.\d+)?\s*\)\s*/\s*\(\s*\d+(?:\.\d+)?\s*\)|pi|oo)"
_OP = r"(?:<=|>=|!=|<|>)"
_OPEQ = r"(?:<=|>=|!=|<|>|(?<![<>!=])=(?!=))"

TYPE_WORDS = [
    (r"positive\s+integers?|positive\s+whole\s+numbers?|natural\s+numbers?|counting\s+numbers?|POSINTEGERS|NATURALS", "positive_integer"),
    (r"non-?\s?negative\s+integers?|nonnegative\s+integers?|non-?\s?negative\s+whole\s+numbers?|NONNEGINTEGERS", "nonneg_integer"),
    (r"negative\s+integers?", "negative_integer"),
    (r"odd\s+integers?|odd\s+numbers?", "odd"),
    (r"even\s+integers?|even\s+numbers?", "even"),
    (r"prime\s+numbers?|primes?", "prime"),
    (r"integers?|whole\s+numbers?|INTEGERS", "integer"),
    (r"positive\s+real\s+numbers?|positive\s+reals?|positive\s+numbers?|POSREALS", "positive"),
    (r"non-?\s?negative\s+real\s+numbers?|non-?\s?negative\s+reals?|non-?\s?negative\s+numbers?|NONNEGREALS", "nonneg"),
    (r"real\s+numbers?|real\s+values?|reals?|REALS", "real"),
    (r"complex\s+numbers?|complex\s+values?|complex|COMPLEXES", "complex"),
]
# adjectives that bound a symbol without fixing its number system
ADJ_WORDS = [
    (r"strictly\s+positive|positive", "positive"),
    (r"non-?\s?negative|nonnegative", "nonneg"),
    (r"negative", "negative"),
    (r"non-?\s?zero|nonzero", "nonzero"),
    (r"odd", "odd"),
    (r"even", "even"),
    (r"prime", "prime"),
]
TYPE_FACTS = {"positive_integer", "nonneg_integer", "negative_integer", "integer", "real", "complex", "prime", "odd", "even"}


def _type_alt(words, prefix):
    return "(?:" + "|".join(f"(?P<{prefix}{i}>{w})" for i, (w, _) in enumerate(words)) + ")"


def _which(m, words, prefix):
    for i, (_, name) in enumerate(words):
        if m.groupdict().get(f"{prefix}{i}"):
            return name
    return None


def _parse_side(s: str, forms: SymbolForms):
    # Prose is untrusted page text: parse with the strict arithmetic grammar, never parse_expr/sympify.
    from formulaci.safeload import parse_simple_expr
    local = {f: sympy.Symbol(n) for f, n in forms.by_form.items()}
    e = parse_simple_expr(s.strip(), local)
    if e is None or not e.free_symbols <= set(local.values()):
        return None
    return e


_RELS = {"<": sympy.StrictLessThan, "<=": sympy.LessThan, ">": sympy.StrictGreaterThan, ">=": sympy.GreaterThan, "!=": sympy.Ne}


def extract_facts(text: str, forms: SymbolForms, *, source: str, local_span=None) -> list[Fact]:
    """Extract facts from one normalized text block.

    `local_span` = (start, end) character range counted as "local" (adjacent to the formula);
    None means the whole text is local (formula tail / translator notes).
    """
    facts: list[Fact] = []
    if not forms.by_form or not text:
        return facts
    symre = GENERIC_SYM

    def is_local(m):
        if local_span is None:
            return True
        return m.end() >= local_span[0] and m.start() <= local_span[1]

    anchor = text.find("\u00b6") if local_span is not None else -1

    def same_sentence(m):
        if anchor < 0:
            return True
        seg = text[anchor:m.start()] if m.start() > anchor else text[m.end():anchor]
        return not re.search(r"[.!?]\s+[A-Z]", seg)

    def foreign(listtext):
        return any(f not in forms.by_form and f.lower() not in _CONNECTORS for f in _rc(symre).findall(listtext))

    sym_list = rf"(?P<list>{symre}(?:\s*,\s*{symre})*(?:\s*,?\s*(?:and|or)\s+{symre})?)"

    def names_in(listtext):
        return [forms.by_form[f] for f in _rc(symre).findall(listtext) if f in forms.by_form]

    # --- comparisons -----------------------------------------------------------------
    atom0 = rf"(?:{_NUM}\s*(?:{symre}|pi)|{_NUM}|{symre})"
    expr0 = rf"-?\s*{atom0}(?:\s*[-+*/^]\s*{atom0})*"
    atom = rf"(?:\|\s*{expr0}\s*\||re\(\s*{symre}\s*\)|im\(\s*{symre}\s*\)|\(\s*{expr0}\s*\)(?:\s*/\s*\(\s*{expr0}\s*\))?|{atom0})"
    expr = rf"-?\s*{atom}(?:\s*[-+*/^]\s*{atom})*"
    chain = _rc(rf"(?<![\w^\\*/+\-.])(?P<first>{expr}|{symre}(?:\s*,\s*{symre})+)(?P<rest>(?:\s*{_OPEQ}\s*{expr})+)")
    # "Re(s) = sigma > 1": drop the alias so the bound attaches to the formula's own quantity
    ctext = re.sub(rf"((?:re|im)\(\s*{symre}\s*\)|{symre})\s*=\s*[A-Za-z]\w*\s*(?=<=|>=|<|>)", r"\1 ", text)
    for m in chain.finditer(ctext):
        # "0 < p < 1 and positive integers n": the expression grammar reads "1 and" as 1*and; drop the connector
        mtext = re.sub(r"\s+(?:and|or|if|for|with|where|when|then|while|whenever|so|but)\s*$", "", m.group(0), flags=re.I)
        parts = re.split(rf"\s*({_OPEQ})\s*", mtext)
        sides, ops = parts[0::2], parts[1::2]
        if all(o == "=" for o in ops):
            continue
        # "Re(s) = sigma > 1": an equality inside a chain lets its left side inherit the bound
        while "=" in ops:
            k = ops.index("=")
            if k + 1 < len(ops):
                del sides[k + 1], ops[k]
            else:
                del sides[k + 1], ops[k]
        first_names = None
        if "," in sides[0] and len(ops) == 1:
            first_names = names_in(sides[0])
        for i, op in enumerate(ops):
            if i == 0 and first_names:
                rhs = _parse_side(sides[1], forms)
                if rhs is None:
                    continue
                if not rhs.is_real and rhs.is_real is not None or rhs.has(sympy.I):
                    continue
                for n in first_names:
                    rel = _RELS[op](sympy.Symbol(n), rhs)
                    facts.append(Fact("bound", "P.compare", n, op, rel, is_local(m), source, m.group(0)))
                continue
            a, b = _parse_side(sides[i], forms), _parse_side(sides[i + 1], forms)
            if a is None or b is None or not (a.free_symbols | b.free_symbols):
                continue
            if not (_simple(a) or _simple(b)):
                continue   # prose arithmetic like "|6x^4 - 2x^3| <= 6x^4 + ...", not a condition
            try:
                rel = _RELS[op](a, b)
            except (TypeError, ValueError):   # e.g. prose "E + I > 0": not a real comparison
                continue
            if rel in (sympy.true, sympy.false):
                continue
            syms = (a.free_symbols | b.free_symbols)
            sym = next(iter(syms)).name if len(syms) == 1 else None
            facts.append(Fact("bound", "P.compare", sym, op, rel, is_local(m), source, m.group(0)))

    # --- set membership: "x in REALS", "z notin INTEGERS", "x in (0,1)" -----------------
    sets = {"POSINTEGERS": "positive_integer", "NATURALS": "positive_integer", "NONNEGINTEGERS": "nonneg_integer",
            "INTEGERS": "integer", "POSREALS": "positive", "NONNEGREALS": "nonneg", "REALS": "real",
            "COMPLEXES": "complex"}
    memb = _rc(rf"{sym_list}\s+(?P<neg>in|notin)\s+(?P<set>POSINTEGERS|NONNEGINTEGERS|NATURALS|INTEGERS|POSREALS|NONNEGREALS|REALS|COMPLEXES|RATIONALS)(?![A-Za-z])")
    for m in memb.finditer(text):
        for n in names_in(m.group("list")):
            if m.group("neg") == "in":
                if m.group("set") == "RATIONALS":
                    continue
                facts.append(Fact("type", "P.member", n, sets[m.group("set")], None, is_local(m), source, m.group(0)))
            elif m.group("set") == "INTEGERS":
                facts.append(Fact("constraint", "P.not_member", n, "not_integer",
                                  sympy.Ne(sympy.Symbol(n), sympy.floor(sympy.re(sympy.Symbol(n)))), is_local(m), source, m.group(0)))
    interval = _rc(rf"{sym_list}\s+in\s+(?P<lb>[\[(])\s*(?P<a>-?{_NUM})\s*,\s*(?P<b>-?{_NUM})\s*(?P<rb>[\])])")
    for m in interval.finditer(text):
        a, b = _parse_side(m.group("a"), forms), _parse_side(m.group("b"), forms)
        if a is None or b is None:
            continue
        for n in names_in(m.group("list")):
            s = sympy.Symbol(n)
            lo = (sympy.StrictGreaterThan if m.group("lb") == "(" else sympy.GreaterThan)(s, a)
            hi = (sympy.StrictLessThan if m.group("rb") == ")" else sympy.LessThan)(s, b)
            facts.append(Fact("type", "P.interval", n, "real", None, is_local(m), source, m.group(0)))
            facts.append(Fact("bound", "P.interval", n, "", lo, is_local(m), source, m.group(0)))
            facts.append(Fact("bound", "P.interval", n, "", hi, is_local(m), source, m.group(0)))

    # --- type phrases ---------------------------------------------------------------------
    tw = _type_alt(TYPE_WORDS, "t")
    aw = _type_alt(ADJ_WORDS, "a")
    quant = r"(?:for|with|where|if|and|of|over|valid|holds)\s+(?:(?:all|any|every|each|arbitrary|some|a|an|fixed|distinct|two|the)\s+)*"
    # "for every positive integer n", "for all complex numbers alpha and X", "for any non-zero real x, y, z"
    p1 = _rc(rf"(?i:{quant})(?P<nz>(?i:non-?\s?zero\s+))?{tw}\s+{sym_list}")
    for m in p1.finditer(text):
        t = _which(m, TYPE_WORDS, "t")
        for n in names_in(m.group("list")):
            facts.append(Fact("type", "P.type_phrase", n, t, None, is_local(m), source, m.group(0)))
            if m.group("nz"):
                facts.append(Fact("bound", "P.type_phrase", n, "!=", sympy.Ne(sympy.Symbol(n), 0), is_local(m), source, m.group(0)))
    # "n is a positive integer", "x and y are real numbers", "b, x and y are all positive"
    lead = r"(?:^|[,;.:(\u00b6]\s*|\b(?:where|and|if|when|that|with|whenever|since|for|let|then|so|as|while|both)\s+)"
    p2 = _rc(rf"{lead}{sym_list}\s+(?:is|are|be|being)\s+(?:all\s+|both\s+|each\s+)?(?:an?\s+|any\s+)?(?:(?P<tw>{tw})|(?P<aw>{aw}))(?![A-Za-z])")
    for m in p2.finditer(text):
        if m.group("tw"):
            t, kind = _which(m, TYPE_WORDS, "t"), "type"
        else:
            t = _which(m, ADJ_WORDS, "a")
            if t is not None and t != "prime":
                # "x is positive real" style is covered by tw; a bare adjective is a bound
                kind = "adj"
            else:
                kind = "type"
        for n in names_in(m.group("list")):
            facts.extend(_adj_or_type(kind, t, n, is_local(m), source, m.group(0)))
    # "for positive x", "with x and y positive", "where p is prime"
    p3 = _rc(rf"(?i:(?:for|with|where|and)\s+(?:all\s+|any\s+|every\s+)?){aw}\s+{sym_list}")
    for m in p3.finditer(text):
        t = _which(m, ADJ_WORDS, "a")
        for n in names_in(m.group("list")):
            facts.extend(_adj_or_type("adj" if t != "prime" else "type", t, n, is_local(m), source, m.group(0)))
    p4 = _rc(rf"(?i:(?:for|with|where)\s+){sym_list}\s+(?:both\s+|all\s+)?{aw}(?![A-Za-z])")
    for m in p4.finditer(text):
        t = _which(m, ADJ_WORDS, "a")
        for n in names_in(m.group("list")):
            facts.extend(_adj_or_type("adj" if t != "prime" else "type", t, n, is_local(m), source, m.group(0)))
    # "n = 0, 1, 2, ..." / "n = 1, 2, 3, ..."  (handled below, then sentence/foreign tagging)
    p5 = _rc(rf"{sym_list}\s*=\s*(?P<s>0|1)\s*,\s*(?:1|2)\s*,\s*(?:2|3)\s*,?\s*(?:\.\.\.|etc)")
    for m in p5.finditer(text):
        t = "nonneg_integer" if m.group("s") == "0" else "positive_integer"
        for n in names_in(m.group("list")):
            facts.append(Fact("type", "P.enumeration", n, t, None, is_local(m), source, m.group(0)))
    for f in facts:
        pos = text.find(f.evidence)
        if pos >= 0 and anchor >= 0:
            seg = text[anchor:pos] if pos > anchor else text[pos + len(f.evidence):anchor]
            f.same_sentence = not re.search(r"[.!?]\s+[A-Z]", seg)
        if f.kind == "type":
            f.foreign = foreign(_list_part(f.evidence))
    return facts


def _list_part(evidence: str) -> str:
    """The symbol-list part of a type phrase (words after the type word / before 'is|are')."""
    m = re.search(r"\b(?:is|are|be|being|in|notin)\b", evidence)
    if m:
        return evidence[:m.start()]
    words = re.split(r"\b(?:integers?|numbers?|reals?|real|complex|values?|primes?|naturals?|positive|negative|non-?\s?negative|NATURALS|INTEGERS|REALS|COMPLEXES|POSINTEGERS|NONNEGINTEGERS|POSREALS|NONNEGREALS)\b", evidence)
    return words[-1] if words else evidence


def _simple(e) -> bool:
    """A bare symbol, |symbol|, re(symbol) or im(symbol)."""
    if isinstance(e, sympy.Symbol):
        return True
    return isinstance(e, (sympy.Abs, sympy.re, sympy.im)) and isinstance(e.args[0], sympy.Symbol)


def _adj_or_type(kind, t, n, local, source, ev):
    s = sympy.Symbol(n)
    if t is None:
        return []
    if kind == "type" or t in ("prime",):
        return [Fact("type", "P.type_phrase", n, t, None, local, source, ev)]
    if t == "positive":
        return [Fact("bound", "P.adjective", n, ">", sympy.StrictGreaterThan(s, 0), local, source, ev)]
    if t == "nonneg":
        return [Fact("bound", "P.adjective", n, ">=", sympy.GreaterThan(s, 0), local, source, ev)]
    if t == "negative":
        return [Fact("bound", "P.adjective", n, "<", sympy.StrictLessThan(s, 0), local, source, ev)]
    if t == "nonzero":
        return [Fact("bound", "P.adjective", n, "!=", sympy.Ne(s, 0), local, source, ev)]
    if t in ("odd", "even"):
        return [Fact("type", "P.type_phrase", n, t, None, local, source, ev)]
    return []


# --------------------------------------------------------------------------- formula tails

_TAIL = re.compile(r"\\q?quad(?![a-zA-Z])|\\text\s*\{\s*(?:for|if|when|where|provided|valid|as)\b|\\mbox\s*\{\s*(?:for|if|when|where)\b"
                   r"|\\(?:mathrm|textrm)\s*\{\s*(?:for|if)\b|,\s*\\\s+(?=\\q?quad|\\text)")


def split_tail(latex: str) -> tuple[str, str]:
    """Split `main \\quad condition` at brace depth 0. Returns (main, tail)."""
    depth = 0
    i = 0
    while i < len(latex):
        c = latex[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0 and c in "\\,":
            m = _TAIL.match(latex, i)
            if m:
                return latex[:i], latex[i:]
        i += 1
    return latex, ""


def notes_conditions(notes: str | None) -> list[str]:
    """`cond: <latex>` entries from the translator's notes."""
    if not notes:
        return []
    out = []
    for m in re.finditer(r"cond:\s*(.+?)(?=\s*(?:;|\n|\|)\s*[a-z_]+:|$)", notes, flags=re.S):
        out.append(m.group(1).strip().rstrip(";"))
    return out
