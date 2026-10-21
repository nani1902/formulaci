# formulaci — a test suite for human knowledge

Goal: machine-verify the formulas people rely on. Phase 1 target: every `<math>` identity in
English Wikipedia's mathematics, physics, statistics and engineering articles, plus the formulas
behind widely used online clinical calculators. Output: a list of **confirmed** wrong formulas
with reproducible evidence, a measured precision figure for the pipeline, and a tool anyone can
rerun.

Prior art we build on, not repeat: Greiner-Petter et al., "Do the Math" (TPAMI 2022) proved
CAS-based checking of Wikipedia formulas works on 103 pages using Maple/Mathematica + LaCASt
(https://github.com/gipplab/LaCASt). It was never deployed. We use free tools (SymPy, mpmath)
and run it at scale.

## Pipeline (each stage = one module = one owner session)

```
extract  ->  translate  ->  semantics  ->  verify  ->  report
(wiki)       (latex->sympy)  (domains)     (numeric)    (findings + HTML)
                                   \-- clinical (separate track: reference formulas + web audit)
                                   \-- bench    (labeled sets, precision/recall measurement)
```

Every stage reads JSONL from `data/<prev>/` and writes JSONL to `data/<own>/`. Records are
joined by `formula_id`. Each stage must be **idempotent and resumable** (skip ids already in
output unless `--force`). Each stage exposes a function `run(in_path, out_path, **opts)` and a
typer sub-app `app` in `formulaci/<stage>/cli.py`; the root CLI (`formulaci/cli.py`, owned by
the coordinator) mounts them. Do not import across stages except via `formulaci.schemas`.

## Shared schemas — `formulaci/schemas.py` (owned by coordinator; propose changes, don't edit)

All records are pydantic models serialized one-per-line as JSON.

### Formula (stage: extract)
- `formula_id: str` — `wiki:{lang}:{page_id}:{revision_id}:{index}`; stable across reruns of the same revision
- `source: str` — `"wikipedia"`
- `lang: str` — `"en"`
- `page_title: str`, `page_id: int`, `revision_id: int`, `url: str`
- `section: str` — section heading path, e.g. `"Properties > Derivative"`
- `index: int` — 0-based order of this `<math>` in the page
- `latex: str` — raw contents of the `<math>` tag (also handle `{{math|...}}` templates where they contain LaTeX via `<math>`; skip pure-HTML math templates but count them)
- `display: bool` — block (`<math display=block>` / `:<math>`) vs inline
- `context_before: str`, `context_after: str` — plain-text prose within ~400 chars on each side, wikitext stripped
- `page_categories: list[str]`

### Parsed (stage: translate)
- `formula_id: str`
- `status: Literal["ok","unparsed","not_checkable"]`
- `kind: Literal["equation","chain","inequality","definition_like","other"]` — `chain` = `a = b = c` (split into pairwise equations, each a `Parsed` with `index_in_chain`)
- `index_in_chain: int | None`
- `lhs: str | None`, `rhs: str | None` — `sympy.srepr()` of each side (so it round-trips with `sympy.sympify`/`eval` of srepr); for inequalities include `relation: str` (`"<", "<=", ...`)
- `free_symbols: list[str]`, `functions: list[str]` — names of undefined functions (e.g. `f`, `g`)
- `has_unsupported: list[str]` — constructs recognized but not translated (e.g. `\oint`, `\mathbb{E}`), so coverage can be reported
- `error: str | None`
- `translator: str` — e.g. `"sympy-lark-1.13"` or `"custom"`; note what preprocessing was applied in `notes: str | None`

### Semantics (stage: semantics)
- `formula_id: str`
- `checkable: bool`, `skip_reason: str | None` — e.g. `"definition"` (`f(x) = x^2` defines f), `"has_undefined_function"`, `"operator_notation"`, `"units"`, `"statement_not_identity"`
- `domains: dict[str, Domain]` where `Domain = {type: "real"|"positive"|"nonneg"|"integer"|"nonneg_integer"|"positive_integer"|"complex"|"unit_interval"|"angle", lower: float|None, upper: float|None, exclude: list[float]}`
- `constants: dict[str, str]` — symbol -> canonical constant (`"pi"`, `"E"`, `"I"`, `"EulerGamma"`, `"GoldenRatio"`), applied when context implies it (e.g. `e` in `e^{x}` is Euler's number; `i` with `i^2=-1`)
- `constraints: list[str]` — sympy-parseable boolean expressions from context (e.g. `"n >= 1"`, `"Ne(x, 0)"`), extracted from prose like "for x > 0", "where n is a positive integer", and from the formula itself (`\quad x>0`, `\text{for } ...`)
- `assumptions_source: list[str]` — which rule fired, for auditability
- `backend: str` — `"rules"` (default). An optional LLM backend may exist but must be off by default.

### Verdict (stage: verify)
- `formula_id: str`
- `verdict: Literal["PASS","FAIL","INCONCLUSIVE","SKIP"]`
- `symbolic: Literal["equal","not_equal","unknown"]` — result of `simplify(lhs - rhs) == 0` with a timeout
- `regimes: list[RegimeResult]` where `RegimeResult = {name: str, n_points: int, n_fail: int, n_error: int}`; regimes must include at least `"small_positive"`, `"unit_interval"`, `"integers_small"`, `"mixed_sign"`, and `"complex"` when domain allows
- `counterexample: {assignments: dict[str,str], lhs: str, rhs: str, abs_diff: str, rel_diff: str} | None` — the single clearest failing point, values as decimal strings at ≥30 digits
- `tolerance: {abs: float, rel: float, dps: int}`
- `reason: str` — one sentence a human can read
- FAIL policy: FAIL only if (a) symbolic is not `equal`, and (b) the identity fails at a clear majority of *evaluable* points in **every** regime where ≥5 points were evaluable, with relative error > 1e-8 at mpmath 50 dps, and (c) the failure is not explained by a known special-case rule (sign of sqrt branch, log branch cut, integer-only identity sampled at non-integers → must resample). Anything else is INCONCLUSIVE or PASS. Precision beats recall: a flag should be worth a human's minute.
  Ratified extensions (verify session): constant identities (no free symbols) use a single `constant` regime and FAIL only when the mismatch is stable at 50 and 65+ digits and symbolic is not `equal`; FAIL needs at least 2 qualifying regimes (3 if the numeric phase hit its deadline); `Tolerance.abs` is 0.0 (near-zero noise is recognised by shrinking with precision).
  Extensions after the 2026-10-21 black-box tests: (i) a near-unanimous failure (≥85% of all evaluable points, at least half of the points in every one of ≥3 qualifying regimes) is a FAIL, since the agreeing points of a wrong polynomial identity are degenerate (a variable 0, two variables equal); (ii) a constant identity whose quadrature/summation does not converge FAILs when symbolic is `not_equal` and SymPy's closed forms of both sides evaluate, stably at 50 and 100 digits, to values that differ (the Dirichlet integral set equal to π); (iii) a symbol whose real (non-integer) type the prose stated is never resampled as an integer, so "x² ≥ x for all real x" cannot become an integer-only PASS; (iv) in semantics, a universal cue in the adjacent prose ("for all a, b") keeps relation-shaped formulas (two polynomials that are not identically equal, expression = constant) checkable, so a wrong identity stated as one FAILs instead of being skipped as an equation to solve.
- Join key: one formula can yield several `Parsed` records (`index_in_chain`); verify emits one `Verdict` per `formula_id` combining the pieces (any FAIL → FAIL, all PASS → PASS, else INCONCLUSIVE). `index_in_chain`, `skip_pieces`, `function_aliases`, `details` fields were added to the schemas as optional.
- `skip_reason` vocabulary (semantics): definition, has_undefined_function, functional_identity, operator_notation, congruence, matrix_or_vector, set_notation, statement_not_identity, plus_minus, indefinite_integral, units, no_relation, unparsed, translator_not_checkable, semantics_error, semantics_timeout, equation_to_solve.

### Finding (stage: report; also produced by human/agent review)
- `formula_id: str`, `verdict: str`, `confidence: float` (0–1)
- `review: {status: "unreviewed"|"confirmed_error"|"false_positive"|"ambiguous", reviewer: str, notes: str}`
- `suggested_fix: str | None` — corrected LaTeX
- `evidence: str` — human-readable, includes counterexample and a pointer to an independent source if one was found

### Clinical track (`formulaci/clinical/`)
- `formulas.py`: pure-Python reference implementations, each with a docstring citing the primary publication (DOI) and the exact equation, and a `@formula(name, version, citation)` registration; cover at minimum: eGFR CKD-EPI 2021 (creatinine; and creatinine-cystatin C), CKD-EPI 2009 (for detecting sites still using the race coefficient), MDRD, Cockcroft–Gault, Schwartz bedside 2009 (pediatric eGFR), BMI, BSA (Mosteller, Du Bois, Haycock), QTc (Bazett, Fridericia, Framingham, Hodges), MAP, anion gap (with/without K), corrected calcium, corrected sodium (Katz, Hillier), FENa, Winters' formula, LDL (Friedewald, Martin-Hopkins), ideal body weight (Devine), Parkland, Holliday–Segar.
- `vectors.json`: for each formula, ≥5 reference input/output pairs computed from the primary source (not from a website), including unit-conversion cases (µmol/L vs mg/dL, cm vs in) and edge cases.
- `targets.yaml`: list of public calculator pages to audit, with CSS selectors or a driving recipe. **Live runs against third-party sites require the user's explicit go-ahead; build and test against a local mock server first.**
- `audit.py`: Playwright harness that fills reference inputs, reads the result, compares to the reference implementation, and writes `data/clinical/audit.jsonl` with `{target, formula, inputs, site_output, reference_output, status: match|mismatch|unreadable, notes}`.

### Bench track (`formulaci/bench/`)
- Build labeled sets to measure the pipeline: (1) `known_good.jsonl` — identities known to be true (from DLMF-style classical identities and from Wikipedia formulas that passed and were spot-checked); (2) `mutated.jsonl` — those identities with injected errors (sign flip, exponent ±1, swapped symbols, dropped factor, off-by-one in a bound, wrong constant), each tagged with the mutation; (3) if obtainable, the 95-entry hand-evaluated Wikipedia benchmark from the LaCASt repository, converted to our `Formula` schema.
- `measure.py`: runs translate→semantics→verify over these sets and reports precision/recall/coverage per mutation type and per translator status. Output `data/bench/metrics.json` + a markdown summary.

## Ground rules for every session
- Own only your directory: `formulaci/<stage>/` and `tests/<stage>/`. Do not edit `formulaci/schemas.py`, `formulaci/cli.py`, `pyproject.toml`, or another stage's directory; if you need a schema change, write it to `PROPOSALS.md` under a heading with your stage name and continue with a local workaround.
- Add dependencies only by appending to `PROPOSALS.md`; the coordinator will add them to `pyproject.toml`. Until then, `uv pip install` locally.
- Do not commit. Do not switch branches. The coordinator commits.
- Tests: `uv run pytest tests/<stage>` must pass; include at least one end-to-end test on real sample data checked into `tests/<stage>/fixtures/`.
- Write `formulaci/<stage>/README.md`: how to run, what is covered, what is not, known failure modes. Honest coverage numbers over marketing.
- Network: Wikipedia API only with a descriptive User-Agent **with contact info** (read from `FORMULACI_CONTACT`, never checked in) and ≤ 5 req/s; cache raw responses under `data/raw/cache/`.
- When done, your final message must state: what works, measured numbers, what does not work, and the exact command to run your stage.
