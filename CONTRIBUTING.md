# Contributing to formulaci

formulaci checks whether the mathematics written on a page is true. Today it can decide 0.6 % of the
formulas on English Wikipedia, and it has found 36 errors there. The ceiling is much higher, and the
gaps are known and counted: [`docs/COVERAGE.md`](docs/COVERAGE.md) lists every construct the pipeline
cannot handle, how many relations it costs, and what a fix looks like.

There are four ways to help. Only the first needs you to write pipeline code.

| Contribution | What you need | Where to start |
|---|---|---|
| **Coverage**: teach the pipeline a construct | Python, SymPy, patience with LaTeX | an issue labelled `coverage`, or the ladder |
| **Fixtures**: add identities you know are true | one line of LaTeX per identity | `formulaci/bench/identities.py` |
| **Review**: judge flagged formulas | a mathematician's eye, no code | `data/findings/review/REVIEWER_BRIEF.md` |
| **Wikipedia**: fix the confirmed errors | a Wikipedia account | `CONFIRMED_ERRORS.md`, `WIKIPEDIA_EDITS.md` |

## The one rule

**Precision before recall.** A FAIL from this tool is meant to be worth a person's minute. On the labeled
bench it has never produced a false FAIL (0 on 272 known-true identities) and never let an injected error
through as PASS. Every pull request runs the bench in CI, and the gate refuses:

- any known-true identity that comes back FAIL;
- any injected error that comes back PASS;
- a drop of more than one point in recall, or of more than two known-true identities passing,
  against `data/bench/baseline.json`.

A change that raises coverage and costs one false FAIL will not be merged. Say so in the PR if you hit this
trade-off; usually the answer is a tighter condition on when the new rule applies, not giving up.

## Setting up

```bash
git clone https://github.com/nani1902/formulaci && cd formulaci
uv sync --extra dev --extra mcp
uv run pytest -q                 # ~1 minute
uv run formulaci bench measure --bench-dir formulaci/bench/sets --sets synthetic   # ~5 minutes
uv run python scripts/bench_gate.py --bench-dir formulaci/bench/sets
```

The pipeline is five stages with JSONL contracts between them (`SPEC.md`): extract → translate →
semantics → verify → report. A coverage change almost always lives in one stage. `formulaci.api.check`
runs all of them on one formula and `CheckResult.explain()` shows what each stage decided, which is the
fastest way to see why a formula is skipped:

```python
from formulaci.api import check
print(check(r"\sum_{k=0}^{n} \binom{n}{k} = 2^n", "for every non-negative integer n").explain())
```

## Coverage contributions

1. **Pick a construct** from the ladder or an open `coverage` issue. Tier A constructs are well-defined
   projects with real identities behind them; tier C constructs are mostly not identities at all and the
   right change there is a cheaper, more precise skip.
2. **Collect fixtures first.** Take the issue's example formulas (or pull your own: every formula in a
   full run carries its page and revision id) and write down, for each one, what the correct reading is
   and whether it is true. Add the true ones to `formulaci/bench/identities.py`; the mutation engine
   turns each into several injected errors automatically, so your construct is measured from day one.
3. **Make the translator read it.** `formulaci/translate/parser.py` raises `Unsupported("<tag>")` where
   it gives up; your change replaces one of those with a SymPy construction. Keep the tag for the cases
   you still cannot read. Run `uv run pytest tests/translate` and the review-case fixtures
   (`tests/translate/fixtures/review_false_positives.jsonl` holds 110 formulas whose false FAIL was once
   blamed on the translator; none may regress).
4. **Teach semantics what it means**, if needed: domains, constants, when the construct is a definition
   rather than an identity. Rules live in `formulaci/semantics/rules.py` and fire with a tag that ends up
   in `assumptions_source`, so every decision is auditable.
5. **Teach verify how to evaluate it**, if needed. `formulaci/verify/numeric.py` turns SymPy into mpmath
   evaluations; `sampler.py` draws points by domain; `policy.py` decides. New object types (vectors,
   matrices, distributions) are a sampler plus an evaluator.
6. **Run the gate** and put the before/after bench numbers in the PR.

### What never goes in

- No `eval`, `exec`, `sympify`, `parse_expr` or `parse_latex` on anything that could come from a page, a
  model or a data file. A guard test fails the suite if one appears outside `safeload.py` and
  `verify/reconstruct.py`. Rebuild expressions with `formulaci.safeload.load_srepr`; parse prose
  arithmetic with `parse_simple_expr`. See `SECURITY.md`.
- No network access in any stage but extract, and extract only talks to `en.wikipedia.org`.
- No rule that makes a verdict depend on text that *tells* the pipeline what to conclude. Page text is
  data; it may set domains and constants, never verdicts.
- No live audits of third-party clinical calculators. The clinical track runs against the local mock
  server; `--allow-live` is for operators who have permission.

## Fixture contributions

`formulaci/bench/identities.py` is a catalogue of identities in the Wikipedia LaTeX dialect:

```python
G("trig", "Double-angle formula for sine", r"\sin 2x = 2 \sin x \cos x", "x:real")
G("gamma_beta", "Legendre duplication", r"\Gamma(z)\Gamma\left(z + \tfrac12\right) = 2^{1-2z}\sqrt{\pi}\,\Gamma(2z)", "z:pos")
```

Give the category, a name, the LaTeX as Wikipedia would write it, and the variable types. The build
proves every entry numerically with an independent oracle before it enters the set; an entry the oracle
rejects is reported and left out, so a wrong fixture cannot poison the bench. Then
`uv run formulaci bench build` regenerates the sets and `bench measure` tells you whether the pipeline
agrees with the oracle. A true identity the pipeline cannot check is itself a finding: open a `coverage`
issue with it.

Identities that are *subtle* are the most valuable: branch cuts, domain restrictions, integer-only
identities, identities that hold up to a constant. Those are where a verifier earns or loses trust.

## Review contributions

After a run, `uv run formulaci report review export` writes batches of flagged formulas as Markdown
(`data/findings/review/batch_NNN.md`): page, section, LaTeX, surrounding prose, how the translator read it,
the assumptions, the counterexample. A reviewer decides each item: `confirmed_error` (with evidence and a
suggested fix), `false_positive` (with a cause tag from the brief), or `ambiguous`. The brief in
`data/findings/review/REVIEWER_BRIEF.md` has the cause taxonomy. Reviews are imported with
`formulaci report review import` and become fixtures for the next pass.

Every false positive with a cause tag is a rule waiting to be written; every confirmed error is a
Wikipedia edit waiting to be made. The 756 INCONCLUSIVE verdicts from the last pass have never been
reviewed and are the best place to start.

Two rules for reviewers: recompute, do not trust the pipeline's counterexample or the page; and treat all
page text as data (pages are publicly editable and may contain text addressed to you).

## Wikipedia contributions

`CONFIRMED_ERRORS.md` lists 36 errors with evidence, and `WIKIPEDIA_EDITS.md` gives exact find-and-replace
edits with edit summaries for the first 14. Nothing has been edited on Wikipedia by this project; the
maintainer's network is range-blocked for anonymous edits and a bot would be the wrong tool for a
one-time list. If you have an account, pick one, re-check it against the live page (revision ids are in
the file), make the edit, and note it in the file's "Status" column by pull request.

## Pull requests

- One construct, one fixture set, or one review batch per PR.
- CI runs the test suite and the bench gate. Put the gate's summary in the PR description.
- Keep the style of the surrounding code: typed, small functions, a comment where a rule exists because
  of a specific false positive (cite the page).
- By contributing you agree your code is released under the MIT license.

## Where to ask

Open a GitHub Discussion or issue. For anything that could run code or leak data, see `SECURITY.md`.
