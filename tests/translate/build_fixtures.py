"""Rebuild tests/translate/fixtures/formulas.jsonl from live Wikipedia.

This is a small, self-contained fetcher so the translate stage has real input before the
extract stage lands. It is not the extract stage: context stripping is crude.

    uv run python tests/translate/build_fixtures.py
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

from formulaci.schemas import Formula

API = "https://en.wikipedia.org/w/api.php"
UA = "formulaci/0.1 (translate-stage fixture builder; https://github.com/formulaci) python-requests"
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "raw" / "cache" / "translate-fixtures"
OUT = Path(__file__).resolve().parent / "fixtures" / "formulas.jsonl"

PAGES = [
    "List of trigonometric identities",
    "Gamma function",
    "Normal distribution",
    "Binomial coefficient",
    "Fourier transform",
    "Hyperbolic functions",
    "Beta function",
    "List of integrals of rational functions",
    "List of integrals of exponential functions",
    "List of integrals of logarithmic functions",
    "Exponential function",
    "Riemann zeta function",
]
PER_PAGE = 120  # keep the fixture small enough for a fast end-to-end test

MATH_RE = re.compile(r"<math(?P<attrs>[^>]*)>(?P<body>.*?)</math>", re.S)
HEAD_RE = re.compile(r"^(={2,6})\s*(.*?)\s*\1\s*$", re.M)


def fetch(title: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (re.sub(r"[^A-Za-z0-9]+", "_", title) + ".json")
    if f.exists():
        return json.loads(f.read_text())
    r = requests.get(
        API,
        params={
            "action": "query", "prop": "revisions|categories", "rvprop": "content|ids",
            "rvslots": "main", "titles": title, "format": "json", "formatversion": "2",
            "redirects": "1", "cllimit": "max", "clshow": "!hidden",
        },
        headers={"User-Agent": UA},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    f.write_text(json.dumps(data))
    time.sleep(0.3)
    return data


def strip_wikitext(s: str) -> str:
    s = MATH_RE.sub(" <formula> ", s)
    s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"'{2,}", "", s)
    return re.sub(r"\s+", " ", s).strip()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with OUT.open("w") as out:
        for title in PAGES:
            page = fetch(title)["query"]["pages"][0]
            rev = page["revisions"][0]
            text = rev["slots"]["main"]["content"]
            cats = [c["title"].removeprefix("Category:") for c in page.get("categories", [])]
            heads = [(m.start(), m.group(2)) for m in HEAD_RE.finditer(text)]
            for idx, m in enumerate(MATH_RE.finditer(text)):
                if idx >= PER_PAGE:
                    break
                body = m.group("body").strip()
                if not body:
                    continue
                section = ""
                for pos, h in heads:
                    if pos < m.start():
                        section = h
                line_start = text.rfind("\n", 0, m.start()) + 1
                display = "block" in m.group("attrs") or text[line_start:m.start()].strip(" ") in (":", "::")
                rec = Formula(
                    formula_id=f"wiki:en:{page['pageid']}:{rev['revid']}:{idx}",
                    page_title=page["title"],
                    page_id=page["pageid"],
                    revision_id=rev["revid"],
                    url="https://en.wikipedia.org/wiki/" + page["title"].replace(" ", "_"),
                    section=section,
                    index=idx,
                    latex=body,
                    display=display,
                    context_before=strip_wikitext(text[max(0, m.start() - 600):m.start()])[-400:],
                    context_after=strip_wikitext(text[m.end():m.end() + 600])[:400],
                    page_categories=cats,
                )
                out.write(rec.model_dump_json() + "\n")
                n += 1
            print(f"{title}: rev {rev['revid']}")
    print(f"wrote {n} formulas to {OUT}")


if __name__ == "__main__":
    main()
