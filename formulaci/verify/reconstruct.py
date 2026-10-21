"""Rebuild sympy expressions from srepr strings and apply Semantics (constants, domains, constraints).

The srepr strings come from Wikipedia LaTeX via the translate stage, so they are untrusted. They
are parsed with `ast`, every node is checked against a whitelist (calls to sympy names, string
and number literals, tuples), and only then evaluated in a namespace holding nothing but sympy
names and no builtins. Constraint strings get the same treatment with a small boolean grammar.
"""
from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass, field

import sympy as sp

from formulaci.schemas import Domain, Parsed, Semantics

# Every public sympy name that is a class or function. Modules and private names are excluded.
SYMPY_NS: dict[str, object] = {
    k: v for k, v in vars(sp).items()
    if not k.startswith("_") and not isinstance(v, type(sp))
}
# srepr spells these as bare names / calls
SYMPY_NS.update({"oo": sp.oo, "zoo": sp.zoo, "nan": sp.nan, "I": sp.I, "pi": sp.pi, "E": sp.E})
# Names that parse strings, generate code, print, plot or run tests are never callable from srepr.
_FORBIDDEN_RE = re.compile(
    r"^(S|var|symbols|python|source|sympify|parse.*|lambdify|preview|init_.*|test|doctest|plot.*|"
    r"textplot|print.*|pprint.*|pager_print|dotprint|srepr|latex|mathml|multiline_latex|evaluate|"
    r"interactive|Lambda)$"
)
# String literals are only allowed as names/numbers of these constructors.
_STRING_TAKERS = {"Symbol", "Dummy", "Wild", "Function", "IndexedBase", "Idx"}
_NUMBER_TAKERS = {"Float", "Integer", "Rational"}
_NUMBER_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(/\d+)?$")

CONSTANTS: dict[str, sp.Basic] = {
    "pi": sp.pi, "E": sp.E, "e": sp.E, "I": sp.I, "i": sp.I, "j": sp.I,
    "EulerGamma": sp.EulerGamma, "gamma": sp.EulerGamma, "GoldenRatio": sp.GoldenRatio,
    "phi": sp.GoldenRatio, "Catalan": sp.Catalan, "oo": sp.oo, "inf": sp.oo,
}

DOMAIN_ASSUMPTIONS: dict[str, dict[str, bool]] = {
    "real": {"real": True},
    "angle": {"real": True},
    "positive": {"positive": True},
    "nonneg": {"nonnegative": True},
    "integer": {"integer": True},
    "nonneg_integer": {"integer": True, "nonnegative": True},
    "positive_integer": {"integer": True, "positive": True},
    "unit_interval": {"nonnegative": True},
    "complex": {"complex": True},
}

INTEGER_TYPES = {"integer", "nonneg_integer", "positive_integer"}


class UnsafeExpression(ValueError):
    pass


def _check_srepr_ast(node: ast.AST) -> None:
    if isinstance(node, ast.Expression):
        return _check_srepr_ast(node.body)
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Call):  # Function('f')(x): an undefined function application
            inner = node.func
            if not (isinstance(inner.func, ast.Name) and inner.func.id == "Function"):
                raise UnsafeExpression("only Function(...) may be applied")
            _check_srepr_ast(inner)
            for a in node.args:
                _check_srepr_ast(a)
            if node.keywords:
                raise UnsafeExpression("no keywords in function application")
            return
        if not isinstance(node.func, ast.Name):
            raise UnsafeExpression("call target must be a plain sympy name")
        _check_srepr_ast(node.func)
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                if node.func.id in _STRING_TAKERS:
                    continue
                if node.func.id in _NUMBER_TAKERS and _NUMBER_RE.match(a.value):
                    continue
                raise UnsafeExpression(f"string argument not allowed for {node.func.id}")
            _check_srepr_ast(a)
        for kw in node.keywords:
            if kw.arg is None or kw.arg.startswith("_"):
                raise UnsafeExpression("bad keyword")
            _check_srepr_ast(kw.value)
        return
    if isinstance(node, ast.Name):
        if node.id not in SYMPY_NS or _FORBIDDEN_RE.match(node.id) or node.id.startswith("_"):
            raise UnsafeExpression(f"name not allowed: {node.id}")
        return
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (str, int, float, bool)) or node.value is None:
            raise UnsafeExpression("bad literal")
        if isinstance(node.value, str):
            raise UnsafeExpression("string literal outside a Symbol/Float constructor")
        return
    if isinstance(node, (ast.Tuple, ast.List)):
        for e in node.elts:
            _check_srepr_ast(e)
        return
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return _check_srepr_ast(node.operand)
    raise UnsafeExpression(f"syntax not allowed in srepr: {type(node).__name__}")


def from_srepr(s: str) -> sp.Basic:
    """Evaluate an srepr string after AST whitelisting. Raises UnsafeExpression or ValueError."""
    if len(s) > 200_000:
        raise UnsafeExpression("srepr too long")
    tree = ast.parse(s.strip(), mode="eval")
    _check_srepr_ast(tree)
    out = eval(compile(tree, "<srepr>", "eval"), {"__builtins__": {}}, dict(SYMPY_NS))  # noqa: S307
    if not isinstance(out, sp.Basic):
        out = sp.sympify(out)  # plain ints/floats from a degenerate srepr
    return out


# ---------------------------------------------------------------- constraints

_CMP = {ast.Lt: sp.Lt, ast.LtE: sp.Le, ast.Gt: sp.Gt, ast.GtE: sp.Ge, ast.Eq: sp.Eq, ast.NotEq: sp.Ne}
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.BitXor: operator.pow,
        ast.Mod: sp.Mod}
_CONSTRAINT_FUNCS = {"Ne", "Eq", "Lt", "Le", "Gt", "Ge", "And", "Or", "Not", "Abs", "re", "im",
                     "sqrt", "exp", "log", "sin", "cos", "tan", "Mod", "Rational", "Integer",
                     "Float", "floor", "ceiling", "gamma", "factorial"}


def parse_constraint(s: str, symbols: dict[str, sp.Symbol]) -> sp.Basic:
    """Parse a constraint like 'n >= 1', '0 < x < 1', 'Ne(x, 0)' into a sympy boolean."""
    tree = ast.parse(s.strip(), mode="eval")

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Compare):
            parts, left = [], ev(node.left)
            for op, comp in zip(node.ops, node.comparators):
                right = ev(comp)
                if type(op) not in _CMP:
                    raise UnsafeExpression("bad comparison")
                parts.append(_CMP[type(op)](left, right))
                left = right
            return sp.And(*parts)
        if isinstance(node, ast.BoolOp):
            vals = [ev(v) for v in node.values]
            return sp.And(*vals) if isinstance(node.op, ast.And) else sp.Or(*vals)
        if isinstance(node, ast.UnaryOp):
            v = ev(node.operand)
            if isinstance(node.op, ast.USub):
                return -v
            if isinstance(node.op, ast.UAdd):
                return v
            if isinstance(node.op, ast.Not):
                return sp.Not(v)
            raise UnsafeExpression("bad unary op")
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _BIN:
                raise UnsafeExpression("bad binary op")
            return _BIN[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _CONSTRAINT_FUNCS:
                raise UnsafeExpression("function not allowed in constraint")
            if node.keywords:
                raise UnsafeExpression("no keywords in constraints")
            return SYMPY_NS[node.func.id](*[ev(a) for a in node.args])
        if isinstance(node, ast.Name):
            if node.id in symbols:
                return symbols[node.id]
            if node.id in CONSTANTS and node.id not in ("e", "i", "j", "gamma", "phi"):
                return CONSTANTS[node.id]
            raise UnsafeExpression(f"unknown name in constraint: {node.id}")
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            return sp.nsimplify(node.value) if isinstance(node.value, float) else sp.Integer(node.value)
        raise UnsafeExpression(f"syntax not allowed in constraint: {type(node).__name__}")

    return ev(tree)


# ---------------------------------------------------------------- problem

@dataclass
class SymSpec:
    name: str
    symbol: sp.Symbol
    type: str = "real"
    lower: float | None = None
    upper: float | None = None
    exclude: list[float] = field(default_factory=list)
    inferred: bool = False  # True when the type came from structure (sum bound), not Semantics

    @property
    def is_integer(self) -> bool:
        return self.type in INTEGER_TYPES

    @property
    def is_complex(self) -> bool:
        return self.type == "complex"


@dataclass
class Problem:
    lhs: sp.Basic
    rhs: sp.Basic
    relation: str  # "=" or one of "<", "<=", ">", ">="
    syms: list[SymSpec]
    constraints: list[sp.Basic]
    notes: list[str] = field(default_factory=list)
    constraint_errors: list[str] = field(default_factory=list)


class NotCheckable(Exception):
    """Raised with a SKIP reason."""


_REL = {"=": "=", "==": "=", None: "=", "": "=",
        "<": "<", "\\lt": "<", "lt": "<",
        "<=": "<=", "≤": "<=", "\\le": "<=", "\\leq": "<=", "\\leqslant": "<=", "le": "<=",
        ">": ">", "\\gt": ">", "gt": ">",
        ">=": ">=", "≥": ">=", "\\ge": ">=", "\\geq": ">=", "\\geqslant": ">=", "ge": ">="}


def normalize_relation(rel: str | None, kind: str) -> str:
    r = (rel or "").strip()
    if r in _REL:
        out = _REL[r]
        if kind == "inequality" and out == "=":
            raise NotCheckable("inequality without a usable relation")
        return out
    raise NotCheckable(f"relation {r!r} is not an identity or ordering")


def _summation_bound_symbols(expr: sp.Basic) -> set[sp.Symbol]:
    out: set[sp.Symbol] = set()
    for node in expr.atoms(sp.Sum, sp.Product):
        for lim in node.limits:
            for b in lim[1:]:
                out |= b.free_symbols
    return out


def build_problem(parsed: Parsed, sem: Semantics) -> Problem:
    """Reconstruct lhs/rhs with constants and domain assumptions. Raises NotCheckable."""
    if parsed.status != "ok":
        raise NotCheckable(f"translate status {parsed.status}")
    if parsed.lhs is None or parsed.rhs is None:
        raise NotCheckable("missing lhs or rhs")
    relation = normalize_relation(parsed.relation, parsed.kind)
    try:
        lhs, rhs = from_srepr(parsed.lhs), from_srepr(parsed.rhs)
    except UnsafeExpression as e:
        raise NotCheckable(f"srepr rejected: {e}") from None
    except Exception as e:  # noqa: BLE001 - malformed srepr
        raise NotCheckable(f"srepr did not evaluate: {type(e).__name__}: {e}") from None
    for side in (lhs, rhs):
        if not isinstance(side, sp.Expr):
            raise NotCheckable(f"side is not a scalar expression ({type(side).__name__})")
        if side.atoms(sp.core.function.AppliedUndef):
            raise NotCheckable("has_undefined_function")
        if side.has(sp.MatrixBase) or side.atoms(sp.MatrixSymbol) or side.atoms(sp.Indexed):
            raise NotCheckable("matrix or indexed objects are not supported")

    # constants: match by name regardless of the symbol's own assumptions
    const_map = {}
    for s in (lhs.free_symbols | rhs.free_symbols):
        canon = sem.constants.get(s.name)
        if canon is not None:
            if canon not in CONSTANTS:
                raise NotCheckable(f"unknown constant {canon!r}")
            const_map[s] = CONSTANTS[canon]
    lhs, rhs = lhs.xreplace(const_map), rhs.xreplace(const_map)

    bound_syms = {s.name for s in _summation_bound_symbols(lhs) | _summation_bound_symbols(rhs)}
    specs: dict[str, SymSpec] = {}
    repl = {}
    for s in sorted(lhs.free_symbols | rhs.free_symbols, key=lambda t: t.name):
        dom = sem.domains.get(s.name)
        inferred = False
        if dom is None:
            if s.name in bound_syms:
                dom, inferred = Domain(type="nonneg_integer"), True
            elif s.is_integer:
                dom, inferred = Domain(type="integer"), True
            else:
                dom = Domain(type="real")
        assumptions = dict(DOMAIN_ASSUMPTIONS[dom.type])
        if dom.lower is not None and dom.lower > 0 and dom.type in ("real", "angle", "nonneg"):
            assumptions = {"positive": True}
        new = sp.Symbol(s.name, **assumptions)
        repl[s] = new
        specs[s.name] = SymSpec(s.name, new, dom.type, dom.lower, dom.upper, list(dom.exclude),
                                inferred)
    lhs, rhs = lhs.xreplace(repl), rhs.xreplace(repl)

    by_name = {n: sp_.symbol for n, sp_ in specs.items()}
    constraints, cerrs = [], []
    for c in sem.constraints:
        try:
            expr = parse_constraint(c, by_name)
        except Exception as e:  # noqa: BLE001
            cerrs.append(f"{c!r}: {e}")
            continue
        if expr is sp.true:
            continue
        if expr is sp.false:
            raise NotCheckable(f"constraint {c!r} is unsatisfiable")
        constraints.append(expr)
    notes = [f"{n} assumed {spec.type} (summation bound)" for n, spec in specs.items() if spec.inferred]
    return Problem(lhs, rhs, relation, list(specs.values()), constraints, notes, cerrs)


def bare_symbol_side(p: Problem) -> str | None:
    """If one side is a bare symbol absent from the other side, return its name."""
    for a, b in ((p.lhs, p.rhs), (p.rhs, p.lhs)):
        if isinstance(a, sp.Symbol) and a not in b.free_symbols:
            return a.name
    return None


BRANCH_FUNCS = (sp.log, sp.asin, sp.acos, sp.atan, sp.acot, sp.asec, sp.acsc, sp.asinh, sp.acosh,
                sp.atanh, sp.acoth, sp.asech, sp.acsch, sp.LambertW, sp.polylog, sp.loggamma,
                sp.arg, sp.atan2)


def has_branch_cut(expr: sp.Basic) -> bool:
    if expr.atoms(*BRANCH_FUNCS):
        return True
    for pw in expr.atoms(sp.Pow):
        b, e = pw.as_base_exp()
        if e.is_Integer:
            continue
        if b.is_positive and e.is_real:  # e.g. 2**x, exp-like
            continue
        if e.is_Rational or e.free_symbols or not e.is_integer:
            return True
    return False
