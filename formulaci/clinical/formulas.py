"""Reference implementations of the formulas behind common online clinical calculators.

Every function is a direct transcription of the equation in its primary publication. Inputs are
in the canonical units declared in ``inputs=`` of the ``@formula`` registration; use
:func:`evaluate` to pass other units (it converts with the factors in :data:`CONVERSIONS`).
Outputs are unrounded floats. Registry keys are ``"<name>@<version>"``.

Nothing here is medical advice; these are test oracles for auditing calculator software.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------------------------
# Conversion factors, as "multiply a value in <unit> by this to get the canonical unit".
#
# Creatinine: molar mass 113.12 g/mol -> 1 mg/dL = 10 mg/L / 113.12 g/mol = 88.40 µmol/L.
#   KDIGO 2012 CKD guideline (Kidney Int Suppl 2013;3:1-150, doi:10.1038/kisup.2012.73) uses 88.4.
# Glucose: molar mass 180.16 g/mol -> 1 mmol/L = 18.016 mg/dL.
# Calcium: molar mass 40.078 g/mol -> 1 mmol/L = 4.008 mg/dL.
# Cholesterol: molar mass 386.65 g/mol -> 1 mmol/L = 38.67 mg/dL.
# Triglyceride (as triolein, 885.4 g/mol) -> 1 mmol/L = 88.57 mg/dL (conventional factor).
#   Laboratory SI conversion factors as tabulated in the AMA Manual of Style, 11th ed., SI units
#   table (Young DS); molar masses from IUPAC standard atomic weights.
# Length/mass: 1 in = 2.54 cm and 1 lb = 0.45359237 kg exactly (International Yard and Pound
#   Agreement, 1959; NIST SP 811 Appendix B).
CREATININE_UMOL_PER_MG_DL = 88.4
GLUCOSE_MG_DL_PER_MMOL = 18.016
CALCIUM_MG_DL_PER_MMOL = 4.008
CHOLESTEROL_MG_DL_PER_MMOL = 38.67
TRIGLYCERIDE_MG_DL_PER_MMOL = 88.57
CM_PER_IN = 2.54
KG_PER_LB = 0.45359237

# quantity -> {unit: factor_to_canonical}; the canonical unit has factor 1.
CONVERSIONS: dict[str, dict[str, float]] = {
    "creatinine": {"mg/dL": 1.0, "umol/L": 1 / CREATININE_UMOL_PER_MG_DL,
                   "µmol/L": 1 / CREATININE_UMOL_PER_MG_DL, "mg/L": 0.1},
    "cystatin": {"mg/L": 1.0},
    "length": {"cm": 1.0, "m": 100.0, "in": CM_PER_IN, "mm": 0.1},
    "mass": {"kg": 1.0, "lb": KG_PER_LB, "g": 0.001},
    "glucose": {"mg/dL": 1.0, "mmol/L": GLUCOSE_MG_DL_PER_MMOL},
    "calcium": {"mg/dL": 1.0, "mmol/L": CALCIUM_MG_DL_PER_MMOL, "mEq/L": CALCIUM_MG_DL_PER_MMOL / 2},
    "albumin": {"g/dL": 1.0, "g/L": 0.1},
    "cholesterol": {"mg/dL": 1.0, "mmol/L": CHOLESTEROL_MG_DL_PER_MMOL},
    "triglyceride": {"mg/dL": 1.0, "mmol/L": TRIGLYCERIDE_MG_DL_PER_MMOL},
    "electrolyte": {"mEq/L": 1.0, "mmol/L": 1.0},
    "time_ms": {"ms": 1.0, "s": 1000.0},
    "rate": {"bpm": 1.0},
    "pressure": {"mmHg": 1.0, "kPa": 7.50061683},
    "age": {"years": 1.0},
    "percent": {"%": 1.0},
}

# input name -> quantity. Inputs not listed (sex, black) are categorical.
QUANTITY: dict[str, str] = {
    "scr": "creatinine", "ucr": "creatinine", "pcr": "creatinine", "scys": "cystatin",
    "height": "length", "weight": "mass", "glucose": "glucose", "ca": "calcium",
    "albumin": "albumin", "tc": "cholesterol", "hdl": "cholesterol", "tg": "triglyceride",
    "na": "electrolyte", "k": "electrolyte", "cl": "electrolyte", "hco3": "electrolyte",
    "una": "electrolyte", "pna": "electrolyte", "qt": "time_ms", "hr": "rate",
    "sbp": "pressure", "dbp": "pressure", "age": "age", "tbsa": "percent",
}


def convert(name: str, value: float, unit: str) -> float:
    """Convert input ``name`` from ``unit`` to its canonical unit."""
    table = CONVERSIONS[QUANTITY[name]]
    if unit not in table:
        raise ValueError(f"unknown unit {unit!r} for {name} (known: {sorted(table)})")
    return value * table[unit]


# ---------------------------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class FormulaSpec:
    key: str
    name: str
    version: str
    citation: str
    doi: str | None
    inputs: dict[str, str]  # input name -> canonical unit ("female|male", "bool" for categorical)
    output_unit: str
    func: Callable[..., float] = field(repr=False)

    @property
    def doc(self) -> str:
        return (self.func.__doc__ or "").strip()


REGISTRY: dict[str, FormulaSpec] = {}


def formula(name: str, version: str, citation: str, *, doi: str | None = None,
            inputs: dict[str, str], output_unit: str):
    """Register a reference implementation under ``name@version``."""
    def deco(fn):
        key = f"{name}@{version}"
        if key in REGISTRY:
            raise ValueError(f"duplicate formula {key}")
        REGISTRY[key] = FormulaSpec(key, name, version, citation, doi, dict(inputs), output_unit, fn)
        return fn
    return deco


def evaluate(key: str, inputs: dict, units: dict[str, str] | None = None) -> float:
    """Evaluate formula ``key`` on ``inputs``; ``units`` maps input name -> unit when not canonical."""
    spec = REGISTRY[key]
    units = units or {}
    args = {}
    for name in spec.inputs:
        if name not in inputs:
            raise KeyError(f"{key}: missing input {name!r}")
        v = inputs[name]
        if name in units:
            v = convert(name, float(v), units[name])
        args[name] = v
    return spec.func(**args)


def _female(sex: str) -> bool:
    s = str(sex).strip().lower()
    if s in ("female", "f", "woman"):
        return True
    if s in ("male", "m", "man"):
        return False
    raise ValueError(f"sex must be 'female' or 'male', got {sex!r}")


SEX = "female|male"

# ---------------------------------------------------------------------------------------------
# Kidney function
# ---------------------------------------------------------------------------------------------
INKER_2021 = ("Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and Cystatin C-Based "
              "Equations to Estimate GFR without Race. N Engl J Med 2021;385:1737-1749.")


@formula("egfr_ckd_epi_cr", "2021", INKER_2021, doi="10.1056/NEJMoa2102953",
         inputs={"scr": "mg/dL", "age": "years", "sex": SEX}, output_unit="mL/min/1.73m²")
def egfr_ckd_epi_cr_2021(scr: float, age: float, sex: str) -> float:
    """CKD-EPI 2021 creatinine equation (race-free).

    eGFRcr = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−1.200 × 0.9938^Age × 1.012 [if female]
    κ = 0.7 (female) or 0.9 (male); α = −0.241 (female) or −0.302 (male); Scr in mg/dL.

    Inker LA et al. N Engl J Med 2021;385:1737-1749. doi:10.1056/NEJMoa2102953
    """
    f = _female(sex)
    k, a = (0.7, -0.241) if f else (0.9, -0.302)
    r = scr / k
    return 142 * min(r, 1) ** a * max(r, 1) ** -1.200 * 0.9938 ** age * (1.012 if f else 1.0)


@formula("egfr_ckd_epi_crcys", "2021", INKER_2021, doi="10.1056/NEJMoa2102953",
         inputs={"scr": "mg/dL", "scys": "mg/L", "age": "years", "sex": SEX},
         output_unit="mL/min/1.73m²")
def egfr_ckd_epi_crcys_2021(scr: float, scys: float, age: float, sex: str) -> float:
    """CKD-EPI 2021 creatinine–cystatin C equation (race-free).

    eGFRcr-cys = 135 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−0.544 × min(Scys/0.8, 1)^−0.323
                 × max(Scys/0.8, 1)^−0.778 × 0.9961^Age × 0.963 [if female]
    κ = 0.7 (female) or 0.9 (male); α = −0.219 (female) or −0.144 (male); Scr mg/dL, Scys mg/L.

    Inker LA et al. N Engl J Med 2021;385:1737-1749. doi:10.1056/NEJMoa2102953
    """
    f = _female(sex)
    k, a = (0.7, -0.219) if f else (0.9, -0.144)
    r, c = scr / k, scys / 0.8
    return (135 * min(r, 1) ** a * max(r, 1) ** -0.544 * min(c, 1) ** -0.323
            * max(c, 1) ** -0.778 * 0.9961 ** age * (0.963 if f else 1.0))


@formula("egfr_ckd_epi_cr", "2009",
         "Levey AS, Stevens LA, Schmid CH, et al. A new equation to estimate glomerular "
         "filtration rate. Ann Intern Med 2009;150:604-612.",
         doi="10.7326/0003-4819-150-9-200905050-00006",
         inputs={"scr": "mg/dL", "age": "years", "sex": SEX, "black": "bool"},
         output_unit="mL/min/1.73m²")
def egfr_ckd_epi_cr_2009(scr: float, age: float, sex: str, black: bool) -> float:
    """CKD-EPI 2009 creatinine equation (with race coefficient; superseded by the 2021 equation).

    GFR = 141 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−1.209 × 0.993^Age × 1.018 [if female]
          × 1.159 [if black]
    κ = 0.7 (female) or 0.9 (male); α = −0.329 (female) or −0.411 (male); Scr in mg/dL.

    Levey AS et al. Ann Intern Med 2009;150:604-612. doi:10.7326/0003-4819-150-9-200905050-00006
    Registered so the audit can recognise sites that still compute it.
    """
    f = _female(sex)
    k, a = (0.7, -0.329) if f else (0.9, -0.411)
    r = scr / k
    return (141 * min(r, 1) ** a * max(r, 1) ** -1.209 * 0.993 ** age
            * (1.018 if f else 1.0) * (1.159 if black else 1.0))


@formula("egfr_mdrd", "175",
         "Levey AS, Coresh J, Greene T, et al. Using standardized serum creatinine values in the "
         "modification of diet in renal disease study equation for estimating glomerular "
         "filtration rate. Ann Intern Med 2006;145:247-254.",
         doi="10.7326/0003-4819-145-4-200608150-00004",
         inputs={"scr": "mg/dL", "age": "years", "sex": SEX, "black": "bool"},
         output_unit="mL/min/1.73m²")
def egfr_mdrd_175(scr: float, age: float, sex: str, black: bool) -> float:
    """MDRD 4-variable equation re-expressed for IDMS-traceable creatinine.

    GFR = 175 × Scr^−1.154 × Age^−0.203 × 0.742 [if female] × 1.212 [if African American]
    Scr in mg/dL (IDMS-standardised).

    Levey AS et al. Ann Intern Med 2006;145:247-254. doi:10.7326/0003-4819-145-4-200608150-00004
    """
    return (175 * scr ** -1.154 * age ** -0.203 * (0.742 if _female(sex) else 1.0)
            * (1.212 if black else 1.0))


@formula("egfr_mdrd", "186",
         "Levey AS, Greene T, Kusek JW, Beck GJ. A simplified equation to predict glomerular "
         "filtration rate from serum creatinine [abstract]. J Am Soc Nephrol 2000;11:155A.",
         inputs={"scr": "mg/dL", "age": "years", "sex": SEX, "black": "bool"},
         output_unit="mL/min/1.73m²")
def egfr_mdrd_186(scr: float, age: float, sex: str, black: bool) -> float:
    """Original (non-IDMS) 4-variable MDRD equation, superseded by the 175 version in 2006.

    GFR = 186 × Scr^−1.154 × Age^−0.203 × 0.742 [if female] × 1.212 [if African American]

    Levey AS et al. J Am Soc Nephrol 2000;11:155A (abstract; no DOI). The 175 re-expression
    (doi:10.7326/0003-4819-145-4-200608150-00004) states the relationship. Registered so the
    audit can recognise sites that never moved to the IDMS-traceable constant.
    """
    return (186 * scr ** -1.154 * age ** -0.203 * (0.742 if _female(sex) else 1.0)
            * (1.212 if black else 1.0))


@formula("crcl_cockcroft_gault", "1976",
         "Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine. "
         "Nephron 1976;16:31-41.", doi="10.1159/000180580",
         inputs={"scr": "mg/dL", "age": "years", "sex": SEX, "weight": "kg"},
         output_unit="mL/min")
def crcl_cockcroft_gault(scr: float, age: float, sex: str, weight: float) -> float:
    """Cockcroft–Gault creatinine clearance.

    Ccr (mL/min) = (140 − age) × weight(kg) / (72 × Scr(mg/dL)), × 0.85 for females.

    Cockcroft DW, Gault MH. Nephron 1976;16:31-41. doi:10.1159/000180580
    (The paper derives the male equation; it states the 15% lower value for females.)
    """
    return (140 - age) * weight / (72 * scr) * (0.85 if _female(sex) else 1.0)


@formula("egfr_schwartz_bedside", "2009",
         "Schwartz GJ, Muñoz A, Schneider MF, et al. New equations to estimate GFR in children "
         "with CKD. J Am Soc Nephrol 2009;20:629-637.", doi="10.1681/ASN.2008030287",
         inputs={"scr": "mg/dL", "height": "cm"}, output_unit="mL/min/1.73m²")
def egfr_schwartz_bedside(scr: float, height: float) -> float:
    """Bedside CKiD ("updated Schwartz") equation for children.

    eGFR = 0.413 × height(cm) / Scr(mg/dL)

    Schwartz GJ et al. J Am Soc Nephrol 2009;20:629-637. doi:10.1681/ASN.2008030287
    """
    return 0.413 * height / scr


# ---------------------------------------------------------------------------------------------
# Body size
# ---------------------------------------------------------------------------------------------
@formula("bmi", "quetelet",
         "Keys A, Fidanza F, Karvonen MJ, Kimura N, Taylor HL. Indices of relative weight and "
         "obesity. J Chronic Dis 1972;25:329-343.", doi="10.1016/0021-9681(72)90027-6",
         inputs={"weight": "kg", "height": "cm"}, output_unit="kg/m²")
def bmi(weight: float, height: float) -> float:
    """Body mass index (Quetelet index).

    BMI = weight(kg) / height(m)²   (imperial: 703.0696 × lb / in², from 0.45359237 / 0.0254²)

    Keys A et al. J Chronic Dis 1972;25:329-343. doi:10.1016/0021-9681(72)90027-6
    """
    return weight / (height / 100) ** 2


@formula("bsa_mosteller", "1987",
         "Mosteller RD. Simplified calculation of body-surface area. N Engl J Med 1987;317:1098.",
         doi="10.1056/NEJM198710223171717",
         inputs={"weight": "kg", "height": "cm"}, output_unit="m²")
def bsa_mosteller(weight: float, height: float) -> float:
    """Mosteller body surface area.

    BSA (m²) = √( height(cm) × weight(kg) / 3600 )

    Mosteller RD. N Engl J Med 1987;317:1098. doi:10.1056/NEJM198710223171717
    """
    return math.sqrt(height * weight / 3600)


@formula("bsa_dubois", "1916",
         "Du Bois D, Du Bois EF. A formula to estimate the approximate surface area if height and "
         "weight be known. Arch Intern Med 1916;17:863-871.",
         doi="10.1001/archinte.1916.00080130010002",
         inputs={"weight": "kg", "height": "cm"}, output_unit="m²")
def bsa_dubois(weight: float, height: float) -> float:
    """Du Bois & Du Bois body surface area.

    A (cm²) = W(kg)^0.425 × H(cm)^0.725 × 71.84   ->   BSA (m²) = 0.007184 × W^0.425 × H^0.725

    Du Bois D, Du Bois EF. Arch Intern Med 1916;17:863-871. doi:10.1001/archinte.1916.00080130010002
    """
    return 0.007184 * weight ** 0.425 * height ** 0.725


@formula("bsa_haycock", "1978",
         "Haycock GB, Schwartz GJ, Wisotsky DH. Geometric method for measuring body surface area: "
         "a height-weight formula validated in infants, children, and adults. J Pediatr "
         "1978;93:62-66.", doi="10.1016/S0022-3476(78)80601-5",
         inputs={"weight": "kg", "height": "cm"}, output_unit="m²")
def bsa_haycock(weight: float, height: float) -> float:
    """Haycock body surface area.

    BSA (m²) = 0.024265 × W(kg)^0.5378 × H(cm)^0.3964

    Haycock GB et al. J Pediatr 1978;93:62-66. doi:10.1016/S0022-3476(78)80601-5
    """
    return 0.024265 * weight ** 0.5378 * height ** 0.3964


@formula("ibw_devine", "1974",
         "Devine BJ. Gentamicin therapy. Drug Intell Clin Pharm 1974;8:650-655.",
         doi="10.1177/106002807400801104",
         inputs={"height": "cm", "sex": SEX}, output_unit="kg")
def ibw_devine(height: float, sex: str) -> float:
    """Devine ideal body weight.

    IBW (kg) = 50 (male) or 45.5 (female) + 2.3 × (height(in) − 60)

    Devine BJ. Drug Intell Clin Pharm 1974;8:650-655. doi:10.1177/106002807400801104
    (indexed by Crossref as a "Clinical Pharmacy: Case Studies" column). Origin reviewed in Pai MP,
    Paloucek FP. Ann Pharmacother 2000;34:1066-1069, doi:10.1345/aph.19381.
    Height in inches = cm / 2.54. Below 60 in the equation is extrapolated linearly (the paper
    does not define it); no clamping is applied here.
    """
    return (45.5 if _female(sex) else 50.0) + 2.3 * (height / CM_PER_IN - 60)


# ---------------------------------------------------------------------------------------------
# ECG
# ---------------------------------------------------------------------------------------------
def _rr_s(hr: float) -> float:
    return 60.0 / hr


@formula("qtc_bazett", "1920",
         "Bazett HC. An analysis of the time-relations of electrocardiograms. Heart 1920;7:353-370.",
         doi="10.1111/j.1542-474X.1997.tb00325.x",
         inputs={"qt": "ms", "hr": "bpm"}, output_unit="ms")
def qtc_bazett(qt: float, hr: float) -> float:
    """Bazett heart-rate-corrected QT.

    QTc = QT / √RR, with RR in seconds (RR = 60 / HR). Returned in ms: QT(ms) / √(60/HR).

    Bazett HC. Heart 1920;7:353-370 (no DOI; reprinted in Ann Noninvasive Electrocardiol
    1997;2:177-194, doi:10.1111/j.1542-474X.1997.tb00325.x).
    """
    return qt / math.sqrt(_rr_s(hr))


@formula("qtc_fridericia", "1920",
         "Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei "
         "Herzkranken. Acta Med Scand 1920;53:469-486.",
         doi="10.1111/j.0954-6820.1920.tb18266.x",
         inputs={"qt": "ms", "hr": "bpm"}, output_unit="ms")
def qtc_fridericia(qt: float, hr: float) -> float:
    """Fridericia heart-rate-corrected QT.

    QTc = QT / RR^(1/3), with RR in seconds.

    Fridericia LS. Acta Med Scand 1920;53:469-486. doi:10.1111/j.0954-6820.1920.tb18266.x
    """
    return qt / _rr_s(hr) ** (1 / 3)


@formula("qtc_framingham", "1992",
         "Sagie A, Larson MG, Goldberg RJ, Bengtson JR, Levy D. An improved method for adjusting "
         "the QT interval for heart rate (the Framingham Heart Study). Am J Cardiol "
         "1992;70:797-801.", doi="10.1016/0002-9149(92)90562-D",
         inputs={"qt": "ms", "hr": "bpm"}, output_unit="ms")
def qtc_framingham(qt: float, hr: float) -> float:
    """Framingham (Sagie) linear QT correction.

    QTc = QT + 0.154 × (1 − RR), all in seconds  ->  QTc(ms) = QT(ms) + 154 × (1 − RR(s)).

    Sagie A et al. Am J Cardiol 1992;70:797-801. doi:10.1016/0002-9149(92)90562-D
    """
    return qt + 154 * (1 - _rr_s(hr))


@formula("qtc_hodges", "1983",
         "Hodges M, Salerno D, Erlien D. Bazett's QT correction reviewed: evidence that a linear "
         "QT correction for heart rate is better [abstract]. J Am Coll Cardiol 1983;1:694.",
         inputs={"qt": "ms", "hr": "bpm"}, output_unit="ms")
def qtc_hodges(qt: float, hr: float) -> float:
    """Hodges linear QT correction.

    QTc(ms) = QT(ms) + 1.75 × (HR − 60)

    Hodges M, Salerno D, Erlien D. J Am Coll Cardiol 1983;1:694 (conference abstract; no DOI).
    Stated in peer-reviewed form by Vandenberk B et al. J Am Heart Assoc 2016;5:e003264,
    doi:10.1161/JAHA.116.003264.
    """
    return qt + 1.75 * (hr - 60)


# ---------------------------------------------------------------------------------------------
# Haemodynamics
# ---------------------------------------------------------------------------------------------
@formula("map", "standard",
         "Meaney E, Alva F, Moguel R, Meaney A, Alva J, Webel R. Formula and nomogram for the "
         "sphygmomanometric calculation of the mean arterial pressure. Heart 2000;84:64.",
         doi="10.1136/heart.84.1.64",
         inputs={"sbp": "mmHg", "dbp": "mmHg"}, output_unit="mmHg")
def mean_arterial_pressure(sbp: float, dbp: float) -> float:
    """Mean arterial pressure, one-third pulse-pressure rule.

    MAP = DBP + (SBP − DBP) / 3

    A textbook convention with no identifiable primary paper. Meaney E et al. Heart 2000;84:64
    (doi:10.1136/heart.84.1.64) compares the 1/3 multiplier with its proposed 0.412; it is cited
    as a source that discusses the rule, not one that endorses it.
    """
    return dbp + (sbp - dbp) / 3


# ---------------------------------------------------------------------------------------------
# Electrolytes and acid–base
# ---------------------------------------------------------------------------------------------
EMMETT_1977 = ("Emmett M, Narins RG. Clinical use of the anion gap. Medicine (Baltimore) "
               "1977;56:38-54.")


@formula("anion_gap", "no-k", EMMETT_1977, doi="10.1097/00005792-197756010-00002",
         inputs={"na": "mEq/L", "cl": "mEq/L", "hco3": "mEq/L"}, output_unit="mEq/L")
def anion_gap(na: float, cl: float, hco3: float) -> float:
    """Serum anion gap without potassium.

    AG = [Na⁺] − ([Cl⁻] + [HCO₃⁻])

    Emmett M, Narins RG. Medicine (Baltimore) 1977;56:38-54. doi:10.1097/00005792-197756010-00002
    """
    return na - (cl + hco3)


@formula("anion_gap", "with-k", EMMETT_1977, doi="10.1097/00005792-197756010-00002",
         inputs={"na": "mEq/L", "k": "mEq/L", "cl": "mEq/L", "hco3": "mEq/L"},
         output_unit="mEq/L")
def anion_gap_k(na: float, k: float, cl: float, hco3: float) -> float:
    """Serum anion gap including potassium.

    AG = ([Na⁺] + [K⁺]) − ([Cl⁻] + [HCO₃⁻])

    Emmett M, Narins RG. Medicine (Baltimore) 1977;56:38-54. doi:10.1097/00005792-197756010-00002
    """
    return (na + k) - (cl + hco3)


PAYNE_1973 = ("Payne RB, Little AJ, Williams RB, Milner JR. Interpretation of serum calcium in "
              "patients with abnormal serum proteins. Br Med J 1973;4:643-646.")


@formula("calcium_corrected", "payne-1973", PAYNE_1973, doi="10.1136/bmj.4.5893.643",
         inputs={"ca": "mg/dL", "albumin": "g/dL"}, output_unit="mg/dL")
def calcium_corrected_payne_1973(ca: float, albumin: float) -> float:
    """Albumin-adjusted calcium exactly as published by Payne et al. 1973.

    Adjusted Ca = Ca − albumin + 4.0   (calcium in mg/100 mL, albumin in g/100 mL; slope 1.0)

    Payne RB et al. Br Med J 1973;4:643-646. doi:10.1136/bmj.4.5893.643 (abstract, verbatim).
    """
    return ca - albumin + 4.0


@formula("calcium_corrected", "0.8",
         "Conventional bedside form; often attributed to Payne 1973 (doi:10.1136/bmj.4.5893.643), "
         "which published a slope of 1.0. Its SI form traces to Payne RB, Carver ME, Morgan DB. "
         "J Clin Pathol 1979;32:56-60 (0.025 per g/L, later rounded to 0.02) per Roberts G, "
         "Thomas A. J Lab Precis Med 2023;8:4.", doi="10.21037/jlpm-22-35",
         inputs={"ca": "mg/dL", "albumin": "g/dL"}, output_unit="mg/dL")
def calcium_corrected(ca: float, albumin: float) -> float:
    """Albumin-corrected total calcium, the 0.8 form used by most calculators.

    Corrected Ca (mg/dL) = Ca (mg/dL) + 0.8 × (4.0 − albumin (g/dL))
    (SI equivalent: Ca (mmol/L) + 0.02 × (40 − albumin (g/L)).)

    No primary paper derives 0.8: Payne et al. 1973 (doi:10.1136/bmj.4.5893.643) published
    Ca − albumin + 4.0 (see ``calcium_corrected@payne-1973``). The SI coefficient 0.025 is from
    Payne, Carver & Morgan, J Clin Pathol 1979;32:56-60 (doi:10.1136/jcp.32.1.56), later rounded
    to 0.02 (= 0.8 in mg/dL units), per the review Roberts G, Thomas A. J Lab Precis Med 2023;8:4,
    doi:10.21037/jlpm-22-35. A site labelling this "Payne" is following convention, not the paper.
    """
    return ca + 0.8 * (4.0 - albumin)


@formula("sodium_corrected", "katz",
         "Katz MA. Hyperglycemia-induced hyponatremia—calculation of expected serum sodium "
         "depression. N Engl J Med 1973;289:843-844.", doi="10.1056/NEJM197310182891607",
         inputs={"na": "mEq/L", "glucose": "mg/dL"}, output_unit="mEq/L")
def sodium_corrected_katz(na: float, glucose: float) -> float:
    """Glucose-corrected sodium, Katz factor.

    Na_corr = Na + 1.6 × (glucose(mg/dL) − 100) / 100

    Katz MA. N Engl J Med 1973;289:843-844. doi:10.1056/NEJM197310182891607
    """
    return na + 1.6 * (glucose - 100) / 100


@formula("sodium_corrected", "hillier",
         "Hillier TA, Abbott RD, Barrett EJ. Hyponatremia: evaluating the correction factor for "
         "hyperglycemia. Am J Med 1999;106:399-403.", doi="10.1016/S0002-9343(99)00055-8",
         inputs={"na": "mEq/L", "glucose": "mg/dL"}, output_unit="mEq/L")
def sodium_corrected_hillier(na: float, glucose: float) -> float:
    """Glucose-corrected sodium, Hillier factor.

    Na_corr = Na + 2.4 × (glucose(mg/dL) − 100) / 100

    Hillier TA et al. Am J Med 1999;106:399-403. doi:10.1016/S0002-9343(99)00055-8
    """
    return na + 2.4 * (glucose - 100) / 100


@formula("fena", "espinel",
         "Espinel CH. The FENa test. Use in the differential diagnosis of acute renal failure. "
         "JAMA 1976;236:579-581.", doi="10.1001/jama.1976.03270060029022",
         inputs={"una": "mEq/L", "pna": "mEq/L", "ucr": "mg/dL", "pcr": "mg/dL"}, output_unit="%")
def fena(una: float, pna: float, ucr: float, pcr: float) -> float:
    """Fractional excretion of sodium.

    FENa (%) = (U_Na × P_Cr) / (P_Na × U_Cr) × 100

    Espinel CH. JAMA 1976;236:579-581. doi:10.1001/jama.1976.03270060029022
    Creatinine units cancel only if urine and plasma creatinine share a unit; :func:`evaluate`
    converts both to mg/dL so mixed-unit inputs are handled.
    """
    return (una * pcr) / (pna * ucr) * 100


@formula("winters", "1967",
         "Albert MS, Dell RB, Winters RW. Quantitative displacement of acid-base equilibrium in "
         "metabolic acidosis. Ann Intern Med 1967;66:312-322.", doi="10.7326/0003-4819-66-2-312",
         inputs={"hco3": "mEq/L"}, output_unit="mmHg")
def winters(hco3: float) -> float:
    """Winters' formula: expected PaCO₂ in metabolic acidosis (centre of the range).

    PaCO₂ = 1.5 × [HCO₃⁻] + 8 ± 2

    Albert MS, Dell RB, Winters RW. Ann Intern Med 1967;66:312-322. doi:10.7326/0003-4819-66-2-312
    The audit accepts any site value inside ±2 only if the site reports a range; a single
    number is compared with the centre.
    """
    return 1.5 * hco3 + 8


# ---------------------------------------------------------------------------------------------
# Lipids
# ---------------------------------------------------------------------------------------------
@formula("ldl_friedewald", "1972",
         "Friedewald WT, Levy RI, Fredrickson DS. Estimation of the concentration of low-density "
         "lipoprotein cholesterol in plasma, without use of the preparative ultracentrifuge. "
         "Clin Chem 1972;18:499-502.", doi="10.1093/clinchem/18.6.499",
         inputs={"tc": "mg/dL", "hdl": "mg/dL", "tg": "mg/dL"}, output_unit="mg/dL")
def ldl_friedewald(tc: float, hdl: float, tg: float) -> float:
    """Friedewald LDL cholesterol.

    LDL-C = TC − HDL-C − TG/5   (all mg/dL; the paper restricts use to TG ≤ 400 mg/dL)

    Friedewald WT et al. Clin Chem 1972;18:499-502. doi:10.1093/clinchem/18.6.499
    SI form: TG/2.2 (EAS/EFLM consensus, Nordestgaard BG et al. Clin Chem 2016;62:930-946,
    doi:10.1373/clinchem.2016.258897); the exact conversion is 5 × 38.67/88.57 = 2.183.
    :func:`evaluate` converts mmol/L inputs with the molar factors, so a TG/2.2 site differs by <1%.
    """
    return tc - hdl - tg / 5


MH_TABLE_PATH = Path(__file__).with_name("martin_hopkins_table.json")


def _mh_table() -> dict | None:
    if MH_TABLE_PATH.exists():
        return json.loads(MH_TABLE_PATH.read_text())
    return None


def _stratum(value: float, bounds: list[list[float | None]]) -> int:
    for i, (lo, hi) in enumerate(bounds):
        if (lo is None or value >= lo) and (hi is None or value < hi):
            return i
    raise ValueError(f"value {value} outside table strata")


@formula("ldl_martin_hopkins", "2013",
         "Martin SS, Blaha MJ, Elshazly MB, et al. Comparison of a novel method vs the Friedewald "
         "equation for estimating low-density lipoprotein cholesterol levels from the standard "
         "lipid profile. JAMA 2013;310:2061-2068.", doi="10.1001/jama.2013.280532",
         inputs={"tc": "mg/dL", "hdl": "mg/dL", "tg": "mg/dL"}, output_unit="mg/dL")
def ldl_martin_hopkins(tc: float, hdl: float, tg: float) -> float:
    """Martin–Hopkins LDL cholesterol.

    LDL-C = TC − HDL-C − TG / F, where F is read from the 180-cell table of the paper
    (triglyceride strata × non-HDL-C strata, mg/dL).

    Martin SS et al. JAMA 2013;310:2061-2068. doi:10.1001/jama.2013.280532
    The table (Figure 2 of the NIH manuscript PMC4226221) lives in ``martin_hopkins_table.json``
    with its provenance; it agrees cell-for-cell with four independent open implementations. The
    medians are not strictly monotone (TG 97–100, non-HDL ≥220 is 4.3 after 4.4), as printed.
    TG ≥ 400 uses the paper's single open row; the 2021 extension for TG 400–799 (Sajja A et al.
    JAMA Netw Open 2021;4:e2128817, doi:10.1001/jamanetworkopen.2021.28817) is not implemented.
    """
    t = _mh_table()
    if t is None:
        raise NotImplementedError("Martin–Hopkins factor table not available; see README")
    i = _stratum(tg, t["tg_bounds"])
    j = _stratum(tc - hdl, t["nonhdl_bounds"])
    return tc - hdl - tg / t["factors"][i][j]


@formula("ldl_sampson", "2020",
         "Sampson M, Ling C, Sun Q, et al. A New Equation for Calculation of Low-Density "
         "Lipoprotein Cholesterol in Patients With Normolipidemia and/or Hypertriglyceridemia. "
         "JAMA Cardiol 2020;5:540-548.", doi="10.1001/jamacardio.2020.0013",
         inputs={"tc": "mg/dL", "hdl": "mg/dL", "tg": "mg/dL"}, output_unit="mg/dL")
def ldl_sampson(tc: float, hdl: float, tg: float) -> float:
    """Sampson (NIH equation 2) LDL cholesterol.

    LDL-C = TC/0.948 − HDL-C/0.971 − (TG/8.56 + TG × non-HDL-C/2140 − TG²/16100) − 9.44

    Sampson M et al. JAMA Cardiol 2020;5:540-548. doi:10.1001/jamacardio.2020.0013
    """
    nonhdl = tc - hdl
    return tc / 0.948 - hdl / 0.971 - (tg / 8.56 + tg * nonhdl / 2140 - tg ** 2 / 16100) - 9.44


# ---------------------------------------------------------------------------------------------
# Fluids
# ---------------------------------------------------------------------------------------------
@formula("parkland", "1968",
         "Baxter CR, Shires T. Physiological response to crystalloid resuscitation of severe "
         "burns. Ann N Y Acad Sci 1968;150:874-894.",
         doi="10.1111/j.1749-6632.1968.tb14738.x",
         inputs={"weight": "kg", "tbsa": "%"}, output_unit="mL/24h")
def parkland(weight: float, tbsa: float) -> float:
    """Parkland burn resuscitation volume over the first 24 h.

    V (mL lactated Ringer's, 24 h) = 4 × weight(kg) × TBSA burned (%); half in the first 8 h.

    Baxter CR, Shires T. Ann N Y Acad Sci 1968;150:874-894. doi:10.1111/j.1749-6632.1968.tb14738.x
    """
    return 4 * weight * tbsa


@formula("holliday_segar", "1957",
         "Holliday MA, Segar WE. The maintenance need for water in parenteral fluid therapy. "
         "Pediatrics 1957;19:823-832.", doi="10.1542/peds.19.5.823",
         inputs={"weight": "kg"}, output_unit="mL/day")
def holliday_segar(weight: float) -> float:
    """Holliday–Segar maintenance water requirement.

    100 mL/kg/day for the first 10 kg, + 50 mL/kg/day for 10–20 kg, + 20 mL/kg/day above 20 kg:
    V (mL/day) = 100·W (W ≤ 10); = 1000 + 50·(W − 10) (10 < W ≤ 20); = 1500 + 20·(W − 20) (W > 20)

    Holliday MA, Segar WE. Pediatrics 1957;19:823-832. doi:10.1542/peds.19.5.823
    """
    return (100 * min(weight, 10) + 50 * min(max(weight - 10, 0), 10)
            + 20 * max(weight - 20, 0))


@formula("holliday_segar_hourly", "4-2-1",
         "Holliday MA, Segar WE. The maintenance need for water in parenteral fluid therapy. "
         "Pediatrics 1957;19:823-832.", doi="10.1542/peds.19.5.823",
         inputs={"weight": "kg"}, output_unit="mL/h")
def holliday_segar_hourly(weight: float) -> float:
    """Hourly "4-2-1 rule" form of Holliday–Segar.

    4 mL/kg/h for the first 10 kg, + 2 mL/kg/h for 10–20 kg, + 1 mL/kg/h above 20 kg:
    V (mL/h) = 4·W (W ≤ 10); = 40 + 2·(W − 10) (10 < W ≤ 20); = 60 + (W − 20) (W > 20)

    This is the conventional rounding of the daily rule (100/24 = 4.17, 50/24 = 2.08,
    20/24 = 0.83); it is not stated in Holliday & Segar 1957 (doi:10.1542/peds.19.5.823). It
    differs from daily/24 by up to ~4%, so sites using either are both "correct" for their
    declared form; the audit compares a site with the form it claims.
    """
    return (4 * min(weight, 10) + 2 * min(max(weight - 10, 0), 10) + 1 * max(weight - 20, 0))
