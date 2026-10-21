"""Formula -> list[Parsed]: preprocessing, relation splitting, classification, srepr round-trip."""
from __future__ import annotations

import re

import sympy as sp
from sympy.core.function import AppliedUndef

from formulaci.schemas import Formula, Parsed

from .lexer import Tok
from .parser import (Ctx, ParseError, Unsupported, _rel_name, _sym_cmd_name, _top_level_idx, indexed_bases, main_letters, prescan_brackets,
                     parse_side, prescan_functions)
from .preprocess import is_relation, preprocess

TRANSLATOR = f"formulaci-rd-0.1/sympy-{sp.__version__}"
LARK_TRANSLATOR = f"sympy-lark-{sp.__version__}"

EQ_RELS = {"=", ":=", "=:", "equiv"}
INEQ_RELS = {"<", "<=", ">", ">=", "!="}
DEF_PROSE = re.compile(
    r"\b(is|are|be) (defined|denoted|given|written)\b|\bdefin(e|es|ed|ing|ition)\b|\bdenot(e|es|ed|ing)\b|"
    r"\bwe (write|set|put|let)\b|\blet\b|\bwhere\b\s*$", re.I)
E = sp.Symbol("e")
I_ = sp.Symbol("i")


class Side:
    __slots__ = ("expr", "error", "unsupported", "latex", "via_lark")

    def __init__(self, latex: str):
        self.expr = None
        self.error: str | None = None
        self.unsupported: str | None = None
        self.latex = latex
        self.via_lark = False

    @property
    def ok(self) -> bool:
        return self.expr is not None and self.unsupported is None and self.error is None


def split_relations(seg: list[Tok]) -> tuple[list[list[Tok]], list[Tok]]:
    top = set(_top_level_idx(seg))
    sides, ops, cur = [], [], []
    for i, t in enumerate(seg):
        if i in top and is_relation(t):
            sides.append(cur)
            ops.append(t)
            cur = []
        else:
            cur.append(t)
    sides.append(cur)
    return sides, ops


def _is_differential_form(segments) -> bool:
    """`dx = \\frac{2}{t^2-1}\\,dt`, `ds^2 = E\\,dx^2 + 2F\\,dx\\,dy`, `df = f'(x)\\,dx`: relations
    between differentials, not products with a symbol `d`. Detected (outside integrals) when at least
    two `d<letter>` pairs start a term: after the start, an operator, a relation, `(`, `}` or a space.
    `ad - bc` (d after a letter) and `\\frac{dy}{dx}` (d right after `{`) do not count."""
    toks = [t for seg, _ in segments for t in seg]
    if any(t.kind == "CMD" and t.value in ("int", "iint", "oint") for t in toks):
        return False
    n = 0
    for seg, _ in segments:
        for k, t in enumerate(seg[:-1]):
            nxt = seg[k + 1]
            if not (t.kind == "LETTER" and t.value == "d" and (nxt.kind == "LETTER" or _sym_cmd_name(nxt) is not None)):
                continue
            prev = seg[k - 1] if k > 0 else None
            prev2 = seg[k - 2] if k > 1 else None
            if _sym_cmd_name(nxt) is not None and not (prev is not None and prev.kind == "CHAR" and prev.value == "{"):
                n += 1  # `d\theta`, `k\,d\phi`: nobody writes d times theta
            elif prev is not None and prev.kind == "DIGIT" and prev2 is not None and prev2.kind == "CHAR" and prev2.value == "^":
                n += 1  # `r^2 dx`
            elif prev is None or prev.kind == "SPACE" or is_relation(prev) or (
                    prev.kind == "CHAR" and prev.value in "+-(}") or (prev.kind == "CMD" and prev.value in ("cdot", "wedge")):
                n += 1
    return n >= 2


def _pm_variants(seg: list[Tok]) -> list[tuple[str, list[Tok]]] | None:
    """`\\sin(a \\pm b) = \\sin a\\cos b \\pm \\cos a\\sin b` -> the + and the - identity.

    Only when the sign choice is clearly coupled: `\\pm` on at least two sides, or `\\mp` used.
    A lone `\\pm` (e.g. `= \\pm\\sqrt{...}`, a sign that depends on the quadrant) is left alone and
    becomes `has_unsupported: pm`.
    """
    has = [t for t in seg if t.kind == "CMD" and t.value in ("pm", "mp")]
    if not has:
        return None
    sides, _ = split_relations(seg)
    n_sides = sum(1 for s in sides if any(t.kind == "CMD" and t.value in ("pm", "mp") for t in s))
    if n_sides < 2 and not any(t.value == "mp" for t in has):
        return None
    out = []
    for label, pm, mp in (("+", "+", "-"), ("-", "-", "+")):
        v = [Tok("CHAR", pm if t.value == "pm" else mp, t.start, t.end)
             if t.kind == "CMD" and t.value in ("pm", "mp") else t for t in seg]
        out.append((label, v))
    return out


def _lark_parse(latex: str):
    from sympy.parsing.latex import parse_latex
    s = re.sub(r"\\(left|right|displaystyle|textstyle|,|;|!|quad|qquad)(?![a-zA-Z])", " ", latex)
    e = parse_latex(s, backend="lark")
    if not isinstance(e, sp.Basic):
        raise ParseError("lark: ambiguous parse")
    if isinstance(e, (sp.Rel, sp.logic.boolalg.Boolean)) and not isinstance(e, sp.Expr):
        raise ParseError("lark: relation in side")
    # lark symbols/functions carry lark Token objects as names; normalize through the srepr text
    text = re.sub(r"Token\('\w+', ('(?:[^'\\]|\\.)*')\)", r"\1", sp.srepr(e))
    return sp.sympify(text)


def _parse_one(tokens: list[Tok], src: str, ctx: Ctx, use_lark: bool) -> Side:
    core = [t for t in tokens if t.kind != "SPACE"]
    latex = src[core[0].start:core[-1].end].strip() if core and core[-1].end > core[0].start else ""
    side = Side(latex)
    if not core:
        side.unsupported = "empty_side"
        return side
    try:
        side.expr = parse_side(tokens, ctx)
        if isinstance(side.expr, sp.logic.boolalg.BooleanAtom):
            side.expr = None
            raise ParseError("side evaluated to a boolean")
    except Unsupported as u:
        side.unsupported = u.name
    except (ParseError, RecursionError, ValueError, TypeError, AttributeError, KeyError, IndexError,
            ZeroDivisionError, NotImplementedError, sp.SympifyError) as ex:
        side.error = f"{type(ex).__name__}: {ex}"[:300]
        if use_lark and latex:
            try:
                side.expr = _lark_parse(latex)
                side.via_lark = True
                side.error = None
                ctx.note("fallback:lark")
            except Exception:  # noqa: BLE001 - lark raises many unrelated types
                pass
    return side


def _definable(expr) -> bool:
    if isinstance(expr, sp.Symbol):
        return True
    if isinstance(expr, AppliedUndef):
        return all(isinstance(a, (sp.Symbol, sp.Integer)) or isinstance(a, sp.Expr) and a.is_Atom for a in expr.args)
    return False


def _functions(*exprs) -> list[str]:
    out = set()
    for e in exprs:
        if e is not None:
            out |= {type(f).__name__ for f in e.atoms(AppliedUndef)}
    return sorted(out)


def _free(*exprs) -> list[str]:
    out = set()
    for e in exprs:
        if e is not None:
            out |= {s.name for s in e.free_symbols if isinstance(s, sp.Symbol)}
    return sorted(out)


def _const_hints(*exprs) -> list[str]:
    hints = []
    es = [e for e in exprs if e is not None]
    for sym, label in ((E, "e"), (I_, "i")):
        if not any(sym in e.free_symbols for e in es):
            continue
        if sym is E:
            stripped = [e.replace(lambda a: a.is_Pow and a.base == E, lambda a: sp.Integer(2)) for e in es]
            only_base = not any(E in e.free_symbols for e in stripped)
            hints.append("hint:e_only_as_exp_base" if only_base else "hint:e_not_only_exp_base")
        else:
            sq = any(e.has(sp.Pow(I_, 2)) for e in es)
            hints.append("hint:i_squared" if sq else "hint:i_present")
    return hints


def roundtrip(expr) -> tuple[str, object]:
    """srepr that sympify reads back to the identical tree.

    Auto-evaluation can make the first srepr a non-fixpoint (`(1/2)**(1-1/a)` is rebuilt as
    `2**(1/a - 1)`); one more srepr/sympify pass yields the canonical, equal-valued form."""
    s = sp.srepr(expr)
    back = sp.sympify(s)
    if back == expr:
        return s, expr
    s2 = sp.srepr(back)
    back2 = sp.sympify(s2)
    if back2 == back:
        return s2, back
    raise ParseError("srepr round-trip mismatch")


def translate(f: Formula, use_lark: bool = False) -> list[Parsed]:
    notes: list[str] = []
    unsupported: list[str] = []
    try:
        src, segments = preprocess(f.latex, notes, unsupported)
    except Exception as ex:  # noqa: BLE001
        return [Parsed(formula_id=f.formula_id, status="unparsed", kind="other",
                       error=f"preprocess: {type(ex).__name__}: {ex}"[:300], translator=TRANSLATOR,
                       notes="\n".join(notes) or None)]
    if not segments:
        return [Parsed(formula_id=f.formula_id, status="unparsed", kind="other", error="empty formula",
                       translator=TRANSLATOR, notes="\n".join(notes) or None)]

    all_toks = [t for seg, _ in segments for t in seg]
    nospace = [t for t in all_toks if t.kind != "SPACE"]
    funcs, fnotes, ambiguous = prescan_functions(nospace)
    ctx = Ctx(notes=notes, funcs=funcs, main_letters=main_letters(nospace), indexed_bases=indexed_bases(nospace),
              ambiguous_funcs=ambiguous, bracket_funcs=prescan_brackets(nospace))
    if _is_differential_form(segments):
        unsupported.append("differential_form")
    notes.extend(fnotes)

    # expand coupled \pm / \mp into two segments
    expanded: list[tuple[str | None, list[Tok], list[str]]] = []
    for seg, conds in segments:
        v = _pm_variants(seg)
        if v:
            expanded.extend((label, vseg, conds) for label, vseg in v)
        else:
            expanded.append((None, seg, conds))

    prose = (f.context_before[-200:] + " ") if f.context_before else ""
    prose_def = bool(DEF_PROSE.search(prose)) or bool(re.match(r"\s*(is|be) (defined|called|known)\b", f.context_after[:60] or "", re.I))

    pending: list[dict] = []
    for variant, seg, conds in expanded:
        first_rel = next((k for k, t in enumerate(seg) if is_relation(t)), len(seg))
        if any(t.kind == "SPACE" and t.value == "colsep" for t in seg[:first_rel]):
            # `\arccos(z) & z & & \sqrt{1-z^2} & ...`: a table row, not one expression
            seg = [t for t in seg if not (t.kind == "SPACE" and t.value == "colsep")]
            table_row = True
        else:
            table_row = False
        sides_t, ops = split_relations(seg)
        sides = [_parse_one(s, src, ctx, use_lark) for s in sides_t]
        rels = [_rel_name(o) for o in ops]
        extra = [f"cond: {c}" for c in conds] + ([f"pm_variant:{variant}"] if variant else [])
        if table_row:
            for sd in sides:
                if sd.expr is not None or sd.error:
                    sd.expr, sd.error, sd.unsupported = None, None, "table_row"
        if not ops:
            pending.append(dict(pair=(sides[0], None), rel=None, extra=extra, pos=0, n=0))
            continue
        for i, rel in enumerate(rels):
            pending.append(dict(pair=(sides[i], sides[i + 1]), rel=rel, extra=extra, pos=i, n=len(rels)))
        # bridge across sides that could not be translated in an '=' chain
        ok_idx = [i for i, s in enumerate(sides) if s.ok]
        for a, b in zip(ok_idx, ok_idx[1:]):
            if b - a > 1 and all(r == "=" for r in rels[a:b]):
                pending.append(dict(pair=(sides[a], sides[b]), rel="=", extra=extra + [f"bridge:{a}-{b}"],
                                    pos=a, n=len(rels), bridge=True))

    records: list[Parsed] = []
    multi = len(pending) > 1
    for k, p in enumerate(pending):
        L, R = p["pair"]
        rel = p["rel"]
        rec_notes = list(notes) + p["extra"]
        translator = LARK_TRANSLATOR if (L.via_lark or (R is not None and R.via_lark)) else TRANSLATOR
        errs = [s.error for s in (L, R) if s is not None and s.error]
        unsup = sorted({s.unsupported for s in (L, R) if s is not None and s.unsupported} | set(unsupported))
        relation = None
        kind = "other"
        lhs_e, rhs_e = L.expr, (R.expr if R is not None else None)
        if rel == "=:":
            lhs_e, rhs_e = rhs_e, lhs_e
            rec_notes.append("swapped_eqcolon")
        if rel in EQ_RELS:
            is_def_marker = rel in (":=", "=:")
            definable = lhs_e is not None and _definable(lhs_e)
            if rel == "equiv" and not definable:
                rec_notes.append("equiv_as_identity")
            if definable and (is_def_marker or rel == "equiv" or (prose_def and p["pos"] == 0)):
                kind = "definition_like"
                if not is_def_marker and rel != "equiv":
                    rec_notes.append("definition_from_prose")
            elif p["n"] > 1:
                kind = "chain"
            else:
                kind = "equation"
            relation = "="
        elif rel in INEQ_RELS:
            kind = "inequality"
            relation = rel
        elif rel is not None:
            relation = rel
        if rel is not None and rel not in EQ_RELS | INEQ_RELS:
            rec_notes.append(f"relation:{rel}")

        status = "ok"
        error = None
        lhs = rhs = None
        if errs:
            status = "unparsed"
            error = " | ".join(errs)
        elif unsup:
            status = "not_checkable"
        elif rel is None or kind == "other":
            status = "not_checkable"
        try:
            if lhs_e is not None:
                lhs, lhs_e = roundtrip(lhs_e)
            if rhs_e is not None:
                rhs, rhs_e = roundtrip(rhs_e)
        except Exception as ex:  # noqa: BLE001
            status = "unparsed"
            error = f"roundtrip: {type(ex).__name__}: {ex}"[:300]
            lhs = rhs = None
        if lhs_e is not None and rhs_e is not None and status == "ok":
            rec_notes.extend(_const_hints(lhs_e, rhs_e))
        if L.latex and R is not None:
            rec_notes.append(f"sides: {L.latex}  ||  {R.latex}")
        records.append(Parsed(
            formula_id=f.formula_id,
            status=status,
            kind=kind,
            index_in_chain=k if multi else None,
            relation=relation,
            lhs=lhs,
            rhs=rhs,
            free_symbols=_free(lhs_e, rhs_e),
            functions=_functions(lhs_e, rhs_e),
            has_unsupported=unsup,
            error=error,
            translator=translator,
            notes="\n".join(dict.fromkeys(rec_notes)) or None,
        ))
    return records
