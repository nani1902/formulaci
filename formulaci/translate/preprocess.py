"""Preprocessing of Wikipedia LaTeX before parsing.

Pipeline (all at token level, after `lexer.tokenize`):

1. `normalize_source`   - unicode math characters -> LaTeX, `\\over`/`\\choose` -> `\\frac`/`\\binom`
2. `clean_tokens`       - drop style/size/spacing-free commands, resolve `\\left`/`\\right`,
                           `\\stackrel{def}{=}` -> `:=`, `\\tag`, `\\label`, `\\color`, `\\phantom`
3. `split_rows`         - `align`/`aligned`/`gather`/... environments and bare `\\\\` rows ->
                           a list of rows (continuation rows `&= ...` are joined into one chain)
4. `split_conditions`   - trailing `\\quad x>0`, `\\text{for } n\\ge1`, `, |x|<1` -> condition,
                           `a=b, \\quad c=d` -> two segments; trailing punctuation dropped

Each step appends short tags to `notes` (e.g. `pre:left_right`) so the record says what was done.
"""
from __future__ import annotations

import re

from .lexer import Tok, tokenize

ALIGN_ENVS = {
    "align", "align*", "aligned", "alignat", "alignat*", "alignedat", "eqnarray", "eqnarray*",
    "gather", "gather*", "gathered", "split", "multline", "multline*", "flalign", "flalign*",
    "equation", "equation*", "displaymath",
}
MATRIX_ENVS = {
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix", "smallmatrix", "array",
    "tabular", "subarray",
}

# Commands removed outright (no argument).
DROP_CMDS = {
    "displaystyle", "textstyle", "scriptstyle", "scriptscriptstyle", "limits", "nolimits",
    "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "Biggl",
    "Biggr", "bigm", "Bigm", "biggm", "Biggm", "mathstrut", "strut", "nonumber", "notag",
    "allowbreak", "nobreak", "relax", "displaylimits", "middle",
}
# Commands removed together with their brace argument.
DROP_WITH_ARG = {"tag", "label", "phantom", "hphantom", "vphantom", "color", "mathchoice", "ref"}
# Commands that are kept as their argument (wrapper only).
UNWRAP = {"boxed", "mathit", "mathnormal", "mathsf", "mathtt", "emph", "fbox", "cancel", "bcancel", "xcancel"}

UNICODE = {
    "−": "-", "–": "-", "×": r"\times ", "⋅": r"\cdot ", "·": r"\cdot ",
    "≤": r"\le ", "≥": r"\ge ", "≠": r"\ne ", "≈": r"\approx ",
    "∞": r"\infty ", "→": r"\to ", "∈": r"\in ", "′": "'", "±": r"\pm ",
    "…": r"\ldots ", "⋯": r"\cdots ", "∂": r"\partial ", "√": r"\sqrt ",
    "π": r"\pi ", "α": r"\alpha ", "β": r"\beta ", "γ": r"\gamma ",
    "δ": r"\delta ", "ε": r"\varepsilon ", "θ": r"\theta ", "λ": r"\lambda ",
    "μ": r"\mu ", "σ": r"\sigma ", "φ": r"\varphi ", "ω": r"\omega ",
    "Γ": r"\Gamma ", "Δ": r"\Delta ", "Σ": r"\Sigma ", "Ω": r"\Omega ",
    " ": " ", " ": r"\, ", "​": "",
}

RELATION_CMDS = {
    "le", "leq", "leqslant", "leqq", "ge", "geq", "geqslant", "geqq", "ne", "neq", "lt", "gt",
    "approx", "simeq", "sim", "cong", "propto", "to", "rightarrow", "longrightarrow", "mapsto",
    "in", "notin", "ni", "subset", "subseteq", "supset", "supseteq", "Rightarrow", "Leftarrow",
    "Leftrightarrow", "implies", "iff", "impliedby", "Longrightarrow", "Longleftrightarrow",
    "ll", "gg", "asymp", "equiv", "triangleq", "coloneqq", "eqqcolon", "doteq", "approxeq",
    "eqsim", "lesssim", "gtrsim", "nless", "ngtr", "perp", "parallel", "colon", "defeq",
}
RELATION_CHARS = {"=", "<", ">", ":=", "=:"}

# Prose that introduces a condition after the formula proper.
COND_WORDS = re.compile(
    r"^\s*\(?\s*(for|if|when|where|whenever|with|as|since|provided|unless|and|or|all|"
    r"except|otherwise|valid|on|in|at|given|assuming|so|such)\b", re.I)


def normalize_source(latex: str, notes: list[str]) -> str:
    s = latex
    if any(ch in s for ch in UNICODE):
        for k, v in UNICODE.items():
            s = s.replace(k, v)
        notes.append("pre:unicode")
    s = s.replace("\n", " ").strip()
    # strip HTML entities that sometimes leak in
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&nbsp;", " ")
    if re.search(r"\\(over|choose|atop)(?![a-zA-Z])", s):
        s = _rewrite_infix_frac(s)
        notes.append("pre:over_choose")
    return s


def _rewrite_infix_frac(s: str) -> str:
    """`{a \\over b}` -> `{\\frac{a}{b}}`, `{n \\choose k}` -> `{\\binom{n}{k}}`.

    Works on the innermost brace group containing the infix command; if none, the whole string.
    """
    pat = re.compile(r"\\(over|choose|atop)(?![a-zA-Z])")
    for _ in range(20):
        m = pat.search(s)
        if not m:
            break
        # find enclosing brace group
        depth = 0
        start = 0
        for j in range(m.start() - 1, -1, -1):
            c = s[j]
            if c == "}" and (j == 0 or s[j - 1] != "\\"):
                depth += 1
            elif c == "{" and (j == 0 or s[j - 1] != "\\"):
                if depth == 0:
                    start = j + 1
                    break
                depth -= 1
        else:
            start = 0
        depth = 0
        end = len(s)
        for j in range(m.end(), len(s)):
            c = s[j]
            if c == "{" and s[j - 1] != "\\":
                depth += 1
            elif c == "}" and s[j - 1] != "\\":
                if depth == 0:
                    end = j
                    break
                depth -= 1
        a, b = s[start:m.start()], s[m.end():end]
        cmd = {"over": "\\frac", "choose": "\\binom", "atop": "\\atopfrac"}[m.group(1)]
        s = s[:start] + f"{cmd}{{{a}}}{{{b}}}" + s[end:]
    return s


def _group_end(toks: list[Tok], i: int) -> int:
    """toks[i] is '{'; return index of the matching '}'."""
    depth = 0
    for j in range(i, len(toks)):
        t = toks[j]
        if t.kind == "CHAR" and t.value == "{":
            depth += 1
        elif t.kind == "CHAR" and t.value == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced braces")


LEFT_MAP = {
    ("CHAR", "("): Tok("CHAR", "(", 0, 0), ("CHAR", "["): Tok("CHAR", "[", 0, 0),
    ("CMD", "{"): Tok("CHAR", "(", 0, 0), ("CMD", "lbrace"): Tok("CHAR", "(", 0, 0),
    ("CMD", "lbrack"): Tok("CHAR", "[", 0, 0),
    ("CHAR", "|"): Tok("CMD", "lvert", 0, 0), ("CMD", "vert"): Tok("CMD", "lvert", 0, 0),
    ("CMD", "lvert"): Tok("CMD", "lvert", 0, 0), ("CMD", "|"): Tok("CMD", "lVert", 0, 0),
    ("CMD", "Vert"): Tok("CMD", "lVert", 0, 0), ("CMD", "lVert"): Tok("CMD", "lVert", 0, 0),
    ("CMD", "langle"): Tok("CMD", "langle", 0, 0), ("CMD", "lfloor"): Tok("CMD", "lfloor", 0, 0),
    ("CMD", "lceil"): Tok("CMD", "lceil", 0, 0),
}
RIGHT_MAP = {
    ("CHAR", ")"): Tok("CHAR", ")", 0, 0), ("CHAR", "]"): Tok("CHAR", "]", 0, 0),
    ("CMD", "}"): Tok("CHAR", ")", 0, 0), ("CMD", "rbrace"): Tok("CHAR", ")", 0, 0),
    ("CMD", "rbrack"): Tok("CHAR", "]", 0, 0),
    ("CHAR", "|"): Tok("CMD", "rvert", 0, 0), ("CMD", "vert"): Tok("CMD", "rvert", 0, 0),
    ("CMD", "rvert"): Tok("CMD", "rvert", 0, 0), ("CMD", "|"): Tok("CMD", "rVert", 0, 0),
    ("CMD", "Vert"): Tok("CMD", "rVert", 0, 0), ("CMD", "rVert"): Tok("CMD", "rVert", 0, 0),
    ("CMD", "rangle"): Tok("CMD", "rangle", 0, 0), ("CMD", "rfloor"): Tok("CMD", "rfloor", 0, 0),
    ("CMD", "rceil"): Tok("CMD", "rceil", 0, 0),
}


def _retok(proto: Tok, src: Tok) -> Tok:
    return Tok(proto.kind, proto.value, src.start, src.end)


def clean_tokens(toks: list[Tok], notes: list[str]) -> list[Tok]:
    out: list[Tok] = []
    tags: set[str] = set()
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        if t.kind == "CMD":
            v = t.value
            if v in DROP_CMDS:
                tags.add("style" if v.endswith("style") else ("size" if v.startswith(("big", "Big")) else "drop"))
                i += 1
                continue
            if v in DROP_WITH_ARG:
                tags.add("drop_" + v)
                j = i + 1
                if v == "color" and j < n and toks[j].is_("CHAR", "{"):
                    i = _group_end(toks, j) + 1
                    continue
                if j < n and toks[j].is_("CHAR", "{"):
                    i = _group_end(toks, j) + 1
                    continue
                i = j + 1
                continue
            if v in UNWRAP:
                tags.add("unwrap")
                i += 1
                continue
            if v in ("left", "right"):
                tags.add("left_right")
                if i + 1 >= n:
                    i += 1
                    continue
                d = toks[i + 1]
                if d.is_("CHAR", "."):
                    i += 2
                    continue
                table = LEFT_MAP if v == "left" else RIGHT_MAP
                key = (d.kind, d.value)
                if key in table:
                    out.append(_retok(table[key], d))
                else:
                    out.append(d)
                i += 2
                continue
            if v in ("stackrel", "overset") and i + 2 < n:
                # \stackrel{\text{def}}{=} / \overset{def}{=} -> :=
                j = i + 1
                if toks[j].is_("CHAR", "{"):
                    e1 = _group_end(toks, j)
                    top = toks[j + 1:e1]
                    k = e1 + 1
                    if k < n and toks[k].is_("CHAR", "{"):
                        e2 = _group_end(toks, k)
                        base = toks[k + 1:e2]
                    elif k < n:
                        e2 = k
                        base = [toks[k]]
                    else:
                        out.append(t)
                        i += 1
                        continue
                    toptext = "".join(x.value for x in top).lower()
                    if len(base) == 1 and base[0].is_("CHAR", "=") and (
                            "def" in toptext or toptext in ("!", "δ", "delta", "△", "triangle", "")):
                        out.append(Tok("CHAR", ":=", t.start, toks[e2].end))
                        tags.add("stackrel_def")
                        i = e2 + 1
                        continue
                    if len(base) == 1 and base[0].is_("CHAR", "="):
                        # e.g. \overset{(1)}{=}: an annotated equals sign
                        out.append(Tok("CHAR", "=", t.start, toks[e2].end))
                        tags.add("annotated_eq")
                        i = e2 + 1
                        continue
            if v in ("lt", "gt"):
                out.append(Tok("CHAR", "<" if v == "lt" else ">", t.start, t.end))
                i += 1
                continue
            if v in ("coloneqq", "defeq", "triangleq", "eqqcolon"):
                out.append(Tok("CHAR", ":=", t.start, t.end))
                tags.add("def_symbol")
                i += 1
                continue
        if t.kind == "SPACE" and t.value == "!":
            tags.add("spacing")
            i += 1
            continue
        if t.kind == "CHAR" and t.value == "{" and i + 1 < n and toks[i + 1].is_("CHAR", "}"):
            # empty group {} (e.g. before a prescript): keep only if followed by _ (hypergeometric)
            if i + 2 < n and toks[i + 2].is_("CHAR", "_"):
                out.append(Tok("CMD", "emptygroup", t.start, toks[i + 1].end))
            i += 2
            continue
        out.append(t)
        i += 1
    for j in range(1, len(out)):
        t = out[j]
        if t.kind == "CMD" and t.value in RELATION_CMDS and out[j - 1].kind == "CHAR" and out[j - 1].value in "_^":
            # `v_\perp`, `\epsilon_\parallel`: a label, not a relation; `W^\perp` stays unsupported
            out[j] = Tok("TEXT", t.value, t.start, t.end) if out[j - 1].value == "_" else Tok("CMD", "perp_sup", t.start, t.end)
            tags.add("script_relation_symbol")
    out = _font_switches(out, tags)
    out = _unwrap_single_command_groups(out, tags)
    out = _unwrap_braced_parens(out, tags)
    if any(t.kind == "SPACE" for t in out):
        tags.add("spacing")
    notes.extend(sorted("pre:" + x for x in tags))
    return out


# Commands whose following brace group is an argument, not a grouping.
ARG_CMDS = {
    "frac", "dfrac", "tfrac", "cfrac", "binom", "tbinom", "dbinom", "sqrt", "mathrm", "mathbf", "mathbb",
    "mathcal", "boldsymbol", "bm", "vec", "hat", "widehat", "bar", "overline", "tilde", "widetilde", "dot",
    "ddot", "underline", "overbrace", "underbrace", "stackrel", "overset", "underset", "mathit", "rm",
    "operatorname", "begin", "end", "left", "right", "mathop", "pmod", "color",
}


FONT_SWITCH = {"rm": "mathrm", "it": "mathit", "bf": "mathbf", "sf": "mathsf", "tt": "mathtt", "cal": "mathcal"}


def _unwrap_single_command_groups(toks: list[Tok], tags: set[str]) -> list[Tok]:
    """`{\\exp}\\bigl(…\\bigr)` -> `\\exp(…)`: braces around a lone argument-free command."""
    out = list(toks)
    i = 0
    while i + 2 < len(out):
        a, b, c = out[i], out[i + 1], out[i + 2]
        prev = out[i - 1] if i > 0 else None
        if (a.is_("CHAR", "{") and b.kind == "CMD" and b.value.isalpha() and b.value not in ARG_CMDS
                and b.value not in FONT_SWITCH and c.is_("CHAR", "}")
                and not (prev is not None and (prev.kind == "CMD" or prev.is_("CHAR", "_") or prev.is_("CHAR", "^")))):
            out[i:i + 3] = [b]
            tags.add("single_command_group")
        i += 1
    return out


def _font_switches(toks: list[Tok], tags: set[str]) -> list[Tok]:
    """`{\\rm cas}(x)` -> `\\mathrm{cas}(x)`: a TeX font switch applies to the rest of its group."""
    out = list(toks)
    i = 0
    while i < len(out):
        t = out[i]
        if t.kind == "CMD" and t.value in FONT_SWITCH and not (i + 1 < len(out) and out[i + 1].is_("CHAR", "{")):
            # find the end of the enclosing group (or of the token list)
            depth = 0
            j = i + 1
            while j < len(out):
                if out[j].is_("CHAR", "{"):
                    depth += 1
                elif out[j].is_("CHAR", "}"):
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            body = out[i + 1:j]
            new = [Tok("CMD", FONT_SWITCH[t.value], t.start, t.end), Tok("CHAR", "{", t.start, t.end)] + body + [
                Tok("CHAR", "}", t.end, t.end)]
            script_arg = i > 1 and out[i - 2].kind == "CHAR" and out[i - 2].value in "^_"
            if i > 0 and out[i - 1].is_("CHAR", "{") and j < len(out) and not script_arg:
                out[i - 1:j + 1] = new  # `{\rm sinc}` -> `\mathrm{sinc}` (the group was only the switch)
                i += 1
            else:
                out[i:j] = new
                i += 2
            tags.add("font_switch")
            continue
        i += 1
    return out


def _unwrap_braced_parens(toks: list[Tok], tags: set[str]) -> list[Tok]:
    """`\\Phi{\\left(x\\right)}` -> `\\Phi(x)`: a brace group holding exactly one bracket group."""
    out = list(toks)
    i = 0
    while i < len(out):
        prev = out[i - 1] if i > 0 else None
        name_before = prev is not None and (prev.kind in ("LETTER", "OPNAME") or (
            prev.kind == "CMD" and prev.value.isalpha() and prev.value not in ARG_CMDS))
        if (name_before and out[i].is_("CHAR", "{") and i + 1 < len(out) and out[i + 1].kind == "CHAR"
                and out[i + 1].value in "(["):
            try:
                e = _group_end(out, i)
                inner_end = _match(out, i + 1)
            except ValueError:
                i += 1
                continue
            if inner_end == e - 1:
                del out[e]
                del out[i]
                tags.add("braced_parens")
                continue
        i += 1
    return out


def _match(toks: list[Tok], i: int) -> int:
    depth = 0
    for j in range(i, len(toks)):
        t = toks[j]
        if t.kind == "CHAR" and t.value in "([{":
            depth += 1
        elif t.kind == "CHAR" and t.value in ")]}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced")


def _depth_delta(t: Tok) -> int:
    if t.kind == "CHAR" and t.value in "([{":
        return 1
    if t.kind == "CHAR" and t.value in ")]}":
        return -1
    if t.kind == "BEGIN":
        return 1
    if t.kind == "END":
        return -1
    if t.kind == "CMD" and t.value in ("lvert", "lVert", "langle", "lfloor", "lceil"):
        return 1
    if t.kind == "CMD" and t.value in ("rvert", "rVert", "rangle", "rfloor", "rceil"):
        return -1
    return 0


def is_relation(t: Tok) -> bool:
    return (t.kind == "CHAR" and t.value in RELATION_CHARS) or (t.kind == "CMD" and t.value in RELATION_CMDS)


def split_rows(toks: list[Tok], notes: list[str], unsupported: list[str]) -> list[list[Tok]]:
    """Split alignment environments and top-level `\\\\` into logical rows.

    A row starting with a relation continues the previous row's chain (`A &= B \\\\ &= C`);
    a row starting with a binary operator continues the previous row's expression.
    """
    # Unwrap a single outer alignment env that spans the whole formula.
    body = toks
    if toks and toks[0].kind == "BEGIN" and toks[0].value in ALIGN_ENVS:
        name = toks[0].value
        depth = 0
        for j, t in enumerate(toks):
            depth += _depth_delta(t)
            if depth == 0:
                break
        if depth == 0 and j == len(toks) - 1 or (j < len(toks) - 1 and all(
                x.kind == "SPACE" or x.is_("CHAR", ".") or x.is_("CHAR", ",") for x in toks[j + 1:])):
            body = toks[1:j]
            notes.append(f"pre:env_{name.rstrip('*')}")
            if name.startswith("alignat") and body and body[0].is_("CHAR", "{"):
                body = body[_group_end(body, 0) + 1:]
    # Any other environment left at top level other than cases is unsupported.
    raw_rows: list[list[Tok]] = [[]]
    depth = 0
    env_depth = 0
    amps = 0
    for k, t in enumerate(body):
        if t.kind == "BEGIN":
            env_depth += 1
        elif t.kind == "END":
            env_depth -= 1
        if depth > 0 and env_depth == 0 and (t.kind == "ROWSEP" or t.is_("CHAR", "&")):
            continue  # a line break inside brackets just continues the expression
        if t.kind == "BEGIN" and depth == 0 and t.value in ALIGN_ENVS:
            # nested alignment env inside an expression, e.g. `f = \begin{aligned}..`: flatten
            notes.append(f"pre:env_{t.value.rstrip('*')}")
            continue
        if t.kind == "END" and depth == 0 and t.value in ALIGN_ENVS:
            continue
        depth += _depth_delta(t)
        if t.kind == "ROWSEP" and depth == 0:
            raw_rows.append([])
            amps = 0
            continue
        if t.is_("CHAR", "&") and depth == 0:
            amps += 1
            if amps > 1 and not (k > 0 and body[k - 1].is_("CHAR", "&")):
                # a later column: `lhs &= rhs && x \ne 0` -> condition column, unless the
                # column just continues the chain (`&&= ...`)
                nxt = next((x for x in body[k + 1:] if x.kind != "SPACE" and not x.is_("CHAR", "&")), None)
                if nxt is not None and not is_relation(nxt):
                    raw_rows[-1].append(Tok("SPACE", "colsep", t.start, t.end))
                    notes.append("pre:align_column_separator")
            continue
        raw_rows[-1].append(t)
    rows: list[list[Tok]] = []
    for r in raw_rows:
        r = _strip_equation_number(r, notes)
        content = [t for t in r if t.kind != "SPACE"]
        if not content:
            continue
        first = content[0]
        r = r[next(i for i, t in enumerate(r) if t.kind != "SPACE"):]
        if rows and (is_relation(first)):
            rows[-1].extend(r)
            notes.append("pre:row_continues_chain")
            continue
        prev = [t for t in rows[-1] if t.kind != "SPACE"] if rows else []
        prev_open = bool(prev) and (prev[-1].kind == "CHAR" and prev[-1].value in "+-" or prev[-1].is_("CMD", "cdot")
                                    or prev[-1].is_("CMD", "times"))
        starts_op = first.kind == "CHAR" and first.value in "+-" or first.is_("CMD", "cdot") or first.is_("CMD", "times")
        # `A = B \\ -C = D` is a new equation that happens to start with a minus sign
        own_relation = _row_has_relation(r)
        if rows and (prev_open or (starts_op and not own_relation)):
            rows[-1].extend(r)
            notes.append("pre:row_continues_expr")
            continue
        rows.append(list(r))
    if len(rows) > 1:
        notes.append(f"pre:rows={len(rows)}")
    for t in toks:
        if t.kind == "BEGIN" and t.value in MATRIX_ENVS:
            unsupported.append("matrix")
            break
    return rows


def _strip_equation_number(row: list[Tok], notes: list[str]) -> list[Tok]:
    """`(16)\\quad B_{21} = …`: a leading equation number followed by spacing is a tag, not a factor."""
    core = [k for k, t in enumerate(row) if t.kind != "SPACE"]
    if len(core) < 4:
        return row
    k0 = core[0]
    if not row[k0].is_("CHAR", "("):
        return row
    k = k0 + 1
    while k < len(row) and (row[k].kind == "DIGIT" or row[k].is_("CHAR", ".")):
        k += 1
    if k == k0 + 1 or k >= len(row) or not row[k].is_("CHAR", ")"):
        return row
    if k + 1 < len(row) and row[k + 1].kind == "SPACE" and row[k + 1].value in ("quad", "qquad", "enspace", " ", ";"):
        notes.append("pre:equation_number")
        return row[k + 1:]
    return row


def _row_has_relation(row: list[Tok]) -> bool:
    depth = 0
    for t in row:
        if depth == 0 and is_relation(t):
            return True
        depth += _depth_delta(t)
    return False


def _text_is_condition(text: str) -> bool:
    return bool(COND_WORDS.match(text)) or text.strip().startswith("(")


def split_conditions(row: list[Tok], src: str, notes: list[str]) -> tuple[list[list[Tok]], list[str]]:
    """Split one row into equation segments and trailing condition strings.

    Returns (segments, conditions). Conditions are LaTeX substrings of `src`.
    """
    toks = list(row)
    # strip trailing punctuation and spacing
    stripped = False
    while toks and (toks[-1].kind == "SPACE" or (toks[-1].kind == "CHAR" and toks[-1].value in ".,;:")
                    or (toks[-1].kind == "TEXT" and toks[-1].value.strip() in (".", ",", ";", ""))):
        toks.pop()
        stripped = True
    if stripped:
        notes.append("pre:trailing_punct")
    segments: list[list[Tok]] = []
    conds: list[str] = []
    rest = toks
    while rest:
        cut = _find_separator(rest)
        if cut is None:
            segments.append(rest)
            break
        head, sep_end = cut
        tail = rest[sep_end:]
        segments.append(rest[:head])
        # classify the tail: another equation, or a condition
        tail_core = [t for t in tail if t.kind != "SPACE"]
        if not tail_core:
            break
        is_cond = _tail_is_condition(rest[head:sep_end], tail_core)
        if is_cond:
            c = _cond_text(tail_core, src)
            if c:
                conds.append(c)
            break
        notes.append("pre:multi_equation")
        rest = tail
    return [s for s in segments if any(t.kind != "SPACE" for t in s)], conds


def _find_separator(toks: list[Tok]) -> tuple[int, int] | None:
    """Find the first top-level separator after a relation has been seen.

    Returns (index where head ends, index where tail starts)."""
    depth = 0
    seen_rel = False
    prev = None
    for i, t in enumerate(toks):
        d = _depth_delta(t)
        if depth == 0 and is_relation(t):
            seen_rel = True
        after_op = prev is not None and (is_relation(prev) or (prev.kind == "CHAR" and prev.value in "+-")
                                         or prev.is_("CMD", "cdot") or prev.is_("CMD", "times"))
        if t.kind != "SPACE":
            prev = t
        if depth == 0 and seen_rel and not after_op:
            if t.kind == "SPACE" and t.value in ("quad", "qquad", "hfill", "hspace", "hskip", "enspace", "colsep"):
                j = i
                while j < len(toks) and (toks[j].kind == "SPACE" or toks[j].is_("CHAR", ",") or toks[j].is_("CHAR", ";")):
                    j += 1
                return i, j
            if t.kind == "CHAR" and t.value in (",", ";"):
                # `i = 1, 2, \dots, n`: an enumeration (the parser reports it as a list). But in
                # `… = Q_j, \quad j = 1, \ldots, m` the tail starts with its own relation: a condition.
                tail_rel = next((k for k in range(i + 1, len(toks)) if is_relation(toks[k])), len(toks))
                if any(x.kind == "CMD" and x.value in ("dots", "ldots", "cdots", "dotsc", "dotsb") for x in toks[i + 1:tail_rel]):
                    return None
                j = i + 1
                while j < len(toks) and toks[j].kind == "SPACE":
                    j += 1
                return i, j
            if t.kind == "TEXT" and (_text_is_condition(t.value) or t.value.strip() == ""):
                return i, i
            if t.kind == "CMD" and t.value in ("forall", "text", "mbox"):
                return i, i
            if t.kind == "SPACE" and t.value in (";", ":", ">", " ", "~") and i + 1 < len(toks) and (
                    toks[i + 1].is_("CHAR", "(") and _paren_has_relation(toks, i + 1)):
                return i, i + 1
        depth += d
    return None


def _paren_has_relation(toks: list[Tok], i: int) -> bool:
    depth = 0
    for t in toks[i:]:
        depth += _depth_delta(t)
        if depth == 1 and is_relation(t):
            return True
        if depth == 0:
            return False
    return False


def _tail_is_condition(sep: list[Tok], tail: list[Tok]) -> bool:
    if any(t.kind == "TEXT" and t.value.strip() for t in sep + tail[:1]):
        return True
    if tail[0].is_("CMD", "forall"):
        return True
    if any(t.kind == "CMD" and t.value in ("dots", "ldots", "cdots", "dotsc", "dotsb") for t in tail):
        return True  # `\quad j = 1, \ldots, m`: an index range
    depth = 0
    rels = []
    for t in tail:
        if depth == 0 and is_relation(t):
            rels.append(t)
        depth += _depth_delta(t)
    if not rels:
        # a parenthesised condition `\quad (a>0)` or a bare list
        return True
    if all(r.kind == "CHAR" and r.value in ("=", ":=") for r in rels) and not any(
            t.kind == "TEXT" for t in tail):
        return False  # another equation
    return True


def _cond_text(tail: list[Tok], src: str) -> str:
    toks = list(tail)
    # drop leading prose like \text{for } / \text{if } / \forall / '('
    while toks and (toks[0].kind == "TEXT" or toks[0].kind == "SPACE" or toks[0].is_("CMD", "forall")):
        toks.pop(0)
    while toks and (toks[-1].kind == "SPACE" or (toks[-1].kind == "TEXT" and not re.search(r"[A-Za-z0-9]", toks[-1].value))
                    or (toks[-1].kind == "CHAR" and toks[-1].value in ".,;")):
        toks.pop()
    if not toks:
        return " ".join(t.value for t in tail if t.kind == "TEXT").strip()
    text = src[toks[0].start:toks[-1].end].strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    return text


def preprocess(latex: str, notes: list[str], unsupported: list[str]) -> tuple[str, list[tuple[list[Tok], list[str]]]]:
    """Return (normalized source, [(equation token segment, its trailing conditions)])."""
    src = normalize_source(latex, notes)
    toks = clean_tokens(tokenize(src), notes)
    rows = split_rows(toks, notes, unsupported)
    out: list[tuple[list[Tok], list[str]]] = []
    for r in rows:
        segs, cs = split_conditions(r, src, notes)
        out.extend((seg, cs) for seg in segs)
    return src, out
