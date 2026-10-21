"""Extract stage end-to-end: pages.txt -> formulas.jsonl from cached real wikitext (no network)."""
from formulaci.extract.fetch import fetch_batch, load_cached, save_cached
from formulaci.extract.pipeline import log_path_for, run, summarize
from formulaci.schemas import Formula, read_jsonl

from .test_parse import PAGES, load


class FakeClient:
    """Answers prop=info / prop=revisions from the fixtures, counting requests."""

    def __init__(self, pages):
        self.pages = {p.page_id: p for p in pages}
        self.calls = []

    def query_pages(self, params):
        self.calls.append(params["prop"])
        ids = [int(x) for x in params["pageids"].split("|")]
        out = {}
        for pid in ids:
            p = self.pages.get(pid)
            if p is None:
                out[pid] = {"pageid": pid, "missing": True}
            elif params["prop"] == "info":
                out[pid] = {"pageid": pid, "title": p.title, "lastrevid": p.revision_id}
            else:
                out[pid] = {"pageid": pid, "title": p.title,
                            "revisions": [{"revid": p.revision_id, "slots": {"main": {"content": p.wikitext}}}],
                            "categories": [{"title": "Category:" + c} for c in p.categories]}
        return out


def test_fetch_uses_cache_by_revision(tmp_path):
    pages = [load(k) for k in PAGES]
    client = FakeClient(pages)
    got, missing = fetch_batch(client, [p.page_id for p in pages] + [999], tmp_path)
    assert [g.page_id for g in got] == [p.page_id for p in pages] and missing == [999]
    assert client.calls == ["revisions|categories"]  # nothing cached yet: no revision check
    assert load_cached(tmp_path, pages[0].page_id, pages[0].revision_id).wikitext == pages[0].wikitext
    client.calls.clear()
    got, _ = fetch_batch(client, [p.page_id for p in pages], tmp_path)
    assert client.calls == ["info"] and len(got) == 3  # rerun: one cheap request, content from cache
    client.pages[pages[0].page_id].revision_id += 1  # page edited -> refetch just that page
    client.calls.clear()
    got, _ = fetch_batch(client, [p.page_id for p in pages], tmp_path)
    assert client.calls == ["info", "revisions|categories"]
    assert got[0].revision_id == pages[0].revision_id


def test_run_end_to_end_resumable(tmp_path):
    cache = tmp_path / "cache"
    pages = [load(k) for k in PAGES]
    for p in pages:
        save_cached(cache, p)
    pages_txt = tmp_path / "pages.txt"
    pages_txt.write_text("".join(f"{p.page_id}\t{p.title}\n" for p in pages) + "4242\tMissing page\n")
    out = tmp_path / "formulas.jsonl"

    totals = run(pages_txt, out, offline=True, cache_dir=cache, limit=2, workers=2)
    assert totals["pages"] == 2
    recs = list(read_jsonl(out, Formula))
    assert len(recs) == 436 + 515
    assert len({r.formula_id for r in recs}) == len(recs)

    totals = run(pages_txt, out, offline=True, cache_dir=cache, workers=1)  # resumes: only page 3 + missing one
    assert totals == {"pages": 1, "formulas": 578, "missing": 1, "errors": 0}
    totals = run(pages_txt, out, offline=True, cache_dir=cache, workers=1)
    assert totals["pages"] == 0 and totals["missing"] == 0
    s = summarize(out)
    assert s["pages"] == 4 and s["pages_with_formulas"] == 3 and s["pages_missing"] == 1
    assert s["n_formulas"] == 436 + 515 + 578 == s["n_inline"] + s["n_display"]

    totals = run(pages_txt, out, offline=True, cache_dir=cache, force=True, workers=1)
    assert totals["formulas"] == 436 + 515 + 578
    assert sum(1 for _ in out.open()) == 436 + 515 + 578
    assert log_path_for(out).read_text().count("\n") == 1 + 4
