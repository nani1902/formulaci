# formulaci

Software has test suites. Human knowledge does not. This project runs the formulas people rely on
— starting with Wikipedia's mathematics/physics/statistics articles and the equations behind online
clinical calculators — through a computer algebra system and reports the ones that are wrong, with
reproducible counterexamples.

See `SPEC.md` for the architecture and `formulaci/<stage>/README.md` for each stage.

```bash
uv sync --all-extras
uv run formulaci --help
```
