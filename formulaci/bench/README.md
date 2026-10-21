# bench — labelled sets and precision/recall of the pipeline

The pipeline's claims are only as good as its measured precision and recall. This stage builds
labelled formula sets and runs translate → semantics → verify over them.

## Sets

All sets are JSONL `Formula` records (the extract schema) plus an extra `bench` key with the labels.
`Formula.model_validate` ignores the extra key, so every stage reads them like extract output. Labels
are mirrored in `page_categories` (`bench-category:trig`, `bench-label:false`, `bench-mutation:sign_flip`).

| file | what | size |
|---|---|---|
| `known_good.jsonl` | classical identities known to be true, ids `bench:good:NNNN` | 272 |
| `mutated.jsonl` | the same identities with one injected error each, ids `bench:mut:NNNN:<type>` | 1320 |
| `lacast_benchmark.jsonl` | LaCASt's 95 hand-evaluated Wikipedia formulas, ids `lacast:gold:NNN` | 95 |

**Known-good** (`identities.py`): 272 identities in the Wikipedia LaTeX dialect (`\frac`, `\sum_{k=0}^{n}`,
`\int_0^\infty … \,dx`, `\binom`, `\Gamma`, `\left( \right)`, `\operatorname{…}`, trailing `\quad x > 0`
conditions), with a `context_before` sentence stating the domain the way Wikipedia prose does
("The Legendre duplication formula states that, for positive real x,"). Per category:

| category | identities |
|---|---|
| trig | 39 |
| inequalities | 24 |
| hyperbolic | 23 |
| integrals | 22 |
| infinite_series | 21 |
| gamma_beta | 20 |
| derivatives | 20 |
| probability | 20 |
| exp_log | 19 |
| binomial | 18 |
| finite_series | 18 |
| algebra | 12 |
| zeta | 9 |
| complex | 7 |

Every identity is **proven numerically before it enters the set** by an independent oracle
(`oracle.py`, below) at 6 sampled points inside its domain; an identity the oracle cannot confirm is
reported in `build_stats.json` → `known_good.rejected_by_oracle` and left out.

**Mutated** (`mutate.py`): for each identity and each of 8 mutation types, candidate edits are
generated on the LaTeX text (never on the `\quad` condition, sum indices or differentials), tried in a
seeded random order, and the first one that still parses and **fails at a strict majority of the
oracle's sample points** is kept. Types:

| type | edit |
|---|---|
| `sign_flip` | one `+`↔`-` (fallback: negate a whole side) |
| `exponent_pm1` | an exponent `e` → `e±1` |
| `dropped_factor` | delete one factor of a product |
| `wrong_constant` | `2`↔`3`, `\pi`↔`2\pi`, `e`→`1`, `1`→`e` (fallback: another integer +1) |
| `swapped_symbols` | swap two same-kind variables on one side, `\sin`↔`\cos`-type function swap, or `\binom{n}{k}`→`\binom{k}{n}` |
| `off_by_one` | a `\sum`/`\prod`/`\int` bound ±1 |
| `num_den_swap` | `\frac{a}{b}` → `\frac{b}{a}` |
| `missing_term` | delete one additive term |

Dropped candidates are counted per type and reason (`preserved` = the edit left the identity true,
`weak` = it fails at only a minority of points, `unparseable`, `unevaluable`); `no_site` = the type
does not apply to that identity. Latest build:

| type | kept | no site | dropped: preserved | weak | unparseable | unevaluable |
|---|---|---|---|---|---|---|
| sign_flip | 272 | 0 | 13 | 8 | 0 | 18 |
| exponent_pm1 | 165 | 99 | 8 | 5 | 0 | 3 |
| dropped_factor | 151 | 102 | 10 | 8 | 29 | 0 |
| wrong_constant | 210 | 53 | 12 | 11 | 0 | 2 |
| swapped_symbols | 116 | 115 | 82 | 6 | 1 | 3 |
| off_by_one | 83 | 177 | 7 | 1 | 0 | 10 |
| num_den_swap | 141 | 122 | 0 | 5 | 0 | 6 |
| missing_term | 182 | 86 | 10 | 7 | 0 | 3 |

Total kept 1320 from 272 identities; 268 candidate edits dropped, 142 of them because they left the identity true. Oracle-rejected known-good: `bench:good:0119` Vandermonde's identity (ValueError: gamma function pole).

**LaCASt** (`lacast.py`, data in `lacast/`): the LaCASt repository (MIT licence, copied to
`lacast/LICENSE`) contains the 95-entry Wikipedia gold set of Greiner-Petter et al. (TPAMI 2022) in
`misc/Results/Wikipedia/gold-data.json` and the human evaluation in `misc/Results/Wikipedia/All.txt`.
Those human labels grade **translation** correctness (semantic LaTeX 48 ✔ / 47 ✘; Mathematica
24 ✔ / 53 ✘ / 18 no translation; Maple likewise), **not whether the formula is true**. The set is
therefore used for (a) translate coverage on real Wikipedia LaTeX, cross-tabulated with the human
labels, and (b) verify FAILs as leads for review; it is not scored for precision. Many entries are
not identities at all (`x = \pm 1`, `s \not = 1`, definitions of polynomials via `{}_3F_2`).

## The oracle

`oracle.py` is a small, independent LaTeX → SymPy parser for exactly the dialect above plus a numeric
checker (mpmath, 30 digits; sums/products/integrals evaluated with `mpmath.nsum`/`nprod`/`quad`,
with a Levin cross-check and Euler–Maclaurin fallback for slowly converging series — SymPy's
`Sum.evalf` returns wrong values for parametric infinite series). It deliberately shares no code with
the translate stage, so the labels do not inherit translate's bugs. Variables are declared per
identity with a sampling type (`real`, `pos`, `unit`, `sym1` = |x|<1, `gt1`, `posint`, `nonnegint`, …).

## Commands

```bash
uv run formulaci bench build                       # writes data/bench/{known_good,mutated,lacast_benchmark}.jsonl + build_stats.json
uv run formulaci bench measure                     # all stages, both sets -> data/bench/metrics.json + REPORT.md
uv run formulaci bench measure --limit 40          # first 40 identities + their mutations (quick)
uv run formulaci bench measure --stages translate --sets lacast
uv run pytest tests/bench
```

`build` also refreshes the committed snapshot in `formulaci/bench/sets/` (the repo's `.gitignore`
excludes `data/**/*.jsonl`). Build takes ~4 min on all cores (the mutation oracle dominates).

`measure` imports `formulaci.<stage>.run` (also `.run`/`.stage`/`.core` submodules), maps our paths onto
its parameter names (`in_path`, `out_path`, `formulas_path`, `semantics_path`, `force`, …) and writes
stage outputs to `data/bench/runs/<set>/`, never to other stages' data directories. A stage that is
missing, still the skeleton stub, or raises is reported as `unavailable`/`error` and everything after it
is not measured.

## Metrics

Positive = "the formula is wrong"; predicted positive = verdict `FAIL`.

- **precision** = FAIL on mutated / (FAIL on mutated + FAIL on known-good)
- **recall** = FAIL on mutated / all mutated (end to end: an untranslated mutation is a miss);
  **recall given verified** restricts to mutations that reached PASS/FAIL/INCONCLUSIVE;
  **recall on mutations of passing identities** restricts to mutations whose known-good source PASSed
  (isolates verify's sensitivity from translate/semantics coverage)
- translate coverage = share of formulas whose every `Parsed` record has `status == "ok"`
- checkability = share of translated formulas that semantics marks `checkable`
- per category, per mutation type, per translator status; the false-positive list (known-good → FAIL)
  and the missed-mutation list are in `metrics.json` and `REPORT.md`; per-formula rows in `rows.jsonl`.

Note the mutated set has ~4.9× as many wrong as right formulas, so precision here is higher than it
would be at Wikipedia's (very low) error prevalence; the false-positive *rate* on known-good formulas is
the number to extrapolate from.

## Latest numbers

Measured 2026-10-21 14:12:07 against the stages' code at that time (`formulaci.translate.run`, `formulaci.semantics.run`, `formulaci.verify.run.run`), total runtime 536.4 s. Full tables: `data/bench/REPORT.md`.

| metric | known-good (272) | mutated (1320) |
|---|---|---|
| translate `ok` | 100.0% | 100.0% |
| semantics checkable (of translated) | 99.6% | 98.9% |
| verdicts | PASS 263, FAIL 0, INCONCLUSIVE 5, SKIP 4, MISSING 0 | PASS 2, FAIL 1082, INCONCLUSIVE 212, SKIP 24, MISSING 0 |
| INCONCLUSIVE rate | 1.8% | 16.1% |

- **precision 100.0%** (TP 1082, FP 0; false-positive rate on known-good 0.0%)
- **recall 82.0%** end to end; 83.5% of mutations that reached a verdict; 83.5% on mutations of identities whose known-good form PASSed (n=1282)
- recall per mutation type: dropped_factor 82.8%, exponent_pm1 90.3%, missing_term 74.7%, num_den_swap 78.0%, off_by_one 77.1%, sign_flip 87.5%, swapped_symbols 74.1%, wrong_constant 82.9%
- mutations judged PASS (worst misses): 2; known-good formulas translate did not handle: 0
- LaCASt set: translate ok 40.0%, checkable end to end 6.3%, verdicts PASS 2, FAIL 2, INCONCLUSIVE 2, SKIP 89, MISSING 0

### What the numbers say (for the other stages)

- **Why recall is 82%:** 133 of the 212 INCONCLUSIVE mutations fail at many points but "not at a
  clear majority in every regime". Verify requires a majority in every regime, including regimes that
  fall outside the stated domain (e.g. `integers_small`/`large` for a |x| < 1 series, or negative
  values for an inequality stated for x ≥ 0). The weakest categories are inequalities (37% recall),
  zeta (61%) and hyperbolic (66%).
- The other misses are series/integrals that verify could not evaluate ("series terms do not tend to
  zero", "integral did not converge"), plus 24 formulas that semantics marked SKIP
  (`has_undefined_function`, `definition`).
- **The 2 PASSed mutations** (`bench:mut:0157:wrong_constant`, `bench:mut:0162:wrong_constant`) are
  wrong |x| < 1 series that verify accepted as "integer-only identities" because they hold at the
  integer sample points. Integer sampling of a variable whose domain is |x| < 1 only reaches x = 0.
- **2 FAILs on the LaCASt Wikipedia set look like false positives:**
  `\operatorname{Si}(ix) = i\operatorname{Shi}(x)` (a true identity; the counterexample sets `i=1`,
  so `i` was not read as the imaginary unit) and the Ince differential equation `w''+…=0` (an ODE, not
  an identity; it should have been skipped as `statement_not_identity`). On LaCASt, translate gets
  `ok` on 40% and only 6% end up checkable, so real Wikipedia LaTeX is much harder than the synthetic set.

## Known limitations

- Known-good identities are classical textbook identities written by us in Wikipedia style; real
  Wikipedia LaTeX is messier (see the LaCASt set for that).
- Mutations are single, local edits; real errors also include wrong conditions/domains, which this
  set does not model.
- The oracle samples 6 points; a mutation that is wrong only on a small part of the domain is dropped
  as `weak`, so recall is measured on clearly wrong formulas, consistent with verify's FAIL policy.
- LaCASt formulas carry no truth labels.
