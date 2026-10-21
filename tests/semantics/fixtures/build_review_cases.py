"""Build `review_cases.jsonl` from human-reviewed real FAILs (data/findings/reviews.jsonl).

Every reviewed id whose cause tag is a semantics problem, plus every confirmed real error, is copied
with its real `Formula` and `Parsed` records (so the fixture is self-contained) and labeled from the
review: what semantics *should* have said. Confirmed errors must stay checkable.

    uv run python tests/semantics/fixtures/build_review_cases.py
"""
import json
import re
from pathlib import Path

from formulaci.schemas import Formula, Parsed, read_jsonl

HERE = Path(__file__).parent
CLASS_DEFAULT = {
    "special_algebra": dict(checkable=False, skip_reason="special_algebra"),
    "defining_equation_or_solve": dict(checkable=False, skip_reason="defining_equation"),
    "intentionally_false_in_context": dict(checkable=False, skip_reason="stated_false"),
    "confirmed_error": dict(checkable=True),
}
# per-id labels (from the reviewer's note) where the class alone does not say what is right
LABELS = {
    # i is the imaginary unit
    "wiki:en:12316:1381182218:135": dict(checkable=True, constants={"i": "I"}),
    "wiki:en:12316:1381182218:136": dict(checkable=True, constants={"i": "I"}),
    "wiki:en:12316:1381182218:140": dict(checkable=True, constants={"i": "I"}),
    "wiki:en:245560:1361311731:26": dict(checkable=True, constants={"i": "I"}),
    "wiki:en:4677:1377889688:129": dict(checkable=True, constants={"i": "I"}),
    "wiki:en:25804104:1379178075:426": dict(checkable=True, constants={"i": "I"}),
    # golden field: varphi is the golden ratio
    "wiki:en:80262208:1376111431:43": dict(checkable=True, constants={"phi": "GoldenRatio"}),
    "wiki:en:80262208:1376111431:44": dict(checkable=True, constants={"phi": "GoldenRatio"}),
    # improper-integral parameters must be positive
    "wiki:en:36423541:1336422728:28": dict(checkable=True, constants={"e": "E"}, domains={"a": "positive", "m": "positive_integer"}),
    # symbols the page fixes to specific values
    "wiki:en:25809:1381282197:146": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:41302121:1380738944:256": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:482471:1380575185:153": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:482471:1380575185:154": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:23601:1380390825:53": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:882902:1377844797:135": dict(checkable=False, skip_reason="named_constant"),
    "wiki:en:30367:1378578661:154": dict(checkable=False, skip_reason="definition"),
    # matrices / operators
    **{k: dict(checkable=False, skip_reason="matrix_or_vector") for k in [
        "wiki:en:29276:1367040217:108", "wiki:en:173997:1375616063:69", "wiki:en:285422:1368909113:107",
        "wiki:en:44135401:1324299460:39", "wiki:en:514534:1350723541:38", "wiki:en:672731:1380739424:17",
        "wiki:en:672731:1380739424:96"]},
    # index ranges
    **{k: dict(checkable=False, skip_reason="statement_not_identity") for k in [
        "wiki:en:26452:1345571927:372", "wiki:en:28479408:1365260495:72", "wiki:en:312877:1374766194:18",
        "wiki:en:324752:1361359420:61", "wiki:en:40087321:1350938227:12"]},
    # conditions written as inequalities
    **{k: dict(checkable=False, skip_reason="condition") for k in [
        "wiki:en:156533:1372897661:11", "wiki:en:180787:1381153688:103", "wiki:en:180787:1381153688:134",
        "wiki:en:180787:1381153688:56", "wiki:en:20556903:1378902473:2", "wiki:en:2091823:1380348958:56",
        "wiki:en:2091823:1380348958:58", "wiki:en:51438:1380346007:39", "wiki:en:51438:1378320581:39",
        "wiki:en:9891:1380489591:37"]},
    # true only under a relation stated in the prose (a^2+b^2=c^2, 4p^3+27q^2=0, ad-bc=±1, ...):
    # the right answer is a constraint the rules cannot extract, so skipping is the safe outcome
    **{k: dict(checkable=False, skip_reason="conditional_on_context") for k in [
        "wiki:en:180787:1381153688:37", "wiki:en:24172:1380816662:15", "wiki:en:19480890:1381118084:59",
        "wiki:en:491316:1379550108:52", "wiki:en:622053:1377937648:52", "wiki:en:53941:1379202452:38"]},
    # approximations: stay checkable with a tolerance hint, except a non-terminating approximation and units
    "wiki:en:105375:1370501651:158": dict(checkable=True),
    "wiki:en:17829294:1381187812:36": dict(checkable=False, skip_reason="approximation"),   # pi = 3927/1250
    "wiki:en:2336224:1364361992:4": dict(checkable=True),
    "wiki:en:577053:1374796707:27": dict(checkable=True),
    "wiki:en:72773869:1339494963:68": dict(checkable=False, skip_reason="approximation"),
    "wiki:en:81761:1376040312:1": dict(checkable=False, skip_reason="units"),
    # notation / convention
    "wiki:en:238686:1378219065:5": dict(checkable=False, skip_reason="special_algebra"),
    "wiki:en:8400:1376450880:9": dict(checkable=False, skip_reason="special_algebra"),
    "wiki:en:374220:1380733448:374": dict(checkable=False, skip_reason="notation_or_convention"),
    "wiki:en:99491:1379331466:211": dict(checkable=False, skip_reason="notation_or_convention"),
}
CLASSES = set(CLASS_DEFAULT) | {"wrong_domain_or_constant", "approximation_or_rounding", "notation_or_convention"}


def main(reviews="data/findings/reviews.jsonl", formulas="data/raw/formulas.jsonl", parsed="data/parsed/parsed.jsonl"):
    rows = [json.loads(l) for l in Path(reviews).read_text().splitlines() if l.strip()]
    cls = {}
    for r in rows:
        m = re.match(r"\[(\w+)\]", r["review"]["notes"])
        tag = "confirmed_error" if r["review"]["status"] == "confirmed_error" else (m.group(1) if m else None)
        if tag in CLASSES:
            cls[r["formula_id"]] = (tag, r["review"]["notes"])
    F = {f.formula_id: f for f in read_jsonl(formulas, Formula) if f.formula_id in cls}
    P = {}
    for p in read_jsonl(parsed, Parsed):
        if p.formula_id in cls:
            P.setdefault(p.formula_id, []).append(p)
    out = []
    for fid in sorted(cls):
        tag, note = cls[fid]
        label = LABELS.get(fid) or CLASS_DEFAULT.get(tag)
        if label is None:
            raise KeyError(f"no label for {fid} [{tag}]")
        exp = {"checkable": label["checkable"], "skip_reason": label.get("skip_reason"),
               "constants": label.get("constants", {}), "domains": label.get("domains", {}), "constraints": []}
        out.append({"case": f"{tag}:{fid}", "review_class": tag, "review_note": note[:300],
                    "formula": F[fid].model_dump(), "parsed": [p.model_dump() for p in P[fid]], "expect": exp,
                    "score_constants": "constants" in label})
    path = HERE / "review_cases.jsonl"
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in out))
    print(f"wrote {len(out)} cases to {path}")


if __name__ == "__main__":
    main()
