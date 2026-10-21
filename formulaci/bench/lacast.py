"""LaCASt Wikipedia gold benchmark (Greiner-Petter et al., "Do the Math", TPAMI 2022).

Source: https://github.com/gipplab/LaCASt (MIT), files ``misc/Results/Wikipedia/gold-data.json``
(95 entries: page title, raw Wikipedia LaTeX, hand-written semantic LaTeX, CAS translations) and
``misc/Results/Wikipedia/All.txt`` (the human evaluation: per entry ✔/✘/- for the semantic LaTeX
(S), Mathematica (M) and Maple (A) translations).

Important: the human labels grade *translation* correctness, not whether the formula is
mathematically true. They are reused here to measure our translate stage on real Wikipedia
LaTeX, and our verify stage is only expected to PASS or stay INCONCLUSIVE on these formulas
(any FAIL is listed for human review, it is not counted as a known false positive).

``vendor()`` copies the compact subset we need into ``formulaci/bench/lacast/`` once; ``build``
then converts that snapshot, so building does not need network access.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from formulaci.schemas import Formula

HERE = Path(__file__).parent / "lacast"
SNAPSHOT = HERE / "gold.json"
_MARK = {"✔": "correct", "✘": "wrong", "-": "none"}


def vendor(repo: str | Path, dest: Path = HERE) -> int:
    """Extract the benchmark from a LaCASt checkout into ``dest`` (gold.json + LICENSE)."""
    repo = Path(repo)
    wiki = repo / "misc" / "Results" / "Wikipedia"
    gold = json.loads((wiki / "gold-data.json").read_text())
    labels = {}
    for line in (wiki / "All.txt").read_text().splitlines():
        m = re.match(r"^(\d+):\s*(\S)\s+(\S)\s+(\S)", line)
        if m:
            labels[int(m.group(1))] = [_MARK[c] for c in m.groups()[1:]]
    out = []
    for e in gold:
        f = e["formulae"][0]
        tr = {k: (v if isinstance(v, dict) else {"translation": v}) for k, v in (f.get("translations") or {}).items()}
        s, mth, mpl = labels.get(e["id"], ["none"] * 3)
        out.append({
            "gold_id": e["id"], "lacast_page_id": e["pid"], "eid": e["eid"], "title": e["title"],
            "latex": f["formula"], "semantic_latex": f.get("semanticFormula"),
            "mathematica": tr.get("Mathematica", {}).get("translation"),
            "maple": tr.get("Maple", {}).get("translation"),
            "definiens": [d["definition"] for d in f.get("definiens", [])[:3]],
            "human": {"semantic_latex": s, "mathematica": mth, "maple": mpl},
        })
    dest.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    shutil.copy(repo / "LICENSE", dest / "LICENSE")
    return len(out)


def records(snapshot: Path = SNAPSHOT) -> list[dict]:
    if not snapshot.exists():
        return []
    out = []
    for e in json.loads(snapshot.read_text()):
        gid = e["gold_id"]
        f = Formula(
            formula_id=f"lacast:gold:{gid:03d}", source="wikipedia", lang="en", page_title=e["title"],
            page_id=0, revision_id=0, url=f"https://en.wikipedia.org/wiki/{quote(e['title'].replace(' ', '_'))}",
            section="", index=gid, latex=e["latex"], display=True,
            context_before="", context_after="",
            page_categories=["bench", "bench-set:lacast"],
        )
        rec = json.loads(f.model_dump_json())
        rec["bench"] = {"set": "lacast", "label": "unknown", "category": "lacast", "name": e["title"],
                        "mutation": None, "source_id": rec["formula_id"], "lacast": {
                            k: e[k] for k in ("eid", "lacast_page_id", "semantic_latex", "mathematica", "maple",
                                              "definiens", "human")}}
        out.append(rec)
    return out
