import sympy as sp

from formulaci.schemas import Formula
from formulaci.translate.core import translate


def make_formula(latex: str, before: str = "", after: str = "", fid: str = "t:0") -> Formula:
    return Formula(formula_id=fid, page_title="T", page_id=1, revision_id=1, url="", index=0, latex=latex,
                   context_before=before, context_after=after)


def tr(latex: str, before: str = "", after: str = "", lark: bool = False):
    return translate(make_formula(latex, before, after), use_lark=lark)


def sides(latex: str, i: int = 0, **kw):
    r = tr(latex, **kw)[i]
    L = sp.sympify(r.lhs) if r.lhs else None
    R = sp.sympify(r.rhs) if r.rhs else None
    return L, R, r
