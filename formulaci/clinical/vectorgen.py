"""Generate ``vectors.json``: reference input/output pairs for every formula.

The expected values are computed here by a *second, independent* transcription of each primary
source equation, in mpmath at 40 significant digits, with its own unit handling. It deliberately
does not import ``formulas.py``: the tests then check that two transcriptions of the paper agree,
which is a real check rather than a tautology. Nothing here is copied from a calculator website.

Run: ``uv run formulaci clinical vectors --regenerate``
"""
from __future__ import annotations

import json
from pathlib import Path

import mpmath as mp

mp.mp.dps = 40
VECTORS_PATH = Path(__file__).with_name("vectors.json")

M = mp.mpf
# unit factors, written out again from the primary definitions (see formulas.py for citations)
UMOL_PER_MGDL = M("88.4")      # creatinine
IN_CM = M("2.54")
LB_KG = M("0.45359237")
GLU = M("18.016")
CA = M("4.008")
CHOL = M("38.67")
TRIG = M("88.57")


def _to_canon(name, v, unit):
    v = M(str(v))
    if unit is None:
        return v
    table = {
        ("scr", "umol/L"): 1 / UMOL_PER_MGDL, ("ucr", "umol/L"): 1 / UMOL_PER_MGDL,
        ("pcr", "umol/L"): 1 / UMOL_PER_MGDL, ("ucr", "mg/L"): M("0.1"),
        ("height", "in"): IN_CM, ("height", "m"): M(100),
        ("weight", "lb"): LB_KG, ("glucose", "mmol/L"): GLU, ("ca", "mmol/L"): CA,
        ("albumin", "g/L"): M("0.1"), ("tc", "mmol/L"): CHOL, ("hdl", "mmol/L"): CHOL,
        ("tg", "mmol/L"): TRIG, ("qt", "s"): M(1000),
    }
    return v * table[(name, unit)]


def _cases(key, f, rows):
    """rows: (inputs, units|None, tags, note)."""
    out = []
    for inputs, units, tags, note in rows:
        canon = {k: (_to_canon(k, v, (units or {}).get(k)) if isinstance(v, (int, float)) and
                     not isinstance(v, bool) else v) for k, v in inputs.items()}
        out.append({"formula": key, "inputs": inputs, "units": units or {},
                    "expected": float(f(**canon)), "tags": tags, "note": note})
    return out


def _fem(s):
    return s == "female"


# --- independent transcriptions (mpmath) -----------------------------------------------------
def ckd21(scr, age, sex):
    k, a = (M("0.7"), M("-0.241")) if _fem(sex) else (M("0.9"), M("-0.302"))
    r = scr / k
    return (142 * min(r, 1) ** a * max(r, 1) ** M("-1.200") * M("0.9938") ** age
            * (M("1.012") if _fem(sex) else 1))


def ckd21cys(scr, scys, age, sex):
    k, a = (M("0.7"), M("-0.219")) if _fem(sex) else (M("0.9"), M("-0.144"))
    r, c = scr / k, scys / M("0.8")
    return (135 * min(r, 1) ** a * max(r, 1) ** M("-0.544") * min(c, 1) ** M("-0.323")
            * max(c, 1) ** M("-0.778") * M("0.9961") ** age * (M("0.963") if _fem(sex) else 1))


def ckd09(scr, age, sex, black):
    k, a = (M("0.7"), M("-0.329")) if _fem(sex) else (M("0.9"), M("-0.411"))
    r = scr / k
    return (141 * min(r, 1) ** a * max(r, 1) ** M("-1.209") * M("0.993") ** age
            * (M("1.018") if _fem(sex) else 1) * (M("1.159") if black else 1))


def mdrd(c):
    def f(scr, age, sex, black):
        return (c * scr ** M("-1.154") * age ** M("-0.203") * (M("0.742") if _fem(sex) else 1)
                * (M("1.212") if black else 1))
    return f


def cg(scr, age, sex, weight):
    return (140 - age) * weight / (72 * scr) * (M("0.85") if _fem(sex) else 1)


def schwartz(scr, height):
    return M("0.413") * height / scr


def bmi(weight, height):
    return weight / (height / 100) ** 2


def mosteller(weight, height):
    return mp.sqrt(height * weight / 3600)


def dubois(weight, height):
    return weight ** M("0.425") * height ** M("0.725") * M("71.84") / 10000


def haycock(weight, height):
    return M("0.024265") * weight ** M("0.5378") * height ** M("0.3964")


def devine(height, sex):
    return (M("45.5") if _fem(sex) else 50) + M("2.3") * (height / IN_CM - 60)


def bazett(qt, hr):
    return qt / mp.sqrt(60 / hr)


def fridericia(qt, hr):
    return qt / mp.cbrt(60 / hr)


def framingham(qt, hr):
    return (qt / 1000 + M("0.154") * (1 - 60 / hr)) * 1000


def hodges(qt, hr):
    return qt + M("1.75") * (hr - 60)


def map_(sbp, dbp):
    return (2 * dbp + sbp) / 3


def ag(na, cl, hco3):
    return na - cl - hco3


def agk(na, k, cl, hco3):
    return na + k - cl - hco3


def corr_ca(ca, albumin):
    return ca + M("0.8") * (4 - albumin)


def payne73(ca, albumin):
    return ca - albumin + 4


def na_katz(na, glucose):
    return na + M("0.016") * (glucose - 100)


def na_hillier(na, glucose):
    return na + M("0.024") * (glucose - 100)


def fena(una, pna, ucr, pcr):
    return 100 * una * pcr / (pna * ucr)


def winters(hco3):
    return M("1.5") * hco3 + 8


def friedewald(tc, hdl, tg):
    return tc - hdl - tg / 5


def sampson(tc, hdl, tg):
    n = tc - hdl
    return (tc / M("0.948") - hdl / M("0.971")
            - (tg / M("8.56") + tg * n / 2140 - tg ** 2 / 16100) - M("9.44"))


def parkland(weight, tbsa):
    return 4 * weight * tbsa


def hs_day(weight):
    w = weight
    if w <= 10:
        return 100 * w
    if w <= 20:
        return 1000 + 50 * (w - 10)
    return 1500 + 20 * (w - 20)


def hs_hour(weight):
    w = weight
    if w <= 10:
        return 4 * w
    if w <= 20:
        return 40 + 2 * (w - 10)
    return 60 + (w - 20)


def mh_factory():
    path = Path(__file__).with_name("martin_hopkins_table.json")
    if not path.exists():
        return None
    t = json.loads(path.read_text())

    def idx(v, bounds):
        for i, (lo, hi) in enumerate(bounds):
            if (lo is None or v >= lo) and (hi is None or v < hi):
                return i
        raise ValueError(v)

    def f(tc, hdl, tg):
        fac = M(str(t["factors"][idx(float(tg), t["tg_bounds"])][idx(float(tc - hdl), t["nonhdl_bounds"])]))
        return tc - hdl - tg / fac
    return f


F, Mx = "female", "male"
T, U, E = "typical", "unit", "edge"


def build() -> list[dict]:
    v: list[dict] = []
    v += _cases("egfr_ckd_epi_cr@2021", ckd21, [
        ({"scr": 1.0, "age": 50, "sex": Mx}, None, [T], "male, above kappa"),
        ({"scr": 0.8, "age": 60, "sex": F}, None, [T], "female, above kappa"),
        ({"scr": 0.6, "age": 40, "sex": F}, None, [T, E], "female, below kappa (alpha branch)"),
        ({"scr": 0.9, "age": 70, "sex": Mx}, None, [E], "male, Scr exactly at kappa"),
        ({"scr": 0.7, "age": 18, "sex": F}, None, [E], "female, Scr at kappa, youngest adult"),
        ({"scr": 4.5, "age": 75, "sex": Mx}, None, [T], "advanced CKD"),
        ({"scr": 106.1, "age": 50, "sex": Mx}, {"scr": "umol/L"}, [U, T], "µmol/L input"),
        ({"scr": 70.72, "age": 60, "sex": F}, {"scr": "umol/L"}, [U], "µmol/L, female"),
    ])
    v += _cases("egfr_ckd_epi_crcys@2021", ckd21cys, [
        ({"scr": 1.0, "scys": 1.0, "age": 50, "sex": Mx}, None, [T], "both above knots"),
        ({"scr": 0.6, "scys": 0.7, "age": 40, "sex": F}, None, [T, E], "both below knots"),
        ({"scr": 0.9, "scys": 0.8, "age": 65, "sex": Mx}, None, [E], "both exactly at knots"),
        ({"scr": 1.4, "scys": 1.6, "age": 72, "sex": F}, None, [T], "CKD, female"),
        ({"scr": 0.5, "scys": 2.0, "age": 30, "sex": Mx}, None, [E], "discordant markers"),
        ({"scr": 132.6, "scys": 1.2, "age": 55, "sex": Mx}, {"scr": "umol/L"}, [U], "µmol/L"),
    ])
    v += _cases("egfr_ckd_epi_cr@2009", ckd09, [
        ({"scr": 1.0, "age": 50, "sex": Mx, "black": False}, None, [T], "non-black male"),
        ({"scr": 1.0, "age": 50, "sex": Mx, "black": True}, None, [T], "race coefficient 1.159"),
        ({"scr": 0.6, "age": 40, "sex": F, "black": False}, None, [E], "female below kappa"),
        ({"scr": 0.8, "age": 60, "sex": F, "black": True}, None, [T], "female, black"),
        ({"scr": 0.9, "age": 70, "sex": Mx, "black": False}, None, [E], "at kappa"),
        ({"scr": 176.8, "age": 65, "sex": F, "black": False}, {"scr": "umol/L"}, [U], "µmol/L"),
    ])
    for c in ("175", "186"):
        v += _cases(f"egfr_mdrd@{c}", mdrd(M(c)), [
            ({"scr": 1.0, "age": 50, "sex": Mx, "black": False}, None, [T], ""),
            ({"scr": 1.0, "age": 50, "sex": F, "black": False}, None, [T], "female 0.742"),
            ({"scr": 1.0, "age": 50, "sex": Mx, "black": True}, None, [T], "black 1.212"),
            ({"scr": 2.5, "age": 70, "sex": F, "black": True}, None, [T], ""),
            ({"scr": 0.4, "age": 19, "sex": Mx, "black": False}, None, [E], "very low Scr"),
            ({"scr": 88.4, "age": 60, "sex": Mx, "black": False}, {"scr": "umol/L"}, [U], "1 mg/dL"),
        ])
    v += _cases("crcl_cockcroft_gault@1976", cg, [
        ({"scr": 1.0, "age": 40, "sex": Mx, "weight": 72}, None, [T], "Ccr = 100 exactly"),
        ({"scr": 1.0, "age": 40, "sex": F, "weight": 72}, None, [T], "female 0.85"),
        ({"scr": 1.5, "age": 80, "sex": Mx, "weight": 60}, None, [T], "elderly"),
        ({"scr": 0.8, "age": 30, "sex": F, "weight": 154}, {"weight": "lb"}, [U], "lb input"),
        ({"scr": 132.6, "age": 65, "sex": Mx, "weight": 80}, {"scr": "umol/L"}, [U], "µmol/L"),
        ({"scr": 3.0, "age": 139, "sex": Mx, "weight": 70}, None, [E], "age near 140"),
    ])
    v += _cases("egfr_schwartz_bedside@2009", schwartz, [
        ({"scr": 0.5, "height": 120}, None, [T], "child"),
        ({"scr": 0.3, "height": 75}, None, [T], "toddler"),
        ({"scr": 1.2, "height": 150}, None, [T], "CKD"),
        ({"scr": 0.4, "height": 47.24}, {"height": "in"}, [U], "height in inches"),
        ({"scr": 44.2, "height": 130}, {"scr": "umol/L"}, [U], "µmol/L"),
        ({"scr": 0.1, "height": 50}, None, [E], "very low Scr"),
    ])
    hw = [
        ({"weight": 70, "height": 175}, None, [T], "adult"),
        ({"weight": 50, "height": 160}, None, [T], ""),
        ({"weight": 3.5, "height": 50}, None, [E], "newborn"),
        ({"weight": 150, "height": 190}, None, [T], ""),
        ({"weight": 154.3, "height": 68.9}, {"weight": "lb", "height": "in"}, [U], "imperial"),
        ({"weight": 80, "height": 1.8}, {"height": "m"}, [U], "height in metres"),
    ]
    v += _cases("bmi@quetelet", bmi, hw)
    v += _cases("bsa_mosteller@1987", mosteller, hw)
    v += _cases("bsa_dubois@1916", dubois, hw)
    v += _cases("bsa_haycock@1978", haycock, hw)
    v += _cases("ibw_devine@1974", devine, [
        ({"height": 152.4, "sex": Mx}, None, [E], "exactly 60 in"),
        ({"height": 152.4, "sex": F}, None, [E], "exactly 60 in"),
        ({"height": 180, "sex": Mx}, None, [T], ""),
        ({"height": 165, "sex": F}, None, [T], ""),
        ({"height": 70, "sex": Mx}, {"height": "in"}, [U], "inches"),
        ({"height": 140, "sex": F}, None, [E], "below 60 in (extrapolated)"),
    ])
    qt = [
        ({"qt": 400, "hr": 60}, None, [E], "HR 60 -> RR 1 s, QTc = QT"),
        ({"qt": 360, "hr": 90}, None, [T], ""),
        ({"qt": 440, "hr": 50}, None, [T], "bradycardia"),
        ({"qt": 320, "hr": 120}, None, [T], "tachycardia"),
        ({"qt": 0.38, "hr": 75}, {"qt": "s"}, [U], "QT in seconds"),
        ({"qt": 300, "hr": 150}, None, [E], "very fast"),
    ]
    v += _cases("qtc_bazett@1920", bazett, qt)
    v += _cases("qtc_fridericia@1920", fridericia, qt)
    v += _cases("qtc_framingham@1992", framingham, qt)
    v += _cases("qtc_hodges@1983", hodges, qt)
    v += _cases("map@standard", map_, [
        ({"sbp": 120, "dbp": 80}, None, [T], ""),
        ({"sbp": 90, "dbp": 60}, None, [T], ""),
        ({"sbp": 180, "dbp": 110}, None, [T], ""),
        ({"sbp": 100, "dbp": 100}, None, [E], "zero pulse pressure"),
        ({"sbp": 70, "dbp": 30}, None, [E], "wide pulse pressure, hypotension"),
    ])
    v += _cases("anion_gap@no-k", ag, [
        ({"na": 140, "cl": 104, "hco3": 24}, None, [T], ""),
        ({"na": 135, "cl": 95, "hco3": 10}, None, [T], "high AG"),
        ({"na": 150, "cl": 120, "hco3": 26}, None, [T], ""),
        ({"na": 130, "cl": 110, "hco3": 22}, None, [E], "negative gap"),
        ({"na": 138.5, "cl": 101.2, "hco3": 23.7}, None, [E], "decimals"),
    ])
    v += _cases("anion_gap@with-k", agk, [
        ({"na": 140, "k": 4, "cl": 104, "hco3": 24}, None, [T], ""),
        ({"na": 135, "k": 5.5, "cl": 95, "hco3": 10}, None, [T], ""),
        ({"na": 150, "k": 3, "cl": 120, "hco3": 26}, None, [T], ""),
        ({"na": 130, "k": 2.5, "cl": 110, "hco3": 22}, None, [E], ""),
        ({"na": 138.5, "k": 4.2, "cl": 101.2, "hco3": 23.7}, None, [E], "decimals"),
    ])
    ca_rows = [
        ({"ca": 8.0, "albumin": 2.0}, None, [T], "hypoalbuminaemia"),
        ({"ca": 9.5, "albumin": 4.0}, None, [E], "albumin = 4: no correction"),
        ({"ca": 10.0, "albumin": 5.0}, None, [E], "high albumin: corrected downward"),
        ({"ca": 7.2, "albumin": 1.5}, None, [T], ""),
        ({"ca": 2.0, "albumin": 25}, {"ca": "mmol/L", "albumin": "g/L"}, [U], "SI inputs"),
    ]
    v += _cases("calcium_corrected@0.8", corr_ca, ca_rows)
    v += _cases("calcium_corrected@payne-1973", payne73, ca_rows)
    v += _cases("sodium_corrected@katz", na_katz, [
        ({"na": 130, "glucose": 600}, None, [T], ""),
        ({"na": 140, "glucose": 100}, None, [E], "glucose 100: no correction"),
        ({"na": 125, "glucose": 1000}, None, [T], ""),
        ({"na": 135, "glucose": 80}, None, [E], "glucose below 100"),
        ({"na": 128, "glucose": 30}, {"glucose": "mmol/L"}, [U], "glucose mmol/L"),
    ])
    v += _cases("sodium_corrected@hillier", na_hillier, [
        ({"na": 130, "glucose": 600}, None, [T], ""),
        ({"na": 140, "glucose": 100}, None, [E], "glucose 100: no correction"),
        ({"na": 125, "glucose": 1000}, None, [T], ""),
        ({"na": 135, "glucose": 80}, None, [E], "glucose below 100"),
        ({"na": 128, "glucose": 30}, {"glucose": "mmol/L"}, [U], "glucose mmol/L"),
    ])
    v += _cases("fena@espinel", fena, [
        ({"una": 20, "pna": 140, "ucr": 100, "pcr": 1.0}, None, [T], "prerenal range"),
        ({"una": 60, "pna": 135, "ucr": 40, "pcr": 3.0}, None, [T], "ATN range"),
        ({"una": 10, "pna": 140, "ucr": 150, "pcr": 1.4}, None, [T], ""),
        ({"una": 40, "pna": 140, "ucr": 8840, "pcr": 176.8},
         {"ucr": "umol/L", "pcr": "umol/L"}, [U], "both µmol/L"),
        ({"una": 40, "pna": 140, "ucr": 80, "pcr": 176.8}, {"pcr": "umol/L"}, [U, E],
         "mixed units: urine mg/dL, plasma µmol/L"),
    ])
    v += _cases("winters@1967", winters, [
        ({"hco3": 12}, None, [T], ""), ({"hco3": 24}, None, [E], "normal HCO3"),
        ({"hco3": 5}, None, [E], "severe acidosis"), ({"hco3": 18}, None, [T], ""),
        ({"hco3": 8.5}, None, [T], "decimal"),
    ])
    lip = [
        ({"tc": 200, "hdl": 50, "tg": 150}, None, [T], ""),
        ({"tc": 180, "hdl": 60, "tg": 100}, None, [T], ""),
        ({"tc": 250, "hdl": 40, "tg": 300}, None, [T], ""),
        ({"tc": 160, "hdl": 45, "tg": 80}, None, [T], ""),
        ({"tc": 5.2, "hdl": 1.3, "tg": 1.7}, {"tc": "mmol/L", "hdl": "mmol/L", "tg": "mmol/L"},
         [U], "SI inputs"),
        ({"tc": 140, "hdl": 70, "tg": 399}, None, [E], "TG near Friedewald limit"),
    ]
    v += _cases("ldl_friedewald@1972", friedewald, lip)
    v += _cases("ldl_sampson@2020", sampson, lip)
    mh = mh_factory()
    if mh is not None:
        v += _cases("ldl_martin_hopkins@2013", mh, lip)
    v += _cases("parkland@1968", parkland, [
        ({"weight": 70, "tbsa": 20}, None, [T], ""), ({"weight": 100, "tbsa": 50}, None, [T], ""),
        ({"weight": 20, "tbsa": 15}, None, [T], "child"),
        ({"weight": 176.4, "tbsa": 30}, {"weight": "lb"}, [U], "lb"),
        ({"weight": 70, "tbsa": 0}, None, [E], "no burn"),
    ])
    v += _cases("holliday_segar@1957", hs_day, [
        ({"weight": 5}, None, [T], ""), ({"weight": 10}, None, [E], "first breakpoint"),
        ({"weight": 15}, None, [T], ""), ({"weight": 20}, None, [E], "second breakpoint"),
        ({"weight": 35}, None, [T], ""), ({"weight": 44.1}, {"weight": "lb"}, [U], "lb"),
    ])
    v += _cases("holliday_segar_hourly@4-2-1", hs_hour, [
        ({"weight": 5}, None, [T], ""), ({"weight": 10}, None, [E], "first breakpoint"),
        ({"weight": 15}, None, [T], ""), ({"weight": 20}, None, [E], "second breakpoint"),
        ({"weight": 70}, None, [T], "adult"), ({"weight": 44.1}, {"weight": "lb"}, [U], "lb"),
    ])
    return v


def write(path: Path = VECTORS_PATH) -> int:
    vecs = build()
    payload = {
        "description": "Reference vectors computed by an independent mpmath (40 digits) "
                       "transcription of each primary-source equation; see vectorgen.py. "
                       "Inputs are in `units` where given, else the formula's canonical units.",
        "vectors": vecs,
    }
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    return len(vecs)


if __name__ == "__main__":
    print(write())
