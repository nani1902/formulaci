"""Build the page list: WikiProject assessment categories -> articles, sorted by page views."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from .api import WikiClient

# WikiProject name as it appears in "Category:<X> articles by quality".
PROJECTS = ["Mathematics", "Physics", "Statistics", "Engineering"]
PAGEVIEW_DAYS = 60
# Assessment classes, best first; used to order categories and to break ties.
CLASS_ORDER = ["FA", "FL", "A", "GA", "B", "List", "C", "Start", "Stub", "Unassessed"]
DEFAULT_CACHE = Path("data/raw/cache/pagelist")


def class_rank(category: str) -> int:
    name = category.removeprefix("Category:")
    for i, c in enumerate(CLASS_ORDER):
        if name.startswith(c + "-Class") or name.startswith(c + " "):
            return i
    return len(CLASS_ORDER)


def quality_categories(client: WikiClient, project: str) -> list[str]:
    """Article-class subcategories (FA ... Stub, List, Unassessed) of `<project> articles by quality`.

    Non-article classes (Category-, Template-, Redirect-, Draft- ... "pages") are dropped.
    """
    cats = []
    for data in client.query({"list": "categorymembers", "cmtitle": f"Category:{project} articles by quality",
                              "cmtype": "subcat", "cmlimit": "500"}):
        for m in data["query"]["categorymembers"]:
            t = m["title"]
            if t.endswith(" articles") and "by quality" not in t:
                cats.append(t)
    return sorted(cats, key=class_rank)


def category_articles(client: WikiClient, category: str, cache_dir: Path | None = None) -> dict[int, str]:
    """Map article page_id -> title for every talk page (or article) in `category`."""
    cpath = cache_dir / "members" / (re.sub(r"[^A-Za-z0-9]+", "_", category) + ".json") if cache_dir else None
    if cpath and cpath.exists():
        return {int(k): v for k, v in json.loads(cpath.read_text()).items()}
    out: dict[int, str] = {}
    for data in client.query({"generator": "categorymembers", "gcmtitle": category, "gcmnamespace": "0|1",
                              "gcmlimit": "500", "prop": "info", "inprop": "subjectid|associatedpage"}):
        for p in data.get("query", {}).get("pages", []):
            if p.get("ns") == 1:
                sid = p.get("subjectid")
                if sid:  # missing when the talk page has no article
                    out[int(sid)] = p.get("associatedpage", p["title"].removeprefix("Talk:"))
            elif p.get("ns") == 0 and "pageid" in p:
                out[int(p["pageid"])] = p["title"]
    if cpath:
        cpath.parent.mkdir(parents=True, exist_ok=True)
        cpath.write_text(json.dumps(out))
    return out


def pageviews(client: WikiClient, page_ids: list[int], cache: Path | None = None) -> dict[int, dict]:
    """page_id -> {title, views, redirect} for article ids, `PAGEVIEW_DAYS` days of views.

    Results are appended to `cache` (JSONL) per batch, so an interrupted build resumes.
    """
    out: dict[int, dict] = {}
    if cache and cache.exists():
        with cache.open() as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    out[int(d.pop("page_id"))] = d
    known = set(out)
    todo = [p for p in page_ids if p not in known]
    print(f"[pages] pageviews: {len(known)} cached, {len(todo)} to fetch", file=sys.stderr)
    page_ids = todo
    for i in range(0, len(page_ids), 50):
        batch = page_ids[i:i + 50]
        got: dict[int, dict] = {}
        pages = client.query_pages({"pageids": "|".join(map(str, batch)), "prop": "info|pageviews",
                                    "pvipdays": str(PAGEVIEW_DAYS)})
        for pid, p in pages.items():
            if p.get("missing") or not isinstance(pid, int):
                continue
            views = sum(v or 0 for v in (p.get("pageviews") or {}).values())
            got[pid] = {"title": p["title"], "views": views, "redirect": bool(p.get("redirect")),
                        "ns": p.get("ns")}
        for pid in batch:  # record missing pages too, so they are not re-requested
            got.setdefault(pid, {"title": "", "views": 0, "redirect": False, "ns": None, "missing": True})
        out.update(got)
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            with cache.open("a") as f:
                for pid, d in got.items():
                    f.write(json.dumps({"page_id": pid, **d}) + "\n")
        if (i // 50) % 10 == 0:
            print(f"[pages] pageviews {i + len(batch)}/{len(page_ids)}", file=sys.stderr)
    return out


def build_pages(out: str | Path = "data/raw/pages.txt", limit: int | None = None,
                projects: list[str] = PROJECTS, client: WikiClient | None = None,
                cache_dir: str | Path = DEFAULT_CACHE, views: bool = True,
                views_upto: str | None = None) -> int:
    """Write `page_id<TAB>title` sorted by views desc, plus `pages_meta.tsv` with views/class/projects.

    With `views=False` (~140 requests, or none with a warm cache) pages are ordered by best
    assessment class, then by any cached views; redirects are then only filtered where views were
    cached (redirect pages yield no formulas anyway). Cold `prop=pageviews` lookups return views for
    only ~7 of 50 pages per request (the rest come via `continue`), so a full views pass over ~65k
    pages costs ~9,000 requests: ~15 h at the Unidentified rate limit, ~45 min with a contact UA.
    """
    client = client or WikiClient()
    cache_dir = Path(cache_dir)
    membership: dict[int, set[str]] = defaultdict(set)
    best_class: dict[int, int] = {}
    titles: dict[int, str] = {}
    for proj in projects:
        for cat in quality_categories(client, proj):
            arts = category_articles(client, cat, cache_dir)
            print(f"[pages] {cat}: {len(arts)} (requests so far: {client.n_requests})", file=sys.stderr)
            for pid, title in arts.items():
                membership[pid].add(proj)
                titles[pid] = title
                best_class[pid] = min(best_class.get(pid, 99), class_rank(cat))
    print(f"[pages] {len(titles)} unique articles", file=sys.stderr)
    # Fetch views best class first, so an interrupted pass has covered the likeliest-read pages.
    order = sorted(titles, key=lambda pid: (best_class[pid], pid))
    if views and views_upto:
        cut = CLASS_ORDER.index(views_upto)
        order = [pid for pid in order if best_class[pid] <= cut]
    cached = pageviews(client, order if views else [], cache_dir / "views.jsonl")
    # Pages without views (not requested): -1, ordered after every page with known views.
    info = {pid: cached.get(pid) or {"title": t, "views": -1, "redirect": False, "ns": 0}
            for pid, t in titles.items()}
    rows = []
    n_dropped = 0
    for pid in titles:
        meta = info.get(pid)
        if not meta or meta.get("missing") or meta["redirect"] or meta["ns"] != 0:
            n_dropped += 1
            continue
        rows.append((meta["views"], best_class[pid], pid, meta["title"], ",".join(sorted(membership[pid]))))
    if not views:  # class first, cached views as tie-break
        rows.sort(key=lambda r: (r[1], -r[0], r[3]))
    else:  # known views desc; pages without views after them, by class
        rows.sort(key=lambda r: (r[0] < 0, -r[0], r[1], r[3]))
    if limit:
        rows = rows[:limit]
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for _, _, pid, title, _ in rows:
            f.write(f"{pid}\t{title}\n")
    with (out.parent / "pages_meta.tsv").open("w") as f:
        f.write(f"page_id\ttitle\tviews_{PAGEVIEW_DAYS}d\tbest_class\tprojects\n")
        for v, cls, pid, title, projs in rows:
            f.write(f"{pid}\t{title}\t{v}\t{CLASS_ORDER[cls] if cls < len(CLASS_ORDER) else '?'}\t{projs}\n")
    print(f"[pages] wrote {len(rows)} pages to {out} (dropped {n_dropped} redirects/missing/non-articles); "
          f"{client.n_requests} API requests this run", file=sys.stderr)
    return len(rows)


def read_pages(path: str | Path) -> list[tuple[int, str]]:
    rows = []
    with Path(path).open() as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            pid, _, title = line.partition("\t")
            rows.append((int(pid), title))
    return rows
