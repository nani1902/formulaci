"""Tokenizer for the Wikipedia LaTeX math dialect.

Tokens keep their character span in the source string so that stripped trailing conditions
can be reported verbatim (`cond: <latex>`).
"""
from __future__ import annotations

from dataclasses import dataclass

# Commands whose single brace argument is prose, captured raw as a TEXT token.
TEXT_CMDS = {"text", "mbox", "textrm", "textit", "textsf", "texttt", "hbox", "textnormal", "textup"}
# Spacing commands. Width is used to tell "big" separators (\quad) from thin ones (\,).
SPACING = {
    ",": 1, ":": 2, ";": 2, ">": 2, " ": 2, "enspace": 3, "thinspace": 1, "medspace": 2,
    "thickspace": 2, "quad": 4, "qquad": 5, "hfill": 5, "hspace": 3, "kern": 1, "mkern": 1,
    "mskip": 1, "hskip": 3,
}
# Commands that take a dimension argument we drop (\hspace{1em}).
SPACING_WITH_ARG = {"hspace", "kern", "mkern", "mskip", "hskip"}


@dataclass
class Tok:
    kind: str  # CMD LETTER DIGIT CHAR SPACE TEXT OPNAME ROWSEP BEGIN END
    value: str
    start: int
    end: int

    def is_(self, kind: str, value: str | None = None) -> bool:
        return self.kind == kind and (value is None or self.value == value)

    def __repr__(self) -> str:  # compact for debugging
        return f"{self.kind}:{self.value}"


class LexError(ValueError):
    pass


def _read_brace(s: str, i: int) -> tuple[str, int]:
    """s[i] == '{'; return (content, index after the matching '}')."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise LexError("unbalanced braces")


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def tokenize(s: str) -> list[Tok]:
    toks: list[Tok] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == "%":  # TeX comment to end of line
            while i < n and s[i] != "\n":
                i += 1
            continue
        if c == "\\":
            if i + 1 >= n:
                raise LexError("dangling backslash")
            d = s[i + 1]
            if d.isalpha():
                j = i + 1
                while j < n and s[j].isalpha():
                    j += 1
                name = s[i + 1:j]
                if j < n and s[j] == "*" and name in ("operatorname",):
                    j += 1
                if name in TEXT_CMDS:
                    k = _skip_ws(s, j)
                    if k < n and s[k] == "{":
                        content, k2 = _read_brace(s, k)
                        toks.append(Tok("TEXT", content, i, k2))
                        i = k2
                        continue
                    toks.append(Tok("TEXT", "", i, j))
                    i = j
                    continue
                if name == "operatorname":
                    k = _skip_ws(s, j)
                    if k < n and s[k] == "{":
                        content, k2 = _read_brace(s, k)
                        toks.append(Tok("OPNAME", content.replace(" ", "").replace("\\,", ""), i, k2))
                        i = k2
                        continue
                    raise LexError("\\operatorname without braces")
                if name in ("begin", "end"):
                    k = _skip_ws(s, j)
                    if k < n and s[k] == "{":
                        content, k2 = _read_brace(s, k)
                        kind = "BEGIN" if name == "begin" else "END"
                        toks.append(Tok(kind, content.strip(), i, k2))
                        i = k2
                        continue
                    raise LexError(f"\\{name} without environment name")
                if name in SPACING:
                    k = j
                    if name in SPACING_WITH_ARG:
                        k = _skip_ws(s, j)
                        if k < n and s[k] == "{":
                            _, k = _read_brace(s, k)
                    toks.append(Tok("SPACE", name, i, k))
                    i = k
                    continue
                toks.append(Tok("CMD", name, i, j))
                i = j
                continue
            # control symbol: \, \; \! \{ \} \| \\ etc.
            if d == "\\":
                # row separator, possibly with an optional [2pt] argument
                j = i + 2
                k = _skip_ws(s, j)
                if k < n and s[k] == "[":
                    close = s.find("]", k)
                    if close != -1 and close - k < 12:
                        j = close + 1
                toks.append(Tok("ROWSEP", "\\\\", i, j))
                i = j
                continue
            if d in SPACING:
                toks.append(Tok("SPACE", d, i, i + 2))
            elif d == "!":
                toks.append(Tok("SPACE", "!", i, i + 2))
            else:
                toks.append(Tok("CMD", d, i, i + 2))
            i += 2
            continue
        if c.isalpha():
            toks.append(Tok("LETTER", c, i, i + 1))
        elif c.isdigit():
            toks.append(Tok("DIGIT", c, i, i + 1))
        elif c == "~":
            toks.append(Tok("SPACE", "~", i, i + 1))
        elif c == "." and s.startswith("..", i):
            j = i
            while j < n and s[j] == ".":
                j += 1
            toks.append(Tok("CMD", "ldots", i, j))  # plain-text `...` / `..`
            i = j
            continue
        elif c == ":" and i + 1 < n and s[i + 1] == "=":
            toks.append(Tok("CHAR", ":=", i, i + 2))
            i += 2
            continue
        elif c == "=" and i + 1 < n and s[i + 1] == ":":
            toks.append(Tok("CHAR", "=:", i, i + 2))
            i += 2
            continue
        else:
            toks.append(Tok("CHAR", c, i, i + 1))
        i += 1
    return toks
