# extract: English Wikipedia `<math>` formulas → `data/raw/formulas.jsonl`

## Run

```bash
uv run python -m formulaci.cli extract pages --out data/raw/pages.txt          # page list, sorted by views
uv run python -m formulaci.cli extract run --pages data/raw/pages.txt --out data/raw/formulas.jsonl --limit 200
uv run python -m formulaci.cli extract run --pages data/raw/pages.txt --out data/raw/formulas.jsonl   # all; resumable
uv run python -m formulaci.cli extract stats                                    # cumulative counts
uv run pytest tests/extract
```

`run` is resumable. It skips every page already listed in `data/raw/formulas_pages.tsv` (one row per
processed page, including pages with zero formulas) or present in the output. `--force` discards the
output and the log and redoes every page; with a warm cache that costs one request per 50 pages.
`--offline` uses only cached wikitext. `--limit N` processes the first N pages of the list (the N
most-viewed), so `--limit 200` followed by `--limit 5000` extends a run instead of repeating it.

Python API: `formulaci.extract.run(in_path, out_path, limit=None, force=False, offline=False)`.

## Rate limits: read this before a big run

Since 2026, Wikimedia rate-limits the API per client
(https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits). A User-Agent **without contact info**
is "Unidentified" and gets **10 requests/minute**. A compliant one (email or URL) gets 200/minute.
SPEC's UA `formulaci/0.1 (knowledge verification research)` has no contact, so by default the client
paces itself at 10 req/min. To run faster, opt in:

```bash
FORMULACI_CONTACT="https://github.com/you/formulaci; you@example.org" uv run python -m formulaci.cli extract run
```

That appends the contact to the UA and paces at 3 req/s. `FORMULACI_RPS` overrides the rate, capped at
5/s. 429 responses are retried after `Retry-After`, with at least 5 s between attempts.

Request budget:

- **Category listings:** ~170 requests for the page list.
- **Page views (the expensive part):** cold `prop=pageviews` lookups return views for only ~7 of 50
  pages per request; the rest come back through `continue`. That is ~7–8 requests per 50 pages:
  **~9,000 requests (~15 h at 10/min) for all ~65k pages**, ~45 min with a contact UA. Hence
  `--views-upto`.
- **Extraction:** 1 request per 50 pages, plus continuations when 50 pages of wikitext exceed the API's
  response limit. ~1,300 requests (~2.2 h at 10/min) for all pages.
- **Reruns:** 1 cheap `prop=info` request per 50 pages. Content is re-downloaded only for pages whose
  latest revision is not cached.

## What it does

1. **Page list** (`pages.py`). For each of WikiProject Mathematics, Physics, Statistics and Engineering,
   takes the article-class subcategories of `Category:<Project> articles by quality` (FA, FL, A, GA,
   B, C, List, Start, Stub, Unassessed; not the Template/Category/Redirect/Draft "pages" classes).
   These list talk pages, so `generator=categorymembers&prop=info&inprop=subjectid|associatedpage`
   maps each talk page to its article id. Results are deduplicated across classes and projects.
   Views come from `prop=pageviews` (60 days), fetched best assessment class first (FA, FL, A, GA, B,
   List, C, Start, Stub, Unassessed). Redirects and missing pages are dropped. The list is sorted by
   views descending; pages without views (see `--views-upto`) come after every page with views, by
   class. Output: `data/raw/pages.txt` (`page_id<TAB>title`), plus
   `data/raw/pages_meta.tsv` (views, best class, projects). Category listings and page views are
   cached under `data/raw/cache/pagelist/`, so an interrupted build resumes. `--no-views` skips page
   views and orders pages by best assessment class. `--views-upto B` fetches views only for pages
   whose best class is at or above B.
2. **Fetch** (`fetch.py`). `prop=revisions|categories&rvprop=content|ids&rvslots=main&clshow=!hidden`
   for 50 page ids per request, continuations merged. The cache is
   `data/raw/cache/pages/<id%100>/<page_id>_<revision>.json.gz`, holding wikitext, title and
   categories. Network and parsing overlap: a fetch thread feeds a process pool of 4 parsers.
3. **Parse** (`parse.py`, mwparserfromhell). One recursive walk in document order:
   - **Formulas:** every `<math>` tag at any depth (templates, infobox parameters, refs, tables, image
     captions, headings), plus every `{{tmath|…}}` (LaTeX rendered through `<math>`, with `{{!}}` and
     `{{=}}` unescaped). `index` runs 0..n-1 per page over extracted formulas only.
   - **Skipped and counted:** `<chem>`, `<ce>`, `<math chem>`, empty `<math></math>`, and pure-HTML
     `{{math|…}}` (no `<math>` inside). Comments, `<nowiki>`, `<pre>` and `<syntaxhighlight>` contain no
     formulas by construction.
   - **`display`:** `display="block"`; or an inline tag that starts a line after `:` (`:`, `::`,
     `*:`), including via a transparent wrapper (`:{{math|<math>…</math>}}`); or anything inside
     `{{NumBlk}}`, `{{Equation box 1}}`, `{{block indent}}`/`{{bi}}`, `{{center}}`. `display="inline"`
     forces False. Table cells and bullets are inline.
   - **`section`:** heading path, e.g. `Definitions > Cumulative distribution function > Quantile
     function`. The lead is `""`.
   - **Context:** up to 400 characters of plain text on each side, cut at a word boundary. Templates
     are dropped except text-bearing ones (`math`, `mvar`, `nowrap`, `sub`/`sup`, `abs`, `lang`,
     `quote`, …). Refs, citations, hatnotes, file links and categories are dropped; link text is kept,
     entities decoded and whitespace collapsed. Other formulas inside the window appear as `$latex$`
     and are never cut in half. Formulas that are not in running prose (infobox parameters, refs,
     captions, other templates) get the surrounding prose plus a container label at the end of
     `context_before`: ` [Infobox probability distribution | pdf]`, ` [ref]`, ` [caption]`.
   - **Records:** `formula_id = wiki:en:{page_id}:{revision_id}:{index}`;
     `url = https://en.wikipedia.org/wiki/<Title_with_underscores>`; `page_categories` holds visible
     categories without the `Category:` prefix.

Per-page counts go to `data/raw/formulas_pages.tsv`: status, n_formulas, n_math, n_tmath, n_inline,
n_display, n_hidden, n_chem, n_html_math, n_empty.

## Measured counts

COUNTS_PLACEHOLDER

## Tests

`tests/extract/` checks in real wikitext for *Gamma function*, *List of trigonometric identities* and
*Normal distribution* (revisions in `fixtures/*.json`). The tests cover:

- formula counts, which equal a naive `<math` tag count and the `{{tmath` count;
- display counts, which equal the `display=block` tags plus `:<math>` lines;
- section paths of known formulas and the infobox context label;
- that contexts contain no wiki markup (`[[`, `{{`, `<ref`, `'''`, `&nbsp;`, `<math`) outside the
  inline `$…$` formulas;
- the display rules, the hidden/ref/caption/chem/comment handling, and `tmath` unescaping, on
  synthetic snippets;
- fetch caching by revision (fake client), and an offline end-to-end run with resume and `--force`.

## Known failure modes / not covered

- **Fragments are extracted as formulas.** Wikipedia often splits one equation across table cells
  (`| <math>\sin 2\theta</math> || <math>= 2\sin\theta\cos\theta</math>`) or writes
  `<math>= \dots</math>` continuation lines. Each piece becomes its own record (e.g. `= \frac{…}{2}`),
  and the extractor does not re-join them. Many records are not identities at all (`x`, `\mu\in\R`);
  deciding that is translate/semantics' job.
- **Pure-HTML math is skipped.** `{{math|''a''<sup>2</sup> + ''b''<sup>2</sup>}}` is counted
  (`n_html_math`) but not emitted. Some pages state their key identities only this way.
- **Display detection follows markup, not rendering.** A `<math>` alone on its own line without `:` is
  reported inline; MediaWiki also renders it inline, but visually it is a block. Rare wrappers
  (`<div style="margin-left">`, `{{quote}}`) are not treated as display.
- **Templates are not expanded.** Formulas produced by templates other than `tmath` (e.g. `{{frac}}`,
  `{{sfrac}}`, `{{radic}}` built equations, or infobox templates that assemble LaTeX from parameters)
  are not seen. Template-generated text missing from contexts can leave small gaps.
- **Context is approximate.** Text inside dropped templates (e.g. `{{efn|…}}` notes, `{{quote box}}`)
  is lost. Contexts can cross paragraph and section boundaries; headings appear as `Heading.`.
- **Page selection follows WikiProject tagging.** Untagged articles with formulas (e.g. some chemistry
  or economics pages) are missing, and some tagged pages are biographies or history with no
  formulas. Pages tagged in several projects appear once.
- **Snapshot.** Each run records the revision it fetched. A rerun after an edit keeps the old page's
  records (resume skips by page id). Use `--force` to refresh everything.
