# verify — PASS / FAIL / INCONCLUSIVE / SKIP for each checkable formula

Input: `data/parsed/parsed.jsonl` (`Parsed`) joined on `formula_id` with
`data/semantics/semantics.jsonl` (`Semantics`). Output: `data/verdicts/verdicts.jsonl` (`Verdict`).

```bash
uv pip install gmpy2            # until it is in pyproject (see PROPOSALS.md); ~2x faster mpmath
uv run formulaci verify run --parsed data/parsed/parsed.jsonl --semantics data/semantics/semantics.jsonl \
    --out data/verdicts/verdicts.jsonl --workers 4      # --limit N, --force, --cap 20, --quiet
uv run formulaci verify one 'wiki:en:12316:1381182218:61'   # every regime and point, for debugging
uv run pytest tests/verify                                  # 45 tests, 60–100 s with 4 workers
```

The run is resumable: ids already in `--out` are skipped, `--force` starts over. Each verdict is appended
as soon as it is ready. A completed run rewrites the file in input order. Sampling is seeded by
`formula_id`, so reruns are identical unless a formula's time budget binds (see weaknesses).

## How a formula is judged

1. **Reconstruction** (`reconstruct.py`). The srepr strings are untrusted, since they come from
   Wikipedia LaTeX. They are parsed with `ast`, and each node is checked against a whitelist: calls to
   sympy names, numeric and boolean literals, and tuples. String literals are allowed only as the name
   of a `Symbol`/`Function` or the digits of a `Float`/`Integer`/`Rational`, because most sympy
   functions sympify strings, which evaluates them. Names that parse, print, plot, lambdify or run tests
   (`S`, `sympify`, `lambdify`, `var`, …) are refused. The whitelisted tree is evaluated with no builtins.
   - Constants (`e`→`E`, `i`→`I`, …) come from `Semantics.constants`.
   - Symbols are recreated with assumptions from `Semantics.domains` (`positive=True`, `integer=True`, …)
     and substituted with `xreplace`. Undomained symbols are real. Symbols used as `Sum`/`Product`
     bounds default to non-negative integers.
   - Constraints are parsed by a small whitelisted grammar.
   - Generated code never sees a Wikipedia symbol name: symbols are renamed `v0, v1, …` before
     `lambdify`.
2. **Symbolic** (`symbolic.py`). Runs `lhs - rhs` through as-is, `expand`, `doit`, `cancel`,
   `trigsimp`, `expand_trig`, `gammasimp`, `combsimp`, `powsimp`, `expand_log`, `simplify`,
   `nsimplify` and `.equals(0)` (True only). It runs in a killable worker capped at 6 s (3 s for
   integrals and infinite series).
   - `not_equal` only when the difference simplifies to a nonzero constant. `equals(0) == False` is
     ignored because its random-point test ignores assumptions: it called the true
     `atan(x)+atan(1/x)=π/2` (x>0) unequal.
   - For inequalities, `equal` means the ordering was proved (`is_nonpositive` of the difference).
3. **Numeric** (`numeric.py`, `sampler.py`). Both sides are lambdified to mpmath at 50 digits.
   - `binomial` maps to `mpmath.binomial`, because lambdify's gamma-ratio form has poles at
     integers. `Derivative`/`Limit` are resolved with `doit()`.
   - `Sum`/`Product`/`Integral` are evaluated by our own closures, per point:
     - finite symbolic bounds are instantiated (reversed ranges are an error, not a convention guess);
     - infinite ranges first check that terms tend to 0 (or 1 for products), then sum directly while
       terms decay geometrically, otherwise use `nsum`/`nprod` extrapolation. The extrapolation is
       accepted only if restarting it 25 terms later, at +10 digits, gives the same value;
     - integrals use `mpmath.quad` with its error estimate **and** a second `quad` on a subdivided
       interval. quad's own error estimate was confidently wrong for sharply peaked integrands
       (`∫₀¹ t^{z-1}(1-t)^{z-1}dt` at z=300).
   - Indefinite integrals are compared by differentiating both sides in the integration variable, so
     the constant of integration drops out.
   - Regimes: `small_positive` (log-uniform 0.05–5), `unit_interval`, `integers_small` (0–12, every
     symbol an integer), `mixed_sign` (±5), `large` (log-uniform 10–1000), and `complex` (box ±3) when
     a symbol's domain is complex. Integer-typed symbols always get integers. Domain bounds and
     excludes are applied, then constraints by rejection.
   - Sample values are exact 6-significant-digit decimals. Points are drawn round-robin across regimes
     until each has 12 evaluable points (6 for integrals and infinite series) or 40 attempts.
   - In real regimes a non-real value is an *error*, not a mismatch, unless the formula contains `I`.
     So are poles, overflow, non-convergence and the 2 s per-point alarm (5 s for slow expressions,
     8 s for constants).
   - **When a mismatch counts.** Relative error > 1e-8 at 50 digits makes a point a candidate. It
     counts as a failure only if both sides reproduce to 1e-15 at the next rung of the precision
     ladder 50→65→100→200→400→1000. A difference that shrinks with precision is rounding noise around
     0, so the point passes. An exact 0 from a non-trivial expression must survive the whole ladder,
     because total cancellation produces stable zeros: `cosh²x − sinh²x` evaluates to exactly 0 at
     x=900 until about 900 digits.
4. **Policy** (`policy.py`), exactly SPEC's FAIL rule plus two documented extensions:
   - **FAIL** iff all of these hold:
     - symbolic is not `equal`;
     - every regime with ≥5 evaluable points has ≥70% failing points ("clear majority");
     - there are ≥2 such regimes (3 if the numeric phase hit its deadline);
     - no special-case rule applies.
     - Extension: *constant identities* (no free symbols) FAIL on one ladder-confirmed point.
   - **Special cases → INCONCLUSIVE:**
     - one side is a bare symbol absent from the other ("solves for symbol", e.g. `\alpha = \pi/4`);
     - failures only in `mixed_sign`/`complex` while every positive regime passes. The reason names
       branch cuts when the formula has sqrt/log/inverse trig/non-integer powers, otherwise "unstated
       domain restriction";
     - failures only in `integers_small` (measure-zero: removable singularity or convention);
     - fails somewhere but not by a clear majority everywhere;
     - symbolic `equal` contradicted by numerics;
     - too few evaluable points.
   - **Integer-only identities.** If `integers_small` passes and a non-integer positive regime fails,
     the formula is resampled at integers (`integers_large` 13–40, `integers_mixed_sign` ±10). It is
     PASS ("integer-only identity whose integer domain was not stated") if all of those pass, else
     INCONCLUSIVE.
   - **PASS:** symbolic `equal` with no numeric failure, or no failure at ≥10 evaluable points
     (unless symbolic is `not_equal`).
   - **Statement guards (FAIL → INCONCLUSIVE):**
     - a free symbol named `e`, `i`, `j` or `pi` that Semantics neither mapped to a constant nor gave
       a domain;
     - an equation with a literal 0 side and free variables (an equation to solve, not an identity).
   - **SKIP:** translate status not `ok`, `checkable=false`, no Semantics record, undefined functions
     (`f(x)`), matrices/indexed objects, or relations `≠ ≈ ∼ ∝`.
   - **Chains** (several `Parsed` per `formula_id`) are verified link by link inside the same 20 s budget
     and combined into one Verdict, since `Verdict` has no `index_in_chain` (proposed).
   - **Counterexample**: the smallest-magnitude failing point. Assignments are the exact sampled
     decimals; lhs/rhs/abs_diff/rel_diff are given to 40 significant digits, or "0" when exactly zero.
     `reason` is one sentence.
5. **Robustness** (`pool.py`, `worker.py`, `run.py`).
   - Each formula runs as three tasks (prepare / symbolic / numeric) in a worker process forked from a
     forkserver that has sympy, mpmath and warm quadrature caches preloaded. A worker that overruns is
     SIGKILLed and re-forked in ~50 ms.
   - The numeric task finishes cooperatively before its kill time. Points run under a SIGALRM, which
     does interrupt pure-Python mpmath.
   - The per-formula cap is 20 s. An internal error becomes INCONCLUSIVE and never stops the batch. The
     run shows a rich progress bar with live verdict counts.

## Measured on the built-in corpus (`tests/verify/fixtures/corpus.jsonl`, 131 Parsed+Semantics pairs)

| category | n | PASS | FAIL | INCONCLUSIVE | SKIP |
|---|---|---|---|---|---|
| true identities (trig, hyperbolic, log/exp, gamma/beta reflection & duplication, binomial & Vandermonde sums, finite/telescoping/geometric/infinite series & products, definite/indefinite integrals, derivatives, AM–GM, Bernoulli, Cauchy–Schwarz, triangle, tangent-line inequalities) | 56 | **56** | 0 | 0 | 0 |
| mutations (sign flip, exponent ±1, dropped factor/term, wrong constant/function/operator, swapped symbols, off-by-one value/bound, flipped inequality) | 55 | 0 | **54** | 1 | 0 |
| branch-cut traps (`√(xy)=√x√y`, `√(x²)=x`, `asin(sin x)=x`, `acos∘cos`, `atan∘tan`, `atan x+atan 1/x=π/2`, `log(xy)`, `log(x/y)`, `log z²`, `(z³)^{1/3}`, `√x/√y`, `(xy)^a`, `z^{ab}` with complex or unrestricted symbols) | 14 | 0 | **0** | **14** | 0 |
| special rules (solves-for-symbol, integer-only `sin(πn)=0`, measure-zero `⌊x⌋+⌊−x⌋=−1`, undefined function, not checkable, `e^{iπ}+1=0`) | 6 | 2 | 0 | 2 | 2 |

**Precision on the corpus: 54 FAIL verdicts, 54 correct (0 false FAILs); recall on mutations 54/55.**
- *Asymptotic misses.* Both are mutations that agree with the truth to 1e-8 in the `large` regime, so
  "every regime fails" cannot hold. They are marked "known miss" in the corpus:
  - `tanh x` vs `(e^x−1)/(e^x+1)`: both → 1;
  - `Σ_{k≥1} x^k/k!` vs `e^x`: relative difference e^{−x}.

  The second still FAILs when its large-regime points run out of time, which they did in the
  measured run.
- *Wall time.* 50 s for the whole corpus with 4 workers on an 8-core Apple Silicon laptop with gmpy2.
  The full `pytest tests/verify` (45 tests) takes 60–100 s.

Real Wikipedia formulas (`fixtures/wiki_sample.jsonl`): 17 formulas with real ids, hand-translated, 2 of them
chains (`\tbinom42 = … = 6`, `Γ(bi)Γ(−bi)=…=π/(b sinh πb)`).
- 11–14 PASS, depending on how many slow ones finish in time.
- 1 INCONCLUSIVE (solves for symbol), 2 SKIP, 0 FAIL.
- 3 can come back INCONCLUSIVE for time: Euler's infinite product for Γ, `|Γ(a+bi)|²` as an infinite
  product, and `Γ²(z)/Γ(2z)=∫…` (quad refuses the sharply peaked or strongly singular cases).

**Real translate output, no semantics yet (diagnostic, not a precision claim).**
- Sample: 300 random formulas from `data/parsed/parsed.jsonl` (all links `ok`, not `definition_like`).
  Each was given an *empty* Semantics record, i.e. everything "checkable" and no constants mapped.
- Result: 22 PASS, 87 SKIP, 41 FAIL, 150 INCONCLUSIVE, in 60 s with 4 workers.
- Before the two statement guards below there were 63 FAILs. Reading all 63: **none is a wrong
  identity.** They are equations to solve (`ax²+bx+c=0`, `xy−1=0`), physical laws relating
  measured quantities (`1/S₁+1/S₂=1/f`, `nh/2π=mvr`), conditions (`n_i n_i=1`), and Euler's formula
  with `e`, `i` left unmapped.
- So verify's real-world precision rests on Semantics: `checkable=false` with
  `skip_reason="statement_not_identity"` for relations between quantities, and constants mapped.
  Verify adds two guards of its own, so these cases can only be INCONCLUSIVE:
  - a symbol named `e`/`i`/`j`/`pi` that Semantics neither mapped nor typed;
  - an equation with a literal `0` side and free variables.
- A formula with **no** Semantics record is SKIPped.

## Known weaknesses

- **Asymptotically equivalent errors are not flagged.** If a wrong formula agrees with the right one to
  1e-8 for large arguments, the `large` regime passes and the FAIL rule (every regime) cannot fire.
  This is the price of the spec's precision-first rule.
- **Time-dependent sample size.** Integrals and infinite products/series cost 0.1–2 s per point (each
  confirmed failure costs at least two evaluations). Under load, or without gmpy2, they may not reach 5
  points per regime and become INCONCLUSIVE "too few evaluable points". Results are deterministic only
  while the budget does not bind.
- **Symbolic `not_equal` is rare by design.** It comes only from constant differences, so the column
  is mostly `equal`/`unknown`. Simplification of large expressions often uses the full 6 s.
- **Domain defaults.** Undomained symbols are real, and the `complex` regime only exists when Semantics
  says a symbol is complex. Real-only identities therefore PASS without complex testing. Identities
  stated "for x>0" without a domain record fall to INCONCLUSIVE via the branch/domain rule; they are
  not false FAILs.
- **Conventions are not modelled.**
  - Principal branches only (mpmath's): a real cube root of a negative number is an error point.
  - `acot` follows sympy's convention.
  - Reversed sum ranges are refused.
- **Not supported numerically:** limits that sympy cannot resolve, derivatives of undefined functions,
  contour/multiple-variable-region integrals, `Indexed` symbols, matrices, oscillatory infinite
  integrals (quad's error estimate rejects them). These end as SKIP or INCONCLUSIVE, never FAIL.
- `Verdict` has no `index_in_chain` yet, so a chain gets one combined verdict (see PROPOSALS.md).
