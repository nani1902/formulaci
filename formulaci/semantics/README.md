# semantics stage

For every parsed formula, decide what the verifier needs: which letters are constants, the
domain of each free symbol, constraints, and whether the formula is checkable at all.
Rules only (no LLM, no network), deterministic, ~25 ms per formula.

```
uv run formulaci semantics run --formulas data/raw/formulas.jsonl --parsed data/parsed/parsed.jsonl \
    --out data/semantics/semantics.jsonl [--limit N] [--force]
uv run formulaci semantics explain 'wiki:en:12316:1381182218:59'   # which rules fired and why
uv run formulaci semantics score                                    # accuracy on the hand-labeled fixtures
uv run formulaci semantics score --fixtures tests/semantics/fixtures/holdout.jsonl
```

`run` is resumable: ids already in `--out` are skipped unless `--force` (which truncates the
output). Python API: `formulaci.semantics.run(in_path=parsed, out_path, formulas_path=..., limit, force)`,
`formulaci.semantics.explain(formula_id, formulas_path, parsed_path)`, `formulaci.semantics.infer(formula, pieces)`.

## Output conventions (for the verify stage)

- One `Semantics` record per `formula_id`. Chains (`a = b = c`, several `Parsed` pieces) are
  merged: the record is checkable only if **every** piece is (see blind spots).
- `constants` maps a symbol name to a sympy constant (`E`, `I`, `pi`, `EulerGamma`, `GoldenRatio`)
  **or an undefined function name to a sympy function** (`B -> beta`, `F -> fibonacci`,
  `H -> harmonic`, `psi -> digamma`, `Gamma -> gamma`, ...). Apply with
  `expr.subs({Symbol(k): getattr(sympy, v)})` for symbols and `expr.replace(Function(k), getattr(sympy, v))`
  for functions.
- `domains[x].type` is one of the schema types; `lower`/`upper` are set only when tighter than
  the type implies (e.g. `positive` with `lower=1` for "x >= 1"). Strictness is not representable
  in `Domain`, so every prose bound is also emitted in `constraints`.
- `constraints` are sympy-parseable strings. Two special forms:
  - Gamma poles: `Not(And(Eq(a, floor(re(a))), re(a) <= 0))` = "a is not a non-positive integer";
    works for real and complex `a`.
  - primes: `Q.prime(p)` (evaluate with `sympy.ask` after substitution).
- `assumptions_source` lists `RULE` or `RULE:symbol` for every rule that fired.

## Rules and measured accuracy

Fixtures: `tests/semantics/fixtures/cases.jsonl`, **124 real formulas** from 21 English Wikipedia
pages (Gamma function, Beta function, List of trigonometric identities, Binomial coefficient,
Riemann zeta function, Normal distribution, Logarithm, Exponential function, Complex number,
Golden ratio, Euler's constant, Euler's formula, Factorial, Inverse trigonometric functions,
Fermat's little theorem, Hyperbolic functions, Kinetic energy, Pythagorean theorem, Cauchy's
functional equation, Big O notation, Expected value), each with the real `<math>`, section and
~400 chars of real context, a hand-written `Parsed` record, and a hand label (80 checkable,
44 not). `build_cases.py` regenerates them from the API (cached).

**Caveat: the rules were developed against these 124 cases**, so their numbers are optimistic.
`holdout.jsonl` holds **36 more cases from 8 other pages** (Geometric series, Error function,
Harmonic number, Digamma function, Fibonacci sequence, Quadratic formula, Poisson distribution,
De Moivre's formula). They were labeled before the rules were run on them, scored once, and
not used for tuning. Treat the held-out column as the honest estimate.

Domains and constraints are scored *semantically*: labeled and inferred
(domains + constraints) are evaluated on a grid of integer, rational and complex sample points.
*Unsafe* = the rules admit a point the label forbids (that is what causes false FAILs downstream).
*Over-restrictive* = the rules exclude a point the label allows (costs coverage only).

| metric | dev (124) | held-out (36) |
|---|---|---|
| checkability accuracy | 99.2% | 100% |
| precision of `checkable=True` | 100% (79/79) | 100% (25/25) |
| skip_reason accuracy (both skipped) | 97.7% | 72.7% |
| recall of `checkable=True` | 98.8% | 100% |
| constants exact match (both checkable) | 100% | 96.0% |
| domain type exact match | 93.3% (89 symbols) | 83.3% (24 symbols) |
| unsafe cases | 2 / 79 | 1 / 25 |
| over-restrictive cases | 9 / 79 | 5 / 25 |
| fully correct cases | 88.7% | 75.0% |

Per-rule accuracy on the dev set (fired / correct; `uv run formulaci semantics score` prints the
current table). A constant rule is correct if that symbol's constant matches the label, a domain
rule if that symbol's final type matches, a constraint rule if none of its constraints excludes a
labeled-valid point, a K rule if checkability and skip_reason both match.

### Constants (`C.*`)

| id | rule | dev |
|---|---|---|
| C.e_power_base | `e` is the base of a power whose exponent is not a small integer literal -> `E` (`e^2` alone could be a squared charge) | 13/13 |
| C.e_log_arg | `ln e`, `log e` -> `E` | 1/1 |
| C.e_context | page/context mentions Euler's number, natural log, exponential (not if eccentricity / charge nearby) | 1/1 |
| C.e_left_variable | no evidence: `e` stays a variable | – |
| C.i_euler_exponent | `i` occurs in an exponent of e / exp -> `I` | 4/4 |
| C.i_squared | `i^2` (even power) occurs -> `I` | 1/1 |
| C.i_context | context or page title mentions imaginary/complex (and no index usage like `a_i`, "i = 1") -> `I` | 7/7 |
| C.i_left_variable | otherwise `i` stays a variable (domain nonneg_integer) | – |
| C.j_imaginary | `j -> I` only with an explicit cue ("imaginary unit j", electrical engineering, phasor) | (unit test) |
| C.gamma_euler_mascheroni | `gamma -> EulerGamma` only if context/title says Euler–Mascheroni | 4/4 |
| C.phi_golden_ratio | `phi/varphi -> GoldenRatio` only if context says golden ratio and phi is not inside a trig function | 4/4 |
| C.pi_symbol | a stray `pi` symbol -> `pi` | – |
| C.function_alias | undefined function -> sympy function when arity matches and (for ambiguous letters) context names it: Gamma, zeta, erf/erfc/erfi, Ei, Si, Ci, li; B -> beta ("beta function"), F -> fibonacci, L -> lucas, H -> harmonic, psi -> digamma, W -> LambertW | 4/4 |

### Domains (`D.*` letter defaults, `P.*` prose, `C.*_domain` expression)

| id | rule | dev |
|---|---|---|
| D.letter_integer | n, m, k, j, l, N -> nonneg_integer (also a leftover variable `i`) | 20/24 |
| D.letter_real | x, y, t, a, b, c -> real | 33/34 |
| D.letter_complex | z, w, s -> complex | 18/18 |
| D.letter_angle | theta, phi, alpha, beta inside a trig function -> angle | 11/11 |
| D.letter_greek_real | same letters outside trig -> real | 1/1 |
| D.letter_positive | epsilon, delta, h -> positive | – |
| D.letter_sigma | sigma -> positive | – |
| D.letter_r | r -> nonneg | – |
| D.prime_p | p with "prime" in adjacent context -> positive_integer + `Q.prime(p)` | (unit test) |
| D.default_positive | any other letter -> **positive real** (safe default) | 1/2 |
| P.compare | "x > 0", "0 <= k <= n", "\|x\| < 1", "Re(s) > 1", "b ≠ 1", "Re(s) = σ > 1" | 8/9 |
| P.type_phrase | "for every positive integer n", "x and y are real numbers", "for all complex numbers α and X", "p is prime", "odd n" | 11/12 |
| P.adjective | "b, x and y are all positive", "for nonzero x" | 3/3 |
| P.member / P.not_member / P.interval | "x ∈ ℝ", "k ∈ ℤ", "z ∉ ℤ", "x ∈ (0, 1)" | 3/3, 4/4 |
| P.enumeration | "n = 0, 1, 2, ..." | 1/1 |
| P.widening_ignored | a prose type that would *widen* a default is ignored unless it is adjacent (last 150 chars before / first 200 after), in the same sentence, and names no symbols foreign to the formula | 1/1 |
| C.factorial_domain | `x!` -> x nonneg_integer; `(n-1)!` -> n >= 1 folded into the domain | 3/3 |
| C.log_domain | bare argument of a real log with a default real domain -> positive | 6/6 |

Precedence: trailing conditions in the formula (`\quad x>0`, `\text{for } ...`) and translator
`cond:` notes > adjacent prose > far prose (only within 250/300 chars) > letter defaults. Explicit
bounds replace the default's sign assumption but keep its number system (n stays an integer).
Prose "integer n" does not widen a nonneg_integer default to negative integers; only a tail /
`cond:` note (e.g. `\text{for every } k\in\Z`) does.

### Constraints from the expression (`C.*`)

All are skipped when the symbol domains already imply them (checked with sympy assumptions).

| id | rule | dev |
|---|---|---|
| C.denominator_nonzero | `Ne(d, 0)` for every denominator (not for Gamma/exp) | 11/11 |
| C.log_arg / C.log_arg_complex | log argument `> 0` in the real regime, `Ne(a, 0)` in the complex regime | 1/1, 3/3 |
| C.sqrt_arg | fractional power base `>= 0` (`> 0` if negative exponent) in the real regime | 2/2 |
| C.real_power_base | base `> 0` when raised to a non-integer symbolic power in the real regime (sum/product indices count as integers) | 0 fired after fixes |
| C.gamma_pole | Gamma/loggamma/digamma/polygamma/beta arguments not non-positive integers (skipped for a Gamma that only divides: 1/Gamma is entire) | 15/15 |
| C.zeta_pole | `Ne(s, 1)` for zeta(s) | 3/3 |
| C.factorial_arg | compound factorial argument `>= 0` | 3/3 |
| C.asin_acos_arg | argument in [-1, 1] (real regime); also C.asec_acsc_arg, C.acosh_arg, C.atanh_arg | 1/1, 1/1 |
| C.trig_pole | tan/sec: `Ne(cos a, 0)`; cot/csc: `Ne(sin a, 0)`; coth/csch: `Ne(sinh a, 0)` | 3/3 |

### Checkability (`K.*`), in order of precedence

| id | skip_reason | rule | dev |
|---|---|---|---|
| K.units | units | a number followed by a unit (`80\,\text{kg}`, `18\,\mathrm{m/s}`, `20°`) | 1/1 |
| K.op_congruence | congruence | `\pmod`, `\bmod`, `\equiv` | 2/2 |
| K.op_asymptotic | operator_notation | `O(...)`, `o(...)`, `\mathcal O` | 2/2 |
| K.op_probability | operator_notation | `\mathbb E`, `\operatorname{E/Var/Cov/P}`, `\Pr`, `E[` | 2/2 |
| K.op_nabla / K.op_contour | operator_notation | `\nabla`, `\oint` | – |
| K.op_matrix | matrix_or_vector | matrices, `\mathbf`, `\vec`, transpose, `\det`, `\otimes` | 2/2 |
| K.op_set | set_notation | `\cup`, `\subset`, `\in`, `\{` in the formula body | 1/1 |
| K.op_logic | statement_not_identity | `\iff`, `\Rightarrow`, `\forall`, `\to` (outside `\lim_{...}`) | 1/1 |
| K.op_approx | statement_not_identity | `\approx`, `\sim`, `\propto`, `\cong`, `\ll` | 3/3 |
| K.op_cycle_notation | operator_notation | permutation cycles `(12)(34)` | (real data) |
| K.op_plusminus | plus_minus | `\pm`/`\mp` anywhere (even when the translator expanded variants) | 1/1 |
| K.op_partial | operator_notation | `\partial` with an undefined function | – |
| K.translator_unsupported / K.translator_status | operator_notation / unparsed / translator_not_checkable | translator flagged it | 1/1 |
| K.no_relation | no_relation | no lhs/rhs | – |
| K.derivative_symbol | differential_equation | a symbol named `*_prime`, `*_dot`, `x'` (the translator's `h''`): an ODE | (real data) |
| K.definition | definition | translator `definition_like`, `:=`, `\stackrel{def}{=}` | 3/3 |
| K.definition_known_function | (checkable) | `definition_like` whose lhs is a known sympy function (`\Gamma(z) = \int ...`): checked as an identity | 2/2 |
| K.functional_identity | functional_identity | an undefined function on both sides or with several argument patterns (`f(x+y) = f(x) + f(y)`) | 4/4 |
| K.undefined_function | has_undefined_function | any other remaining undefined function | 4/4 |
| K.indefinite_integral | indefinite_integral | an integral without bounds (equal only up to + C) | 2/2 |
| K.existential_context | statement_not_identity | adjacent prose: "there are infinitely many", "there exists", "at least one" | 1/1 |
| K.bare_symbol_definition | definition | one side is a bare symbol absent from the other side (`y = log_b x`, `E_k = mv^2/2`) | 4/5 |
| K.unbalanced_sides | statement_not_identity | *each* side has a symbol the other lacks (`a^2 + b^2 = c^2`, `E^2 = (pc)^2 + (mc^2)^2`) | 5/5 |
| K.condition_fragment | statement_not_identity | every side is a number, a bare symbol or `±|symbol|` (`|x| < 1`, `|k_j| = 1`, `|H| = -H`): a condition, not a claim. Also skips true `|z| >= 0` (the one dev recall loss) | 0/1 |
| K.polynomial_equation | statement_not_identity | polynomial in the variables equated to a constant (`x^2 + y^2 = 1`) | 2/2 |
| K.nonconstant_equals_constant | statement_not_identity | one side constant, the other numerically varies (`2βe^{1-β} = 1`); not applied to sides with sums/integrals/limits | (real data) |
| K.polynomial_relation | statement_not_identity | two polynomials that are not identically equal (Descartes' theorem, `4xyz = n(xy+xz+yz)`). **Deliberate trade-off:** a *wrong* polynomial identity also lands here; filter `assumptions_source` for this id to review them | (real data) |
| K.cancelling_symbol | – | a one-sided symbol that numerically cancels (`log_k x / log_k b`) is not treated as one-sided | 2/2 |
| K.context_relation | statement_not_identity | a one-sided symbol is tied to the others by an equation in adjacent prose (`ln z = ln\|z\| + iφ` after "z = \|z\| e^{iφ}") | 2/2 |
| K.inequality / K.numeric_only / K.chain | (checkable) | recorded for audit | 3/3, 15/15, 9/9 |

## Real data (extract + translate output, run end to end)

`data/raw/formulas.jsonl` (14,304 formula ids from extract) was translated with the translate
stage's own code into a scratch file and run through this stage: **14,304 records in ~95 s, no
errors, no timeouts**. 309 come out checkable. Most skips come from the translator
(`translator_not_checkable` 7,506, `operator_notation` 2,369, mostly flagged by the translator); of the
2,523 formulas the translator parsed completely, semantics skips definitions (1,145),
relations/conditions (`statement_not_identity` 857), undefined functions (346), matrices (767) etc.

Hand review of formulas the rules call checkable (random samples of 30, disjoint):

| sample | genuine identities | notes |
|---|---|---|
| 1 (before the real-data rules) | 24/30 | polynomial relations, `\|x\|<1` fragments, `2βe^{1-β}=1`, `e^2` read as Euler's e → added K.polynomial_relation, K.condition_fragment, K.nonconstant_equals_constant, tightened C.e_power_base |
| 2 | 27/30 | cycle notation `2143 = (12)(34)`, an ODE `h''+h=1/h`, a deliberately false example `1+1=3` → added K.op_cycle_notation, K.derivative_symbol |
| 3 (fresh, after all fixes but one) | 28/30 | `1+1=1` (deliberately false example on *Arithmetic*), `\|H\| = -H` (fixed afterwards). One unsafe domain: `Li_s(z) = Σ z^k/k^s` has no `\|z\|<1` |

So on real Wikipedia text, about **93% of "checkable" formulas are genuine identities**
(sample 3, n=30, so ±5%), and deliberately false textbook examples (`1+1=3` on *Equality*) cannot
be told apart by rules: the report stage's human review has to catch those. Every other number in
this README comes from curated fixtures and overstates real-world precision.

The translator turned `\lambda^{core}` into `λ^(c·e·o·r)` (superscript text read as a product);
that made one formula take 150 s here before the numeric test switched to floats. `run` now has a
per-formula `--timeout` (default 10 s) and records `semantics_timeout` / `semantics_error` instead
of crashing.

## Second pass: rules from the review of real FAILs

The coordinator's review of 266 real FAILs (`data/findings/reviews.jsonl`) tagged 135 false positives
as semantics problems. `uv run formulaci semantics review-check` recomputes semantics for exactly those
ids (plus the 13 confirmed real errors), runs the verify stage on them through its CLI, and reports:

| review class | n | skipped now | still checkable → verify |
|---|---|---|---|
| special_algebra | 39 | 39 | – |
| wrong_domain_or_constant | 42 | 31 | 8 PASS, 3 FAIL |
| defining_equation_or_solve | 31 | 29 | 2 FAIL |
| intentionally_false_in_context | 12 | 12 | – |
| approximation_or_rounding | 6 | 3 | 3 PASS |
| notation_or_convention | 5 | 4 | 1 INCONCLUSIVE |
| **confirmed real errors** | 13 | 1 (semigroup, by `special_algebra`) | 11 FAIL, 1 INCONCLUSIVE (verify's decimal-truncation leniency) |

**130 of 135 semantics-caused false FAILs no longer FAIL.** The 5 left are relations true only under
a condition stated in prose that the rules cannot extract (law of cosines with c fixed by a, b, γ;
`ad − bc = ±1`; `e^{iδ} = ±i`; a Born–von Karman boundary condition; the Soddy radius).

All 148 reviewed items are a fixture (`tests/semantics/fixtures/review_cases.jsonl`, built by
`build_review_cases.py`, labeled from the reviewer's note), scored by `test_review_cases_floors`:
of the formulas the rules call checkable 82.8% are genuinely checkable, recall of checkable 96%.
The dev and held-out fixtures did not regress (checkability 99.2% / 100%, precision 100% / 100%).

| id | skip_reason | rule |
|---|---|---|
| K.special_algebra | special_algebra | page title, section, ±400 chars of context or the LaTeX mention modulo/mod n, characteristic 2/p, finite/Galois field, GF(, 𝔽_q, ℤ/nℤ, ordinal, cardinal, ℵ, transfinite, (bi)quaternion, split-complex, dual/hypercomplex numbers, versor, semigroup, monoid, idempotent, Boolean, tropical, duodecimal/binary/base 12, floating point, Dirac matrices, non-Diophantine, trivial ring, Coxeter group, "square roots of minus one" (Hamilton). Costs one confirmed error (a semigroup identity) and every ordinary identity on such pages |
| K.stated_false | stated_false | within 200 chars before / 150 after: "is false", "a false statement", incorrect, not true, contradiction, no solution, cannot be justified, counterexample, fallacy, crank, purported, erroneous, invalid proof, faulty, redefinition of; before only: "claimed that", "if one would have", "instead of simply", "there is no x such that" |
| K.defining_cue | defining_equation | the last 80 chars before the formula: "the/this equation", "gives the equation", solve, solution, root of, unknown, determined by, "satisfying:" / "such that" at the very end, condition, boundary, implicit, "holds only when", writing, fixed point; cancelled by then / we have / can be written / is given by / follows / proof / obeys / satisfies. The first 150 chars after: solve, the solution, unknown, nonlinear equation, implicit, must lie, by definition, and "if/when ..." only when the clause names one of the formula's own symbols ("if σ is odd") |
| K.decimal_literal_side | defining_equation | a decimal literal equated to an expression in free symbols (`∫ ... = 0.95` defines z_{.975}) |
| K.condition_inequality | condition | an expression compared with a constant, with no "for all/every/any" nearby (`4p^3+27q^2 < 0`, `μ^2 < 0`, `\|1+hλ\| ≤ 1`). Also skips true `\|z\| ≥ 0` (the one dev recall loss) |
| K.rational_relation | statement_not_identity | two rational expressions not identically equal (checked symbolically *and* numerically, so φ² = φ+1 identities survive): the golden-ratio hypothesis, `(c+a)/b = b/(c−a)`, the cubic factorization under 4p³+27q²=0 |
| K.index_range | statement_not_identity | `i = 1, \ldots, n`, `i = 1,2,3` (and `i` is then never mapped to I) |
| K.noncommuting | matrix_or_vector | capital-letter or σ_k symbols with matrix/operator/Lie algebra/Pauli/Hermitian/commutator/symplectic/bivector/spinor in title, section or context, or a free `I` next to other capitals |
| K.named_constant / K.named_parameter / K.pi_named_object | named_constant | `\varpi` (lemniscate constant, no longer mapped to π); a symbol the prose fixes ("Define ρ = ½(√5−1)", "where q is eπ", "a, b, c are certain rational numbers"); `π = 0` (π names a bivector) |
| K.irrational_equals_rational | approximation | π, e, φ or γ equated to a rational (`π = 355/113`, `π = 3927/1250`) |
| K.acot_convention / K.multivalued_power | notation_or_convention | arccot (sympy's range differs from (0, π)); a complex power of a non-positive base |
| K.function_name_misread | definition | `e(t) = exp(2πit)`: a function being defined, read by the translator as e·t |
| C.i_factor | (constant) | `i` multiplying other quantities (`a+bi`, `Si(ix)`, `(cos x + i sin x)^3`) is the imaginary unit unless index usage is seen |
| C.phi_golden_ratio | (constant) | now also on "golden field" / "golden rectangle" pages |
| D.improper_integral_parameter | (domain) | free parameters inside an integral with an infinite limit default to positive (positive_integer for integer letters) |
| C.sqrt_arg / C.log_arg | (constraint) | no longer emitted when the formula itself contains `i` (complex principal branches: `arccos x = -i ln(x + √(x²−1))` holds on [−1, 1]) |
| tol:<d> | (hint, stays checkable) | a numeric equation with a decimal literal side (`10.585`, `0.74048`, `0.67`), or a terminating rational next to "approximately/about/rounded/taking": recorded as `tol:<decimal places>` in `assumptions_source` so verify can compare to half a unit in the last place. The rounding error 9.414 (should be 9.415) still fails under that tolerance |
| K.units (extended) | units | plain-text units after a number: `0.75 kg/L`, `3 km`, `5 MeV` |

## Known blind spots (and the safe choice we made)

Precision matters more than coverage: a wrong domain creates false FAILs downstream. When unsure
the rules pick the narrower, safe choice: unknown letters are **positive reals**, integer letters
are **non-negative**, and prose may widen a domain only when it is adjacent, in the same sentence,
and about this formula.

- **Branch cuts are not inferred.** `log(cos θ + i sin θ) = iθ` holds only for -π < θ ≤ π;
  `tan(arcsec x) = sqrt(x^2 - 1)` only for x ≥ 1. These are the two unsafe dev cases. The verifier's
  "known special-case" rule (sqrt/log branches) must cover them.
- **Convergence conditions stated far from the formula** are missed (`Σ z^n H_n = -ln(1-z)/(1-z)`
  needs |z| < 1; the held-out unsafe case). Series identities with no adjacent condition get no
  convergence constraint.
- **Conditions about a neighbouring formula** are sometimes applied (Re(z) > 0 from the integral
  definition applied to `zΓ(z) = Γ(z+1)`; `z ∉ ℤ` from the reflection formula). This only narrows
  (over-restrictive, safe) and accounts for most over-restrictive cases.
- **Narrow defaults cost coverage**: `n` in `(cos θ + i sin θ)^n` is sampled as nonneg, not all
  integers; `p` in `log_b(x^p) = p log_b x` as positive, not real; a log base `k` as a nonneg integer.
- **Chains are all-or-nothing.** `z z̄ = (x+iy)(x-iy) = x² + y²` is skipped although the second
  piece is a valid identity: the schema has one record per formula_id (see PROPOSALS.md).
- **`±` formulas are always skipped**, even when the translator expanded both variants.
- **skip_reason is coarse** (held-out 72.7%): recurrences written with subscripted symbols
  (`F_n = F_{n-1} + F_{n-2}`) are called `definition` or `statement_not_identity` somewhat
  arbitrarily; both are not checkable, which is what matters.
- **Golden ratio / Euler–Mascheroni need the words nearby** (within the ~400-char context or the
  page title). On the Fibonacci page `log_φ x = ln x / ln φ` is left with φ as a variable (safe:
  φ gets a positive domain, but the identity then reads as a generic change of base).
- **Context relations** (`K.context_relation`) look for `=` within 40 chars of the symbols in
  adjacent prose. A derivation in the preceding paragraph can trigger it (a lost formula, never a
  false FAIL).
- **Units** are only detected as number + unit macro; a physics law written with symbols only
  (`F = ma`) is caught by `K.bare_symbol_definition`/`K.unbalanced_sides`, not by units.
- **Prose parsing is regex based**: sentences like "when m (or n, by symmetry) is a positive integer"
  are not understood; the rules fall back to the letter default.
- Numerical cancellation test (`K.cancelling_symbol`) is skipped for expressions containing sums,
  integrals, limits or undefined functions (they are assumed to depend on the symbol).
- `mpmath.binomial(-1, -1) = 1` while sympy and Wikipedia's convention give 0; Pascal's rule at
  n = 0 is fine for sympy but not for an mpmath-only verifier. Semantics does not add `n >= 1`.

## Files

- `rules.py` — `infer(formula, pieces) -> (Semantics, Trace)`: all rules.
- `prose.py` — LaTeX/Unicode normalization, trailing-condition split, prose fact extraction.
- `stage.py` — `run`, `explain`, joining of formulas and parsed pieces.
- `accuracy.py` — fixture scoring (semantic comparison by sampling).
- `context_rules.py` — second-pass context rules (special algebra, stated false, defining equations, ...).
- `review_check.py` — `review-check`: re-run semantics + verify on the human-reviewed FAILs.
- `cli.py` — typer app: `run`, `explain`, `score`, `review-check`.
- `tests/semantics/fixtures/build_cases.py` — dev + held-out fixture source of truth (labels live there).
- `tests/semantics/fixtures/build_review_cases.py` — 148 reviewed real FAILs with labels from the review.
