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

## Results (two full passes, 2026-10-21)

- **Corpus:** 64,617 articles tagged by WikiProjects Mathematics, Physics, Statistics and Engineering; 952,136 `<math>` formulas.
- **Checkable identities (second pass):** 6,140. Verdicts: 5,076 PASS, 756 INCONCLUSIVE, 308 FAIL.
- **Review:** every FAIL from both passes was reviewed by an independent reviewer (553 flags). **36 confirmed errors on live
  Wikipedia pages**, 518 pipeline mistakes, 0 ambiguous. Each confirmed error was re-fetched from the live page and, where
  computable, recomputed independently at 30 digits. The list with evidence and fixes is in
  [`CONFIRMED_ERRORS.md`](CONFIRMED_ERRORS.md); exact wikitext edits for the first 14 are in [`WIKIPEDIA_EDITS.md`](WIKIPEDIA_EDITS.md).
  Among them: two derivative series on *Taylor series* missing factors of 2 and 6; two wrong series in the *Dirichlet
  integral* proof; a limit on *Euler's constant* with the wrong sign; two "sine" identities on *List of trigonometric
  identities* that sum cosines; reduction formulas on *List of definite integrals* with ∞ where m−1 belongs; Γ(3/2) = π/2 on
  *Volume of an n-ball*; arccos written as the arcsin integral on *Extreme learning machine*; swapped bounds on *Gautschi's
  inequality*; a reversed inequality on *Holm–Bonferroni method*; a missing i in the flux-quantization exponent on
  *Ginzburg–Landau theory*; a wrong arctangent argument in the *Tridecagon* construction; a sign error on *Universal joint*;
  sin 54° given as 2√5/4 on *54 (number)*; a negative upper bound on *Area of a circle*.
- **Measured quality on labeled data** (`data/bench/REPORT.md`): precision 100 % (0 false positives on 272 known-true
  identities), recall 82 % on 1,320 injected errors.
- **Measured quality on real pages:** pre-review precision was 4.9 % in the first pass (13 of 266 flags) and 10.4 % in the
  second (32 of 308) after the 253 first-pass false positives were tagged by cause and turned into rules and fixtures;
  242 of those 253 no longer fail. The cost: 3 of the 13 first-pass errors became INCONCLUSIVE or skipped. The remaining
  false positives are dominated by notation the translator still misreads (double zeta, elliptic nome, coefficient
  extraction), named constants read as variables, and equations to be solved rather than identities.

Coverage is the honest limitation: only identities with an explicit relation are checked, which is a small fraction of
all `<math>` tags (most are bare expressions, definitions, operators, matrices or sets).

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

## Security

Untrusted text never reaches `eval`, `sympify` or `parse_expr`: every stage rebuilds expressions through an
AST-whitelisted loader, inputs are size-capped, verification runs in killable workers with memory limits, the
HTML report autoescapes, and page text is fenced as data wherever an AI reads it. Threat model, findings and
limits are in [`SECURITY.md`](SECURITY.md); adversarial tests live in `tests/security/`.

## License

MIT. Findings and data may be reused with attribution; see `CITATION.cff`.
