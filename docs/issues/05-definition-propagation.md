coverage: use a page's own definitions to make later formulas checkable (50,850 definitions, 27,052 undefined functions)
labels: coverage, help-wanted, tier-B

A page writes `f(x) = x^2 + 1` and three formulas later `f(2) = 5` or `f'(x) = 2x`. Today the first is skipped as a `definition` (correct: nothing to check) and the second as `has_undefined_function`, because the semantics stage sees each formula alone. 50,850 formulas define a symbol and 27,052 use a page-specific function; a page-level symbol table would make a real fraction of the second group checkable, and it touches no LaTeX parsing.

**What to build.** In `formulaci/semantics`, a per-page pass before the per-formula rules: collect `name(args) = body` and `name = body` definitions (the `K.bare_symbol_definition` and `definition` rules already identify them), keyed by page and section order; when a later formula uses `name`, substitute the body (with argument renaming) and mark the result with a tag such as `S.definition_applied:f` in `assumptions_source` so a FAIL can be traced to the definition it used. Redefinitions within a page (`f` means something else in another section) must reset the table; a definition that is itself conditional (`\begin{cases}`) should be applied as a `Piecewise`.

**Precision risk.** A symbol defined on one page section and reused with a different meaning in another; `f` defined as "a function with property P" (not a formula); definitions that depend on parameters fixed in prose. Apply only explicit closed-form definitions, and only within the same section unless the name is unique on the page.

**Fixtures.** Build a small synthetic "page" set for the bench: a definition followed by true and mutated consequences, in the `Formula` JSONL format, so the gate measures this feature directly.
