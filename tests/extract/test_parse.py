"""Extract stage: parser tests on synthetic snippets and real wikitext fixtures."""
import json
import re
from pathlib import Path

import pytest

from formulaci.extract.fetch import PageData
from formulaci.extract.parse import extract_formulas
from formulaci.extract.pipeline import page_to_formulas, page_url
from formulaci.schemas import Formula

FIX = Path(__file__).parent / "fixtures"
PAGES = ["gamma_function", "list_of_trigonometric_identities", "normal_distribution"]


def load(key: str) -> PageData:
    meta = json.loads((FIX / f"{key}.json").read_text())
    return PageData(page_id=meta["page_id"], title=meta["title"], revision_id=meta["revision_id"],
                    wikitext=(FIX / f"{key}.wikitext").read_text(), categories=meta["categories"])


def prose(s: str) -> str:
    """Context with inline formulas ($...$) and hidden-formula labels ([...]) removed."""
    s = re.sub(r"\$[^$]*\$", " ", s)
    return re.sub(r"\[[^\]]*\]$", " ", s)


# --- synthetic --------------------------------------------------------------------------------

def test_display_detection_rules():
    wt = ("Lead <math>a</math> text.\n"
          ":<math>b = c</math>\n"
          "::<math>d</math>\n"
          "* <math>e</math> in a bullet\n"
          "Inline then:<math>f</math>\n"
          '<math display="block">g</math>\n'
          ':<math display="inline">h</math>\n'
          "{{NumBlk|:|<math>i</math>|{{EquationRef|1}}}}\n"
          ":{{math|<math>j</math>}}\n"
          "{{math|x}} and {{tmath|k^2}}\n")
    fs, st = extract_formulas(wt)
    got = {f.latex: f.display for f in fs}
    assert got == {"a": False, "b = c": True, "d": True, "e": False, "f": False, "g": True, "h": False,
                   "i": True, "j": True, "k^2": False}
    assert [f.index for f in fs] == list(range(10))
    assert st.n_html_math == 1 and st.n_tmath == 1 and st.n_math == 9


def test_sections_chem_comments_and_hidden():
    wt = ("Lead <math>x_0</math>.\n"
          "== Properties ==\nText <math>x_1</math>.\n"
          "=== Derivative ===\n<!-- <math>ignored</math> -->Then <chem>H2O</chem> <ce>CO2</ce> "
          "<math chem>NaCl</math> <math></math> <math>x_2</math>.\n"
          "== Other ==\n{{Infobox foo|pdf=<math>x_3</math>}}Body.<ref>See <math>x_4</math></ref>\n"
          "[[File:a.png|thumb|Plot of <math>x_5</math>]]\n")
    fs, st = extract_formulas(wt)
    assert [f.latex for f in fs] == ["x_0", "x_1", "x_2", "x_3", "x_4", "x_5"]
    assert [f.section for f in fs] == ["", "Properties", "Properties > Derivative", "Other", "Other", "Other"]
    assert st.n_chem == 3 and st.n_empty == 1 and st.n_hidden == 3
    assert fs[3].context_before.endswith("[Infobox foo | pdf]")
    assert fs[4].context_before.endswith("[ref]")
    assert fs[5].context_before.endswith("[caption]")
    # hidden formulas and refs do not leak into prose
    assert "See" not in fs[2].context_after and "x_4" not in fs[2].context_after


def test_context_stripping():
    wt = ("The '''gamma function''' [[Function (mathematics)|function]] of {{mvar|z}} "
          "is defined<ref>{{cite book|title=Foo}}</ref> by {{math|''z'' > 0}}: "
          "{{Main|Other article}}&nbsp;see [https://example.org the site] and <math>\\Gamma(z)</math>"
          " where <math>z>0</math> holds.{{citation needed|date=2020}}\n")
    fs, _ = extract_formulas(wt)
    before, after = fs[0].context_before, fs[0].context_after
    assert before == "The gamma function function of z is defined by z > 0: see the site and"
    assert after == "where $z>0$ holds."


def test_numbered_and_text_templates_kept():
    wt = ("when {{math|1=m=n}}, the {{visible anchor|Euclidean norm}} of {{lang|fr|mot}} is <math>x</math> "
          "and {{mvar|2=ignored|1=y}} {{gaps|1|000}}.")
    fs, _ = extract_formulas(wt)
    assert fs[0].context_before == "when m=n, the Euclidean norm of mot is"
    assert fs[0].context_after == "and y 1 000."


def test_tmath_unescapes_pipes():
    fs, _ = extract_formulas("Norm {{tmath|1= \\{x {{!}} x {{=}} 1\\} }} end")
    assert fs[0].latex == "\\{x | x = 1\\}"


def test_context_length_bounded():
    wt = ("word " * 500) + "<math>x</math>" + (" word" * 500)
    fs, _ = extract_formulas(wt)
    assert 300 <= len(fs[0].context_before) <= 400
    assert 300 <= len(fs[0].context_after) <= 400


# --- real fixtures ----------------------------------------------------------------------------

def naive_math_count(wt: str) -> int:
    wt = re.sub(r"<!--.*?-->", "", wt, flags=re.S)
    return len(re.findall(r"<math[\s>]", wt)) - len(re.findall(r"<math[^>]*\bchem\b", wt))


@pytest.mark.parametrize("key,n_math,n_tmath,n_display", [
    ("gamma_function", 306, 130, 130),
    ("list_of_trigonometric_identities", 512, 3, 109),
    ("normal_distribution", 401, 177, 96),
])
def test_fixture_counts(key, n_math, n_tmath, n_display):
    page = load(key)
    fs, st = extract_formulas(page.wikitext)
    assert st.n_math == n_math == naive_math_count(page.wikitext)
    assert st.n_tmath == n_tmath == len(re.findall(r"\{\{\s*tmath\s*\|", page.wikitext))
    assert st.n_display == n_display
    # display count agrees with the raw markup: display=block tags plus `:<math>` lines
    lines = re.findall(r"^[:*#]*:\s*<math(?![^>]*display)", page.wikitext, flags=re.M)
    blocks = re.findall(r"<math[^>]*display\s*=\s*\"?block", page.wikitext)
    assert st.n_display == len(lines) + len(blocks)
    assert len(fs) == n_math + n_tmath and [f.index for f in fs] == list(range(len(fs)))


@pytest.mark.parametrize("key", PAGES)
def test_fixture_contexts_are_plain_text(key):
    fs, _ = extract_formulas(load(key).wikitext)
    for f in fs:
        for side in (f.context_before, f.context_after):
            p = prose(side)
            for junk in ("[[", "]]", "{{", "}}", "<ref", "</", "'''", "<!--", "&nbsp;", "<math"):
                assert junk not in p, (f.index, junk, side)
            assert len(side) <= 400 + 80  # + optional label
    with_ctx = sum(bool(f.context_before or f.context_after) for f in fs)
    assert with_ctx == len(fs)


def test_fixture_normal_distribution_specifics():
    fs, _ = extract_formulas(load("normal_distribution").wikitext)
    pdf = next(f for f in fs if f.latex.strip().startswith("f(x) = \\frac{1}{\\sqrt{2\\pi\\sigma^2}}"))
    assert pdf.display and pdf.section == ""
    std = [f for f in fs if f.section == "Definitions > Standard normal distribution"]
    assert any(f.display and f.latex.startswith("\\varphi(z) = \\frac{e^{-z^2/2}}") for f in std)
    infobox = [f for f in fs if "[infobox probability distribution |" in f.context_before.lower()]
    assert len(infobox) >= 8 and infobox[0].index == 0
    assert any("normal distribution or Gaussian distribution" in f.context_after for f in infobox)


def test_fixture_trig_specifics():
    fs, _ = extract_formulas(load("list_of_trigonometric_identities").wikitext)
    pyth = next(f for f in fs if f.latex.strip() == "\\sin^2\\theta + \\cos^2\\theta = 1,")
    assert pyth.display and pyth.section == "Pythagorean identities"
    assert pyth.context_before.endswith("Pythagorean identity:")
    jac = next(f for f in fs if f.latex.strip().startswith("\\cos(t \\sin x) = J_0(t)"))
    assert jac.display  # `: <math>` line
    dbl = [f for f in fs if f.section.endswith("Double-angle formulae")]
    assert len(dbl) == 17 and not any(f.display for f in dbl)  # table cells are inline


def test_fixture_gamma_specifics():
    fs, _ = extract_formulas(load("gamma_function").wikitext)
    lead_def = next(f for f in fs if f.display)
    assert lead_def.section == "" and "\\int_0^\\infty t^{z-1} e^{-t}" in lead_def.latex
    assert "Re(z) > 0" in lead_def.latex
    secs = {f.section for f in fs}
    assert "Definition > Main definition" in secs and "Properties > Residues" in secs


def test_page_to_formulas_records():
    page = load("gamma_function")
    recs, st = page_to_formulas(page)
    assert all(isinstance(r, Formula) for r in recs)
    r = recs[5]
    assert r.formula_id == f"wiki:en:{page.page_id}:{page.revision_id}:5"
    assert r.url == "https://en.wikipedia.org/wiki/Gamma_function"
    assert r.page_categories == page.categories and r.page_categories
    assert Formula.model_validate_json(r.model_dump_json()) == r
    assert page_url("Bayes' theorem") == "https://en.wikipedia.org/wiki/Bayes'_theorem"
    assert page_url("1 − 2 + 3 − 4 + ⋯").startswith("https://en.wikipedia.org/wiki/1_%E2%88%92_2")
