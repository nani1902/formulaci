"""Build the page list: WikiProject assessment categories -> articles, sorted by page views."""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from .api import WikiClient

# WikiProject name as it appears in "Category:<X> articles by quality".
PROJECTS = ["Mathematics", "Physics", "Statistics", "Engineering"]
PAGEVIEW_DAYS = 60


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
    return cats


def category_articles(client: WikiClient, category: str) -> dict[int, str]:
    """Map article page_id -> title for every talk page (or article) in `category`."""
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
    return out


def pageviews(client: WikiClient, page_ids: list[int]) -> dict[int, dict]:
    """page_id -> {title, views, redirect} for article ids, `PAGEVIEW_DAYS` days of views."""
    out: dict[int, dict] = {}
    for i in range(0, len(page_ids), 50):
        batch = page_ids[i:i + 50]
        pages = client.query_pages({"pageids": "|".join(map(str, batch)), "prop": "info|pageviews",
                                    "pvipdays": str(PAGEVIEW_DAYS)})
        for pid, p in pages.items():
            if p.get("missing") or not isinstance(pid, int):
                continue
            views = sum(v or 0 for v in (p.get("pageviews") or {}).values())
            out[pid] = {"title": p["title"], "views": views, "redirect": bool(p.get("redirect")),
                        "ns": p.get("ns")}
        if (i // 50) % 50 == 0:
            print(f"[pages] pageviews {i + len(batch)}/{len(page_ids)}", file=sys.stderr)
    return out


def build_pages(out: str | Path = "data/raw/pages.txt", limit: int | None = None,
                projects: list[str] = PROJECTS, client: WikiClient | None = None) -> int:
    """Write `page_id<TAB>title` sorted by views desc, plus `pages_meta.tsv` with views/projects."""
    client = client or WikiClient()
    membership: dict[int, set[str]] = defaultdict(set)
    titles: dict[int, str] = {}
    for proj in projects:
        for cat in quality_categories(client, proj):
            arts = category_articles(client, cat)
            print(f"[pages] {cat}: {len(arts)}", file=sys.stderr)
            for pid, title in arts.items():
                membership[pid].add(proj)
                titles[pid] = title
    print(f"[pages] {len(titles)} unique articles; fetching pageviews", file=sys.stderr)
    info = pageviews(client, sorted(titles))
    rows = []
    n_redirect = 0
    for pid, meta in info.items():
        if meta["redirect"] or meta["ns"] != 0:
            n_redirect += 1
            continue
        rows.append((meta["views"], pid, meta["title"], ",".join(sorted(membership[pid]))))
    rows.sort(key=lambda r: (-r[0], r[2]))
    if limit:
        rows = rows[:limit]
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for views, pid, title, _ in rows:
            f.write(f"{pid}\t{title}\n")
    with (out.parent / "pages_meta.tsv").open("w") as f:
        f.write(f"page_id\ttitle\tviews_{PAGEVIEW_DAYS}d\tprojects\n")
        for views, pid, title, projs in rows:
            f.write(f"{pid}\t{title}\t{views}\t{projs}\n")
    print(f"[pages] wrote {len(rows)} pages to {out} (dropped {n_redirect} redirects/non-articles, "
          f"{len(titles) - len(info)} missing); {client.n_requests} API requests", file=sys.stderr)
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
