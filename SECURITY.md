# Security

formulaci reads untrusted text, turns it into SymPy expressions, evaluates them, and publishes verdicts that
people and AI assistants act on. This document gives the threat model, what the review found, what was
fixed, what remains, and how to report a problem. Defaults are safe without configuration; nothing below
requires the user to set anything.

## Threat model

**Assets.** The machine running the pipeline (CLI, library, MCP server); the integrity of verdicts (a false
formula must never come back PASS, and a true one should not be reported as an error); the AI agents that
read our outputs (review batches, MCP tool results); the people who open the HTML report.

**Untrusted inputs.**
- Wikipedia wikitext: LaTeX, prose context, page titles, section names. Anyone can edit it.
- LaTeX and context passed to `formulaci.api.check` / `check_many` / `extract_formulas` and to the MCP tools
  `verify_formula`, `verify_text`, `explain_verdict`. These come from a language model that may itself be
  repeating a web page.
- Intermediate JSONL files (`parsed.jsonl`, `semantics.jsonl`, `verdicts.jsonl`, `reviews.jsonl`) are
  pipeline-produced, but must still be unable to run code if tampered with.
- Clinical audit targets (`targets.yaml`) and the calculator pages they point at.

**Trusted.** The operator's CLI arguments and environment variables, the pinned dependencies in `uv.lock`,
and the code in this repository (including the bench identity tables in `formulaci/bench/identities.py`,
which are Python source, not data).

## Findings and fixes

| # | Area | Finding | Severity | Status |
|---|---|---|---|---|
| 1 | MCP server | `_readable` passed srepr-looking strings from the model to `sympy.sympify`, which parses arbitrary Python. A crafted "formula" could run code in the server process. | High | **Fixed.** Uses the AST-whitelisted loader (`formulaci/safeload.py`). Test: `test_mcp_readable_does_not_use_sympify`. |
| 2 | semantics | `load_expr` rebuilt expressions with `eval` on srepr strings (restricted namespace, no builtins, but no AST check) with a `sympify` fallback. | High | **Fixed.** `load_srepr(evaluate=False)`; no fallback. |
| 3 | semantics | `prose.py` fed prose-derived strings (page text matched by regex) to `parse_expr` with implicit multiplication, which evaluates Python syntax. | High | **Fixed.** New strict arithmetic grammar `parse_simple_expr` builds SymPy directly from a whitelisted AST; rejects attributes, calls outside a fixed set, exponents > 2000, inputs > 300 chars. |
| 4 | translate | `roundtrip` and the lark fallback rebuilt via `sympify(srepr)`. Symbol names are repr-quoted so this was not exploitable as found, but it was eval by another name. | Medium | **Fixed.** Both use `from_srepr`; an unsafe srepr is a `ParseError`. |
| 5 | report | Review export used `eval` to pretty-print; HTML report escaped most fields by hand but not all (`href` was raw). | Medium | **Fixed.** Jinja2 autoescape for the whole template; only `https://en.wikipedia.org/` links are rendered as links; export uses the safe loader. Tests: `test_html_report_escapes_everything`. |
| 6 | AI readers | Page text reached reviewer agents and MCP clients without being marked as data; `verify_text` advice echoed formula LaTeX into an instruction sentence. | Medium | **Fixed.** Review batches carry a standing data-not-instructions note and fence every quoted field in « »; `REVIEWER_BRIEF.md` states the rule; MCP advice refers to formulas by index only, LaTeX stays in `results`. |
| 7 | resources | No input-size caps in the library/MCP; no memory limit in verify workers. | Medium | **Fixed.** Caps: LaTeX 20,000 chars, context 20,000, document 2,000,000, 1,000 items per batch, 200 formulas per MCP call, timeouts ≤ 60 s. Worker children set `RLIMIT_AS`/`RLIMIT_DATA` (8 GiB, best effort per platform). Pathological inputs (exponent towers, giant factorials, 10⁹-term sums, 60-deep fractions, 1 MB input) terminate within the timeout: `test_api_pathological_inputs_terminate`. |
| 8 | verify | Already had an AST-whitelisted srepr loader, a boolean constraint grammar, and a supervisor that kills the child process on timeout. | — | Verified; now the shared loader for every stage. |
| 9 | extract | Only talks to `https://en.wikipedia.org/w/api.php`; cache paths are derived from numeric page/revision ids; the contact string from `FORMULACI_CONTACT` is sent only in the User-Agent header and never logged. | — | Verified; regression test `test_extract_cache_paths_are_id_based_and_contact_not_logged`. |
| 10 | clinical | Non-local hosts are refused without `--allow-live`, enforced both before launch and by a Playwright route guard that aborts every non-local request (so a redirect cannot escape); the mock server binds to 127.0.0.1; only synthetic reference vectors are typed, never real patient data. | — | Verified; `test_clinical_refuses_remote_hosts_without_flag`. |
| 11 | subprocess | Verify workers are forked with `multiprocessing`; the only pickled data crosses a pipe between parent and child of the same process tree. No `shell=True`, no `os.system`, no network in workers. | — | Verified. |
| 12 | supply chain | `pip-audit` over the exported lockfile: no known vulnerabilities (2026-10-21). No secrets, tokens or personal addresses in the repository or its history. | — | Verified. |
| 13 | correctness as safety | Could page prose make the pipeline confirm a false formula as PASS, e.g. by stating a domain that collapses to one point? Domains are typed ranges, not point sets; constraints are intersected with the sampling regimes, and a regime with fewer than 5 evaluable points cannot contribute to a verdict, so a point-constraint produces INCONCLUSIVE, not PASS. A symbolic `equal` alone also never yields FAIL. | Low | Verified by reading `formulaci/verify/policy.py`; no change. |

A guard test, `test_no_string_evaluation_outside_safe_modules`, fails the suite if any module other than
`safeload.py` and `verify/reconstruct.py` (and the bench oracle, which evaluates conditions from the
repository's own Python identity tables) calls `eval`, `exec`, `sympify` or `parse_expr`.

## What remains

- `formulaci/bench/oracle.py` evaluates sampling conditions written in the repository's own
  `identities.py`. That is code in the repo, not data, and it is excluded from the guard test; do not load
  bench sets from untrusted sources.
- Memory limits are best effort: macOS does not enforce `RLIMIT_AS`; the supervisor's time cap is the
  binding limit there.
- The MCP server runs with the privileges of whoever starts it and exposes no file or network access, but
  it is a stdio server: do not expose it over a network without an authenticating transport.
- Verdicts are advice, not proof. PASS means "no counterexample found under the inferred assumptions";
  roughly one in ten FAILs on messy real pages is a true error before human review.

## Reporting

Open a GitHub issue at https://github.com/nani1902/formulaci with the input that triggered the problem
and the version. For anything that could run code or leak data, email the maintainer first via the
address on the GitHub profile and allow a few days before public disclosure.
