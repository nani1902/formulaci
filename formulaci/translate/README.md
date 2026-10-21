# translate — Wikipedia LaTeX → SymPy

Reads `Formula` records (`data/raw/formulas.jsonl`), writes `Parsed` records
(`data/parsed/parsed.jsonl`): each relation in a `<math>` formula becomes a pair of sides as
`sympy.srepr` strings, classified as `equation` / `chain` / `inequality` / `definition_like` / `other`.

```bash
uv run formulaci translate run --in data/raw/formulas.jsonl --out data/parsed/parsed.jsonl
#   --limit N      translate at most N new formulas
#   --force        discard the output file and start over (default: resume, skip ids already present)
#   --workers K    worker processes (default 4; 0 = in-process, soft timeout only)
#   --timeout S    hard per-formula timeout, default 20 s (worker is killed and restarted)
#   --lark         enable the sympy-lark fallback (off by default, see "Fallback")
uv run formulaci translate one '\Gamma(z+1) = z\Gamma(z)'    # debug one formula
uv run formulaci translate stats data/parsed/parsed.jsonl    # coverage summary of an output file
uv run pytest tests/translate                                # 79 tests, ~10-40 s
uv run python -m formulaci.translate.check_reviews     # re-check the 110 reviewed false FAILs
```

Python API: `formulaci.translate.run(in_path, out_path, limit=, force=, workers=, timeout=, use_lark=)`
returns the summary dict; `formulaci.translate.core.translate(formula)` returns `list[Parsed]`.
A summary is also written next to the output (`parsed.jsonl.summary.json`).

## Coverage (measured)

"Equation-kind formula" = a formula with at least one record of kind `equation`, `chain` or
`definition_like`. A formula counts as **ok** when at least one of those records has status `ok`.

| Input | formulas | equation-kind | ok | all eq. records ok | records ok / eq. records | time |
|---|---|---|---|---|---|---|
| Fixtures (12 pages, `tests/translate/fixtures`) | 1,174 | 674 | **576 (85.5%)** | 544 (80.7%) | 778 / 970 (80.2%) | 4 s, 1 process |
| Real extract output, full (`data/raw/formulas.jsonl`, 952,136 formulas) | 952,136 | 272,013 | **140,226 (51.6%)** | 129,093 (47.5%) | 173,336 / 352,683 (49.1%) | 247 s, 6 workers |
| Real, the first 180,016 formulas (same ids as the first pass) | 180,016 | 53,712 | **29,073 (54.1%)** (first pass: 30,662, 57.1%) | | | |

**The 60% target is not met on the real data (51.6% on the full corpus).** The gap is almost entirely
notation that is deliberately refused rather than misread. Of the 131,787 equation-kind formulas
without an ok record, 123,249 carry a recognized `has_unsupported` reason; only **8,538 (3.1% of
equation-kind formulas) are genuine parse errors**. Among formulas in supported notation, 94.3%
translate. The full corpus is broad physics/engineering/statistics/abstract algebra: sets, tuples,
matrices, index/label superscripts, ellipses, inner products and vector calculus dominate.

**Second pass (2026-10-21, driven by human review of 266 real FAILs).** Reviewers attributed about 110
false FAILs to the translator (`[translator_misread_other]` 69, `[superscript_is_label]` 32,
`[mixed_number_or_juxtaposition]` 9). All 110 are in `tests/translate/fixtures/review_false_positives.jsonl`
and re-checked by `uv run python -m formulaci.translate.check_reviews`:
**71 are now refused (`not_checkable` with a reason), 38 are now read correctly** (`\bar z` →
`conjugate(z)`, `e^{iax}` a power, `\sin\tfrac12(\theta+\varphi)` → sin((θ+φ)/2), `\theta_4[q]`,
`M_2[f]`, `\text{ri}(x)`, `{\rm sinc}(x)`, `\mathrm{N}(\cdot)` as function applications, …),
**1 is unresolved** (`|cd| = |cs| + |sd|`, segment lengths that cannot be told from `|c·d|`).
The new refusals cost 3.0 points on the same 180k formulas (57.1% → 54.1%). The formerly-ok
formulas lost there were sampled by category: mostly index/label superscripts (650), unit and word
symbols like `\text{kg}` and `\mathrm{constant}` (353), and enumerations `i = 1, 2, \dots, k` that the
first pass wrongly read as `i = 1` (254). The rest are named operators, Legendre symbols, matrix
inverses, bars that could be means or conjugates, and limits of symbols that don't mention the limit
variable. Collateral found while sampling was fixed and pinned by tests: subscripted coefficients
`k_3(c-1)`, `a_n(x-c)^n`, `V_{w2}`, roman subscripts `U_\mathrm{el}(x)`, `n\,2^{n-1}`, `i2\pi`,
`\cos(ax)\,dx`, `\operatorname{sech}(\tau)\,e^{…}`, `\lim_n f_n(x)`, `{\exp}\bigl(…\bigr)`,
`\quad j=1,\ldots,m`.

Top reasons on the full real data (equation-kind records): `set_notation` 13,035, `tuple` 9,784,
`matrix` 9,335, `superscript_label` 9,220, `ellipsis` 8,534, `sum_index_set` 5,913, `inner_product`
5,798, `uppercase_juxtaposition` 4,682, `conjugate_star` 4,580, `differential_form` 4,465,
`vector_calculus` 4,404, `subscript_on_expression` 4,333, `probability` 3,977, `partial_operator`
3,977, `integral_domain` 3,688, parse error "unexpected token" 3,627, `vector_product` 3,336,
`word_symbol` 3,244, `transpose` 2,761.

Status of all 1,070,126 real records: ok 210,782; not_checkable 811,878 (663,041 are kind `other`:
expressions without a relation, `\approx`, `\in`, …); unparsed 47,466. No formula hit the timeout.

**Silent-mis-translation audit.** Every `ok` equation on the fixtures without undefined functions or
integrals was evaluated numerically (3 random points, `e`→E and `i`→I): all 57 that fail are
statements that are not identities (`x^2+y^2 = 1`, `b^2-4ac = 0`, substitutions), none were
translator errors after the fixes listed below. A random sample of 2,500 real `ok` records (677
evaluable non-trivial ones) was reviewed the same way; the failures are overwhelmingly physics
relations that are not identities (`F s = m a s`, `\Delta S = nR\ln(V/V_0)`), and every translator
error found there was turned into a guard and a test (see the table below). Remaining known
non-guarded cases are listed under "Known remaining risks".

## How it works

1. **Preprocessing** (`preprocess.py`, token level, every step leaves a `pre:*` note):
   unicode math → LaTeX; `{a \over b}`, `{n \choose k}` → `\frac`, `\binom`; drop `\displaystyle`,
   `\textstyle`, `\big…`, `\limits`, `\tag`, `\label`, `\color`, `\phantom`, `\!`; `\left( … \right)`
   → brackets, `\left| … \right|` → abs, `\left.` dropped; `\stackrel{\text{def}}{=}`,
   `\overset{def}{=}`, `\coloneqq`, `\triangleq` → `:=`; `\Phi{\left(x\right)}` → `\Phi(x)`.
   Environments `align(*)`, `aligned`, `alignat`, `gather`, `split`, `multline`, `eqnarray` are split
   into rows; a row starting with a relation continues the previous chain (`&= …`), a row starting or
   ending with `+ - \cdot` continues the expression, a `\\` inside brackets is a line break; later `&`
   columns become separators (`… && x \neq 0` is a condition column, `… &\quad& y=2` a second equation).
   `cases` → `Piecewise` (conditions such as `x \ge 0`, `(n>-1,\ a>0)`, `\text{otherwise}`, `n \text{ odd}`).
   Matrices/arrays are unsupported.
2. **Conditions**: after the first top-level relation, the first `\quad`/`\qquad`, top-level `,`/`;`,
   `\text{for …}` / `\text{if …}` / `\mbox{(for …)}` / `\forall`, or `\; (…)` starts a tail. A tail
   whose only relations are `=` is another equation (`\sin(-x) = -\sin x, \quad \cos(-x) = \cos x` →
   2 records); otherwise it is a condition, recorded as `cond: <latex>` in `notes` and removed.
   Trailing `. , ; :` are dropped.
3. **Parsing** (`parser.py`): a recursive-descent parser written for this dialect (precedence:
   relation < `+ -` < product/implicit product < unary minus < power/postfix). Supports numbers
   (`1{,}000`, decimals as exact rationals), single-letter and greek symbols with subscripts
   (`x_1` → `x_1`, `\alpha_n` → `alpha_n`, `v_{\max}` → `v_max`), accents (`\hat x` → `x_hat`,
   `\bar`, `\tilde`, `\dot`…), `\vec`/`\mathbf`/`\boldsymbol` (→ `vec_v`/`bf_A`, flagged), `\frac`
   family, `\sqrt`, `\sqrt[n]`, `\binom`, `!`, `!!`, `|x|`, `\lfloor\rfloor`, `\lceil\rceil`,
   trig/hyperbolic/inverse functions (commands and `\operatorname{arsinh}` / `\mathrm{erf}` /
   `\text{sgn}` spellings), `\sin^2 x`, `\sin^{-1} x` (→ asin, flagged), `\log_b`, `\ln`, `\exp`,
   `\Gamma`, `\Gamma(s,x)`, `\gamma(s,x)`, `\zeta`, `\Beta`/`\mathrm{B}`, `\operatorname{Li}_s`, `\erf`,
   `\Ei`, `\Si`, `\Ci`, `\Re`, `\Im`, `\arg`, `\max`, `\min`, `\gcd`; `\sum`/`\prod` with
   `k=a`, `n,m=0`, `0\le k\le n`, `k\ge 1` limits; `\int_a^b … dx` (`dx`, `d\theta`, `\mathrm{d}x`,
   `\text{dx}`, `\frac{dx}{x}`, `\int{…\,dx}`, `\int_{u=0}^\infty`, iterated integrals); `\lim_{x\to a}`
   (incl. `0^+`); Leibniz `\frac{d}{dx}`, `\frac{d^2y}{dx^2}`, `\frac{\partial^2 u}{\partial x\partial y}`;
   primes `f'(x)`, `\Gamma'(z)`, `\theta^{\prime}`; `30^\circ`; coupled `\pm`/`\mp` (both sides) are
   split into the `+` and `-` identity.
4. **Classification** (`core.py`): each top-level relation splits the row; consecutive pairs become
   records (`chain` if more than one pair). In an `=` chain, a side that cannot be translated is
   bridged (`a = \cdots = c` also yields `a = c`, note `bridge:0-2`). `<, \le, >, \ge, \ne` →
   `inequality` with `relation`; `\approx`, `\sim`, `\to`, `\in`, `\propto`, … → `other`,
   `not_checkable`. `definition_like` when the LHS is a bare symbol / `f(x)` / indexed symbol and the
   relation is `:=`/`=:`/`\equiv`/def-equals, or the prose just before says "defined/denote/let/we
   write…" (note `definition_from_prose`).
5. **Output**: `srepr` of each side, re-read with `sympy.sympify` and compared (a mismatch → `unparsed`);
   `free_symbols`, undefined `functions`, `has_unsupported`, `translator`
   (`formulaci-rd-0.1/sympy-1.14.0`, or `sympy-lark-1.14.0` when the fallback produced a side), `notes`.
6. **Never hangs**: each formula runs in a worker process with a SIGALRM soft timeout (75 % of
   `--timeout`) and a hard timeout after which the worker is killed and restarted; every exception
   becomes an `unparsed` record. Integer powers with exponent > 2000 and factorials > 2000 of literal
   numbers are refused (`huge_number`) because SymPy would evaluate them in C where no signal can
   interrupt.
7. **Fallback (off by default, `--lark`)**: if the custom parser raises a parse error (not an
   "unsupported" verdict), sympy's `parse_latex(backend="lark")` is tried; ambiguous results
   (`Tree('_ambig', …)`) are rejected. On the 180k real formulas it produced 13 `ok` records: 12
   bra-ket operator expressions and one silent mis-translation (`3.\overline{142\,857}` → `365082.0`).
   That is worse than nothing, so it is disabled unless asked for.

`e` and `i` stay `Symbol('e')` / `Symbol('i')` (the semantics stage decides), with hints in notes.

## Why not just `parse_latex(backend="lark")`?

On SymPy 1.14 the lark grammar returns an *ambiguous tree* for `\sin^2 x + \cos^2 x` (one reading is
`sin(x + cos(x)^2)^2`), for `f(x)` (`f(x)` vs `f*x`), `\zeta(s)`, `\sinh x` (`sin(h*x)`); it cannot
parse `\pi`, `\Gamma(z)`, `\operatorname{…}`, `\mathrm{d}x`; and its symbols carry lark `Token` objects
as names, so `srepr` does not round-trip. Building on it would have meant fighting the grammar for
every rule above, with silent mis-parses hidden inside the ambiguity resolution.

## Not supported (→ `not_checkable`, with the reason in `has_unsupported`)

ellipses (`\cdots`, `\ldots`, `\dots`, continued fractions with `\ddots`); contour/surface/multiple
integral signs (`\oint`, `\iint`), integrals over a named domain (`\int_C`, `\int_{\mathbb R}`);
sums over index sets (`\sum_{d|n}`, `\sum_{p \text{ prime}}`) or without bounds; vectors, matrices,
`\nabla`, norms `\|x\|`, inner products, transposes, vector products (`vector_product` whenever two
vector/bold factors are multiplied); expectation/probability (`\mathbb E`, `\operatorname{Var}`, `\Pr`);
set notation and `\in` inside expressions; lone `\pm` (sign that depends on the quadrant);
`f^{-1}(x)`, `f^{(n)}(x)`, `f'(0)` (prime at a point); `(x)_n` (Pochhammer — rising or falling depends
on the field); `n^{\underline k}`; `\overline{a+b}`; `z^*`; hypergeometric `{}_pF_q`;
`\Beta(x;a,b)` (semicolon arguments); `\pmod`; `*` (convolution); `\circ`; juxtaposed capital letters
(`AB`, `OA + OB`: matrices or geometric segments); differential forms (`dx = \frac{2}{t^2-1}dt`);
lists (`z_1, z_2`); integrals without a differential (`\int_a^b f`, `\int d^4x\,…`);
`P(A|B)`; `\{0,1\}`; `W^\perp`; quantifiers; `\angle`.

## Known ambiguities and how they are guarded

The dangerous failure is a *silent wrong translation*: a formula that parses into something else and
then FAILs in `verify`. Policy: when two readings exist, prefer the one downstream will **skip**
(an undefined function, an unsupported marker) over one that could produce a false FAIL, and record
the decision in `notes`.

| Notation | Risk | What translate does |
|---|---|---|
| `f(x)` vs `a(b+c)` | function call vs product | Call if the argument is structurally a call (comma `B(x,y)`, single atom `y(t)`, primed `f'(x)`), or the name is conventionally a function (f g h F G H φ ψ χ, any greek letter, a capital) **and** never used bare in the same formula; otherwise product. `(e+f\,x)^p … f(m+1)` → product (`mult_not_call:f`). Notes `funcapp_rule:NAME:REASON`. |
| `\pi(x)` | prime-counting vs `π·x` | single-letter argument → undefined `pi(x)` (`ambig:pi_as_function`); `2\pi(r+h)` stays a product. |
| `\theta(it)`, `\delta(\xi - n/P)` | Jacobi theta / Dirac delta vs product | greek letter followed by `(` → function unless the letter is also used bare. |
| `x_n = x_{n-1} - 1`, `B_{2n}`, `\sum a_n x^n` | recurrences / sequences as unrelated constants | subscripts mentioning a bound index, a letter used elsewhere, or arithmetic (`n-1`, `2n`) → `x(n)`; `a_{ij}` → `a(i, j)`. Word subscripts (`v_{\max}`) stay names. |
| `dx` in integrals | `d·x` | `d<var>` ends the integrand only at the integrand's own nesting level (plus `\frac{dx}{…}` numerators and an integrand wrapped in braces); inside brackets `(a\,d\,f+b)` it is a product. An integral with no differential is an error, not a guess. |
| `\frac{dy}{dx}` | derivative of a constant symbol = 0 | Leibniz numerators that are bare symbols become functions of the variables: `Derivative(y(x), x)`. |
| `\frac{d}{dx}[...](...)` | operator scope | applies to the bracket right after it; otherwise to the following term. |
| `\log x` | base e / 10 / 2 | natural log, note `log:unspecified_base`. |
| `\sin^{-1} x` | arcsin vs `1/sin x` | arcsin, note `ambig:sin^-1_as_inverse`. |
| `\sin 2x \cos y`, `\sin x^2` | argument scope | argument = first factor plus following plain letters/greek symbols; stops at `\cdot`, operators, brackets, other functions and `d<var>` inside integrals. |
| `e`, `i` | constant vs variable | left as symbols, with `hint:e_only_as_exp_base` / `hint:e_not_only_exp_base` / `hint:i_squared`. |
| `\dot x` | time derivative | symbol `x_dot`, note `ambig:time_derivative:x_dot` (bars: see the second-pass rows below). |
| `\vec a \times \vec b`, `\mathbf{AB}` | non-commutative products as scalars | `vector_product` unsupported. |
| `AB = BA`, `OA + OB = OC` | matrices / segments | `uppercase_juxtaposition` unsupported. |
| `\sin(a\pm b) = … \pm …` vs `= \pm\sqrt{…}` | dual identity vs quadrant sign | split only when `\pm` is on ≥ 2 sides or `\mp` is present. |
| `&&` columns in `align` | condition glued into the expression (`csch(x·x)`) | later `&` columns are separators. |
| `cases` conditions with commas | `n>-1, a>0` merged into `n > -a` | conditions split on top-level commas / `\text{and}` before parsing. |
| `dx = \frac{2}{1+t^2}dt`, `ds^2 = E\,dx^2+…`, `\mathrm{d}U = T\,\mathrm{d}S` | `d·x` product | `differential_form` unsupported (≥ 2 `d<letter>` starting a term, or any `d\theta`, outside integrals). |
| `\alpha^2 m c / 2 h`, `/k_{\rm B}T` | `(x/2)·h` vs `x/(2h)` | `ambiguous_division`: implicit product right after a `/` divisor (`a/b \cdot c` is fine). |
| `A^T`, `A^\mathsf{T}` | transpose read as power | `transpose` unsupported (except on numbers and `e`). |
| `\gamma^\mu`, `B^{i\alpha}_{j\beta}`, `\eta^{\mu\nu}` | tensor indices read as powers | `tensor_index` unsupported (superscript of index letters only, with a greek index). |
| `X^{\mathrm{qc}}`, `z^{ideal}` | label read as power | symbol `X^qc` (note `superscript_label`). |
| `[\mathcal{L}_T f](y)`, `(f*g)(t)` | operator applied to an argument | `operator_application` unsupported; `\mathcal{F} f` → `operator`. |
| `\mathcal{L}_T f … f(\frac{y}{2})` | `f` both bare and applied | `ambiguous_application` unsupported, unless the formula has a coefficient run `a…e` (integral tables), where it is a product. |
| `e_2 e_3 e_1` | Clifford basis (non-commutative) | `basis_product` unsupported. |
| `x[n]`, `u[1]` | indexing read as product | undefined function `x(n)` when some `x[atom]` appears (note `bracket_index`). |
| `\arccos(z) & z & & \sqrt{1-z^2}` | table cells glued into one product | `table_row` unsupported. |
| `A = B \\ -C = D` in `align` | new row merged into previous equation | a row starting with `-` continues the previous one only if it has no relation of its own. |
| lark fallback | `3.\overline{142857}` → `365082.0` | fallback off by default. |
| `\operatorname{vers}\theta`, `\operatorname{cis}x`, `{\rm sinc}x` | unknown named operator read as `vers·θ`, or `{\rm sinc}` as c·i·n·s | `named_operator`; with `(…)` an undefined function `sinc(x)`; `{\rm …}` font switches are rewritten to `\mathrm{…}`. |
| `\text{median}`, `\mathrm{Re}`, `\text{kg}` alone | words as free variables | `word_symbol`. |
| `\bar z`, `\overline{z}` next to a plain `z` | conjugate read as an independent variable | `conjugate(z)` when the letter is z/w/ζ or the prose mentions complex numbers/conjugates; otherwise `ambiguous_bar`. A bar alone (`\bar x = …`) stays `x_bar`. |
| `\left(\frac{a}{p}\right)`, `\Bigg[\frac{\alpha}{\pi}\Bigg]` | Legendre/Jacobi/residue symbols read as fractions | `residue_symbol` (square brackets always; parentheses when the prose mentions Legendre/Jacobi/residues/reciprocity). |
| `\left(\!\binom{n}{k}\!\right)` | multiset coefficient read as a binomial | `multiset_coefficient`. |
| `X^{(0)}`, `f^{(n)}`, `F^H`, `M^X`, `A^\mathrm{g}`, `G^\circ`, `E^\infty`, `a^\omega`, `h^i_k`, `C_3^0`, `Y_l^m(\theta,\varphi)` | labels/indices/derivative orders read as powers | `superscript_label`; `U^{-1}`, `H^{-1}` on a capital → `inverse_or_reciprocal`. `x^n`, `x^0`, `2^n`, `30^\circ`, `\hat x^n`, `L^i` stay powers. |
| `3\frac12`, `314\frac{64}{625}` | mixed number read as a product | `mixed_number`. |
| `\mathrm{p}K`, `h2`, Church numerals `f\ x\ y` | operator/label juxtaposition | `p_function`, `letter_digit` (letter glued to a digit, except `i2\pi`), `juxtaposition_application` (≥ 3 control-spaced letters). |
| `e_s(T)`, `\theta_4[q]`, `\tau[A]`, `M_2[f]` | function application read as a product | subscripted `e`/`i` may be functions; a subscripted or greek name before `[` is applied. |
| `p(2n+1) = \sum p(n-k)q(2k+1)`, `E = E(R/\mathfrak p)` | partition functions / injective hull read as products | `ambiguous_application`: a letter applied twice with compound arguments and never used plainly, or a name that is both a whole side and applied. One `s(1-t)` is still a product. |
| `\gcd(a,b,c)` | SymPy's polynomial gcd of symbols = 1 | undefined function `gcd` unless all arguments are integers. |
| `\gamma(a,q)` | Euler–Lehmer constants read as the lower incomplete gamma | lowergamma only when the prose says "incomplete gamma"; else undefined. |
| `\lim_{\beta\to0}\mu` | limit of a symbol that depends on β only through prose | `limit_of_unrelated_symbol` (a name like `f_n` with the variable in its subscript counts as dependent). |
| `\cos(2k-1)\alpha`, `\sin(k+1)x` | argument scope after a bracket | `ambiguous_function_argument` when a bare letter follows the bracket (not `e`, not a differential). `\sin\tfrac12(\theta+\varphi)` takes the bracket into the argument. |
| `\frac{dc}{c}`, `\frac{dM^2}{M^2}`, `d\theta` | differentials read as `d·c` | counted toward `differential_form`. |
| `\Delta f`, `\Delta\epsilon`, `\delta y` | `\Delta f / f` cancelled to `\Delta` | one symbol `Delta_f`; `\frac{\delta u}{\delta\theta}` → `variational_derivative`. |
| `i = 1, 2, \dots, k` | read as the equation `i = 1` | `list`; after an equation (`…, \quad j = 1,\ldots,m`) it is a condition. |
| `(16)\quad B_{21} = …` | equation number read as a factor 16 | stripped (note `pre:equation_number`). |

Known remaining risks (not guarded): segment lengths `|cd| = |cs| + |sd|` read as `|c·d|`;
a lowercase letter applied once to a compound argument is a product (`a(n+1)` in a geometric series
is fine, a function `q(uv)` written once is not); `x_0^{n-1}`, `\mu_1^b`, `z_m^k` (letter
superscript on a subscripted symbol) are refused as labels even when they are powers; `\sin \frac{\pi}{2} x` is read as `sin(πx/2)`;
`\sin x y` as `sin(xy)`; single-letter function names applied to a single atom are always calls
(`x(t)`), so a product written `a(b)` becomes `a(b)`; `\Gamma`, `\zeta`, `\Beta` followed by `(` are
always the special functions; `\psi(z)` is left undefined (digamma is not assumed);
`\operatorname{sinc}` is undefined (normalized vs unnormalized). Non-commutative algebra written with
plain letters (`(gN)^{-1} = g^{-1}N`, `yx = (-1)^{|x||y|}xy`, group actions `h\cdot(g\cdot x)`) and
`\gamma^5` (a matrix, read as a power) cannot be told apart from scalar algebra and are translated as
commutative scalars; `\delta y` (a variation) is `delta*y`; `x^{\alpha\beta}` is refused as tensor
indices even when it is a power.

## Notes vocabulary (`Parsed.notes`, newline-separated)

`pre:*` (preprocessing applied), `cond: <latex>`, `sides: <lhs latex>  ||  <rhs latex>`,
`funcapp_rule:N:reason`, `funcapp:N`, `mult_not_call:N`, `named_function:N`, `indexed:B`,
`subscript_expr:N`, `leibniz_function:N`, `log:unspecified_base`, `log_base_given`, `ambig:*`,
`hint:e_only_as_exp_base`, `hint:e_not_only_exp_base`, `hint:i_squared`, `hint:i_present`,
`e:roman`, `i:roman`, `vector_symbol:N`, `definition_from_prose`, `equiv_as_identity`,
`swapped_eqcolon`, `bridge:a-b`, `pm_variant:+|-`, `relation:R`, `implicit_function_arg`,
`derivative_operator`, `indefinite_integral`, `piecewise`, `nth_root`, `degrees`, `percent`,
`text_symbol:W`, `roman_word:W`, `primed_symbol:N`, `power_of_function:N`, `bare_function_name:W`,
`fallback:lark`, `op:times`, `index_range_from_inequality`, `brace_annotation`, `superscript_label:N`,
`bracket_index:N`, `ambiguous_application:N`, `styled_symbol:N` (`\mathcal{L}` → `cal_L`),
`conjugate:z`, `increment:DeltaX`, `numeric_coefficient_function_arg`, `ambiguous_application:N`,
`pre:font_switch`, `pre:single_command_group`, `pre:equation_number`, `pre:script_relation_symbol`.

## Fixtures

`tests/translate/fixtures/formulas.jsonl`: 1,174 real formulas (first 120 `<math>` tags of each of 12
pages: List of trigonometric identities, Gamma function, Normal distribution, Binomial coefficient,
Fourier transform, Hyperbolic functions, Beta function, Lists of integrals of rational / exponential /
logarithmic functions, Exponential function, Riemann zeta function), fetched by
`tests/translate/build_fixtures.py` (MediaWiki API, cached under `data/raw/cache/translate-fixtures/`).
Context strings there are crude; the extract stage's are better.
