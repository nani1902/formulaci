"""Rules-based semantic inference: constants, domains, constraints and checkability.

`infer(formula, parsed_pieces)` returns a `Semantics` record and a trace of the rules that
fired. Every rule has a stable id (listed in README.md) recorded in `assumptions_source`.

Design rule: precision over coverage. A domain that is too wide creates false FAILs
downstream; a domain that is too narrow only costs coverage. So when unsure we pick the
narrower safe choice, and context that *widens* a default domain is only trusted when it
sits right next to the formula.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import sympy
from sympy.core.function import AppliedUndef

from formulaci.schemas import Domain, Formula, Parsed, Semantics
from formulaci.semantics import context_rules as cr
from formulaci.semantics import prose
from formulaci.semantics.prose import base_letter

BEFORE_LOCAL = 150   # chars of context_before (normalized) that count as "adjacent"
AFTER_LOCAL = 200    # chars of context_after (normalized) that count as "adjacent"
BEFORE_NEAR = 250    # prose facts further away than this are ignored altogether
AFTER_NEAR = 300


@dataclass
class Trace:
    entries: list[tuple[str, str]] = field(default_factory=list)

    def add(self, rule: str, why: str):
        self.entries.append((rule, why))

    def ids(self) -> list[str]:
        seen, out = set(), []
        for r, why in self.entries:
            tag = r
            m = re.match(r"\[(\S+)\]", why)
            if m:
                tag = f"{r}:{m.group(1)}"
            if tag not in seen:
                seen.add(tag)
                out.append(tag)
        return out


# --------------------------------------------------------------------------- expression loading

_NS = None


def _namespace():
    global _NS
    if _NS is None:
        _NS = {k: getattr(sympy, k) for k in dir(sympy) if not k.startswith("_")}
        _NS["Token"] = lambda kind, val: str(val)   # lark-backend srepr artifacts
    return _NS


def load_expr(s: str | None):
    """Rebuild a sympy object from the translator's srepr string (or a plain sympy string)."""
    if s is None or s == "":
        return None
    try:
        with sympy.evaluate(False):   # keep the formula as written: e^{log z} must not collapse to z
            return eval(s, {"__builtins__": {}}, _namespace())  # noqa: S307 - srepr from our own pipeline
    except Exception:
        try:
            return sympy.sympify(s)
        except Exception:
            return None


# --------------------------------------------------------------------------- internal domain

@dataclass
class Dom:
    nfield: str = "real"         # "real" | "complex"
    integer: bool = False
    lo: float | None = None
    lo_strict: bool = False
    hi: float | None = None
    hi_strict: bool = False
    exclude: set = field(default_factory=set)
    angle: bool = False
    origin: str = "default"      # "default" | "prose" | "expr"

    @classmethod
    def of(cls, t: str, origin="default"):
        d = cls(origin=origin)
        if t == "complex":
            d.nfield = "complex"
        elif t in ("integer", "nonneg_integer", "positive_integer", "negative_integer", "prime", "odd", "even"):
            d.integer = True
            if t in ("nonneg_integer",):
                d.lo = 0
            if t in ("positive_integer", "prime"):
                d.lo = 1
            if t == "negative_integer":
                d.hi = -1
        elif t == "positive":
            d.lo, d.lo_strict = 0, True
        elif t == "nonneg":
            d.lo = 0
        elif t == "unit_interval":
            d.lo, d.hi = 0, 1
        elif t == "angle":
            d.angle = True
        return d

    def meet(self, o: "Dom") -> "Dom":
        d = Dom(nfield="real" if "real" in (self.nfield, o.nfield) else "complex",
                integer=self.integer or o.integer, exclude=self.exclude | o.exclude,
                angle=self.angle or o.angle, origin=o.origin)
        d.lo, d.lo_strict = self.lo, self.lo_strict
        if o.lo is not None and (d.lo is None or o.lo > d.lo or (o.lo == d.lo and o.lo_strict)):
            d.lo, d.lo_strict = o.lo, o.lo_strict
        d.hi, d.hi_strict = self.hi, self.hi_strict
        if o.hi is not None and (d.hi is None or o.hi < d.hi or (o.hi == d.hi and o.hi_strict)):
            d.hi, d.hi_strict = o.hi, o.hi_strict
        return d

    def wider_than(self, o: "Dom") -> bool:
        """True if self admits points o does not (coarse lattice comparison)."""
        if self.nfield == "complex" and o.nfield == "real":
            return True
        if o.integer and not self.integer:
            return True
        if o.lo is not None and (self.lo is None or self.lo < o.lo):
            return True
        if o.hi is not None and (self.hi is None or self.hi > o.hi):
            return True
        return False

    def to_schema(self) -> Domain:
        if self.nfield == "complex":
            return Domain(type="complex", exclude=sorted(float(x) for x in self.exclude))
        lo, hi = self.lo, self.hi
        if self.integer:
            ilo = None if lo is None else (int(sympy.floor(lo)) + 1 if self.lo_strict else int(sympy.ceiling(lo)))
            ihi = None if hi is None else (int(sympy.ceiling(hi)) - 1 if self.hi_strict else int(sympy.floor(hi)))
            if ilo is not None and ilo >= 1:
                t, implied = "positive_integer", 1
            elif ilo is not None and ilo >= 0:
                t, implied = "nonneg_integer", 0
            else:
                t, implied = "integer", None
            return Domain(type=t, lower=None if ilo in (None, implied) else float(ilo),
                          upper=None if ihi is None else float(ihi), exclude=sorted(float(x) for x in self.exclude))
        if lo is not None and hi is not None and lo == 0 and hi == 1:
            return Domain(type="unit_interval", exclude=sorted(float(x) for x in self.exclude))
        if lo is not None and (lo > 0 or (lo == 0 and self.lo_strict)):
            t, lower = "positive", (None if lo == 0 else float(lo))
        elif lo is not None and lo == 0:
            t, lower = "nonneg", None
        else:
            t, lower = ("angle" if self.angle else "real"), (None if lo is None else float(lo))
        return Domain(type=t, lower=lower, upper=None if hi is None else float(hi),
                      exclude=sorted(float(x) for x in self.exclude))

    def assumptions(self) -> dict:
        if self.nfield == "complex":
            return {}
        a = {"real": True}
        if self.integer:
            a["integer"] = True
        if self.lo is not None and (self.lo > 0 or (self.lo == 0 and self.lo_strict)):
            a["positive"] = True
        elif self.lo is not None and self.lo >= 0:
            a["nonnegative"] = True
        if self.hi is not None and (self.hi < 0 or (self.hi == 0 and self.hi_strict)):
            if "positive" in a or "nonnegative" in a:
                a.pop("positive", None), a.pop("nonnegative", None)   # contradictory prose: assume only real
            else:
                a["negative"] = True
        if 0 in self.exclude or 0.0 in self.exclude:
            a["nonzero"] = True
        return a


# --------------------------------------------------------------------------- tables

INTEGER_LETTERS = {"n", "m", "k", "j", "l", "N"}
REAL_LETTERS = {"x", "y", "t", "a", "b", "c"}
COMPLEX_LETTERS = {"z", "w", "s"}
ANGLE_LETTERS = {"theta", "phi", "alpha", "beta"}
POSITIVE_LETTERS = {"epsilon", "delta", "h"}

TRIG = (sympy.sin, sympy.cos, sympy.tan, sympy.cot, sympy.sec, sympy.csc)
NEVER_ZERO = (sympy.gamma, sympy.exp)

# undefined-function name -> (sympy function name, arity, context cue regex or None)
FUNCTION_ALIASES = {
    "Gamma": ("gamma", 1, None), "Γ": ("gamma", 1, None),
    "zeta": ("zeta", (1, 2), None), "erf": ("erf", 1, None), "erfc": ("erfc", 1, None),
    "erfi": ("erfi", 1, None), "Ei": ("Ei", 1, None), "Si": ("Si", 1, None), "Ci": ("Ci", 1, None),
    "Shi": ("Shi", 1, None), "Chi": ("Chi", 1, None), "li": ("li", 1, None),
    "B": ("beta", 2, r"beta function"), "Beta": ("beta", 2, None), "mathrm{B}": ("beta", 2, None),
    "psi": ("digamma", 1, r"digamma|polygamma"), "F": ("fibonacci", 1, r"fibonacci"),
    "L": ("lucas", 1, r"lucas number"), "H": ("harmonic", 1, r"harmonic number"),
    "W": ("LambertW", 1, r"lambert"),
}

UNITS = (r"(?:k|m|c|n|µ|μ)?m|kg|g|mg|s|ms|min|h|hr|J|kJ|MJ|eV|keV|MeV|GeV|W|kW|MW|N|kN|Pa|kPa|MPa|hPa|bar|atm|K|°C|°F|C|V|kV|mV"
         r"|A|mA|Ω|ohm|Hz|kHz|MHz|GHz|mol|L|mL|cal|kcal|T|lm|cd|Wb|ft|in|lb|lbs|psi|mph|km/h|m/s|m/s\^2|AU|ly|pc|Da|u")

OPERATOR_RULES = [
    ("K.op_congruence", r"\\pmod|\\bmod|\\mod(?![a-zA-Z])|\\equiv|\\not\\equiv|≡", "congruence"),
    ("K.op_asymptotic", r"(?<![A-Za-z\\])O\s*(?:\\left|\\bigl|\\big|\\Bigl)?\s*\(|\\mathcal\s*\{?O\}?|(?<![A-Za-z\\])o\s*\(", "operator_notation"),
    ("K.op_probability", r"\\mathbb\s*\{?\s*E\s*\}?|\\operatorname\s*\{\s*(?:E|Var|Cov|P|Pr|Corr)\s*\}|\\mathrm\s*\{\s*(?:E|Var|Cov|P)\s*\}\s*[\[(]|\\Pr(?![a-zA-Z])|(?<![A-Za-z\\])E\s*\[", "operator_notation"),
    ("K.op_nabla", r"\\nabla|\\square(?![a-zA-Z])", "operator_notation"),
    ("K.op_contour", r"\\oint|\\iint|\\iiint|\\oiint", "operator_notation"),
    ("K.op_matrix", r"\\begin\s*\{\s*[pbvBV]?matrix\s*\}|\\begin\s*\{\s*array\s*\}|\\mathbf\s*[{\\A-Za-z]|\\vec\s*[{\\A-Za-z]|\\boldsymbol|\\overrightarrow|\\bm\s*\{"
                    r"|\^\s*\{?\s*(?:\\mathsf\s*\{?\s*T\s*\}?|\\top|\\intercal|\\mathrm\s*\{\s*T\s*\})|\\det(?![a-zA-Z])|\\operatorname\s*\{\s*(?:tr|det|rank|diag)\s*\}|\\otimes|\\langle", "matrix_or_vector"),
    ("K.op_set", r"\\cup|\\cap|\\setminus|\\subset|\\subseteq|\\supset|\\supseteq|\\emptyset|\\varnothing|\\\{|\\in(?![a-zA-Z])|\\notin|∈", "set_notation"),
    ("K.op_logic", r"\\iff|\\implies|\\Rightarrow|\\Leftrightarrow|\\Longrightarrow|\\Longleftrightarrow|\\forall|\\exists|\\mapsto|\\to(?![a-zA-Z])|\\rightarrow|\\leftrightarrow", "statement_not_identity"),
    ("K.op_approx", r"\\approx|\\sim(?![a-zA-Z])|\\simeq|\\propto|\\asymp|\\cong|\\ll(?![a-zA-Z])|\\gg(?![a-zA-Z])|\\lesssim|\\gtrsim|≈|∼", "statement_not_identity"),
    ("K.op_cycle_notation", r"\(\s*\d{2,}\s*\)\s*\(\s*\d{2,}\s*\)", "operator_notation"),
    ("K.op_plusminus", r"\\pm(?![a-zA-Z])|\\mp(?![a-zA-Z])|±|∓", "plus_minus"),
]

E_CONTEXT = re.compile(r"euler'?s number|base of (?:the )?natural log|natural logarithm|natural log\b|exponential|napier|"
                       r"\be\s*(?:=|≈|\\approx)\s*2\.71|mathematical constant e\b|\\ln\s*e\b|\bln\s*e\b", re.I)
E_COUNTER = re.compile(r"eccentricit|elementary charge|electron|charge\b|\be\s+is\s+the\s+(?:charge|eccentricity)", re.I)
I_CONTEXT = re.compile(r"imaginary|complex|\bi\s*\^\s*2\s*=\s*-\s*1|square root of\s*-\s*1|sqrt\(-1\)|\\sqrt\{-1\}", re.I)
I_TITLE = re.compile(r"complex|imaginary|euler's formula|de moivre|fourier|gaussian integer|quaternion|hyperbolic function", re.I)
I_INDEX = re.compile(r"\bi\s*=\s*[01]\b|\bi-?th\b|\bfor (?:each|every|all) i\b|\bindex i\b|\bi\s*=\s*1\s*,", re.I)
J_CONTEXT = re.compile(r"imaginary unit j|j is the imaginary|\bj\s*\^\s*2\s*=\s*-\s*1|electrical engineering|phasor|impedance", re.I)
GAMMA_CONTEXT = re.compile(r"euler\s*[-–—−]?\s*mascheroni|mascheroni", re.I)
GAMMA_TITLE = re.compile(r"mascheroni|^euler's constant$", re.I)
GOLDEN_CONTEXT = re.compile(r"golden ratio|golden mean|golden section|golden number|golden field|golden rectangle", re.I)
PRIME_CONTEXT = re.compile(r"\bprimes?\b|prime numbers?", re.I)
EXISTENTIAL = re.compile(r"there (?:exists?|is|are) (?:a|an|some|infinitely|at least)|infinitely many|at least one\b|has (?:a|no) solution|"
                         r"\bsolutions? (?:of|to)\b|\bsuch that,?\s*$", re.I)
TRIG_ALL = TRIG + (sympy.asin, sympy.acos, sympy.atan)


# --------------------------------------------------------------------------- helpers

def _sides(p: Parsed):
    return load_expr(p.lhs), load_expr(p.rhs)


def _free(e):
    return set() if e is None else {s for s in e.free_symbols if isinstance(s, sympy.Symbol)}


def _undef(e):
    return set() if e is None else {f for f in e.atoms(AppliedUndef)}


def _in_trig(e, sym):
    for f in e.atoms(*TRIG_ALL):
        if sym in f.free_symbols:
            return True
    return False


def _subst_constants(e, constants: dict[str, str]):
    if e is None:
        return None
    rep = {}
    for s in e.free_symbols:
        if isinstance(s, sympy.Symbol) and s.name in constants:
            rep[s] = getattr(sympy, constants[s.name])
    for f in e.atoms(AppliedUndef):
        name = f.func.__name__
        target = getattr(sympy, constants[name], None) if name in constants else None
        if callable(target):          # function aliases only; `e(x)` must not become E(x)
            rep[f] = target(*f.args)
    if not rep:
        return e
    with sympy.evaluate(False):
        return e.xreplace(rep)


def _context(formula: Formula | None):
    if formula is None:
        return "", "", "", ""
    return formula.context_before or "", formula.context_after or "", formula.page_title or "", formula.section or ""


# --------------------------------------------------------------------------- the rules

def infer(formula: Formula | None, pieces: list[Parsed]) -> tuple[Semantics, Trace]:
    fid = pieces[0].formula_id if pieces else formula.formula_id
    tr = Trace()
    sem = Semantics(formula_id=fid)
    latex = formula.latex if formula else ""
    before, after, title, section = _context(formula)
    full_ctx = f"{title} . {section} . {before} {after}"
    main_latex, tail_latex = prose.split_tail(latex)
    if tail_latex:
        tr.add("P.tail", f"formula carries a trailing condition: {tail_latex.strip()!r}")

    exprs = [(_sides(p), p) for p in pieces]
    all_e = [e for (l, r), _ in exprs for e in (l, r) if e is not None]
    syms = set().union(*(_free(e) for e in all_e)) if all_e else set()
    if not all_e:
        syms = {sympy.Symbol(n) for p in pieces for n in p.free_symbols}
    undefs = set().union(*(_undef(e) for e in all_e)) if all_e else set()

    # ---------------------------------------------------------------- constants
    constants: dict[str, str] = {}
    names = {s.name for s in syms}
    by_key = {}
    for s in syms:
        by_key.setdefault(prose.sym_key(s.name), []).append(s)

    def sym_named(*keys):
        for k in keys:
            for s in by_key.get(k, []):
                return s
        return None

    e_sym = sym_named("e", "mathrm{e}")
    if e_sym is not None:
        # e^x, e^{-t}, e^{1/2}: strong evidence; e^2 alone is as likely a squared charge as Euler's number
        power_base = any(isinstance(p, sympy.Pow) and p.base == e_sym and not (p.exp.is_Integer and abs(p.exp) <= 4)
                         for e in all_e for p in e.atoms(sympy.Pow))
        log_arg = any(f.args and f.args[0] == e_sym for e in all_e for f in e.atoms(sympy.log))
        if power_base:
            constants[e_sym.name] = "E"
            tr.add("C.e_power_base", f"[{e_sym.name}] `e` is the base of a power, read as Euler's number")
        elif log_arg:
            constants[e_sym.name] = "E"
            tr.add("C.e_log_arg", f"[{e_sym.name}] `ln e` / `log e` appears, read as Euler's number")
        elif E_CONTEXT.search(full_ctx) and not E_COUNTER.search(before[-BEFORE_LOCAL:] + after[:AFTER_LOCAL]):
            constants[e_sym.name] = "E"
            tr.add("C.e_context", f"[{e_sym.name}] context mentions {E_CONTEXT.search(full_ctx).group(0)!r}")
        else:
            tr.add("C.e_left_variable", f"[{e_sym.name}] no evidence that `e` is Euler's number; kept as a variable")

    def in_exponent_of_e(sym):
        for e in all_e:
            for p in e.atoms(sympy.Pow):
                if (p.base == sympy.E or (e_sym is not None and p.base == e_sym)) and sym in p.exp.free_symbols:
                    return True
            for f in e.atoms(sympy.exp):
                if sym in f.args[0].free_symbols:
                    return True
        return False

    i_sym = sym_named("i", "mathrm{i}")
    if i_sym is not None:
        squared = any(isinstance(p, sympy.Pow) and p.base == i_sym and p.exp.is_Integer and p.exp % 2 == 0
                      for e in all_e for p in e.atoms(sympy.Pow))
        index_cue = bool(re.search(r"_\s*\{?\s*i\b|_\{[^}]*\bi\b", latex)) or bool(I_INDEX.search(before[-BEFORE_LOCAL:] + after[:AFTER_LOCAL]))
        ctx_cue = I_CONTEXT.search(full_ctx) or I_TITLE.search(title)
        if in_exponent_of_e(i_sym):
            constants[i_sym.name] = "I"
            tr.add("C.i_euler_exponent", f"[{i_sym.name}] `i` multiplies an exponent of e, read as the imaginary unit")
        elif squared:
            constants[i_sym.name] = "I"
            tr.add("C.i_squared", f"[{i_sym.name}] `i^2` appears, read as the imaginary unit")
        elif not index_cue and not cr.index_range(latex) and _multiplies(all_e, i_sym):
            constants[i_sym.name] = "I"
            tr.add("C.i_factor", f"[{i_sym.name}] `i` multiplies other quantities (a+bi, Si(ix), i sin x): read as the imaginary unit")
        elif ctx_cue and not index_cue and not cr.index_range(latex):
            constants[i_sym.name] = "I"
            tr.add("C.i_context", f"[{i_sym.name}] context/page mentions {ctx_cue.group(0)!r}")
        else:
            tr.add("C.i_left_variable", f"[{i_sym.name}] no imaginary-unit evidence{' (index usage seen)' if index_cue else ''}; kept as a variable")

    j_sym = sym_named("j", "mathrm{j}")
    if j_sym is not None:
        jcue = J_CONTEXT.search(full_ctx)
        if jcue or (I_CONTEXT.search(full_ctx) and i_sym is None and in_exponent_of_e(j_sym)):
            constants[j_sym.name] = "I"
            tr.add("C.j_imaginary", f"[{j_sym.name}] context marks j as the imaginary unit")

    g_sym = sym_named("gamma")
    if g_sym is not None:
        if GAMMA_CONTEXT.search(full_ctx) or GAMMA_TITLE.search(title):
            constants[g_sym.name] = "EulerGamma"
            tr.add("C.gamma_euler_mascheroni", f"[{g_sym.name}] context names the Euler–Mascheroni constant")
        else:
            tr.add("C.gamma_left_variable", f"[{g_sym.name}] no Euler–Mascheroni cue; kept as a variable")

    phi_sym = sym_named("phi")
    if phi_sym is not None:
        in_trig = any(_in_trig(e, phi_sym) for e in all_e)
        if GOLDEN_CONTEXT.search(full_ctx) and not in_trig:
            constants[phi_sym.name] = "GoldenRatio"
            tr.add("C.phi_golden_ratio", f"[{phi_sym.name}] context names the golden ratio")
        elif GOLDEN_CONTEXT.search(full_ctx):
            tr.add("C.phi_left_variable", f"[{phi_sym.name}] golden ratio mentioned but φ is an angle here; kept as a variable")

    pi_sym = sym_named("pi")
    if pi_sym is not None:
        constants[pi_sym.name] = "pi"
        tr.add("C.pi_symbol", f"[{pi_sym.name}] translator left `pi` as a symbol; mapped to pi")

    # undefined functions that are really known special functions
    for f in sorted(undefs, key=str):
        name = f.func.__name__
        alias = FUNCTION_ALIASES.get(name) or FUNCTION_ALIASES.get(prose.sym_key(name))
        if not alias:
            continue
        target, arity, cue = alias
        ok_arity = len(f.args) in (arity if isinstance(arity, tuple) else (arity,))
        if ok_arity and (cue is None or re.search(cue, full_ctx, re.I)):
            constants[name] = target
            tr.add("C.function_alias", f"[{name}] undefined function `{name}` with {len(f.args)} args read as sympy `{target}`")
        elif not ok_arity:
            tr.add("C.function_alias_rejected", f"[{name}] `{name}` has {len(f.args)} args; `{target}` takes {arity}")

    sem.constants = constants

    # substitute constants
    subst = [((_subst_constants(l, constants), _subst_constants(r, constants)), p) for (l, r), p in exprs]
    all_s = [e for (l, r), _ in subst for e in (l, r) if e is not None]
    var_syms = sorted((s for s in syms if s.name not in constants), key=lambda s: s.name)
    remaining_undef = {f.func.__name__ for e in all_s for f in e.atoms(AppliedUndef)}
    remaining_undef |= {n for p in pieces for n in p.functions if n not in constants and n not in _known_function_names()}

    # ---------------------------------------------------------------- domains: letter defaults
    doms: dict[str, Dom] = {}
    for s in var_syms:
        b = base_letter(s.name)
        in_trig = any(_in_trig(e, s) for e in all_s)
        if b == "i" and i_sym is not None and s == i_sym:
            doms[s.name] = Dom.of("nonneg_integer")
            tr.add("D.letter_integer", f"[{s.name}] `i` kept as a variable: index letter -> nonneg_integer")
        elif b in INTEGER_LETTERS:
            doms[s.name] = Dom.of("nonneg_integer")
            tr.add("D.letter_integer", f"[{s.name}] conventional index letter -> nonneg_integer")
        elif b in REAL_LETTERS:
            doms[s.name] = Dom.of("real")
            tr.add("D.letter_real", f"[{s.name}] conventional real variable -> real")
        elif b in COMPLEX_LETTERS:
            doms[s.name] = Dom.of("complex")
            tr.add("D.letter_complex", f"[{s.name}] conventional complex variable -> complex")
        elif b in ANGLE_LETTERS:
            if in_trig:
                doms[s.name] = Dom.of("angle")
                tr.add("D.letter_angle", f"[{s.name}] Greek letter used inside a trig function -> angle")
            else:
                doms[s.name] = Dom.of("real")
                tr.add("D.letter_greek_real", f"[{s.name}] Greek parameter outside trig -> real")
        elif b in POSITIVE_LETTERS:
            doms[s.name] = Dom.of("positive")
            tr.add("D.letter_positive", f"[{s.name}] small-quantity letter -> positive")
        elif b == "sigma":
            doms[s.name] = Dom.of("positive")
            tr.add("D.letter_sigma", f"[{s.name}] sigma (scale / standard deviation) -> positive")
        elif b == "r":
            doms[s.name] = Dom.of("nonneg")
            tr.add("D.letter_r", f"[{s.name}] r (radius / modulus) -> nonneg")
        elif b == "p" and PRIME_CONTEXT.search(before[-BEFORE_LOCAL:] + " " + after[:AFTER_LOCAL] + " " + tail_latex):
            doms[s.name] = Dom.of("positive_integer")
            sem.constraints.append(f"Q.prime({s.name})")
            tr.add("D.prime_p", f"[{s.name}] context says prime -> positive_integer with Q.prime({s.name})")
        else:
            doms[s.name] = Dom.of("positive")
            tr.add("D.default_positive", f"[{s.name}] no convention for `{s.name}`; safe default positive real")

    # ---------------------------------------------------------------- domains: prose & tails
    forms = prose.SymbolForms.build([s.name for s in var_syms])
    facts: list[prose.Fact] = []
    if tail_latex:
        facts += prose.extract_facts(prose.normalize_text(tail_latex), forms, source="tail")
    for c in prose.notes_conditions(pieces[0].notes if pieces else None):
        facts += prose.extract_facts(prose.normalize_text(c), forms, source="notes")
    nb, na = prose.normalize_text(before), prose.normalize_text(after)
    near_b, near_a = nb[-BEFORE_NEAR:], na[:AFTER_NEAR]
    ctx_text = f"{near_b} \u00b6 {near_a}"
    facts += prose.extract_facts(ctx_text, forms, source="context",
                                 local_span=(max(0, len(near_b) - BEFORE_LOCAL), len(near_b) + 3 + AFTER_LOCAL))

    prose_constraints: list[str] = []
    type_facts = [f for f in facts if f.kind == "type" and f.sym in doms]
    applied_type: set[str] = set()
    for f in sorted(type_facts, key=lambda f: (not f.local, f.source != "tail")):
        cur = doms[f.sym]
        new = Dom.of(f.value, origin="prose")
        if cur.origin == "default":
            if f.value == "integer" and cur.integer and f.source == "context":
                # prose "integer n" means "whole number", not "n may be negative"
                applied_type.add(f.sym)
                tr.add(f.rule, f"[{f.sym}] context says integer; kept the nonneg default ({f.evidence.strip()!r})")
                continue
            if new.wider_than(cur) and not (f.local and f.same_sentence and not f.foreign):
                why = "is not adjacent" if not f.local else ("is in another sentence" if not f.same_sentence else "also names other symbols")
                tr.add("P.widening_ignored", f"[{f.sym}] {f.value!r} would widen the default but the phrase {why}; ignored ({f.evidence.strip()!r})")
                continue
            new.angle = cur.angle and new.nfield == "real" and not new.integer
            doms[f.sym] = new
        else:
            doms[f.sym] = cur.meet(new)
        applied_type.add(f.sym)
        tr.add(f.rule, f"[{f.sym}] {f.source} says {f.value} ({f.evidence.strip()!r})")
        if f.value == "prime":
            prose_constraints.append(f"Q.prime({f.sym})")
        if f.value in ("odd", "even"):
            prose_constraints.append(f"Eq(Mod({f.sym}, 2), {1 if f.value == 'odd' else 0})")

    for f in facts:
        if f.kind == "constraint":
            if f.rel.free_symbols <= {sympy.Symbol(n) for n in doms}:
                prose_constraints.append(sympy.sstr(f.rel))
                tr.add(f.rule, f"[{f.sym}] {f.source}: {f.evidence.strip()!r} -> {sympy.sstr(f.rel)}")
            continue
        if f.kind != "bound":
            continue
        rel = f.rel
        if not rel.free_symbols <= {sympy.Symbol(n) for n in doms}:
            continue
        prose_constraints.append(sympy.sstr(rel))
        tr.add(f.rule, f"[{f.sym or ','.join(sorted(s.name for s in rel.free_symbols))}] {f.source}: {f.evidence.strip()!r} -> {sympy.sstr(rel)}")
        _apply_bound(doms, rel, f, applied_type)

    # ---------------------------------------------------------------- expression-implied domain tightening
    for e in all_s:
        for fa in e.atoms(sympy.factorial):
            a = fa.args[0]
            if isinstance(a, sympy.Symbol) and a.name in doms and doms[a.name].origin == "default" and not doms[a.name].integer:
                doms[a.name] = Dom.of("nonneg_integer", origin="expr")
                tr.add("C.factorial_domain", f"[{a.name}] argument of factorial -> nonneg_integer")
            elif not isinstance(a, sympy.Symbol):
                for s in a.free_symbols:
                    if s.name in doms and doms[s.name].origin == "default" and doms[s.name].nfield == "real" and not doms[s.name].integer:
                        doms[s.name] = Dom.of("integer", origin="expr").meet(doms[s.name])
                        tr.add("C.factorial_domain", f"[{s.name}] appears in a factorial argument -> integer")
    for e in all_s:
        for lg in e.atoms(sympy.log):
            a = lg.args[0]
            if isinstance(a, sympy.Symbol) and a.name in doms and doms[a.name].origin == "default" \
                    and doms[a.name].nfield == "real" and not doms[a.name].integer and doms[a.name].lo is None:
                doms[a.name] = Dom.of("positive", origin="expr")
                tr.add("C.log_domain", f"[{a.name}] bare argument of a real logarithm -> positive")

    for e in all_s:
        for it in e.atoms(sympy.Integral):
            if not any(len(lim) == 3 and (lim[1].has(sympy.oo, -sympy.oo) or lim[2].has(sympy.oo, -sympy.oo)) for lim in it.limits):
                continue
            for s_ in it.function.free_symbols - {lim[0] for lim in it.limits}:
                d = doms.get(s_.name)
                if d is not None and d.origin == "default" and d.nfield == "real" and d.lo is None:
                    doms[s_.name] = Dom.of("positive_integer" if d.integer else "positive", origin="expr")
                    tr.add("D.improper_integral_parameter", f"[{s_.name}] parameter of an improper integral: convergence usually needs it positive")
                elif d is not None and d.origin == "default" and d.integer and d.lo == 0:
                    doms[s_.name] = Dom.of("positive_integer", origin="expr")
                    tr.add("D.improper_integral_parameter", f"[{s_.name}] parameter of an improper integral: convergence usually needs it positive")
    sem.domains = {n: d.to_schema() for n, d in sorted(doms.items())}

    # ---------------------------------------------------------------- constraints from the expression
    assumed = {sympy.Symbol(n): sympy.Symbol(n, **d.assumptions()) for n, d in doms.items()}
    real_names = {n for n, d in doms.items() if d.nfield == "real"}

    formula_complex = any(e.has(sympy.I) for e in all_s)

    def is_real_regime(a):
        # a formula that itself contains i is read with complex principal branches (arccos x = -i ln(x + sqrt(x^2-1)))
        return all(s.name in real_names for s in a.free_symbols) and not a.has(sympy.I) and not formula_complex

    def holds(rel):
        try:
            v = rel.xreplace(assumed)
            if v is sympy.true:
                return True
            if isinstance(v, sympy.Ne):
                d = v.lhs - v.rhs
                if d.is_nonzero:
                    return True
            if isinstance(v, (sympy.StrictGreaterThan, sympy.GreaterThan)):
                d = v.lhs - v.rhs
                return bool(d.is_positive) or (isinstance(v, sympy.GreaterThan) and bool(d.is_nonnegative))
        except Exception:
            return False
        return False

    expr_constraints: list[tuple[str, str, str]] = []   # (rule, constraint, why)
    outer = set(doms)

    def ok_sub(a):
        return a.free_symbols and {s.name for s in a.free_symbols} <= outer

    def emit(rule, rel, why):
        if rel in (sympy.true,) or rel is True:
            return
        if holds(rel):
            return
        expr_constraints.append((rule, sympy.sstr(rel), why))

    bound_int = {lim[0] for e in all_s for sp in e.atoms(sympy.Sum, sympy.Product) for lim in sp.limits}
    for e in all_s:
        for p in e.atoms(sympy.Pow):
            b, ex = p.base, p.exp
            if not ok_sub(b):
                continue
            if ex.is_number and ex.is_negative:
                if not (isinstance(b, NEVER_ZERO) or (isinstance(b, sympy.Pow) and b.base == sympy.E)):
                    emit("C.denominator_nonzero", sympy.Ne(b, 0), f"{sympy.sstr(b)} appears in a denominator")
            if ex.is_Rational and not ex.is_Integer and is_real_regime(b):
                rel = sympy.StrictGreaterThan(b, 0) if ex.is_negative else sympy.GreaterThan(b, 0)
                emit("C.sqrt_arg", rel, f"fractional power of {sympy.sstr(b)} in the real regime")
            elif not ex.is_number and is_real_regime(b) and (ex.free_symbols - bound_int or not ex.free_symbols <= bound_int):
                ex_int = all(s in bound_int or (s.name in doms and doms[s.name].integer) for s in ex.free_symbols) \
                    and all(c.is_integer for c in ex.atoms(sympy.Number))
                if not ex_int:
                    emit("C.real_power_base", sympy.StrictGreaterThan(b, 0), f"{sympy.sstr(b)} raised to a non-integer symbolic power")
        for f in e.atoms(sympy.log):
            a = f.args[0]
            if not ok_sub(a):
                continue
            if is_real_regime(a):
                emit("C.log_arg", sympy.StrictGreaterThan(a, 0), f"log of {sympy.sstr(a)} in the real regime")
            else:
                emit("C.log_arg_complex", sympy.Ne(a, 0), f"log of {sympy.sstr(a)} (complex): argument nonzero")
        recip_only = {p.base for p in e.atoms(sympy.Pow) if p.exp.is_number and p.exp.is_negative and isinstance(p.base, sympy.gamma)}
        recip_only -= {f for f in e.atoms(sympy.gamma) if _appears_outside_reciprocal(e, f)}
        for f in e.atoms(sympy.gamma, sympy.loggamma, sympy.digamma, sympy.polygamma, sympy.beta):
            if f in recip_only:
                continue   # 1/Gamma is entire: a Gamma that only divides adds no pole
            args = f.args[1:] if isinstance(f, sympy.polygamma) else f.args
            for a in args:
                if not ok_sub(a):
                    continue
                rel = sympy.Not(sympy.And(sympy.Eq(a, sympy.floor(sympy.re(a))), sympy.re(a) <= 0), evaluate=False)
                if (a.xreplace(assumed)).is_positive:
                    continue
                expr_constraints.append(("C.gamma_pole", f"Not(And(Eq({sympy.sstr(a)}, floor(re({sympy.sstr(a)}))), re({sympy.sstr(a)}) <= 0))",
                                         f"{type(f).__name__}({sympy.sstr(a)}): argument not a non-positive integer"))
        for f in e.atoms(sympy.zeta):
            a = f.args[0]
            if ok_sub(a) and len(f.args) == 1:
                emit("C.zeta_pole", sympy.Ne(a, 1), f"zeta({sympy.sstr(a)}) has a pole at 1")
        for f in e.atoms(sympy.factorial, sympy.factorial2):
            a = f.args[0]
            lin = _single_symbol_offset(a)
            if lin and lin[0].name in doms and doms[lin[0].name].integer and doms[lin[0].name].nfield == "real":
                sym, c = lin
                d = doms[sym.name]
                if d.lo is None or d.lo < -c:
                    doms[sym.name] = d.meet(Dom(lo=-c, origin=d.origin))
                    sem.domains[sym.name] = doms[sym.name].to_schema()
                    tr.add("C.factorial_domain", f"[{sym.name}] factorial({sympy.sstr(a)}) needs {sym.name} >= {-c}")
                continue
            if ok_sub(a) and not isinstance(a, sympy.Symbol):
                emit("C.factorial_arg", sympy.GreaterThan(a, 0), f"factorial argument {sympy.sstr(a)} must be a nonneg integer")
        for f in e.atoms(sympy.asin, sympy.acos):
            a = f.args[0]
            if ok_sub(a) and is_real_regime(a):
                expr_constraints.append(("C.asin_acos_arg", f"(({sympy.sstr(a)}) >= -1) & (({sympy.sstr(a)}) <= 1)",
                                         f"{type(f).__name__} argument in [-1, 1]"))
        for f in e.atoms(sympy.asec, sympy.acsc):
            a = f.args[0]
            if ok_sub(a) and is_real_regime(a):
                emit("C.asec_acsc_arg", sympy.GreaterThan(sympy.Abs(a), 1), f"{type(f).__name__} argument has |.| >= 1")
        for f in e.atoms(sympy.acosh):
            a = f.args[0]
            if ok_sub(a) and is_real_regime(a):
                emit("C.acosh_arg", sympy.GreaterThan(a, 1), "acosh argument >= 1")
        for f in e.atoms(sympy.atanh):
            a = f.args[0]
            if ok_sub(a) and is_real_regime(a):
                emit("C.atanh_arg", sympy.StrictLessThan(sympy.Abs(a), 1), "atanh argument |.| < 1")
        for f in e.atoms(sympy.tan, sympy.sec, sympy.cot, sympy.csc):
            a = f.args[0]
            if not ok_sub(a):
                continue
            g = sympy.cos(a) if isinstance(f, (sympy.tan, sympy.sec)) else sympy.sin(a)
            emit("C.trig_pole", sympy.Ne(g, 0), f"{type(f).__name__}({sympy.sstr(a)}) has poles where {sympy.sstr(g)} = 0")
        for f in e.atoms(sympy.coth, sympy.csch):
            a = f.args[0]
            if ok_sub(a):
                emit("C.trig_pole", sympy.Ne(sympy.sinh(a), 0), f"{type(f).__name__} has a pole where sinh = 0")

    seen = set()
    out = []
    for c in sem.constraints + prose_constraints:
        if c not in seen:
            seen.add(c)
            out.append(c)
    for rule, c, why in expr_constraints:
        if c not in seen:
            seen.add(c)
            out.append(c)
            tr.add(rule, f"[{c}] {why}")
    sem.constraints = out

    # ---------------------------------------------------------------- checkability
    reason = _checkability(pieces, subst, main_latex, latex, remaining_undef, constants, before, after, nb, na, var_syms, tr,
                           title=title, section=section, forms=forms)
    if reason:
        sem.checkable, sem.skip_reason = False, reason
    else:
        sem.checkable = True
    sem.assumptions_source = tr.ids()
    return sem, tr


def _sides_latex(p) -> tuple[str, str]:
    """The translator records `sides: <lhs latex>  ||  <rhs latex>` in its notes."""
    m = re.search(r"^sides:\s*(.*?)\s*\|\|\s*(.*)$", p.notes or "", re.M)
    return (m.group(1), m.group(2)) if m else ("", "")


def _multiplies(exprs, sym) -> bool:
    """`sym` is a factor of a product with something other than index letters (a+bi, Si(ix), i sin x)."""
    for e in exprs:
        for m in sympy.preorder_traversal(e):
            if isinstance(m, sympy.Mul) and sym in m.args:
                others = [a for a in m.args if a != sym]
                if others and not all(isinstance(a, sympy.Symbol) and base_letter(a.name) in INTEGER_LETTERS for a in others):
                    return True
    return False


def _single_symbol_offset(a):
    """`n - 1` -> (n, -1); `n` -> (n, 0); anything else -> None."""
    a = sympy.sympify(a)
    syms = a.free_symbols
    if len(syms) != 1:
        return None
    s = next(iter(syms))
    c = sympy.expand(a - s)
    if c.is_Integer:
        return s, int(c)
    return None


def _appears_outside_reciprocal(e, f) -> bool:
    """True if `f` occurs in `e` other than as the base of a negative power."""
    if e == f:
        return True
    if isinstance(e, sympy.Pow) and e.base == f and e.exp.is_number and e.exp.is_negative:
        return False
    return any(_appears_outside_reciprocal(a, f) for a in e.args)


def _known_function_names():
    return {"gamma", "beta", "zeta", "erf", "erfc", "exp", "log", "sin", "cos", "tan", "binomial", "factorial"}


def _apply_bound(doms, rel, f, applied_type):
    """Fold a numeric bound `sym op number` into the symbol's domain."""
    if not isinstance(rel, sympy.core.relational.Relational):
        return
    lhs, rhs = rel.lhs, rel.rhs
    op = rel.rel_op
    if isinstance(rhs, sympy.Symbol) and lhs.is_number:
        lhs, rhs = rhs, lhs
        op = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "!=": "!=", "==": "=="}[op]
    if isinstance(lhs, sympy.Abs) and isinstance(lhs.args[0], sympy.Symbol) and rhs.is_number and op in ("<", "<="):
        n = lhs.args[0].name
        if n in doms and doms[n].nfield == "real":
            c = float(rhs)
            nd = Dom(lo=-c, lo_strict=op == "<", hi=c, hi_strict=op == "<", origin="prose")
            doms[n] = _fold(doms[n], nd, n in applied_type)
        return
    if not (isinstance(lhs, sympy.Symbol) and lhs.name in doms and rhs.is_number and rhs.is_real):
        return
    n, c = lhs.name, float(rhs)
    cur = doms[n]
    if cur.nfield == "complex":
        return
    if op == "!=":
        cur.exclude = cur.exclude | {c}
        return
    nd = Dom(origin="prose")
    if op in (">", ">="):
        nd.lo, nd.lo_strict = c, op == ">"
    elif op in ("<", "<="):
        nd.hi, nd.hi_strict = c, op == "<"
    else:
        return
    doms[n] = _fold(cur, nd, n in applied_type)


def _fold(cur: Dom, nd: Dom, has_prose_type: bool) -> Dom:
    if cur.origin == "default" and not has_prose_type:
        # explicit bounds replace the default's sign assumptions, keep its number system
        base = Dom(nfield=cur.nfield, integer=cur.integer, angle=cur.angle, exclude=cur.exclude, origin="prose")
        return base.meet(nd)
    return cur.meet(nd)


def _checkability(pieces, subst, main_latex, latex, remaining_undef, constants, before, after, nb, na, var_syms, tr,
                  title="", section="", forms=None) -> str | None:
    # units
    um = re.search(r"\d\s*(?:\\[,;:! ]|~|\s|\\cdot|\)|\})*\s*\\(?:mathrm|text|rm|mbox|textrm|operatorname)\s*\{\s*~?\s*(?:" + UNITS + r")\s*[}^/\s]", latex) \
        or re.search(r"\d\s*(?:\\,|~|\s)*(?:°|\\circ|\^\{?\\circ\}?)(?:\s*\\?mathrm\{?C)?", latex) \
        or re.search(r"\d\s*(?:\\,|~|\s)*(?:kg|km|cm|mm|kJ|kW|MW|keV|MeV|GeV|kHz|MHz|GHz|mol|mL|(?:kg|g|m|km|L|J|W|mol)/(?:L|s|h|m|kg|mol|K))(?![A-Za-z])", latex)
    if um:
        tr.add("K.units", f"number followed by a unit: {um.group(0)!r}")
        return "units"
    # operator notation the pipeline cannot evaluate (main body only, condition tail ignored)
    body = re.sub(r"_\s*\{[^{}]*\}|_\s*\\?[A-Za-z0-9]+", " ", main_latex)   # drop subscripts (\lim_{n\to\infty}, \sum_{k\in S})
    for rule, rx, why in OPERATOR_RULES:
        m = re.search(rx, body if rule in ("K.op_logic", "K.op_set") else main_latex)
        if m:
            tr.add(rule, f"found {m.group(0)!r}")
            return why
    if re.search(r"\\partial", main_latex) and remaining_undef:
        tr.add("K.op_partial", "partial derivative of an undefined function")
        return "operator_notation"
    # translator status
    bad = [p for p in pieces if p.status != "ok"]
    if bad:
        if any(p.has_unsupported for p in bad):
            tr.add("K.translator_unsupported", f"translator could not translate {sorted({u for p in bad for u in p.has_unsupported})}")
            return "operator_notation"
        st = bad[0].status
        tr.add("K.translator_status", f"translator status {st!r}: {bad[0].error or ''}")
        return "unparsed" if st == "unparsed" else "translator_not_checkable"
    if any(p.has_unsupported for p in pieces):
        tr.add("K.translator_unsupported", f"translator flagged {sorted({u for p in pieces for u in p.has_unsupported})}")
        return "operator_notation"
    # ---- second pass: context the reviewers found behind real false FAILs
    names = [s_.name for s_ in var_syms]
    if cr.index_range(latex):
        tr.add("K.index_range", "an index range such as `i = 1, ..., n`, not an equation")
        return "statement_not_identity"
    m = cr.special_algebra(title, section, before, after, latex)
    if m:
        tr.add("K.special_algebra", f"arithmetic is not ordinary here ({m})")
        return "special_algebra"
    m = cr.stated_false(before, after)
    if m:
        tr.add("K.stated_false", f"the prose presents the formula as false / a fallacy / a counterfactual ({m})")
        return "stated_false"
    m = cr.noncommuting(names, title, section, before, after)
    if m:
        tr.add("K.noncommuting", f"matrices or operators, not scalars ({m})")
        return "matrix_or_vector"
    for n in names:
        if prose.sym_key(n) in cr.NAMED_SYMBOLS:
            tr.add("K.named_constant", f"[{n}] {cr.NAMED_SYMBOLS[prose.sym_key(n)]}")
            return "named_constant"
    if forms is not None:
        m = cr.named_parameter(names, lambda n: sorted({f for f, v in forms.by_form.items() if v == n}, key=len, reverse=True), before, after)
        if m:
            tr.add("K.named_parameter", f"[{m.split(':')[0]}] the adjacent prose fixes this symbol to a specific value ({m})")
            return "named_constant"
    for (l, r), p in subst:
        if l is None or r is None:
            continue
        for a, b in ((l, r), (r, l)):
            if a == sympy.pi and b.is_Integer:
                tr.add("K.pi_named_object", f"`pi = {b}`: pi names an object here (a bivector, a permutation), not 3.14159")
                return "named_constant"
        for a, b in ((l, r), (r, l)):
            if a in (sympy.pi, sympy.E, sympy.GoldenRatio, sympy.EulerGamma) and b.is_number and sympy.nsimplify(b).is_Rational:
                tr.add("K.irrational_equals_rational", f"{a} equated to the rational {sympy.sstr(b)}: a historical or working approximation")
                return "approximation"
        if l.has(sympy.acot) or r.has(sympy.acot):
            tr.add("K.acot_convention", "arccot: sympy's range (-pi/2, pi/2] differs from the common (0, pi) convention")
            return "notation_or_convention"
        for e in (l, r):
            for pw in e.atoms(sympy.Pow):
                if pw.base != sympy.E and pw.exp.has(sympy.I) and not (pw.base.is_number and pw.base.is_positive):
                    tr.add("K.multivalued_power", f"{sympy.sstr(pw)}: a complex power of a non-positive base is multivalued")
                    return "notation_or_convention"
    letter = cr.function_name_misread(latex)
    if letter:
        for (l, r), p in subst[:1]:
            target = {"e": sympy.E, "i": sympy.I}.get(letter) if letter in constants else sympy.Symbol(letter)
            if isinstance(l, sympy.Mul) and (sympy.Symbol(letter) in l.args or target in l.args):
                tr.add("K.function_name_misread", f"[{letter}] `{letter}(...)` on the left is a function being defined, read as a product")
                return "definition"
    # relation present?
    for (l, r), p in subst:
        if l is None or r is None:
            tr.add("K.no_relation", "no left/right hand side (not an equation or inequality)")
            return "no_relation"
    # derivative notation that survived as symbols (h'' -> h_prime_prime, \dot x -> x_dot): an ODE
    ds = [s_.name for s_ in var_syms if re.search(r"(?:^|_)(?:prime|dot|ddot)(?:_|$)|'", s_.name)]
    if ds:
        tr.add("K.derivative_symbol", f"[{ds[0]}] derivative written as a symbol: a differential equation")
        return "differential_equation"
    # ellipsis that the translator turned into symbols
    if any(base_letter(s.name) in ("cdots", "ldots", "dots") for s in var_syms):
        tr.add("K.ellipsis_symbol", "an ellipsis survived translation as a symbol")
        return "unparsed"
    # definitions
    for (l, r), p in subst:
        if p.kind == "definition_like":
            if isinstance(l, sympy.Function) and not isinstance(l, AppliedUndef) and not remaining_undef:
                tr.add("K.definition_known_function", f"definition of a known function ({type(l).__name__}); checked as an identity")
            else:
                tr.add("K.definition", "translator marked the formula definition_like")
                return "definition"
    if re.search(r":=|=:|\\coloneqq|\\triangleq|\\stackrel\s*\{\s*\\?(?:mathrm|text)?\s*\{?\s*def|\\overset\s*\{\s*\\?(?:mathrm|text)?\s*\{?\s*def|\\equiv", main_latex):
        tr.add("K.definition", "definitional `:=` / `def` marker")
        return "definition"
    # undefined functions
    if remaining_undef:
        functional = False
        for (l, r), p in subst:
            for name in remaining_undef:
                apps = [f for e in (l, r) for f in e.atoms(AppliedUndef) if f.func.__name__ == name]
                on_both = any(f.func.__name__ == name for f in l.atoms(AppliedUndef)) and any(f.func.__name__ == name for f in r.atoms(AppliedUndef))
                if on_both or len({f.args for f in apps}) >= 2:
                    functional = True
        if functional:
            tr.add("K.functional_identity", f"undefined function(s) {sorted(remaining_undef)} appear with several arguments: a functional equation")
            return "functional_identity"
        tr.add("K.undefined_function", f"undefined function(s) {sorted(remaining_undef)}")
        return "has_undefined_function"
    # indefinite integrals (constant of integration)
    for (l, r), p in subst:
        for e in (l, r):
            for it in e.atoms(sympy.Integral):
                if any(len(lim) == 1 for lim in it.limits):
                    tr.add("K.indefinite_integral", "indefinite integral: equal only up to a constant")
                    return "indefinite_integral"
    # equations that define a constant or are to be solved, and conditions written as inequalities
    sides_latex = [_sides_latex(p) for (_, _), p in subst]
    for ((l, r), p), (ll, rl) in zip(subst, sides_latex):
        is_eq_ = p.kind != "inequality" and p.relation in (None, "=", "==")
        fl_, fr_ = _free(l), _free(r)
        if is_eq_:
            for dl, other in ((cr.decimal_places(ll), fr_), (cr.decimal_places(rl), fl_)):
                if dl is not None and other:
                    tr.add("K.decimal_literal_side", "a decimal literal equated to an expression in free symbols: it defines a value (z_{.975}, a root)")
                    return "defining_equation"
        elif (not fl_ or not fr_) and (fl_ or fr_) and not cr.universal_cue(before, after):
            tr.add("K.condition_inequality", "an expression compared with a constant, with no 'for all' nearby: a condition such as `4p^3+27q^2 < 0`")
            return "condition"
    if var_syms:
        fforms = sorted({f for f in (forms.by_form if forms is not None else {})}, key=len, reverse=True)
        m = cr.defining_cue(before, after, fforms)
        if m:
            tr.add("K.defining_cue", f"the prose introduces an equation to solve / a defining condition ({m})")
            return "defining_equation"
    # existential / approximation statements in the adjacent prose
    near = nb[-200:] + " \u00b6 " + na[:60]
    m = EXISTENTIAL.search(near)
    if m:
        tr.add("K.existential_context", f"adjacent prose is existential: {m.group(0)!r}")
        return "statement_not_identity"
    # structure: definitions and relations between distinct quantities
    for (l, r), p in subst:
        fl, fr = _free(l), _free(r)
        for side, other in ((l, r), (r, l)):
            if isinstance(side, sympy.Symbol) and side not in _free(other):
                tr.add("K.bare_symbol_definition", f"[{side.name}] one side is the bare symbol {side.name}, absent from the other side")
                return "definition"
        # a symbol that cancels out of its side (log_k x / log_k b) is not really one-sided
        for s_ in list(fl - fr):
            if not _depends(l, s_):
                fl.discard(s_)
                tr.add("K.cancelling_symbol", f"[{s_.name}] {s_.name} cancels out of the left side")
        for s_ in list(fr - fl):
            if not _depends(r, s_):
                fr.discard(s_)
                tr.add("K.cancelling_symbol", f"[{s_.name}] {s_.name} cancels out of the right side")
        if (fl - fr) and (fr - fl):
            tr.add("K.unbalanced_sides", f"each side has symbols the other lacks ({sorted(s.name for s in fl - fr)} vs {sorted(s.name for s in fr - fl)}): a relation, not an identity")
            return "statement_not_identity"
        if (fl or fr) and _is_simple(l) and _is_simple(r):
            tr.add("K.condition_fragment", "every side is a number or a bare symbol / |symbol|: a condition such as `|x| < 1`, not a claim")
            return "statement_not_identity"
        is_eq = p.kind != "inequality" and p.relation in (None, "=", "==")
        if is_eq and (not fl or not fr) and (fl or fr):
            side = l if fl else r
            try:
                poly = sympy.Poly(sympy.expand(l - r), *sorted(fl | fr, key=str))
                if not side.atoms(sympy.Function) and not poly.is_zero and poly.total_degree() >= 1:
                    tr.add("K.polynomial_equation", "polynomial in the variables equated to a constant: an equation to solve, not an identity")
                    return "statement_not_identity"
            except Exception:
                pass
            if not side.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit, sympy.Derivative, sympy.Subs) \
                    and any(_depends(side, s_) for s_ in sorted(_free(side), key=str)):
                tr.add("K.nonconstant_equals_constant", "one side is a constant and the other varies with its variables: an equation to solve")
                return "statement_not_identity"
        if is_eq and fl and fr and not (l.atoms(sympy.Function) | r.atoms(sympy.Function)) \
                and not l.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit, sympy.Abs) and not r.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit, sympy.Abs) \
                and all(pw.exp.is_Integer for e_ in (l, r) for pw in e_.atoms(sympy.Pow)):
            try:
                num, _ = sympy.fraction(sympy.cancel(sympy.together(sympy.expand(l - r))))
                if num.free_symbols and not sympy.expand(num).is_zero and not _numerically_zero(num):
                    tr.add("K.rational_relation", "two rational expressions that are not identically equal: a relation that holds only under "
                                                  "extra conditions (the golden-ratio hypothesis, 4p^3+27q^2=0). Wrong rational identities also land here.")
                    return "statement_not_identity"
            except Exception:
                pass
        if is_eq and fl and fr and not (l.atoms(sympy.Function) | r.atoms(sympy.Function)) \
                and not l.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit) and not r.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit):
            try:
                d = sympy.expand(l - r)
                if d.free_symbols and sympy.Poly(d, *sorted(fl | fr, key=str)).total_degree() >= 1:
                    tr.add("K.polynomial_relation", "two polynomials that are not identically equal: a relation between quantities "
                                                    "(e.g. Descartes' theorem), not an identity. Wrong polynomial identities also land here.")
                    return "statement_not_identity"
            except Exception:
                pass
        one_sided = (fl - fr) | (fr - fl)
        if one_sided and (fl & fr):
            rel = _context_relation(nb[-250:] + " " + na[:200], one_sided, fl | fr)
            if rel:
                tr.add("K.context_relation", f"[{rel}] symbol {rel} appears on one side only and the adjacent prose ties it to the others by an equation")
                return "statement_not_identity"
    for (l, r), p in subst:
        if p.kind == "inequality" or (p.relation and p.relation not in ("=", "==")):
            tr.add("K.inequality", f"inequality kept checkable with relation {p.relation!r}")
            break
    for ((l, r), p), (ll, rl) in zip(subst, sides_latex):
        if _free(l) or _free(r):
            continue
        dp = cr.decimal_places(rl) if cr.decimal_places(rl) is not None else cr.decimal_places(ll)
        if dp is not None:
            tr.add("tol", f"[{dp}] a side is a decimal literal with {dp} places: compare to half a unit in the last place")
            break
        ap = cr.approx_cue(before, after)
        if ap:
            for side in (r, l):
                q = sympy.nsimplify(side) if side.is_number else None
                if q is not None and q.is_Rational and not q.is_Integer:
                    den = int(q.q)
                    while den % 2 == 0:
                        den //= 2
                    while den % 5 == 0:
                        den //= 5
                    if den == 1:
                        places = len(str(sympy.Float(q, 30)).rstrip("0").split(".")[1])
                        tr.add("tol", f"[{places}] prose says approximate ({ap}); {sympy.sstr(q)} has {places} decimal places")
                        break
                    tr.add("K.approximation", f"prose says approximate ({ap}) and {sympy.sstr(q)} is a non-terminating rational approximation")
                    return "approximation"
    if len(pieces) > 1:
        tr.add("K.chain", f"chain of {len(pieces)} pairwise relations; all pieces checkable")
    if not var_syms:
        tr.add("K.numeric_only", "no free symbols: a numeric identity, checkable")
    return None


def _numerically_zero(e) -> bool:
    """True if `e` vanishes at a few deterministic sample points (catches identities that need
    constant relations such as phi^2 = phi + 1, which symbolic expansion misses)."""
    syms = sorted(e.free_symbols, key=lambda x: x.name)
    try:
        for k in range(3):
            pt = {x: sympy.Float(0.37 + 0.61 * (j + 1) * (k + 1) / 7, 30) for j, x in enumerate(syms)}
            if abs(complex(sympy.N(e.subs(pt), 30))) > 1e-12:
                return False
        return True
    except Exception:
        return False


def _is_simple(e) -> bool:
    """A number, a bare symbol, or |symbol|, re(symbol), im(symbol)."""
    if e is None:
        return False
    if e.is_number:
        return True
    if isinstance(e, sympy.Mul) and len(e.args) == 2 and e.args[0] == -1:
        e = e.args[1]                      # -H
    if isinstance(e, sympy.Symbol):
        return True
    return isinstance(e, (sympy.Abs, sympy.re, sympy.im)) and isinstance(e.args[0], sympy.Symbol)


def _depends(e, sym) -> bool:
    """Numerically: does `e` change when only `sym` changes? (deterministic sample values)"""
    if e.has(sympy.Sum, sympy.Product, sympy.Integral, sympy.Limit, sympy.Derivative, sympy.Subs, AppliedUndef):
        return True   # too expensive / impossible to evaluate here: assume it depends
    others = sorted((x for x in e.free_symbols if x != sym), key=lambda x: x.name)
    base = {x: sympy.Float((37 + 11 * k) / 29, 30) for k, x in enumerate(others)}   # floats: exact rationals can explode
    try:
        vals = []
        for v in (sympy.Float(0.7, 30), sympy.Float(1.9, 30), sympy.Float(3.25, 30)):
            z = complex(sympy.N(e.subs({**base, sym: v}), 30))
            vals.append(z)
        scale = max(1.0, *(abs(z) for z in vals))
        return any(abs(z - vals[0]) > 1e-9 * scale for z in vals[1:])
    except Exception:
        return True


def _context_relation(text, one_sided, all_syms):
    """A one-sided symbol named in an equation (`=`) next to another formula symbol in prose."""
    for s in sorted(one_sided, key=lambda s: s.name):
        forms = prose.SymbolForms.build([s.name])
        rx = forms.regex()
        others = prose.SymbolForms.build([o.name for o in all_syms if o != s]).regex()
        if not rx or not others:
            continue
        for m in re.finditer(r"(?<![<>!=])=(?!=)", text):
            win = text[max(0, m.start() - 40): m.end() + 40]
            if re.search(rx, win) and re.search(others, win):
                return s.name
    return None
