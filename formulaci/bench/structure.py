"""Light-weight structural scan of a LaTeX formula body, used to find mutation sites.

It does not build values (that is ``oracle``'s job); it only finds where the atoms (factors),
additive terms, fractions, exponents and sum/product/integral bounds are, as token ranges.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .oracle import _FUNCS, _GREEK, _PFUNCS, _RELS, Tok, tokenize

_SPACING = {"\\,", "\\;", "\\!", "\\:", "\\ ", "\\displaystyle", "\\textstyle", "\\left", "\\right",
            "\\bigl", "\\bigr", "\\Bigl", "\\Bigr", "\\big", "\\Big"}
_MULOPS = {"\\cdot", "\\times", "*", "/"}
_FRACS = {"\\frac", "\\dfrac", "\\tfrac"}


@dataclass
class Atom:
    kind: str  # num | sym | frac | sqrt | binom | func | pfunc | group | abs | bigop | deriv | const
    a: int  # token index range [a, b)
    b: int
    ctx: str  # "body" | "script" (inside ^/_ argument) | "bound" (bigop bounds)
    extra: dict = field(default_factory=dict)


@dataclass
class Group:
    """An expression region: a sequence of terms separated by +/- at its own level."""
    a: int
    b: int
    ctx: str
    terms: list[tuple[int, int, int | None]] = field(default_factory=list)  # (a, b, sign_tok)
    products: list[list[Atom]] = field(default_factory=list)


@dataclass
class Scan:
    text: str
    toks: list[Tok]
    sides: list[tuple[int, int]]
    rel_toks: list[int]
    atoms: list[Atom] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    bigops: list[dict] = field(default_factory=list)  # {tok, lower:(a,b), upper:(a,b), var}
    protected: set[int] = field(default_factory=set)  # token indices never to touch

    def span(self, a: int, b: int) -> tuple[int, int]:
        return self.toks[a].start, self.toks[b - 1].end

    def src(self, a: int, b: int) -> str:
        s, e = self.span(a, b)
        return self.text[s:e]


class _Scanner:
    def __init__(self, text: str):
        self.text = text
        self.toks = tokenize(text)
        self.match = _match_brackets(self.toks)
        rel = [i for i, t in enumerate(self.toks) if t.text in _RELS and self._depth0(i)]
        bounds = [-1, *rel, len(self.toks)]
        sides = [(bounds[k] + 1, bounds[k + 1]) for k in range(len(bounds) - 1)]
        self.scan = Scan(text, self.toks, sides, rel)

    def _depth0(self, i: int) -> bool:
        d = 0
        for t in self.toks[:i]:
            d += t.text in ("{", "(", "[")
            d -= t.text in ("}", ")", "]")
        return d == 0

    def skip(self, i: int, hi: int) -> int:
        while i < hi and self.toks[i].text in _SPACING:
            i += 1
        return i

    def run(self) -> Scan:
        for a, b in self.scan.sides:
            self.group(a, b, "body")
        return self.scan

    # -- groups / terms / products ---------------------------------------------------------
    def group(self, a: int, b: int, ctx: str) -> None:
        g = Group(a, b, ctx)
        i = self.skip(a, b)
        term_start, sign = i, None
        if i < b and self.toks[i].text in ("+", "-"):
            sign = i
            i += 1
        product: list[Atom] = []
        while True:
            i = self.skip(i, b)
            if i >= b:
                break
            t = self.toks[i]
            if t.text in ("+", "-", "\\pm"):
                g.terms.append((term_start, i, sign))
                if len(product) >= 2:
                    g.products.append(product)
                product = []
                term_start, sign = i, i
                i += 1
                continue
            if t.text in _MULOPS:
                i += 1
                continue
            if t.text in _RELS or t.text in (",", "&", ".", ";") or t.kind == "text":
                i += 1
                continue
            atom, i = self.atom(i, b, ctx)
            if atom is None:
                i += 1
                continue
            product.append(atom)
        if term_start < b:
            g.terms.append((term_start, b, sign))
        if len(product) >= 2:
            g.products.append(product)
        self.scan.groups.append(g)

    def atom(self, i: int, hi: int, ctx: str) -> tuple[Atom | None, int]:
        toks = self.toks
        t = toks[i]
        x, k = t.text, t.kind
        start = i
        kind = "sym"
        extra: dict = {}
        if x in ("{", "(", "["):
            j = self.match.get(i)
            if j is None:
                return None, i + 1
            self.group(i + 1, j, ctx)
            i, kind = j + 1, "group"
        elif x == "|":
            j = next((m for m in range(i + 1, hi) if toks[m].text == "|"), None)
            if j is None:
                return None, i + 1
            self.group(i + 1, j, ctx)
            i, kind = j + 1, "abs"
        elif k == "num":
            i, kind = i + 1, "num"
        elif k == "letter" or (k == "name" and len(x) == 1 and x not in _PFUNCS):
            i = self.script(i + 1, hi, "_", ctx)
        elif x in _FRACS:
            na, nb, i = self.brace_arg(i + 1, hi)
            da, db, i = self.brace_arg(i, hi)
            if _is_deriv(toks[na:nb], toks[da:db]):
                kind = "deriv"
                self.scan.protected.update(range(start, i))
            else:
                kind = "frac"
                extra = {"num": (na, nb), "den": (da, db)}
                self.group(na, nb, ctx)
                self.group(da, db, ctx)
        elif x == "\\sqrt":
            i = self.skip(i + 1, hi)
            if i < hi and toks[i].text == "[":
                j = self.match.get(i, i)
                self.group(i + 1, j, "script")
                i = j + 1
            a, b, i = self.brace_arg(i, hi)
            self.group(a, b, ctx)
            kind = "sqrt"
        elif x in ("\\binom", "\\tbinom", "\\dbinom"):
            a1, b1, i = self.brace_arg(i + 1, hi)
            a2, b2, i = self.brace_arg(i, hi)
            self.group(a1, b1, ctx)
            self.group(a2, b2, ctx)
            kind, extra = "binom", {"args": [(a1, b1), (a2, b2)]}
        elif x in ("\\sum", "\\prod", "\\int"):
            return self.bigop(i, hi, ctx)
        elif x in _FUNCS:
            kind = "func"
            i = self.script(i + 1, hi, "^", ctx)
            i = self.script(i, hi, "_", ctx)
            j = self.skip(i, hi)
            if j < hi and toks[j].text in ("(", "["):
                m = self.match.get(j, j)
                self.group(j + 1, m, ctx)
                i = m + 1
            else:  # argument: a run of atoms up to the next operator or function
                arg_start = j
                while True:
                    j = self.skip(i, hi)
                    if j >= hi or toks[j].text in ("+", "-", "\\pm", *_MULOPS, *_RELS, ",") \
                            or (toks[j].text == "|" and j != arg_start) \
                            or toks[j].text in _FUNCS or toks[j].text in _PFUNCS or toks[j].kind == "text" \
                            or toks[j].text in ("}", ")", "]", "\\sum", "\\prod", "\\int"):
                        break
                    if j == arg_start and toks[j].text == "-":
                        break
                    _, i = self.atom(j, hi, ctx)
                    if i <= j:
                        break
            extra = {"name": x}
        elif x in _PFUNCS:
            j = self.skip(i + 1, hi)
            if j < hi and toks[j].text == "(":
                m = self.match.get(j, j)
                self.group(j + 1, m, ctx)
                i = m + 1
            else:
                i = j
            kind, extra = "pfunc", {"name": x}
        elif k == "cmd" and (x[1:] in _GREEK or x in ("\\pi", "\\infty")):
            kind = "const" if x in ("\\pi", "\\infty") else "sym"
            i = self.script(i + 1, hi, "_", ctx)
        else:
            return None, i + 1
        # postfix: ^ and !
        while True:
            j = self.skip(i, hi)
            if j < hi and toks[j].text == "^":
                i = self.script(j, hi, "^", ctx)
            elif j < hi and toks[j].text == "!":
                i = j + 1
            else:
                break
        at = Atom(kind, start, i, ctx, extra)
        self.scan.atoms.append(at)
        return at, i

    def script(self, i: int, hi: int, which: str, ctx: str) -> int:
        j = self.skip(i, hi)
        if j < hi and self.toks[j].text == which:
            a, b, end = self.script_arg(j + 1, hi)
            if which == "^":
                self.group(a, b, "script")
                self.scan.atoms.append(Atom("exponent", j, end, ctx, {"arg": (a, b)}))
            else:
                self.scan.protected.update(range(j, end))
            return end
        return i

    def script_arg(self, i: int, hi: int) -> tuple[int, int, int]:
        j = self.skip(i, hi)
        if j < hi and self.toks[j].text == "{":
            m = self.match.get(j, j)
            return j + 1, m, m + 1
        return j, j + 1, j + 1

    def brace_arg(self, i: int, hi: int) -> tuple[int, int, int]:
        j = self.skip(i, hi)
        if j < hi and self.toks[j].text == "{":
            m = self.match.get(j, j)
            return j + 1, m, m + 1
        return j, j + 1, j + 1

    def bigop(self, i: int, hi: int, ctx: str) -> tuple[Atom, int]:
        toks = self.toks
        start = i
        info: dict = {"tok": i, "op": toks[i].text}
        i += 1
        for _ in range(2):
            j = self.skip(i, hi)
            if j < hi and toks[j].text in ("_", "^"):
                a, b, i = self.script_arg(j + 1, hi)
                info["lower" if toks[j].text == "_" else "upper"] = (a, b)
                self.scan.protected.add(j)
        lo = info.get("lower")
        if lo and toks[lo[0]].kind == "letter" and lo[1] - lo[0] >= 3 and toks[lo[0] + 1].text == "=":
            info["var"] = toks[lo[0]].text
            self.scan.protected.update((lo[0], lo[0] + 1))
        if info["op"] == "\\int":
            # integrand runs to the differential "d<var>"
            j = i
            while j < hi - 1 and not (toks[j].text == "d" and toks[j + 1].kind == "letter"
                                      and (j == 0 or toks[j - 1].text in ("\\,", "\\;", "\\!") or toks[j].kind == "name")):
                j += 1
            body = (i, j)
            self.scan.protected.update((j, j + 1))
            end = min(j + 2, hi)
        else:
            body_start = self.skip(i, hi)
            end = body_start
            while True:
                j = self.skip(end, hi)
                if j >= hi or toks[j].text in ("+", "-", "\\pm", *_RELS, ",") or toks[j].kind == "text" \
                        or toks[j].text in ("}", ")", "]"):
                    break
                if toks[j].text in _MULOPS:
                    end = j + 1
                    continue
                _, nxt = self.atom(j, hi, ctx)
                if nxt <= j:
                    break
                end = nxt
            body = (body_start, end)
        self.group(body[0], body[1], ctx)
        info["body"] = body
        self.scan.bigops.append(info)
        at = Atom("bigop", start, end, ctx, info)
        self.scan.atoms.append(at)
        return at, end


def _match_brackets(toks: list[Tok]) -> dict[int, int]:
    pairs = {"{": "}", "(": ")", "[": "]"}
    stack: list[int] = []
    out: dict[int, int] = {}
    for i, t in enumerate(toks):
        if t.text in pairs:
            stack.append(i)
        elif t.text in pairs.values():
            # ignore unmatched closers (e.g. "[a, b)" intervals never occur in bodies we scan)
            while stack and pairs[toks[stack[-1]].text] != t.text:
                stack.pop()
            if stack:
                out[stack.pop()] = i
    return out


def _is_deriv(num: list[Tok], den: list[Tok]) -> bool:
    n = [t.text for t in num if t.text not in _SPACING]
    d = [t.text for t in den if t.text not in _SPACING]
    return bool(n) and n[0] in ("d", "\\partial") and (len(n) == 1 or n[1] == "^") \
        and len(d) >= 2 and d[0] in ("d", "\\partial")


def scan(body: str) -> Scan:
    return _Scanner(body).run()


def balanced(s: str) -> bool:
    depth = 0
    for t in tokenize(s):
        depth += t.text == "{"
        depth -= t.text == "}"
        if depth < 0:
            return False
    return depth == 0
