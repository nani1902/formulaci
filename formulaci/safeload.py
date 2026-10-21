"""Safe reconstruction of SymPy objects from strings, shared by every stage.

Rule for the whole package: no text that could derive from a Wikipedia page, a model, or a data
file may reach ``eval``, ``exec``, ``sympify``, ``parse_expr`` or ``parse_latex`` directly. Use:

- ``load_srepr(s)``: rebuild an expression from an ``sympy.srepr`` string after AST whitelisting
  (calls to public SymPy names only, string literals only inside Symbol/Function constructors,
  no attributes, no subscripts, no builtins). Returns ``None`` instead of raising.
- ``readable(s)``: the same, rendered with ``sympy.sstr`` for humans; falls back to the input.
- ``parse_simple_expr(text, names)``: a strict arithmetic grammar for short expressions found in
  prose ("2n+1", "|x|", "sqrt(2)"), built directly from the AST without evaluating any string.
- ``parse_constraint``: boolean constraint grammar (re-exported from the verify stage).
- Input size caps used by the library API and the MCP server.
"""
from __future__ import annotations

import ast
import re
from typing import Mapping

import sympy as sp

from formulaci.verify.reconstruct import UnsafeExpression, from_srepr, parse_constraint  # noqa: F401

MAX_LATEX_CHARS = 20_000      # one formula
MAX_CONTEXT_CHARS = 20_000    # prose around it
MAX_TEXT_CHARS = 2_000_000    # a whole document for extract_formulas / verify_text
MAX_ITEMS = 1_000             # formulas per check_many call
MAX_SIMPLE_EXPR_CHARS = 300   # prose-derived arithmetic


def load_srepr(s: str | None, *, evaluate: bool = True) -> sp.Basic | None:
    """Rebuild a SymPy object from an srepr string; ``None`` if the string is not a safe srepr."""
    if not s or not isinstance(s, str):
        return None
    try:
        if evaluate:
            return from_srepr(s)
        with sp.evaluate(False):
            return from_srepr(s)
    except (UnsafeExpression, ValueError, SyntaxError, TypeError, RecursionError, MemoryError):
        return None
    except Exception:
        return None


def readable(s: str | None, *, limit: int = 400) -> str:
    """Human-readable form of an srepr string (or the input itself when it is not one)."""
    if not s:
        return ""
    e = load_srepr(s)
    out = sp.sstr(e) if e is not None else str(s)
    return out if len(out) <= limit else out[: limit - 3] + "..."


# ---------------------------------------------------------------- prose arithmetic

_TOKEN = re.compile(r"\s*(?:(\d+\.\d*|\.\d+|\d+)|([A-Za-z][A-Za-z0-9]*)|(\*\*|[-+*/()^,]))")
_FUNCS: dict[str, object] = {
    "Abs": sp.Abs, "abs": sp.Abs, "sqrt": sp.sqrt, "re": sp.re, "im": sp.im, "exp": sp.exp,
    "log": sp.log, "ln": sp.log, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "floor": sp.floor,
    "ceiling": sp.ceiling, "ceil": sp.ceiling, "Rational": sp.Rational,
}
_CONSTS: dict[str, object] = {"pi": sp.pi, "oo": sp.oo, "inf": sp.oo, "E": sp.E}
_BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
           ast.Div: lambda a, b: a / b, ast.Pow: lambda a, b: a ** b}


def _tokenize(text: str) -> list[tuple[str, str]] | None:
    """Tokens as (kind, value); ``None`` when the text contains anything outside the grammar."""
    out: list[tuple[str, str]] = []
    pos = 0
    text = text.strip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            return None
        num, name, op = m.groups()
        if num is not None:
            out.append(("num", num))
        elif name is not None:
            out.append(("name", name))
        else:
            out.append(("op", "**" if op == "^" else op))
        pos = m.end()
    return out


def _with_implicit_multiplication(tokens: list[tuple[str, str]]) -> str:
    """Rebuild source text, inserting ``*`` where prose arithmetic leaves it implicit (``2n``, ``2(x+1)``,
    ``n(n+1)`` for a non-function name, ``(a)(b)``)."""
    parts: list[str] = []
    prev: tuple[str, str] | None = None
    for kind, val in tokens:
        if prev is not None:
            pk, pv = prev
            starts_operand = kind in ("num", "name") or (kind == "op" and val == "(")
            prev_is_operand_end = pk in ("num", "name") or (pk == "op" and pv == ")")
            prev_is_function = pk == "name" and pv in _FUNCS
            if starts_operand and prev_is_operand_end and not (prev_is_function and kind == "op" and val == "("):
                if not (pk == "name" and kind == "op" and val == "(" and pv in _FUNCS):
                    parts.append("*")
        parts.append(val)
        prev = (kind, val)
    return "".join(parts)


def _build(node: ast.AST, names: Mapping[str, sp.Basic]) -> sp.Basic:
    if isinstance(node, ast.Expression):
        return _build(node.body, names)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise UnsafeExpression("bad literal")
        return sp.Integer(node.value) if isinstance(node.value, int) else sp.Float(node.value)
    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        if node.id in _CONSTS:
            return _CONSTS[node.id]
        raise UnsafeExpression(f"unknown name {node.id}")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _build(node.operand, names)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        a, b = _build(node.left, names), _build(node.right, names)
        if isinstance(node.op, ast.Pow) and b.is_Number and abs(b) > 2000:
            raise UnsafeExpression("exponent too large")
        return _BINOPS[type(node.op)](a, b)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        if node.keywords or len(node.args) > 2:
            raise UnsafeExpression("bad call")
        return _FUNCS[node.func.id](*[_build(a, names) for a in node.args])
    raise UnsafeExpression(f"syntax not allowed: {type(node).__name__}")


def parse_simple_expr(text: str, names: Mapping[str, sp.Basic]) -> sp.Expr | None:
    """Parse short prose arithmetic into SymPy without evaluating any string. ``names`` maps the
    identifiers allowed to appear to their symbols. Returns ``None`` for anything outside the grammar."""
    if not text or len(text) > MAX_SIMPLE_EXPR_CHARS:
        return None
    s = re.sub(r"\|([^|]*)\|", r"Abs(\1)", text)
    tokens = _tokenize(s)
    if tokens is None or not tokens:
        return None
    for kind, val in tokens:
        if kind == "name" and val not in names and val not in _FUNCS and val not in _CONSTS:
            return None
    # rename every identifier to a neutral placeholder so Python keywords (lambda, in, not) parse
    alias: dict[str, str] = {}
    safe_tokens: list[tuple[str, str]] = []
    for kind, val in tokens:
        if kind == "name" and val not in _FUNCS and val not in _CONSTS:
            alias.setdefault(val, f"v{len(alias)}")
            safe_tokens.append((kind, alias[val]))
        else:
            safe_tokens.append((kind, val))
    safe_names = {**names, **{a: names[v] for v, a in alias.items()}}  # a symbol named E or re keeps priority
    try:
        tree = ast.parse(_with_implicit_multiplication(safe_tokens), mode="eval")
        e = _build(tree, safe_names)
    except (UnsafeExpression, SyntaxError, ValueError, TypeError, ZeroDivisionError, RecursionError):
        return None
    except Exception:
        return None
    return e if isinstance(e, sp.Expr) else None
