"""Extract stage: page list (talk page -> article mapping, dedup, ordering) with a fake API client."""
from formulaci.extract.pages import build_pages, class_rank, read_pages

CATS = {
    "Mathematics": ["Category:B-Class mathematics articles", "Category:FA-Class mathematics articles",
                    "Category:Template-Class mathematics pages"],
    "Physics": ["Category:Start-Class physics articles", "Category:Physics articles by quality and importance"],
}
MEMBERS = {  # category -> talk pages (ns 1) with subject ids
    "Category:B-Class mathematics articles": [(1, 101, "Pi"), (1, 102, "Gamma function"), (1, None, "Orphan")],
    "Category:FA-Class mathematics articles": [(1, 103, "Euler's identity")],
    "Category:Start-Class physics articles": [(1, 101, "Pi"), (1, 104, "Ohm's law"), (1, 105, "Redirected")],
}
VIEWS = {101: 900, 102: 500, 103: 50, 104: 700, 105: 10}


class FakeClient:
    n_requests = 0

    def query(self, params):
        self.n_requests += 1
        if params.get("list") == "categorymembers":
            proj = params["cmtitle"].removeprefix("Category:").removesuffix(" articles by quality")
            yield {"query": {"categorymembers": [{"title": t} for t in CATS.get(proj, [])]}}
        else:
            pages = []
            for ns, sid, title in MEMBERS.get(params["gcmtitle"], []):
                p = {"ns": ns, "title": "Talk:" + title, "pageid": 9000 + (sid or 0)}
                if sid:
                    p.update(subjectid=sid, associatedpage=title)
                pages.append(p)
            yield {"query": {"pages": pages}}

    def query_pages(self, params):
        self.n_requests += 1
        return {int(i): {"pageid": int(i), "ns": 0, "title": f"T{i}", "redirect": int(i) == 105,
                         "pageviews": {"2026-10-01": VIEWS[int(i)], "2026-10-02": None}}
                for i in params["pageids"].split("|")}


def test_class_rank():
    assert class_rank("Category:FA-Class mathematics articles") < class_rank("Category:B-Class physics articles")
    assert class_rank("Category:List-Class Statistics articles") < class_rank("Category:C-Class Statistics articles")
    assert class_rank("Category:Unassessed Engineering articles") == 9


def test_build_pages_views_order(tmp_path):
    out = tmp_path / "pages.txt"
    n = build_pages(out, client=FakeClient(), projects=["Mathematics", "Physics"], cache_dir=tmp_path / "c")
    assert n == 4  # deduplicated (Pi in two projects), orphan talk page and redirect dropped
    assert read_pages(out) == [(101, "T101"), (104, "T104"), (102, "T102"), (103, "T103")]
    meta = (tmp_path / "pages_meta.tsv").read_text().splitlines()
    assert meta[1].split("\t") == ["101", "T101", "900", "B", "Mathematics,Physics"]
    # rebuilding from the cache costs only the subcategory listings
    c = FakeClient()
    build_pages(out, client=c, projects=["Mathematics", "Physics"], cache_dir=tmp_path / "c")
    assert c.n_requests == 2


def test_build_pages_partial_views(tmp_path):
    out = tmp_path / "pages.txt"
    build_pages(out, client=FakeClient(), projects=["Mathematics", "Physics"], cache_dir=tmp_path / "c",
                views_upto="B")
    # views known for FA/B pages (sorted by views), Start-class pages follow by class
    assert [pid for pid, _ in read_pages(out)] == [101, 102, 103, 104, 105]
    build_pages(out, client=FakeClient(), projects=["Mathematics", "Physics"], cache_dir=tmp_path / "d",
                views=False)
    assert [pid for pid, _ in read_pages(out)] == [103, 102, 101, 104, 105]  # FA, B (by title), Start
