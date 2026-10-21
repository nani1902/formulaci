"""Extract `<math>` formulas from wikitext with section path, display flag and plain-text context.

One recursive walk over the mwparserfromhell tree does everything, in document order:
  * every `<math>` tag (at any depth: templates, refs, tables, captions) and every `{{tmath|...}}`
    becomes a formula, numbered 0.. in that order;
  * prose is rendered to plain text alongside; formulas inside things that are not prose
    (infoboxes, refs, captions, unknown templates) are walked "hidden": still extracted, with
    context taken from the surrounding prose and a `[template | param]` label;
  * other formulas appearing inside a context window are rendered as `$latex$`.
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field

import mwparserfromhell as mwp
from mwparserfromhell.nodes import (Argument, Comment, ExternalLink, Heading, HTMLEntity, Tag, Template,
                                    Text, Wikilink)
from mwparserfromhell.wikicode import Wikicode

CONTEXT_CHARS = 400

# `:<math>`, `::<math>`, `*:<math>` — an indented line that starts with the formula.
COLON_PREFIX = re.compile(r"^[ \t]*[:*#;]*:[ \t]*$")

CHEM_TAGS = {"chem", "ce"}
# Tags whose contents are not prose (still walked hidden so their formulas are extracted).
HIDDEN_TAGS = {"ref", "references", "gallery", "imagemap", "timeline", "score", "graph", "mapframe",
               "templatestyles", "syntaxhighlight", "source", "pre", "poem", "hiero", "categorytree"}
NEWLINE_TAGS = {"br", "tr", "p", "div", "li", "dd", "dt", "table"}

# Templates that render as display blocks; formulas inside them are display.
DISPLAY_TEMPLATES = {"numblk", "equation box 1", "bi", "block indent", "blockindent", "center", "centre",
                     "math display", "equation"}
# Templates whose (positional) content is prose to keep: name -> how to render.
INLINE_TEMPLATES = {
    "math": "first", "mvar": "first", "var": "first", "nowrap": "first", "nobr": "first", "nowr": "first",
    "em": "first", "strong": "first", "small": "first", "big": "first", "smallcaps": "first",
    "sub": "first", "sup": "first", "su": "first", "overline": "first", "underline": "first",
    "serif": "first", "sans-serif": "first", "mono": "first", "italics correction": "first",
    "visible anchor": "first", "vanchor": "first", "dfn": "first", "ill": "first", "bold": "first",
    "italic": "first", "nowiki": "first", "sc": "first", "gaps": "join", "val": "join", "angle bracket": "first",
    "linktext": "join", "lang": "second", "transl": "second", "nobold": "first", "noitalic": "first",
    "centre": "first", "center": "first", "bi": "text", "block indent": "text", "blockindent": "text",
    "quote": "text", "blockquote": "text", "quotation": "text", "numblk": "second",
    "equation box 1": "equation", "unbulleted list": "join", "plainlist": "join", "ubl": "join",
    "math display": "first", "equation": "first",
    "abs": "abs", "norm": "norm", "mset": "mset", "sfrac": "frac", "frac": "frac",
}
LITERAL_TEMPLATES = {"!": "|", "=": "=", "pi": "π", "nbsp": " ", "spaces": " ", "thinsp": " ", "ndash": "–",
                     "mdash": "—", "snd": " – ", "'": "'", "''": "''", "sqrt": "√", "minus": "−",
                     "times": "×", "middot": "·", "dot": "·", "e": "e", "hair space": " ", "nbhyph": "-"}
SENT_OPEN, SENT_CLOSE = "", ""


@dataclass
class Extracted:
    index: int
    latex: str
    display: bool
    section: str
    context_before: str = ""
    context_after: str = ""
    label: str = ""          # e.g. "Infobox probability distribution | pdf" for hidden formulas
    kind: str = "math"       # "math" | "tmath"


@dataclass
class PageStats:
    n_math: int = 0          # <math> tags extracted
    n_tmath: int = 0         # {{tmath}} formulas extracted
    n_display: int = 0
    n_inline: int = 0
    n_hidden: int = 0        # formulas found outside prose (infobox, ref, caption, other templates)
    n_chem: int = 0          # <chem>, <ce>, <math chem> skipped
    n_html_math: int = 0     # {{math|...}} without a <math> inside: pure HTML math, skipped
    n_empty: int = 0         # empty <math></math> skipped


@dataclass
class _Ctx:
    visible: bool = True
    display_wrapper: bool = False
    parent_colon: bool = False
    label: str = ""


def tname(t: Template) -> str:
    n = str(t.name).strip()
    n = re.sub(r"<!--.*?-->", "", n, flags=re.S).strip()
    if n[:9].lower() == "template:":
        n = n[9:]
    return n.replace("_", " ").strip().lower()


def _param_value_text(v: Wikicode) -> str:
    """Raw text of a template parameter value with {{!}} / {{=}} unescaped (used for tmath latex)."""
    s = str(v)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\{\{\s*!\s*\}\}", "|", s)
    s = re.sub(r"\{\{\s*=\s*\}\}", "=", s)
    return s.strip()


def _heading_text(h: Heading) -> str:
    parts = []
    for node in h.title.nodes:
        if isinstance(node, Tag) and str(node.tag).lower() == "math":
            parts.append(str(node.contents or "").strip())
        else:
            parts.append(Wikicode([node]).strip_code())
    return re.sub(r"\s+", " ", "".join(parts)).strip().strip("=").strip()


_JUNK = [
    (re.compile(r"'{2,}"), ""),
    (re.compile(r"__[A-Z]+__"), ""),
    (re.compile(r"^\s*(\{\||\|\}|\|-|\|\+|!|\|)", re.M), " "),
    (re.compile(r"\[\[|\]\]"), ""),
]


def _clean_text(s: str) -> str:
    for rx, rep in _JUNK:
        s = rx.sub(rep, s)
    return s


class _Walker:
    def __init__(self):
        self.out: list[str] = []
        self.formulas: list[Extracted] = []
        self.stats = PageStats()
        self.sections: list[tuple[int, str]] = []

    # -- output helpers -------------------------------------------------------------------------
    def emit(self, s: str, ctx: _Ctx) -> None:
        if ctx.visible and s:
            self.out.append(s)

    def add_formula(self, latex: str, display: bool, ctx: _Ctx, kind: str) -> None:
        idx = len(self.formulas)
        latex_ctx = re.sub(r"\s+", " ", latex.replace(SENT_OPEN, "").replace(SENT_CLOSE, "")).strip()
        f = Extracted(index=idx, latex=latex, display=display, kind=kind,
                      section=" > ".join(t for _, t in self.sections), label="" if ctx.visible else ctx.label)
        self.formulas.append(f)
        self.stats.n_display += display
        self.stats.n_inline += not display
        self.stats.n_hidden += not ctx.visible
        if kind == "tmath":
            self.stats.n_tmath += 1
        else:
            self.stats.n_math += 1
        body = f"${latex_ctx}$" if ctx.visible else ""
        # Sentinel-delimited so spans survive whitespace normalisation; index recovered by order.
        self.out.append(f" {SENT_OPEN}{body}{SENT_CLOSE} ")

    # -- traversal ------------------------------------------------------------------------------
    def walk(self, code: Wikicode, ctx: _Ctx) -> None:
        line = ""  # raw text of the current source line before the node, within this Wikicode
        for node in code.nodes:
            if isinstance(node, Comment):
                continue
            self.node(node, ctx, line)
            s = str(node)
            nl = s.rfind("\n")
            line = s[nl + 1:] if nl >= 0 else line + s

    def node(self, node, ctx: _Ctx, line: str) -> None:
        if isinstance(node, Text):
            self.emit(node.value, ctx)
        elif isinstance(node, HTMLEntity):
            self.emit(node.normalize(), ctx)
        elif isinstance(node, Heading):
            level = node.level
            while self.sections and self.sections[-1][0] >= level:
                self.sections.pop()
            self.sections.append((level, _heading_text(node)))
            self.emit("\n\n", ctx)
            if any(isinstance(x, (Tag, Template)) for x in node.title.nodes):
                self.walk(node.title, ctx)
            else:
                self.emit(self.sections[-1][1], ctx)
            self.emit(".\n\n", ctx)
        elif isinstance(node, Tag):
            self.tag(node, ctx, line)
        elif isinstance(node, Template):
            self.template(node, ctx, line)
        elif isinstance(node, Wikilink):
            self.wikilink(node, ctx)
        elif isinstance(node, ExternalLink):
            if node.title is not None:
                self.walk(node.title, ctx)
        elif isinstance(node, Argument):
            pass

    def child_ctx(self, ctx: _Ctx, line: str, **kw) -> _Ctx:
        return _Ctx(visible=kw.get("visible", ctx.visible),
                    display_wrapper=kw.get("display_wrapper", ctx.display_wrapper),
                    parent_colon=bool(COLON_PREFIX.match(line)) or (ctx.parent_colon and not line.strip()),
                    label=kw.get("label", ctx.label))

    def tag(self, node: Tag, ctx: _Ctx, line: str) -> None:
        name = str(node.tag).strip().lower()
        if name == "math":
            if node.has("chem"):
                self.stats.n_chem += 1
                return
            latex = str(node.contents) if node.contents is not None else ""
            if not latex.strip():
                self.stats.n_empty += 1
                return
            attr = str(node.get("display").value).strip().strip("\"'").lower() if node.has("display") else ""
            if attr == "block":
                display = True
            elif attr == "inline":
                display = False
            else:
                display = (bool(COLON_PREFIX.match(line)) or ctx.display_wrapper
                           or (ctx.parent_colon and not line.strip()))
            self.add_formula(latex, display, ctx, "math")
            return
        if name in CHEM_TAGS:
            self.stats.n_chem += 1
            return
        if node.contents is None:
            if name in NEWLINE_TAGS:
                self.emit("\n", ctx)
            return
        if name in HIDDEN_TAGS:
            self.walk(node.contents, self.child_ctx(ctx, line, visible=False,
                                                    label=ctx.label if not ctx.visible else name))
            return
        if name == "nowiki":
            self.emit(str(node.contents), ctx)
            return
        sep = "\n" if name in NEWLINE_TAGS else (" " if name in {"td", "th"} else "")
        self.emit(sep, ctx)
        self.walk(node.contents, self.child_ctx(ctx, line))
        self.emit(sep, ctx)

    def wikilink(self, node: Wikilink, ctx: _Ctx) -> None:
        title = str(node.title).strip()
        ns = title.lstrip(":").split(":", 1)[0].strip().lower() if ":" in title else ""
        if ns in ("file", "image", "media"):
            if node.text is not None:
                self.walk(node.text, _Ctx(visible=False, label="caption"))
            return
        if ns == "category" and not title.startswith(":"):
            return
        if node.text is not None:
            self.walk(node.text, ctx)
        else:
            self.emit(title.lstrip(":").split("#")[0] if not title.startswith("#") else title[1:], ctx)

    def template(self, t: Template, ctx: _Ctx, line: str) -> None:
        name = tname(t)
        if name == "tmath":
            if t.params:
                latex = _param_value_text(t.params[0].value)
                if latex:
                    self.add_formula(latex, False, ctx, "tmath")
            return
        if name in LITERAL_TEMPLATES and not t.params:
            self.emit(LITERAL_TEMPLATES[name], ctx)
            return
        if name == "math" and not any(isinstance(x, Tag) and str(x.tag).lower() == "math"
                                      for p in t.params for x in p.value.filter_tags(recursive=True)):
            self.stats.n_html_math += 1
        mode = INLINE_TEMPLATES.get(name)
        display_wrapper = ctx.display_wrapper or name in DISPLAY_TEMPLATES
        # Positional = unnamed or explicitly numbered (`{{math|1=a=b}}`), in numeric order.
        pos = sorted((p for p in t.params if str(p.name).strip().isdigit()), key=lambda p: int(str(p.name)))
        if mode and ctx.visible:
            keep = self._kept_params(t, mode, pos)
            pre, mid, post = {"abs": ("|", "", "|"), "norm": ("‖", "", "‖"), "mset": ("{", "", "}"),
                              "frac": ("", "/", "")}.get(mode, ("", " ", ""))
            if display_wrapper and not ctx.display_wrapper:
                self.emit("\n", ctx)
            self.emit(pre, ctx)
            for p in t.params:
                c = self.child_ctx(ctx, line, display_wrapper=display_wrapper,
                                   visible=any(p is k for k in keep))
                if not c.visible:
                    c.label = f"{t.name.strip()} | {str(p.name).strip()}"
                self.walk(p.value, c)
                if c.visible and p is not keep[-1]:
                    self.emit(mid, ctx)
            self.emit(post, ctx)
            if display_wrapper and not ctx.display_wrapper:
                self.emit("\n", ctx)
            return
        # Any other template: not prose. Walk hidden so formulas inside (infoboxes!) are extracted.
        for p in t.params:
            label = ctx.label if not ctx.visible else f"{str(t.name).strip()} | {str(p.name).strip()}"
            self.walk(p.value, self.child_ctx(ctx, line, visible=False, label=label,
                                              display_wrapper=display_wrapper))

    @staticmethod
    def _kept_params(t: Template, mode: str, pos: list) -> list:
        if mode == "first":
            return pos[:1]
        if mode == "second":
            return pos[1:2]
        if mode == "text":
            named = [p for p in t.params if str(p.name).strip() in ("text", "1", "quote")]
            return named[:1] or pos[:1]
        if mode == "equation":
            return [p for p in t.params if str(p.name).strip() == "equation"]
        return pos  # join / abs / norm / mset / frac


def _assemble(walker: _Walker, n_ctx: int) -> None:
    raw = "".join(_clean_text(s) if SENT_OPEN not in s else s for s in walker.out)
    text = re.sub(r"\s+", " ", raw)
    # Strip sentinels while recording each formula's span in the clean text.
    clean: list[str] = []
    spans: list[tuple[int, int]] = []
    pos = 0
    i = 0
    n = len(text)
    while i < n:
        j = text.find(SENT_OPEN, i)
        if j < 0:
            clean.append(text[i:])
            pos += n - i
            break
        clean.append(text[i:j])
        pos += j - i
        k = text.find(SENT_CLOSE, j)
        body = text[j + 1:k]
        spans.append((pos, pos + len(body)))
        clean.append(body)
        pos += len(body)
        i = k + 1
    full = "".join(clean)
    assert len(spans) == len(walker.formulas)
    starts = [a for a, _ in spans]

    def inside(x: int) -> tuple[int, int] | None:
        """The formula span strictly containing position x, if any."""
        k = bisect.bisect_right(starts, x) - 1
        if k >= 0 and spans[k][0] < x < spans[k][1]:
            return spans[k]
        return None

    for f, (a, b) in zip(walker.formulas, spans):
        lo = max(0, a - n_ctx)
        if lo > 0:  # start at a word boundary, never in the middle of another formula
            if not inside(lo):
                nxt = full.find(" ", lo, a)
                lo = nxt + 1 if nxt >= 0 else lo
            sp = inside(lo)
            lo = sp[1] if sp else lo
        before = full[lo:a]
        hi = min(len(full), b + n_ctx)
        if hi < len(full):
            if not inside(hi):
                prv = full.rfind(" ", b, hi)
                hi = prv if prv >= 0 else hi
            sp = inside(hi)
            hi = sp[0] if sp else hi
        after = full[b:hi]
        before = re.sub(r"\s+", " ", before).strip()
        if f.label:
            before = (before + f" [{f.label}]").strip()
        f.context_before = before
        f.context_after = re.sub(r"\s+", " ", after).strip()


def extract_formulas(wikitext: str, n_ctx: int = CONTEXT_CHARS) -> tuple[list[Extracted], PageStats]:
    code = mwp.parse(wikitext)
    w = _Walker()
    w.walk(code, _Ctx())
    _assemble(w, n_ctx)
    return w.formulas, w.stats
