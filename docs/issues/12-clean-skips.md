coverage: cheap, precise skips for sets, tuples, words and empty sides (~33,000 relations)
labels: coverage, good-first-issue, tier-C

Four of the largest buckets in the ladder are not identities at all and never will be: set builder notation (14,359 relations), tuples and lists (10,535), words used as symbols such as `\text{PVR}` (4,688) and relations with an empty side from a formula split across `<math>` tags (3,947). Today they reach the translator, which tokenises and partially parses them before raising `Unsupported`. That costs run time on 952k formulas (the translate stage is a measurable share of a full pass) and, worse, the tags are coarse: a `\{ \ldots \}` that is a Stirling number, or a `\text{}` that is a function name (`\text{erf}`), is lost with the rest.

**What to build.** A cheap pre-classifier in `formulaci/translate/core.py` that recognises these shapes from the token stream before parsing, with precise reasons (`set_builder`, `set_literal`, `tuple_definition`, `word_symbol`, `split_formula`), plus recovery for the exceptions above. For `empty_side`, the right fix is upstream: the extract stage could join consecutive `<math>` tags whose relation is dangling (`\le k` following a tag ending in an expression).

**Acceptance.** Bench gate green; the translate stage's `parsed.jsonl.summary.json` shows the new reasons; no formula that was checkable before becomes unchecked (compare `checkable` counts on the review fixtures).

A good first issue: no mathematics, just careful pattern work with an immediate measurable effect.
