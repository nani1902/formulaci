# Proposals (schema changes, new dependencies) — append under your stage heading

## extract

1. **User-Agent contact (blocking throughput).** Wikimedia's 2026 API rate limits
   (https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits) classify a User-Agent without contact
   info as *Unidentified*: 10 requests/minute. A compliant UA (email or URL) gets 200/minute. SPEC's
   UA `formulaci/0.1 (knowledge verification research)` has no contact, so a full run (~2,400
   requests) takes ~4 h instead of ~12 min. The extract client reads `FORMULACI_CONTACT` and appends it
   to the UA (`formulaci/0.1 (knowledge verification research; <contact>)`), raising its rate to
   3 req/s. Proposal: amend SPEC's network rule to "descriptive User-Agent **with contact info**".
2. **Optional `Formula` fields** (currently encoded in `context_before`; no schema change is required):
   - `container: str = ""`: where a formula sits when it is not in running prose, e.g.
     `"Infobox probability distribution | pdf"`, `"ref"`, `"caption"`. Today this is appended to
     `context_before` as ` [container]`.
   - `markup: Literal["math", "tmath"] = "math"`: `{{tmath|...}}` templates are extracted as formulas too
     (LaTeX rendered through `<math>`); today only distinguishable by re-reading the wikitext.

## clinical
- No new dependencies. Uses `mpmath`, `pyyaml`, `pydantic`, `typer` (already declared) and `playwright` from the `web` extra. The end-to-end test in `tests/clinical/test_audit_e2e.py` needs `uv sync --all-extras && uv run playwright install chromium`; consider installing the extra in CI.
- Schema (optional): `formulaci/clinical/audit.py` defines a local `AuditRecord` (`target, formula, inputs, site_output, reference_output, status: match|mismatch|unreadable, notes` + `url, claimed_version, site_text, tolerance, diagnosis`). If the report stage wants to render clinical results, move it into `formulaci/schemas.py`.
- Packaging: `formulaci/clinical/vectors.json`, `targets.yaml`, `mock/targets.yaml` and `mock/pages/*` are data files read at runtime; hatch includes them in the wheel by default as they live under `formulaci/`, but please keep them if a wheel `include` list is ever added.

## bench
- No new dependencies (sympy, mpmath, pydantic, typer only).
- No schema change required. Bench records are `Formula` JSON plus an extra top-level key `bench`
  (set, label, category, mutation, source_id, oracle variables); `Formula.model_validate` ignores it.
  Labels are mirrored in `page_categories` (`bench-category:*`, `bench-label:*`, `bench-mutation:*`).
  Optional proposal: `Formula.labels: dict[str, str] = {}` would make this explicit and survive
  re-serialisation by stages that rebuild `Formula` objects.
- `.gitignore` excludes `data/**/*.jsonl`, so the built sets are also snapshotted (committable) in
  `formulaci/bench/sets/`; `formulaci/bench/lacast/` holds the vendored LaCASt gold data (MIT, LICENSE copied).

## translate
- No new dependencies (sympy's lark backend is used only as a fallback; `lark` is already declared).
- **Join key (important for semantics/verify/report).** One formula can yield several `Parsed` records:
  chains `a = b = c` (pairwise, consecutive), `align` rows, `a=b, \quad c=d`, coupled `\pm` variants,
  and "bridge" records that skip an untranslatable middle side. They share `formula_id` and are told
  apart by `index_in_chain` (0..n-1 over all records of the formula; `None` when there is only one).
  `Semantics` and `Verdict` currently have only `formula_id`, so per-record verdicts collide.
  Proposal: add `index_in_chain: Optional[int] = None` to `Semantics` and `Verdict` (and `Finding`), and
  join on `(formula_id, index_in_chain)`. Until then: downstream stages should copy `index_in_chain`
  into their own notes / treat the pair as the key.
- Optional `Parsed.conditions: list[str] = []` for trailing conditions (`\quad x>0`,
  `\text{for } n\ge1`). Today they are lines `cond: <latex>` in `notes`.
- Optional `Parsed.hints: list[str] = []` for machine-readable translator flags (today `notes` lines:
  `hint:e_only_as_exp_base`, `hint:i_squared`, `log:unspecified_base`, `ambig:*`, `indexed:*`,
  `leibniz_function:*`, `funcapp_rule:*`). The full list is in `formulaci/translate/README.md`.

## semantics
- No new dependencies (sympy, pydantic, typer only).
- **Function aliases in `Semantics.constants` (no schema change needed, but please document).** Besides
  `symbol -> constant` (`e -> E`), semantics maps undefined *functions* to sympy functions there
  (`B -> beta`, `F -> fibonacci`, `H -> harmonic`, `psi -> digamma`, `Gamma -> gamma`). Verify applies
  them with `expr.replace(Function(name), getattr(sympy, value))`. Optional cleaner schema:
  `Semantics.function_aliases: dict[str, str] = {}`.
- **Per-piece checkability for chains (schema).** One `Semantics` per `formula_id` forces
  all-or-nothing: `z z̄ = (x+iy)(x-iy) = x^2+y^2` is skipped because piece 0 is a relation, though
  piece 1 is a valid identity. Proposal: `Semantics.skip_pieces: list[int] = []` (indices of
  `index_in_chain` pieces to skip) so `checkable` can be True for the rest.
- **skip_reason vocabulary** used (SPEC lists examples only): `special_algebra`, `stated_false`,
  `defining_equation`, `condition`, `named_constant`, `approximation`, `notation_or_convention`,
  `differential_equation`, `definition`, `has_undefined_function`,
  `functional_identity`, `operator_notation`, `congruence`, `matrix_or_vector`, `set_notation`,
  `statement_not_identity`, `plus_minus`, `indefinite_integral`, `units`, `no_relation`, `unparsed`,
  `translator_not_checkable`, `semantics_error`, `semantics_timeout`. Worth fixing in SPEC so report
  can group them.
- **Constraint special forms** verify must evaluate: `Not(And(Eq(a, floor(re(a))), re(a) <= 0))`
  (Gamma pole) and `Q.prime(p)` (use `sympy.ask` after substitution). Domain strictness is not
  representable in `Domain`, so prose bounds are always repeated in `constraints`.

## verify
- **Dependency: `gmpy2>=2.1`** (strongly recommended). Without it mpmath falls back to its pure-Python
  backend, about 2x slower at 50 digits. Integral and infinite-series formulas then often hit the 20 s
  cap and come back INCONCLUSIVE. It never changes a verdict's direction. Installed locally with `uv pip install gmpy2`.
- **`Verdict.index_in_chain` (agrees with translate's proposal).** Today verify emits **one** Verdict per
  `formula_id`: chain/align links are verified separately and combined (any FAIL → FAIL with
  "Chain link k: …", all PASS → PASS, otherwise INCONCLUSIVE). With `index_in_chain` on `Semantics` and
  `Verdict`, verify would emit one Verdict per link instead; the combining code is `policy.combine_chain`.
- **Optional `Verdict.details: dict = {}`** for audit data the report stage may want: symbolic steps tried,
  evaluated lhs/rhs (as sympy strings), notes such as "summation bound n assumed nonneg_integer" or
  "indefinite integral compared by differentiating". Currently these are only printed by `verify one`.
- **SPEC FAIL policy, two documented extensions** (please ratify or reject):
  1. *Constant identities* (no free symbols, e.g. `\sum 1/k^2 = \pi^2/6`) have one point, so "every
     regime with ≥5 points" can never hold. Verify reports a single regime `constant` and FAILs when the
     mismatch is stable at 50 and 65+ digits and symbolic is not `equal`.
  2. *At least 2 qualifying regimes* (3 if the numeric phase hit its deadline) are required for FAIL, so
     a formula judged on one surviving regime is INCONCLUSIVE.
- **`Tolerance.abs` is reported as `0.0`.** There is no fixed absolute floor. A fixed 1e-20 floor
  passes genuinely different tiny values, e.g. `B(x,y)` vs `Γ(x)Γ(y)/Γ(x+y+1)` at x≈400, both ≈1e-300.
  Near-zero rounding noise is recognised instead by a difference that shrinks as the precision grows.
- **For semantics:** verify accepts relation strings `= == < <= > >= ≤ ≥ \le \leq \ge \geq \lt \gt`.
  `!=`, `\approx`, `\sim` and `\propto` give SKIP. Constants accepted: `pi E e I i j EulerGamma gamma
  GoldenRatio phi Catalan oo inf`. Constraints are parsed with a whitelisted grammar: comparisons
  including chained `0 < x < 1`, `and`/`or`/`not`, `Ne Eq Lt Le Gt Ge And Or Not Abs re im sqrt exp log
  sin cos tan Mod floor ceiling gamma factorial`, `^` = power. Unparseable constraints are ignored and
  listed by `verify one`. A formula with no Semantics record is SKIPped.
- **Tolerance hint for verify (second pass).** Numeric equations with a decimal literal side get
  `tol:<decimal places>` in `assumptions_source`. Proposal: verify compares to half a unit in that place
  (0.5·10^-d) instead of exact equality. Optional schema: `Semantics.tolerance_decimals: int | None`.
- **For semantics: tolerance hints (verify reads these from `assumptions_source`).**
  - `tol:rel=1e-3` and `tol:abs=0.005` widen the numeric comparison and are reported in `Verdict.tolerance`.
  - `tol:digits=3` means half a unit in the 3rd decimal.
  - `tol:approx` means the context says ≈, "approximately" or "about", so the formula is never FAILed.

  Without hints, verify already accepts a decimal-literal side of a constant formula when it is
  correctly rounded (`π/(3√2) = 0.74048`), or truncated when the digits end in `\ldots`. It treats
  `<irrational constant> = <fraction>` (`π = 355/113`) as an approximation.
- **For translate:** verify relies on the `sides: L || R` note line for decimal literals and LaTeX label
  checks, and on `superscript_label:<name>` lines. Please keep both formats stable. The optional
  `Parsed.hints` list proposed under translate would serve the same purpose.
