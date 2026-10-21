"""Extract stage driver: pages.txt -> formulas.jsonl (+ per-page log), resumable."""
from __future__ import annotations

import os
import queue
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from urllib.parse import quote

from formulaci.schemas import Formula, append_jsonl, read_jsonl

from .api import WikiClient
from .fetch import DEFAULT_CACHE, PageData, iter_pages
from .pages import read_pages
from .parse import PageStats, extract_formulas

LOG_COLUMNS = ["page_id", "revision_id", "title", "status", "n_formulas", "n_math", "n_tmath", "n_inline",
               "n_display", "n_hidden", "n_chem", "n_html_math", "n_empty"]


def page_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe=";@$!*(),/~:'")


def page_to_formulas(page: PageData) -> tuple[list[Formula], PageStats]:
    extracted, stats = extract_formulas(page.wikitext)
    url = page_url(page.title)
    recs = [Formula(formula_id=f"wiki:en:{page.page_id}:{page.revision_id}:{f.index}", page_title=page.title,
                    page_id=page.page_id, revision_id=page.revision_id, url=url, section=f.section,
                    index=f.index, latex=f.latex, display=f.display, context_before=f.context_before,
                    context_after=f.context_after, page_categories=page.categories)
            for f in extracted]
    return recs, stats


def _safe_page_to_formulas(page: PageData) -> tuple[list[Formula], PageStats, str]:
    try:
        recs, st = page_to_formulas(page)
        return recs, st, "ok"
    except Exception as e:  # never let one page stop the run
        return [], PageStats(), f"error:{type(e).__name__}:{str(e)[:100]}"


def log_path_for(out_path: Path) -> Path:
    return out_path.with_name(out_path.stem + "_pages.tsv")


def done_page_ids(out_path: Path) -> set[int]:
    done: set[int] = set()
    log = log_path_for(out_path)
    if log.exists():
        with log.open() as f:
            next(f, None)
            for line in f:
                if line.strip():
                    done.add(int(line.split("\t", 1)[0]))
    if out_path.exists():
        # Pages whose formulas were written but whose log line was lost (crash between writes).
        with out_path.open() as f:
            for line in f:
                i = line.find('"page_id":')
                if i >= 0:
                    j = line.find(",", i)
                    done.add(int(line[i + 10:j]))
    return done


def _write_log(log: Path, rows: list[list]) -> None:
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write("\t".join(LOG_COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")


def run(in_path: str | Path = "data/raw/pages.txt", out_path: str | Path = "data/raw/formulas.jsonl",
        limit: int | None = None, force: bool = False, offline: bool = False,
        cache_dir: str | Path = DEFAULT_CACHE, client: WikiClient | None = None,
        workers: int | None = None) -> dict:
    in_path, out_path, cache_dir = Path(in_path), Path(out_path), Path(cache_dir)
    log = log_path_for(out_path)
    pages = read_pages(in_path)
    if limit:
        pages = pages[:limit]
    if force:
        for p in (out_path, log):
            p.unlink(missing_ok=True)
    done = done_page_ids(out_path)
    todo = [pid for pid, _ in pages if pid not in done]
    titles = dict(pages)
    print(f"[extract] {len(pages)} pages selected, {len(pages) - len(todo)} already done, {len(todo)} to do",
          file=sys.stderr)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not offline and client is None:
        client = WikiClient()

    # Fetch in a background thread so network and parsing overlap.
    q: queue.Queue = queue.Queue(maxsize=4)

    def producer():
        try:
            for item in iter_pages(client, todo, cache_dir, offline):
                q.put(item)
        except BaseException as e:  # surface in main thread
            q.put(e)
        q.put(None)

    threading.Thread(target=producer, daemon=True).start()
    totals = {"pages": 0, "formulas": 0, "missing": 0, "errors": 0}
    workers = workers if workers is not None else min(4, os.cpu_count() or 1)
    pool = ProcessPoolExecutor(workers) if workers > 1 and len(todo) > 1 else None
    t0 = time.monotonic()
    try:
        _consume(q, pool, out_path, log, titles, totals, len(todo), t0)
    finally:
        if pool:
            pool.shutdown(cancel_futures=True)
    return totals


def _consume(q, pool, out_path, log, titles, totals, n_todo, t0) -> None:
    while True:
        item = q.get()
        if item is None:
            break
        if isinstance(item, BaseException):
            raise item
        batch, missing = item
        recs_all, rows = [], []
        results = pool.map(_safe_page_to_formulas, batch) if pool else map(_safe_page_to_formulas, batch)
        for page, (recs, st, status) in zip(batch, results):
            totals["errors"] += status != "ok"
            recs_all.extend(recs)
            rows.append([page.page_id, page.revision_id, page.title, status, len(recs), st.n_math, st.n_tmath,
                         st.n_inline, st.n_display, st.n_hidden, st.n_chem, st.n_html_math, st.n_empty])
        for pid in missing:
            rows.append([pid, 0, titles.get(pid, ""), "missing"] + [0] * (len(LOG_COLUMNS) - 4))
        append_jsonl(out_path, recs_all)
        _write_log(log, rows)
        totals["pages"] += len(batch)
        totals["missing"] += len(missing)
        totals["formulas"] += len(recs_all)
        n = totals["pages"] + totals["missing"]
        el = time.monotonic() - t0
        eta = el / n * (n_todo - n) if n else 0
        print(f"[extract] {n}/{n_todo} pages, {totals['formulas']} formulas, "
              f"{el:.0f}s elapsed, ETA {eta / 60:.1f} min", file=sys.stderr)


def summarize(out_path: str | Path = "data/raw/formulas.jsonl") -> dict:
    """Aggregate the per-page log into the counts reported in the README."""
    log = log_path_for(Path(out_path))
    s = {k: 0 for k in LOG_COLUMNS[4:]}
    s.update(pages=0, pages_ok=0, pages_with_formulas=0, pages_missing=0, pages_error=0)
    with log.open() as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != len(LOG_COLUMNS):
                continue
            s["pages"] += 1
            st = parts[3]
            if st == "ok":
                s["pages_ok"] += 1
            elif st == "missing":
                s["pages_missing"] += 1
            else:
                s["pages_error"] += 1
            for k, v in zip(LOG_COLUMNS[4:], parts[4:]):
                s[k] += int(v)
            s["pages_with_formulas"] += int(parts[4]) > 0
    return s


__all__ = ["run", "summarize", "page_to_formulas", "read_jsonl"]
