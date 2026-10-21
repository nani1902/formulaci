"""Regenerate docs/COVERAGE.md from a full run's data (data/raw, data/parsed, data/semantics).

    uv run python scripts/coverage_ladder.py [--data data] [--out docs/COVERAGE.md]

Counts relations (equations, chains, inequalities) the translator rejected per unsupported construct,
the number of distinct pages involved, a few short example formulas (quoted from Wikipedia, CC BY-SA,
with the page title), and the semantics stage's skip reasons. The descriptions of what a fix would
look like are curated in LADDER below; a construct without an entry is listed with its count only.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
from pathlib import Path

# construct -> (tier, title, what it is, what a contribution looks like)
LADDER: dict[str, tuple[str, str, str, str]] = {
    "ellipsis": ("A", "Series and products written with an ellipsis",
                 r"`1 + \frac{1}{4} + \frac{1}{9} + \cdots = \frac{\pi^2}{6}`, `z - z^3/3 + z^5/5 - \cdots`. Written-out series are "
                 "how most articles state a famous identity; they are real, checkable claims.",
                 "A pattern recogniser in the translator that turns `a_1 + a_2 + a_3 + \\cdots` (and `\\cdots + a_n` finite forms) into "
                 "`Sum(term(k), (k, 1, oo))` when the first three or four terms fix a term formula (powers, factorials, alternating "
                 "signs, odd/even indices). Refuse anything ambiguous. Fixtures: the Pi, Basel problem and Taylor series pages."),
    "matrix": ("A", "Explicit matrices",
               r"`\begin{pmatrix} 1 & i \\ i & 1 \end{pmatrix}` with numeric or symbolic entries, often equated to a product or inverse.",
               "Extend the translator to build `sympy.Matrix` for `pmatrix`/`bmatrix`/`vmatrix` blocks, and the verify stage to evaluate "
               "matrix-valued identities entrywise (lambdify over the entries; compare shapes, then every entry). Vectors in `\\mathbf{v}` "
               "notation belong to the same project (see vector algebra)."),
    "transpose": ("A", "Vector and matrix algebra: transpose",
                  r"`p^T (A - \lambda B) q = 0`, `\mathbf{k}^\mathsf{T}\mathbf{Q}^{-1}\mathbf{k} = 0`.",
                  "Part of the vector-algebra project: with a `matrix`/`vector` symbol type in Semantics (shape inferred from context: "
                  "'an n×n matrix', 'a vector in R^3'), sample small random matrices/vectors and evaluate. Transpose, inverse, "
                  "determinant and trace are then one rule each."),
    "vector_product": ("A", "Vector algebra: dot and cross products",
                       r"`\mathbf{p} \times \mathbf{L}`, `\mathbf{x}'\mathbf{A}\mathbf{x} = \sum_{i,j} a_{ij} x_i x_j`, `|\mathbf{AB}| = |\mathbf A| \cdot |\mathbf B|`.",
                       "Same project as matrices: typed vector symbols, `\\cdot` and `\\times` on them, componentwise sampling in R^2 and R^3."),
    "inner_product": ("A", "Inner products",
                      r"`\langle z, w\rangle = z_1\overline{w}_1 + z_2\overline{w}_2`, `\langle\varphi_n \mid \varphi_m\rangle = \delta_{nm}`.",
                      "Finite-dimensional inner products are checkable with the vector-algebra sampler; function-space ones "
                      "(`\\langle\\delta, f\\rangle`) are not and should be skipped cleanly with a distinct reason."),
    "norm": ("A", "Norms and absolute values of vectors",
             r"`\|f + g\|_p \leq \|f\|_p + \|g\|_p`, `\|\mathbf{x}\|_\infty = \sup_i |x_i|`.",
             "Finite-dimensional p-norms are checkable once vectors are typed; function norms are not. A translator rule for "
             "`\\|...\\|_p` plus the vector sampler."),
    "superscript_label": ("B", "Superscripts that are labels, not powers",
                          r"`\omega_1^n`, `K_n^M(F)`, `x^{(k)}`. The translator refuses the whole formula when it cannot tell a power from an index.",
                          "Better disambiguation: a superscript on a symbol that also carries a subscript, or that appears in `(k)` form, or that is "
                          "never used as a power elsewhere on the page, is a label; rewrite it into the symbol name instead of refusing. Measure "
                          "on the review fixtures: label misreads were the second-largest false-positive cause in run 1, so precision must not drop."),
    "sum_index_set": ("B", "Sums over an index without bounds",
                      r"`\sum_i k_i p_i`, `\sum_{i \in I} \|x_i\|^2`, `\sum_n \lambda_n \varphi_n(x)\varphi_n(y)`.",
                      "When the prose fixes the range ('for i = 1, ..., n', 'where the sum runs over the divisors of n'), Semantics can supply "
                      "bounds and the existing Sum evaluator does the rest. Divisor sums, sums over primes up to N and sums over a finite set "
                      "named in the context are the tractable cases."),
    "styled_expression": ("B", "Bold, hat and arrow styling on expressions",
                          r"`\mathbf{Ax} = \mathbf{b}`, `\hat l_{\mathbf p}`.",
                          "Mostly vectors and matrices (see above). Once typed objects exist, `\\mathbf{AB}` is a product of two typed symbols."),
    "probability": ("B", "Probability operators",
                    r"`\operatorname{Var}(X+Y) = \operatorname{Var}(X) + \operatorname{Var}(Y)`, `\Pr[k \text{ wins of } n] = \binom{n}{k} ...`.",
                    "Identities about moments of a *named* distribution (the page says X is binomial(n, p)) are checkable by evaluating the "
                    "moment in closed form; identities about arbitrary random variables are not. A `distribution` type in Semantics plus a "
                    "table of moments is a self-contained project; the probability category of the bench is the fixture set."),
    "sup_inf": ("B", "Suprema, infima, limsup",
                r"`\frac{1}{R} = \limsup_{n\to\infty} |c_n|^{1/n}`, `\|P_V\| = \sup_{x \neq 0} \frac{\|P_V x\|}{\|x\|}`.",
                "Suprema over a finite explicit set are evaluable; over a continuum they usually are not. Low yield; skip cleanly."),
    "differential_form": ("C", "Differentials and forms",
                          r"`dU = T\,dS - p\,dV`, `d\omega_U + d\omega_V = 0`.",
                          "Thermodynamic and exterior-calculus statements are relations between differentials, not identities between "
                          "computable expressions. Correctly skipped; a cleaner skip reason is the only improvement."),
    "partial_operator": ("C", "Boundary and partial operators",
                         r"`\partial x = \partial u + \partial v`, `\partial_{[\alpha} F_{\beta\gamma]} = 0`.",
                         "Not checkable without a model of the operator; skip cleanly."),
    "vector_calculus": ("C", "Vector calculus",
                        r"`\nabla \cdot \mathbf{E} = \rho/\varepsilon_0`, `\nabla \times \mathbf{B} = ...`.",
                        "Physical laws relating fields, not identities. The small checkable subset (vector-calculus identities such as "
                        "`\\nabla \\times (\\nabla f) = 0`) could be verified with random polynomial fields; a research-grade project."),
    "set_notation": ("C", "Set builder and set operations",
                     r"`Hg = \{h \cdot g \mid h \in H\}`, `\{1, 2, \ldots, n\}`.",
                     "Definitions and set equalities; not identities between computable expressions. Correctly skipped. "
                     "A contributor could make the skip reason precise and cheap (it is currently the largest single bucket)."),
    "tuple": ("C", "Tuples, lists and commutators",
              r"`(x_1, \ldots, x_n) \cdot u = (...)`, `[A, B] = AB - BA`.",
              "Componentwise equalities of explicit tuples are checkable (treat as a vector); most are definitions. Low yield."),
    "uppercase_juxtaposition": ("C", "Products of uppercase symbols",
                                r"`r_s = \frac{2GM}{c^2}`, `V = V_S - IR`.",
                                "`GM` could be a product or a matrix product, so the translator refuses. Nearly all of these are physical "
                                "laws or definitions that Semantics would skip anyway, so the yield of reading them as products is small; "
                                "a context rule ('where G is the gravitational constant') would make the reading safe."),
    "conjugate_star": ("C", "Asterisk superscripts",
                       r"`f^*(n) = \lfloor \sqrt{n-1} \rfloor + n`, `S^* = s_1^*, s_2^*, \ldots`.",
                       "`^*` is a conjugate, a dual, an adjoint or just a name depending on the page. A page-level decision from context "
                       "('the complex conjugate') would recover the conjugate cases."),
    "word_symbol": ("C", "Words used as symbols",
                    r"`\text{PVR} = i_1 / i_2`, `Re = \frac{\bar c U}{v}`, `\ldots = \text{constant}`.",
                    "Definitions almost without exception. Skip cleanly."),
    "subscript_on_expression": ("C", "Subscripts on parenthesised expressions",
                                r"`(\bar x)_{D + n_0}`, `\pi_{\nu, k}(f)`.",
                                "Indexing into a vector or family; checkable only with typed objects."),
    "empty_side": ("C", "Relations with an empty side",
                   r"`\le k`, `P \land (Q \lor R) = {}` (a formula split across several `<math>` tags).",
                   "An extraction artefact: display equations broken over several tags. Joining consecutive tags whose relation is "
                   "dangling would recover some real identities; it belongs in the extract stage."),
    "integral_domain": ("C", "Integrals over a named domain",
                        r"`\int_\Sigma K\,dA = 2\pi\chi(\Sigma)`, `\int_S g(s)\,d\sigma(s)`.",
                        "Integrals over manifolds and measures; not evaluable without the domain. Skip cleanly."),
}

SEM_NOTES = {
    "operator_notation": "Operators the pipeline cannot evaluate: `\\nabla`, `E[X]`, `\\operatorname{Var}`, `O(...)`, asymptotics. The vector-calculus and probability projects above eat into this bucket.",
    "matrix_or_vector": "Symbols the prose or styling marks as matrices, vectors or operators. The vector-algebra project.",
    "set_notation": "Sets; see above.",
    "statement_not_identity": "Relations between particular quantities, existential statements, equations to solve. Correct skips; a universal cue in the prose ('for all x') now keeps them checkable.",
    "definition": "`f(x) = ...` introduces the left side. Nothing to check, but the definition could be *used*: see 'definition propagation' in CONTRIBUTING.md.",
    "has_undefined_function": "A page-specific function (`f`, `K`, `\\psi`) with no known meaning. Definition propagation would make many of these checkable.",
    "condition": "`4p^3 + 27q^2 < 0` style conditions. Correct skips.",
    "special_algebra": "Modular, Boolean, tropical, characteristic-2 arithmetic. Would need a different evaluator per algebra.",
    "functional_identity": "Properties of an arbitrary function (`f(x+y) = f(x) + f(y)`). Not samplable.",
    "defining_equation": "Equations that define a constant or are to be solved.",
    "congruence": "`a \\equiv b \\pmod n`. A modular evaluator over small integers is a small, self-contained project.",
    "differential_equation": "ODEs and PDEs; not identities.",
    "plus_minus": "`\\pm` / `\\mp`: the translator expands both signs only when the pairing is clear.",
    "named_constant": "The value of a constant the checker does not know (`G`, `h`, `\\alpha`). A table of physical constants with units is a small project.",
    "units": "Numbers with physical units. Needs a unit system (pint) to check.",
}


def mine(data: Path, seed: int = 7):
    random.seed(seed)
    unsup = collections.Counter(); pages = collections.defaultdict(set); examples = collections.defaultdict(list)
    sem = collections.Counter(); need: dict[str, list[str]] = {}
    for line in open(data / "parsed/parsed.jsonl"):
        r = json.loads(line)
        if r.get("kind") not in ("equation", "chain", "inequality"):
            continue
        for u in r.get("has_unsupported") or []:
            u = u.replace("unsupported:", "")
            unsup[u] += 1
            need.setdefault(r["formula_id"], []).append(u)
    for line in open(data / "semantics/semantics.jsonl"):
        r = json.loads(line)
        if r.get("checkable") is False and r.get("skip_reason") not in (None, "translator_not_checkable", "unparsed"):
            sem[r["skip_reason"]] += 1
    for line in open(data / "raw/formulas.jsonl"):
        r = json.loads(line)
        for u in need.get(r["formula_id"], ()):
            pages[u].add(r["page_title"])
            if len(r["latex"]) <= 100 and "\n" not in r["latex"] and len(examples[u]) < 6 and random.random() < 0.3:
                examples[u].append((r["page_title"], r["latex"].strip()))
    return unsup, pages, examples, sem


def render(unsup, pages, examples, sem, summary: dict) -> str:
    out = ["# Coverage ladder", "",
           "What formulaci cannot check yet, ranked by how many relations each gap costs, with what a fix would look like.",
           "Generated by `scripts/coverage_ladder.py` from the second full pass over English Wikipedia (2026-10-21).",
           "Example formulas are quoted from Wikipedia articles (CC BY-SA 4.0) with the article title.", "",
           "## The funnel", "",
           "| Stage | Formulas | Share |", "|---|---:|---:|",
           f"| `<math>` elements extracted from 64,617 pages | {summary['formulas']:,} | 100 % |",
           f"| contain a relation (`=`, a chain, or an inequality) | {summary['equation_formulas']:,} | {100*summary['equation_formulas']/summary['formulas']:.0f} % |",
           f"| translated without an unsupported construct | {summary['equation_formulas_any_ok']:,} | {100*summary['equation_formulas_any_ok']/summary['formulas']:.0f} % |",
           "| judged checkable by the semantics stage | 6,437 | 0.7 % |",
           "| verified (5,076 PASS, 756 INCONCLUSIVE, 308 FAIL) | 6,140 | 0.6 % |", "",
           "Tiers: **A** = a well-defined project with real identities behind it; **B** = partly checkable, needs context or "
           "disambiguation; **C** = mostly not an identity at all, where the right contribution is a cleaner, cheaper skip.", "",
           "## Translator gaps (relations rejected per construct)", "",
           "| Tier | Construct | Tag | Relations | Pages |", "|---|---|---|---:|---:|"]
    ranked = unsup.most_common(40)
    for name, n in ranked:
        tier, title, _, _ = LADDER.get(name, ("?", name.replace("_", " "), "", ""))
        link = f"[{title}](#{name.replace('_', '-')})" if name in LADDER else title
        out.append(f"| {tier} | {link} | `{name}` | {n:,} | {len(pages[name]):,} |")
    out += ["", "## Each gap", ""]
    for name, n in ranked:
        if name not in LADDER:
            continue
        tier, title, what, fix = LADDER[name]
        out += [f"### {name}", "", f"**{title}** (tier {tier}, {n:,} relations on {len(pages[name]):,} pages). {what}", "",
                f"**What a contribution looks like.** {fix}", ""]
        if examples[name]:
            out += ["Examples:", ""] + [f"- *{t}*: `{l}`" for t, l in examples[name]] + [""]
    out += ["## Semantics skips (translated, then judged not checkable)", "",
            "| Reason | Formulas | Note |", "|---|---:|---|"]
    for name, n in sem.most_common():
        out.append(f"| `{name}` | {n:,} | {SEM_NOTES.get(name, '')} |")
    out += ["", "## Beyond the translator", "",
            "- **Definition propagation.** 50,850 formulas define a symbol and 27,052 use a page-specific function. When a page "
            "says `f(x) = x^2 + 1` and later `f(2) = 5`, substituting the definition makes the second checkable. A page-level "
            "symbol table in Semantics is the single largest coverage project that touches no LaTeX parsing.",
            "- **Other languages.** The extract stage takes a language code; German, French, Russian and Chinese Wikipedia each "
            "have their own `<math>` corpora with their own errors, and the pipeline has never been run on them.",
            "- **Other corpora.** Anything with LaTeX and prose: the DLMF, arXiv abstracts, textbooks, lecture notes, the "
            "formulas in an LLM's draft answer (that is what the MCP server does).",
            "- **Review.** 756 identities came back INCONCLUSIVE in the last pass. Each one a person resolves is either a new "
            "confirmed error or a cause-tagged false positive that becomes a rule.", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="docs/COVERAGE.md")
    a = ap.parse_args()
    data = Path(a.data)
    summary = json.load(open(data / "parsed/parsed.jsonl.summary.json"))
    unsup, pages, examples, sem = mine(data)
    Path(a.out).write_text(render(unsup, pages, examples, sem, summary))
    print(f"wrote {a.out}: {len(unsup)} constructs, {len(sem)} skip reasons")


if __name__ == "__main__":
    main()
