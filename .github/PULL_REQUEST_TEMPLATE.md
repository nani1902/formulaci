## What this changes

<!-- one construct, one fixture set, or one review batch -->

## Bench gate

<!-- paste the output of `uv run python scripts/bench_gate.py --bench-dir formulaci/bench/sets` -->

```
```

## Fixtures

<!-- identities added to formulaci/bench/identities.py, or review batches imported -->

## Checklist

- [ ] `uv run pytest -q` passes
- [ ] no known-true identity FAILs, no injected error PASSes
- [ ] no `eval`/`sympify`/`parse_expr` on untrusted text (the guard test enforces this)
- [ ] new rules carry a tag that appears in `assumptions_source`
