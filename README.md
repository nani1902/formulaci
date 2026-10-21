# formulaci — a test suite for human knowledge

Software has test suites. Human knowledge does not. Billions of people act on formulas in Wikipedia,
textbooks and online calculators, and nobody runs them. formulaci runs them.

It extracts every `<math>` formula from English Wikipedia's mathematics, physics, statistics and
engineering articles, translates the LaTeX to SymPy, infers variable domains and constraints from the
surrounding prose, checks each identity symbolically and numerically (mpmath, 50 digits, several
sampling regimes), and reports the ones that fail with a reproducible counterexample. Every flag is then
reviewed before it is called an error. A separate track audits the formulas behind online clinical
calculators against the primary literature.

Prior art: Greiner-Petter et al., ["Do the Math: Making Mathematics in Wikipedia Computable"](https://doi.org/10.1109/tpami.2022.3195261)
(IEEE TPAMI, 2022) proved the approach on 103 pages with Maple/Mathematica and LaCASt; it was never
deployed. formulaci uses free tools and runs at the scale of the whole encyclopedia.

## Results so far (first pass, 2026-10-21)

- **Corpus:** 64,617 articles, 952,136 formulas extracted. The first full verification pass covered the
  180,016 formulas from the most-read ~4,800 pages.
- **Checkable identities in that pass:** 2,867. Verdicts: 2,067 PASS, 398 INCONCLUSIVE, 266 FAIL.
- **Review of all 266 FAILs:** 13 confirmed errors on live Wikipedia pages (plus one found next to a
  confirmed one), 253 pipeline mistakes, 0 ambiguous. The 14 errors, each recomputed independently and
  re-checked on the live page, are in [`CONFIRMED_ERRORS.md`](CONFIRMED_ERRORS.md); ready-to-paste fixes
  are in [`WIKIPEDIA_EDITS.md`](WIKIPEDIA_EDITS.md). Among them: two derivative series on *Taylor
  series* missing factors of 2 and 6, two wrong series in the *Dirichlet integral* proof, a sign error in
  a limit on *Euler's constant*, two mislabeled sums on *List of trigonometric identities*, two reduction
  formulas with wrong bounds on *List of definite integrals*, and Γ(3/2) given as π/2 on *Volume of an n-ball*.
- **Measured quality on labeled data** (`data/bench/REPORT.md`): precision 100 % (0 false positives on
  272 known-true identities), recall 82 % on 1,320 injected errors (sign flips, wrong constants, dropped
  factors, off-by-one bounds, swapped symbols).
- **Measured quality on real pages:** first-pass precision before review was 5 % (13 of 266). The 253 false
  positives were tagged by cause (misread operators and conjugates, label superscripts, arithmetic in finite
  fields and ordinals, equations the page itself calls false, defining equations, rounding) and fed back as
  rules and fixtures; the second pass clears 109 of 110 translator cases and 130 of 135 semantics cases
  while keeping 11 of the 13 confirmed errors flagged. A full second run over all 952k formulas is in progress.

Coverage is the honest limitation: most `<math>` tags are expressions without a relation, definitions,
operators, matrices or notation the translator refuses rather than guesses at. Only identities are checked.

## Layout

```
SPEC.md                 architecture, record schemas, FAIL policy, ground rules
formulaci/extract/      Wikipedia page list + formula extraction with prose context
formulaci/translate/    Wikipedia-dialect LaTeX -> SymPy, with explicit refusal of ambiguous notation
formulaci/semantics/    rules-based domains, constants, constraints, checkability
formulaci/verify/       symbolic + numeric verification, precision-first FAIL policy
formulaci/report/       findings, HTML report, review batch export/import
formulaci/clinical/     reference implementations of 25 clinical formulas + calculator audit harness
formulaci/bench/        labeled sets, mutation engine, precision/recall measurement
scripts/run_pipeline.sh end-to-end run (resumable; FORCE=1 to redo)
```

Each stage has its own README with measured numbers and known failure modes.

## Run it

```bash
uv sync --all-extras
uv run pytest                                  # ~450 tests
uv run formulaci extract pages --out data/raw/pages.txt --limit 200
uv run formulaci extract run --pages data/raw/pages.txt --out data/raw/formulas.jsonl
./scripts/run_pipeline.sh                      # translate -> semantics -> verify -> report
uv run formulaci report export-review          # Markdown batches for reviewing FAILs
uv run formulaci bench build && uv run formulaci bench measure
```

Wikipedia asks for a contact in the User-Agent; set `FORMULACI_CONTACT` to an email or URL to get the
faster rate tier. The clinical audit runs against a local mock server by default and refuses live sites
without an explicit flag.

## How it was built

Designed and directed by Mahesh Balaram. The stages were implemented by a coordinated set of AI coding
agents (Claude) working from the written spec, with every flagged formula reviewed and every confirmed
error recomputed independently before being reported. Nothing on Wikipedia has been edited by the tool.

## License

MIT. Findings and data may be reused with attribution; see `CITATION.cff`.
