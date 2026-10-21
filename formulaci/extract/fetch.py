"""Fetch page wikitext + categories in batches of 50, with an on-disk cache keyed by page_id+revision."""
from __future__ import annotations

import gzip
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

from .api import WikiClient

DEFAULT_CACHE = Path("data/raw/cache")


@dataclass
class PageData:
    page_id: int
    title: str
    revision_id: int
    wikitext: str
    categories: list[str] = field(default_factory=list)


def _cache_path(cache_dir: Path, page_id: int, rev: int) -> Path:
    return cache_dir / "pages" / f"{page_id % 100:02d}" / f"{page_id}_{rev}.json.gz"


def load_cached(cache_dir: Path, page_id: int, rev: int | None = None) -> PageData | None:
    """Load a cached page; with rev=None, the newest cached revision."""
    if rev is not None:
        p = _cache_path(cache_dir, page_id, rev)
        if not p.exists():
            return None
    else:
        d = cache_dir / "pages" / f"{page_id % 100:02d}"
        cands = sorted(d.glob(f"{page_id}_*.json.gz"), key=lambda q: int(q.name.split("_")[1].split(".")[0]))
        if not cands:
            return None
        p = cands[-1]
    with gzip.open(p, "rt") as f:
        return PageData(**json.load(f))


def save_cached(cache_dir: Path, page: PageData) -> None:
    p = _cache_path(cache_dir, page.page_id, page.revision_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with gzip.open(tmp, "wt") as f:
        json.dump(asdict(page), f)
    tmp.replace(p)


def fetch_batch(client: WikiClient | None, page_ids: list[int], cache_dir: Path = DEFAULT_CACHE,
                offline: bool = False) -> tuple[list[PageData], list[int]]:
    """Return (pages, missing_ids) for up to 50 page ids.

    One cheap `prop=info` request finds each page's latest revision; only pages whose
    (page_id, revision) is not cached are downloaded. With `offline`, use whatever is cached.
    """
    assert len(page_ids) <= 50
    if offline or client is None:
        pages, missing = [], []
        for pid in page_ids:
            pg = load_cached(cache_dir, pid)
            (pages.append(pg) if pg else missing.append(pid))
        return pages, missing

    # Pages with no cached revision at all need no revision check: fetch them directly.
    seen = [pid for pid in page_ids
            if any((cache_dir / "pages" / f"{pid % 100:02d}").glob(f"{pid}_*.json.gz"))]
    info = client.query_pages({"pageids": "|".join(map(str, seen)), "prop": "info"}) if seen else {}
    result: dict[int, PageData] = {}
    to_fetch = [pid for pid in page_ids if pid not in set(seen)]
    for pid in seen:
        p = info.get(pid)
        if not p or p.get("missing") or "lastrevid" not in p:
            continue
        cached = load_cached(cache_dir, pid, int(p["lastrevid"]))
        if cached:
            result[pid] = cached
        else:
            to_fetch.append(pid)
    if to_fetch:
        pages = client.query_pages({"pageids": "|".join(map(str, to_fetch)), "prop": "revisions|categories",
                                    "rvprop": "content|ids", "rvslots": "main", "clshow": "!hidden",
                                    "cllimit": "max"})
        for pid in to_fetch:
            p = pages.get(pid)
            if not p or not p.get("revisions"):
                continue
            rev = p["revisions"][-1]
            slot = rev.get("slots", {}).get("main", {})
            if "content" not in slot:
                continue
            cats = [c["title"].removeprefix("Category:") for c in p.get("categories", [])]
            pg = PageData(page_id=pid, title=p["title"], revision_id=int(rev["revid"]),
                          wikitext=slot["content"], categories=cats)
            save_cached(cache_dir, pg)
            result[pid] = pg
    pages = [result[pid] for pid in page_ids if pid in result]
    missing = [pid for pid in page_ids if pid not in result]
    return pages, missing


def iter_pages(client: WikiClient | None, page_ids: list[int], cache_dir: Path = DEFAULT_CACHE,
               offline: bool = False) -> Iterator[tuple[list[PageData], list[int]]]:
    for i in range(0, len(page_ids), 50):
        yield fetch_batch(client, page_ids[i:i + 50], cache_dir, offline)
