# Using formulaci as a library

`formulaci.api` checks a LaTeX formula end to end: translate it to SymPy, infer domains and constants from the
formula and its context, then verify it symbolically and numerically. It returns a verdict with a reason, the
reading it checked, the assumptions it made and, for a FAIL, a reproducible counterexample.

## Install

```bash
pip install git+https://github.com/nani1902/formulaci
```

Once the package is on PyPI: `pip install formulaci` or `uv add formulaci`. Requires Python 3.12+.
SymPy, mpmath and gmpy2 come in as dependencies.

## `check(latex, context="", title="", *, timeout=20.0, workers=0) -> CheckResult`

```python
from formulaci.api import check

r = check(r"\sin^2 x + \cos^2 x = 2")
r.verdict          # 'FAIL'
r.counterexample   # {'assignments': {'x': '0'}, 'lhs': '1.000…', 'rhs': '2.000…', 'abs_diff': '1.000…', 'rel_diff': '0.5000…'}
print(r.explain())
```

```text
FAIL: \sin^2 x + \cos^2 x = 2
  The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0: lhs=1.000000000000, rhs=2.000000000000).
  read as: sin(x)**2 + cos(x)**2 = 2
  domains: x real
  counterexample: x = 0: lhs = 1, rhs = 2, relative difference 0.5
  sampled: small_positive 0/12 ok, unit_interval 0/12 ok, integers_small 0/12 ok, mixed_sign 0/12 ok, large 0/12 ok
  (0.18s)
```

- `context` is the prose around the formula. It is where assumptions come from: "for positive integers n",
  "for |x| < 1", "where e is Euler's number". A qualifier starting with *for/where/when/if/with/valid/provided* is
  read as text after the formula, other text as text before it. If the context contains the formula itself, as
  the sentences from `extract_formulas` do, it is split around it.
- `title` is a page or topic name. Some rules use it, for example to detect modular arithmetic or matrix contexts.
- `timeout` caps the whole check in seconds. Verification runs in a separate worker process that is killed when the
  cap is reached. The process is started on the first call, which adds a few seconds, and is then reused for
  the life of your process. A worker that dies is restarted on the next call.
- `workers` is accepted for symmetry with `check_many`. A single check always uses one worker.
- `check` never raises. Unparsable LaTeX gives `SKIP` with `skip_reason="unparsed"` and the parser's error in
  `reason`. An internal error gives `INCONCLUSIVE` with the exception summarised in `reason`.

More examples, with the outputs from the test suite:

```python
>>> check(r"\sin^2 x + \cos^2 x = 1").verdict
'PASS'      # "The identity was proved symbolically and holds at all 60 evaluable sample points."
>>> check(r"\Gamma(n+1) = n!", "for positive integers n").verdict
'PASS'      # domains: n positive_integer
>>> check(r"e^{i\pi} + 1 = 0").verdict
'PASS'      # constants: e = E, i = I
>>> r = check(r"\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2}", "for |x|<1")
>>> r.verdict, r.counterexample["assignments"], r.counterexample["rhs"][:6]
('FAIL', {'x': '0'}, '2.0000')   # a real Wikipedia error: the series sums to 2/(1-x)^3
>>> r = check("not latex at all \\foo{")
>>> r.verdict, r.skip_reason, r.reason
('SKIP', 'unparsed', 'Could not parse the LaTeX (ParseError: unknown command \\foo).')
>>> r = check("x = 5")
>>> r.verdict, r.skip_reason
('SKIP', 'definition')   # "It defines a symbol rather than stating an identity, so there is nothing to check."
```

### `CheckResult`

A pydantic model. `r.model_dump()` / `r.model_dump_json()` give plain JSON.

| field | meaning |
|---|---|
| `latex` | the input formula |
| `verdict` | `PASS`, `FAIL`, `INCONCLUSIVE` or `SKIP` (see below) |
| `reason` | one readable sentence explaining the verdict |
| `skip_reason` | for `SKIP`: a short code such as `unparsed`, `definition`, `statement_not_identity`, `operator_notation` |
| `symbolic` | `equal`, `not_equal` or `unknown`: the outcome of the symbolic check |
| `counterexample` | for `FAIL`: `assignments` (symbol → value), `lhs`, `rhs`, `abs_diff`, `rel_diff`, all as strings at 40 digits |
| `translation` | one entry per relation in the formula (a chain `a = b = c` has two): `lhs`, `rhs` as SymPy `str`, `relation`, `index_in_chain`, `status`, `kind`, `free_symbols`, `unsupported`, `error`, `notes` |
| `assumptions` | `domains` (symbol → `real`, `positive`, `integer`, `positive_integer`, `complex`, …), `constants` (symbol → SymPy constant such as `E`, `I`, `pi`), `constraints` (SymPy strings such as `Abs(x) < 1`), `assumptions_source` (ids of the rules that fired) |
| `regimes` | per sampling regime: `name`, `n_points`, `n_fail`, `n_error` |
| `elapsed_s` | wall-clock seconds for this check |
| `formula_id` | `api:<sha1 of latex and context>` |
| `context` | the context that was passed in |

`r.explain()` returns the short multi-line summary shown above.

## `check_many(items, *, timeout=20.0, workers=4) -> list[CheckResult]`

Checks many formulas in parallel worker processes. Results come back in input order. Items are
`(latex, context)` tuples or dicts with `latex` and optional `context` and `title`. `timeout` applies to each
formula. A malformed item gets a `SKIP` or `INCONCLUSIVE` result in its slot instead of an exception.

```python
from formulaci.api import check_many

rs = check_many([(r"\sin^2 x + \cos^2 x = 2", ""), ("a+b=b+a", ""),
                 {"latex": r"\Gamma(n+1) = n!", "context": "for positive integers n"}])
[r.verdict for r in rs]   # ['FAIL', 'PASS', 'PASS']
```

## `extract_formulas(text) -> list[tuple[str, str]]`

Pulls formulas out of free text: `$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `<math>...</math>` and
`\begin{equation}` blocks (also `align`, `gather`, `multline`, `eqnarray`, starred or not). Each formula comes
with the sentence around it, math delimiters removed, ready to pass to `check` as context. A `$5` price is not
treated as math.

```python
from formulaci.api import check_many, extract_formulas

md = ("Recall the Pythagorean identity $\\sin^2 x + \\cos^2 x = 1$, valid for every real angle. "
      "Euler's identity $e^{i\\pi} + 1 = 0$ links five constants.")
found = extract_formulas(md)
# [('\\sin^2 x + \\cos^2 x = 1',
#   'Recall the Pythagorean identity \\sin^2 x + \\cos^2 x = 1, valid for every real angle.'),
#  ('e^{i\\pi} + 1 = 0', "Euler's identity e^{i\\pi} + 1 = 0 links five constants.")]
[r.verdict for r in check_many(found)]   # ['PASS', 'PASS']
```

## Verdicts

- **PASS**: proved symbolically, or the two sides agree to a relative error of 1e-8 at 50-digit precision at every
  sampled point in every regime.
- **FAIL**: the formula is wrong under the stated assumptions. Each FAIL comes with a counterexample you can
  reproduce by hand.
- **INCONCLUSIVE**: checked but no decision. Too few points could be evaluated, the time cap was hit, failures
  are confined to a branch cut, or the formula looks like an equation to solve, a label or an approximation.
- **SKIP**: not checked. The LaTeX did not parse, the notation is not supported, or the formula is a definition,
  a physical law, a condition or an approximation rather than an identity. `skip_reason` says which.

## FAIL policy

A formula is FAILed only if the symbolic check did not prove it, and it fails at a clear majority of evaluable
points in every sampling regime with at least five such points (at least two regimes, at 50 digits, relative error
above 1e-8), and no known special case explains the failure (branch cuts, integer-only identities, rounded
decimals, label superscripts, unmapped constants). Everything else is PASS or INCONCLUSIVE: precision is put before
recall so that every flag is worth a person's minute.

## Limits

- Only identities and inequalities with an explicit relation are checked. Definitions, physical laws, equations to
  solve, operator, matrix and set notation, and undefined functions are SKIPped.
- Assumptions come from rules over the formula and its context, not from understanding the text. A missing
  "for n ≥ 1" can turn a true formula into a FAIL, and a wrongly mapped constant can hide an error. Always read
  `assumptions` and the `translation` before trusting a verdict.
- Measured precision is 100 % on labeled data (0 false FAILs on 272 known-true identities; recall 82 % on 1,320
  injected errors). On messy real Wikipedia pages, roughly 10 % of FAILs were true errors before human review
  (32 of 308 in the second pass). Treat a FAIL as a lead to review, not a finding.
- Each check takes from a few milliseconds to the full `timeout`. Integrals and infinite series are the slow ones.
- The `timeout` on translation and assumption inference uses `SIGALRM`, so it applies only when `check` is called
  from the main thread. The verification phase is always capped, because it runs in a killable process.
- Worker processes are started with the `forkserver` method (`spawn` on Windows). You do not need an
  `if __name__ == "__main__":` guard: `formulaci` hides your script from the worker start-up so it is not re-run.
