# clinical — audit the formulas behind online medical calculators

Motivation: a 2020 audit of 47 free online eGFR calculators found 11 gave wrong results
(Eur J Clin Pharmacol, PMC7481157), and the 2021 race-free CKD-EPI equation has not reached every
site. This track has three parts:

1. **Reference implementations** (`formulas.py`) transcribed from the primary publications.
2. **Reference vectors** (`vectors.json`) computed by a *second, independent* transcription in
   mpmath at 40 digits (`vectorgen.py`, which does not import `formulas.py`), so the tests compare
   two readings of each paper rather than the code with itself. No value comes from a website.
3. **An audit harness** (`audit.py`) that drives calculator pages in headless Chromium with those
   inputs, reads the displayed result, compares it with the reference, and — on a mismatch — tries
   to explain it (other formula versions, unit mix-ups, RR in ms).

Nothing here is medical advice. These are test oracles for software.

## Run it

```bash
uv sync --all-extras && uv run playwright install chromium   # once
uv run formulaci clinical vectors                    # self-check: 178/178 vectors, 31 formulas
uv run formulaci clinical audit --mock               # mock server in-process, writes data/clinical/audit.jsonl
uv run pytest tests/clinical                          # 203 tests, ~45 s (the e2e audit is most of it)
```

Or run the mock server yourself and point the audit at it:

```bash
uv run formulaci clinical mock-serve --port 8765
uv run formulaci clinical audit --targets formulaci/clinical/mock/targets.yaml --base-url http://127.0.0.1:8765 --out data/clinical/audit.jsonl
```

`audit` appends to `--out` and skips (target, inputs) pairs already there; `--force` starts over.
`--only <target-id>` restricts the run, `--max-cases N` (default 3) sets how many typical
reference vectors each page gets, `--headed` shows the browser.

### Result on the mock site (measured)

12 pages, 14 targets (two pages are audited in two modes). Planted faults:

| target | what is wrong | audit result | diagnosis it prints |
|---|---|---|---|
| `mock-egfr-ckd-epi-legacy` | says "updated 2021", computes CKD-EPI 2009 with race coefficient | mismatch 3/3 | matches `egfr_ckd_epi_cr@2009` |
| `mock-crcl-cockcroft-gault` | weight field labelled lb, used as kg | mismatch 3/3 | weight entered in lb but used as kg |
| `mock-qtc-bazett` | RR = 60000/HR (ms) under the square root | mismatch 3/3 | RR interval used in ms instead of s |
| `mock-sodium-corrected` | claims Hillier 2.4, uses Katz 1.6 | mismatch 2/2 | matches `sodium_corrected@katz` |
| `mock-winters` | script error, result never renders | unreadable 3/3 | (page error reported in notes) |

The other 9 targets (CKD-EPI 2021 in mg/dL and µmol/L, Fridericia, BMI, BSA in lb/in, anion gap
with and without K, corrected calcium, MAP) match on every case. The e2e test asserts the set of
mismatching targets equals the planted set exactly.

### Output record (`data/clinical/audit.jsonl`, one per target × case)

`{target, formula, inputs, site_output, reference_output, status: match|mismatch|unreadable, notes}`
plus `url, claimed_version, site_text, tolerance, diagnosis`.

Tolerance: half a unit in the last displayed digit + 0.5% of the reference (absorbs legitimate
constant differences such as 88.4 vs 88.42 µmol/L per mg/dL, or 703 vs 703.07 in imperial BMI;
the smallest planted error, Katz vs Hillier at glucose 600 mg/dL, is 2.9%). A page that rounds
eGFR to an integer still matches. Per-target `tolerance: {rel, abs}` overrides it.

## Live audit (NOT run; needs the user's explicit go-ahead)

`targets.yaml` lists real public calculator pages. The harness refuses any non-local host:

```
$ uv run formulaci clinical audit --targets formulaci/clinical/targets.yaml
refused: refusing to drive non-local hosts without --allow-live: ...
```

The check runs before a browser starts (tested). Once authorised, a live run would be:

```bash
uv run formulaci clinical audit --targets formulaci/clinical/targets.yaml --allow-live --out data/clinical/audit-live.jsonl --max-cases 2
```

What it would do: one fresh page per (target, case); type reference inputs into the page's form;
read the result element; 3 s pause between cases by default; a descriptive User-Agent. In live
mode every **non-GET request to a non-local host is aborted**, so inputs are only processed by the
page's own client-side code and are never posted to the site's server. Calculators that compute
server-side by POST (ClinCalc, GlobalRPh, NHLBI) will therefore show as `unreadable` rather than be
submitted. Sites whose form submits by **GET** (calculator.net, Inch Calculator, bmi-calculator.net)
would receive the synthetic reference inputs as a query string; drop those targets with `--only`
if that is not acceptable. MSD Manuals calculators live in an iframe; their `iframe_src` is
driven directly. Before a live run:
re-check each recipe whose `selectors_verified` is `false` with `--headed --only <id>`; many
selectors were inferred from static HTML or are guesses for JS-rendered pages (see below).

## Formulas covered

Keys are `name@version`; all inputs are in canonical units, other units via
`formulas.evaluate(key, inputs, units={...})`.

| key | equation (canonical units) | primary source |
|---|---|---|
| `egfr_ckd_epi_cr@2021` | 142·min(Scr/κ,1)^α·max(Scr/κ,1)^−1.200·0.9938^age·1.012[F] | Inker, NEJM 2021, doi:10.1056/NEJMoa2102953 |
| `egfr_ckd_epi_crcys@2021` | 135·min(Scr/κ,1)^α·max(Scr/κ,1)^−0.544·min(Scys/0.8,1)^−0.323·max(Scys/0.8,1)^−0.778·0.9961^age·0.963[F] | Inker, NEJM 2021, doi:10.1056/NEJMoa2102953 |
| `egfr_ckd_epi_cr@2009` | 141·min(Scr/κ,1)^α·max(Scr/κ,1)^−1.209·0.993^age·1.018[F]·1.159[black] | Levey, Ann Intern Med 2009, doi:10.7326/0003-4819-150-9-200905050-00006 |
| `egfr_mdrd@175` | 175·Scr^−1.154·age^−0.203·0.742[F]·1.212[black] | Levey, Ann Intern Med 2006, doi:10.7326/0003-4819-145-4-200608150-00004 |
| `egfr_mdrd@186` | as above with 186 (pre-IDMS; for diagnosis) | Levey, J Am Soc Nephrol 2000;11:155A (abstract) |
| `crcl_cockcroft_gault@1976` | (140−age)·wt/(72·Scr)·0.85[F] | Cockcroft & Gault, Nephron 1976, doi:10.1159/000180580 |
| `egfr_schwartz_bedside@2009` | 0.413·height(cm)/Scr | Schwartz, JASN 2009, doi:10.1681/ASN.2008030287 |
| `bmi@quetelet` | kg/m² | Keys, J Chronic Dis 1972, doi:10.1016/0021-9681(72)90027-6 |
| `bsa_mosteller@1987` | √(cm·kg/3600) | Mosteller, NEJM 1987, doi:10.1056/NEJM198710223171717 |
| `bsa_dubois@1916` | 0.007184·W^0.425·H^0.725 | Du Bois & Du Bois, Arch Intern Med 1916, doi:10.1001/archinte.1916.00080130010002 |
| `bsa_haycock@1978` | 0.024265·W^0.5378·H^0.3964 | Haycock, J Pediatr 1978, doi:10.1016/S0022-3476(78)80601-5 |
| `ibw_devine@1974` | 50 [M] / 45.5 [F] + 2.3·(in − 60) | Devine, Drug Intell Clin Pharm 1974 |
| `qtc_bazett@1920` | QT/√RR (RR s) | Bazett, Heart 1920 |
| `qtc_fridericia@1920` | QT/∛RR | Fridericia, Acta Med Scand 1920 |
| `qtc_framingham@1992` | QT + 154·(1−RR) ms | Sagie, Am J Cardiol 1992, doi:10.1016/0002-9149(92)90562-D |
| `qtc_hodges@1983` | QT + 1.75·(HR−60) | Hodges, J Am Coll Cardiol 1983;1:694 (abstract) |
| `map@standard` | DBP + (SBP−DBP)/3 | textbook convention; no primary source found (Meaney, Heart 2000, discusses it and proposes 0.412) |
| `anion_gap@no-k`, `@with-k` | Na − (Cl + HCO₃); (Na + K) − (Cl + HCO₃) | Emmett & Narins, Medicine 1977 |
| `calcium_corrected@0.8` | Ca + 0.8·(4 − alb) | convention; no primary derivation found (see below) |
| `calcium_corrected@payne-1973` | Ca − alb + 4.0 | Payne, BMJ 1973, doi:10.1136/bmj.4.5893.643 |
| `sodium_corrected@katz`, `@hillier` | Na + 1.6 / 2.4·(glu − 100)/100 | Katz, NEJM 1973; Hillier, Am J Med 1999 |
| `fena@espinel` | 100·UNa·PCr/(PNa·UCr) | Espinel, JAMA 1976, doi:10.1001/jama.1976.03270060029022 |
| `winters@1967` | 1.5·HCO₃ + 8 (± 2) | Albert, Dell & Winters, Ann Intern Med 1967, doi:10.7326/0003-4819-66-2-312 |
| `ldl_friedewald@1972` | TC − HDL − TG/5 | Friedewald, Clin Chem 1972, doi:10.1093/clinchem/18.6.499 |
| `ldl_martin_hopkins@2013` | TC − HDL − TG/F(TG, non-HDL), 180-cell table | Martin, JAMA 2013, doi:10.1001/jama.2013.280532 |
| `ldl_sampson@2020` (extra) | TC/0.948 − HDL/0.971 − (TG/8.56 + TG·nonHDL/2140 − TG²/16100) − 9.44 | Sampson, JAMA Cardiol 2020, doi:10.1001/jamacardio.2020.0013 |
| `parkland@1968` | 4·kg·%TBSA mL/24 h | Baxter & Shires, Ann N Y Acad Sci 1968 |
| `holliday_segar@1957` | 100/50/20 mL/kg/day | Holliday & Segar, Pediatrics 1957 |
| `holliday_segar_hourly@4-2-1` | 4/2/1 mL/kg/h (conventional rounding, not in the paper) | — |

Full citations, DOIs and the exact equations are in each function's docstring. Every DOI was
checked against Crossref. Findings from that check that matter for auditing:

- **Corrected calcium.** Payne et al. 1973 published *Ca − albumin + 4.0* (slope 1.0), not the
  0.8 that nearly every calculator attributes to "Payne". The 0.025 mmol/L-per-g/L SI slope is from
  Payne, Carver & Morgan, J Clin Pathol 1979 (doi:10.1136/jcp.32.1.56), later rounded to 0.02 (0.8 in
  mg/dL units), per Roberts & Thomas, J Lab Precis Med 2023 (doi:10.21037/jlpm-22-35). Both versions
  are registered; live targets are filed under `@0.8`.
- **Martin–Hopkins.** The 180-cell factor table is public as Figure 2 of the NIH manuscript
  (PMC4226221). `martin_hopkins_table.json` was transcribed from it and agrees cell-for-cell with
  four independent open-source implementations; this session re-checked one (0/180 differences).
  The 2021 extension for TG 400–799 (Sajja et al., doi:10.1001/jamanetworkopen.2021.28817, 240
  cells) is **not** implemented: its supplement PDF did not extract cleanly and there was no second
  source to check it against.
- **Secondary-source only.** For Winters, Parkland, Holliday–Segar, Devine and Du Bois the
  coefficients were confirmed from secondary sources (reviews, NIH/StatPearls), not by reading
  the primary paper; for Hodges the primary is a 1983 abstract (stated in Vandenberk et al. JAHA
  2016, doi:10.1161/JAHA.116.003264).
- Friedewald's SI divisor 2.2 is per the EAS/EFLM consensus (doi:10.1373/clinchem.2016.258897);
  Espinel's ATN cut-off is FENa > 3%, not the often-quoted > 2%.

Unit factors (`formulas.py` header): creatinine 88.4 µmol/L per mg/dL (KDIGO 2012), glucose 18.016,
calcium 4.008, cholesterol 38.67, triglyceride 88.57 mg/dL per mmol/L (molar masses), 1 in = 2.54 cm
and 1 lb = 0.45359237 kg exactly.

## What is not covered / known limitations

- Martin–Hopkins extended (TG 400–799) table; Rautaharju QTc.
- Pediatric eGFR beyond bedside Schwartz (CKiD U25, EKFC), CKD-EPI 2012 cystatin, and Kidney
  Failure Risk Equation are not implemented.
- Winters' ± 2 range is compared against its centre; a site that only shows a range must use a
  regex that captures one end and a `tolerance: {abs: 2}` override.
- The harness reads one number per page. Pages that show several results (e.g. eGFR by three
  equations) need one target entry per result selector.
- Live recipes are best-effort. A JS-rendered page (MDCalc, Omni, QxMD) cannot be fully inspected
  without running it; such entries are marked `selectors_verified: false`.
- Display rounding is assumed to be round-half-to-even-or-up; a site that truncates can produce
  a mismatch up to one display unit — the half-unit allowance plus 0.5% usually absorbs it, but
  check `notes` before reporting.

## Live targets (`targets.yaml`)

84 pages across MDCalc, NKF, NIDDK, Kidney Health Australia, calculator.net, ClinCalc, GlobalRPh,
Omni, MSD Manuals, QxMD, Medscape, Stanford, NHLBI, CDC, Inch Calculator, bmi-calculator.net and
Johns Hopkins. Collected on 2026-10-21 by **read-only GET requests** (no forms submitted, no
buttons clicked, no headless browser). "Selectors seen" means the *input* ids/names were present
in server HTML; result selectors were often not visible before a calculation and are best
guesses. No numeric check has been run against any of them.

Observations from reading page text and source alone (unconfirmed until a live audit is authorised):
GlobalRPh, Omni, calculator.net and an MSD legacy page still present CKD-EPI 2009 with the race
coefficient (NIDDK keeps a 2009 page on purpose — a good positive control); Medscape/QxMD MDRD code
uses the pre-IDMS 186 constant; MSD "MDRD" is the 6-variable 170 equation; MSD "Ideal Body Weight"
is BMI-based, not Devine; Medscape IBW uses Robinson for women; Medscape's cystatin C unit is
labelled mg/dL (should be mg/L); Omni's Framingham QTc text mixes ms and s. Unreachable while
researching: ldlcalculator.com (Cloudflare challenge, not bypassed), CDC and Mayo BMI (403),
RapidTables BMI (404).

| id | site | claims | rendering | selectors seen |
|---|---|---|---|---|
| [mdcalc-ckd-epi](https://www.mdcalc.com/calc/3939/ckd-epi-equations-glomerular-filtration-rate-gfr) | MDCalc | `egfr_ckd_epi_cr@2021` | js | no |
| [mdcalc-mdrd](https://www.mdcalc.com/calc/76/mdrd-gfr-equation) | MDCalc | `egfr_mdrd@175` | js | yes |
| [mdcalc-cockcroft-gault](https://www.mdcalc.com/calc/43/creatinine-clearance-cockcroft-gault-equation) | MDCalc | `crcl_cockcroft_gault@1976` | js | yes |
| [mdcalc-qtc](https://www.mdcalc.com/calc/48/corrected-qt-interval-qtc) | MDCalc | `qtc_bazett@1920` | js | yes |
| [mdcalc-calcium-correction](https://www.mdcalc.com/calc/31/calcium-correction-hypoalbuminemia) | MDCalc | `calcium_corrected@0.8` | js | yes |
| [mdcalc-sodium-correction](https://www.mdcalc.com/calc/50/sodium-correction-hyperglycemia) | MDCalc | `sodium_corrected@katz` | js | yes |
| [mdcalc-anion-gap](https://www.mdcalc.com/calc/1669/anion-gap) | MDCalc | `anion_gap@no-k` | js | yes |
| [mdcalc-fena](https://www.mdcalc.com/calc/60/fractional-excretion-sodium-fena) | MDCalc | `fena@espinel` | js | yes |
| [mdcalc-winters](https://www.mdcalc.com/calc/117/winters-formula-metabolic-acidosis-compensation) | MDCalc | `winters@1967` | js | yes |
| [mdcalc-map](https://www.mdcalc.com/calc/74/mean-arterial-pressure-map) | MDCalc | `map@standard` | js | yes |
| [mdcalc-parkland](https://www.mdcalc.com/calc/83/parkland-formula-burns) | MDCalc | `parkland@1968` | js | yes |
| [mdcalc-maintenance-fluids](https://www.mdcalc.com/calc/72/maintenance-fluids-calculations) | MDCalc | `holliday_segar_hourly@4-2-1` | js | yes |
| [mdcalc-ibw](https://www.mdcalc.com/calc/68/ideal-body-weight-adjusted-body-weight) | MDCalc | `ibw_devine@1974` | js | yes |
| [mdcalc-bmi-bsa](https://www.mdcalc.com/calc/29/body-mass-index-bmi-body-surface-area-bsa) | MDCalc | `bmi@quetelet` | js | yes |
| [mdcalc-ldl-friedewald](https://www.mdcalc.com/calc/70/friedewald-equation-low-density-lipoprotein-cholesterol-ldl-c) | MDCalc | `ldl_friedewald@1972` | js | yes |
| [mdcalc-schwartz](https://www.mdcalc.com/calc/10008/revised-schwartz-equation-glomerular-filtration-rate-gfr-2009) | MDCalc | `egfr_schwartz_bedside@2009` | js | yes |
| [nkf-egfr-adult](https://www.kidney.org/professionals/gfr_calculator) | National Kidney Foundation | `egfr_ckd_epi_cr@2021` | static | yes |
| [nkf-egfr-pediatric](https://www.kidney.org/professionals/kdoqi/gfr_calculatorPed) | National Kidney Foundation | `egfr_schwartz_bedside@2009` | static | yes |
| [niddk-egfr-adult](https://www.niddk.nih.gov/health-information/professionals/clinical-tools-patient-management/kidney-disease/laboratory-evaluation/estimated-gfr-calculators/adults-pediatrics) | NIH NIDDK | `egfr_ckd_epi_cr@2021` | js | no |
| [niddk-ckid-bedside](https://www.niddk.nih.gov/health-information/professionals/clinical-tools-patient-management/kidney-disease/laboratory-evaluation/estimated-gfr-calculators/adults-pediatrics) | NIH NIDDK | `egfr_schwartz_bedside@2009` | static | yes |
| [niddk-ckd-epi-2009-previous](https://www.niddk.nih.gov/health-information/professionals/clinical-tools-patient-management/kidney-disease/laboratory-evaluation/estimated-gfr-calculators/previous) | NIH NIDDK | `egfr_ckd_epi_cr@2009` | static | yes |
| [kha-egfr](https://kidney.org.au/health-professionals/egfr-calculator/) | Kidney Health Australia | `egfr_ckd_epi_cr@2009` | static | yes |
| [calculatornet-gfr](https://www.calculator.net/gfr-calculator.html) | calculator.net | `egfr_mdrd@175` | static | yes |
| [calculatornet-bmi](https://www.calculator.net/bmi-calculator.html) | calculator.net | `bmi@quetelet` | static | yes |
| [calculatornet-bsa](https://www.calculator.net/body-surface-area-calculator.html) | calculator.net | `bsa_mosteller@1987` | static | yes |
| [calculatornet-ideal-weight](https://www.calculator.net/ideal-weight-calculator.html) | calculator.net | `ibw_devine@1974` | static | yes |
| [clincalc-crcl](https://clincalc.com/kinetics/crcl.aspx) | ClinCalc | `crcl_cockcroft_gault@1976` | static | yes |
| [clincalc-ibw](https://clincalc.com/kinetics/idealbw.aspx) | ClinCalc | `ibw_devine@1974` | static | yes |
| [globalrph-ckd-epi](https://globalrph.com/medcalcs/chronic-kidney-disease-epidemiology-collaboration-ckd-epi-calculator/) | GlobalRPh | `egfr_ckd_epi_cr@2009` | static | yes |
| [globalrph-crcl](https://globalrph.com/medcalcs/creatinine-clearance-adult/) | GlobalRPh | `crcl_cockcroft_gault@1976` | static | yes |
| [globalrph-bsa](https://globalrph.com/medcalcs/body-surface-area-bsa/) | GlobalRPh | `bsa_mosteller@1987` | js | no |
| [globalrph-anion-gap](https://globalrph.com/medcalcs/anion-gap-calculator-metabolic-acidosis/) | GlobalRPh | `anion_gap@no-k` | static | yes |
| [globalrph-ibw](https://globalrph.com/medcalcs/adjusted-body-weight-ajbw-and-ideal-body-weight-ibw-calc/) | GlobalRPh | `ibw_devine@1974` | static | yes |
| [omni-gfr](https://www.omnicalculator.com/health/glomerular-filtration-rate) | Omni Calculator | `egfr_ckd_epi_cr@2009` | js | no |
| [omni-qtc](https://www.omnicalculator.com/health/qtc) | Omni Calculator | `qtc_bazett@1920` | js | no |
| [omni-bmi](https://www.omnicalculator.com/health/bmi) | Omni Calculator | `bmi@quetelet` | js | no |
| [omni-bsa](https://www.omnicalculator.com/health/bsa) | Omni Calculator | `bsa_mosteller@1987` | js | no |
| [omni-anion-gap](https://www.omnicalculator.com/health/anion-gap) | Omni Calculator | `anion_gap@no-k` | js | no |
| [omni-corrected-calcium](https://www.omnicalculator.com/health/corrected-calcium) | Omni Calculator | `calcium_corrected@0.8` | js | no |
| [omni-ldl](https://www.omnicalculator.com/health/ldl) | Omni Calculator | `ldl_friedewald@1972` | js | no |
| [omni-map](https://www.omnicalculator.com/health/mean-arterial-pressure) | Omni Calculator | `map@standard` | js | no |
| [omni-sodium-correction](https://www.omnicalculator.com/health/sodium-correction) | Omni Calculator | `sodium_corrected@katz` | js | no |
| [omni-fena](https://www.omnicalculator.com/health/fena) | Omni Calculator | `fena@espinel` | js | no |
| [omni-winters](https://www.omnicalculator.com/health/winters-formula) | Omni Calculator | `winters@1967` | js | no |
| [omni-parkland](https://www.omnicalculator.com/health/parkland-formula) | Omni Calculator | `parkland@1968` | js | no |
| [omni-ideal-weight](https://www.omnicalculator.com/health/ideal-weight) | Omni Calculator | `ibw_devine@1974` | js | no |
| [msd-ckd-epi-2021](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/glomerular-filtration-rate-estimation-egfr-by-ckd-epi-equation-with-creatinine-without-race-2021) | MSD Manuals | `egfr_ckd_epi_cr@2021` | iframe | yes |
| [msd-ckd-epi-legacy](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/glomerular-filtration-rate-estimate-by-ckd-epi-equation) | MSD Manuals | `egfr_ckd_epi_cr@2009` | iframe | yes |
| [msd-ckd-epi-crcys-2021](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/glomerular-filtration-rate-estimation-egfr-by-ckd-epi-equation-with-creatinine-and-cystatin-c-without-race-2021) | MSD Manuals | `egfr_ckd_epi_crcys@2021` | iframe | yes |
| [msd-mdrd](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/glomerular-filtration-rate-estimate-by-the-mdrd-equation) | MSD Manuals | `egfr_mdrd@175` | iframe | yes |
| [msd-cockcroft-gault](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/creatinine-clearance-estimate-by-cockcroft-gault-equation) | MSD Manuals | `crcl_cockcroft_gault@1976` | iframe | yes |
| [msd-bmi](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/body-mass-index-quetelets-index) | MSD Manuals | `bmi@quetelet` | iframe | yes |
| [msd-bsa](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/body-surface-area-du-bois-method) | MSD Manuals | `bsa_dubois@1916` | iframe | yes |
| [msd-qtc](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/qt-interval-correction-ekg) | MSD Manuals | `qtc_bazett@1920` | iframe | yes |
| [msd-calcium-correction](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/calcium-correction-in-hypoalbuminemia) | MSD Manuals | `calcium_corrected@0.8` | iframe | yes |
| [msd-sodium-katz](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/sodium-correction-in-hyperglycemia-katz-1973) | MSD Manuals | `sodium_corrected@katz` | iframe | yes |
| [msd-fena](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/fractional-excretion-of-sodium) | MSD Manuals | `fena@espinel` | iframe | yes |
| [msd-winters](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/winters-formula-for-expected-pco2) | MSD Manuals | `winters@1967` | iframe | yes |
| [msd-ldl-friedewald](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/friedewald-equation-for-low-density-lipoprotein-ldl-c) | MSD Manuals | `ldl_friedewald@1972` | iframe | yes |
| [msd-ldl-martin](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/martin-equation-for-low-density-lipoprotein-ldl-c) | MSD Manuals | `ldl_martin_hopkins@2013` | iframe | yes |
| [msd-ibw](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/ideal-body-weight) | MSD Manuals | `ibw_devine@1974` | iframe | yes |
| [msd-parkland](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/burn-injury-fluid-resuscitation-adult-parkland-crystalloid-estimate) | MSD Manuals | `parkland@1968` | iframe | yes |
| [msd-maintenance-fluid-children](https://www.msdmanuals.com/professional/multimedia/clinical-calculator/maintenance-fluid-calculation-for-children) | MSD Manuals | `holliday_segar@1957` | iframe | yes |
| [qxmd-ckd-epi-2021](https://qxmd.com/calculate/calculator_251/egfr-using-ckd-epi-2021-update) | QxMD | `egfr_ckd_epi_cr@2021` | js | no |
| [medscape-mdrd](https://reference.medscape.com/calculator/140/mdrd-egfr) | Medscape | `egfr_mdrd@175` | js | no |
| [medscape-qtc](https://reference.medscape.com/calculator/48/ecg-corrected-qt) | Medscape | `qtc_bazett@1920` | js | no |
| [medscape-bmi-bsa-mosteller](https://reference.medscape.com/calculator/28/bmi-and-bsa-mosteller) | Medscape | `bsa_mosteller@1987` | js | no |
| [medscape-bmi-bsa-dubois](https://reference.medscape.com/calculator/30/bmi-and-bsa-du-bois) | Medscape | `bsa_dubois@1916` | js | no |
| [medscape-anion-gap](https://reference.medscape.com/calculator/11/anion-gap) | Medscape | `anion_gap@no-k` | js | no |
| [medscape-calcium-correction](https://reference.medscape.com/calculator/267/calcium-correction-for-hypoalbuminemia) | Medscape | `calcium_corrected@0.8` | js | no |
| [medscape-sodium-correction](https://reference.medscape.com/calculator/360/corrected-sodium-in-hyperglycemia) | Medscape | `sodium_corrected@hillier` | js | no |
| [medscape-fena](https://reference.medscape.com/calculator/96/fractional-excretion-of-sodium) | Medscape | `fena@espinel` | js | no |
| [medscape-map](https://reference.medscape.com/calculator/486/mean-arterial-pressure-map) | Medscape | `map@standard` | js | no |
| [medscape-parkland](https://reference.medscape.com/calculator/175/parkland-formula) | Medscape | `parkland@1968` | js | no |
| [medscape-maintenance-fluids](https://reference.medscape.com/calculator/526/maintenance-fluid-calculations) | Medscape | `holliday_segar_hourly@4-2-1` | js | no |
| [medscape-ibw](https://reference.medscape.com/calculator/246/ideal-body-weight) | Medscape | `ibw_devine@1974` | js | no |
| [medscape-schwartz](https://reference.medscape.com/calculator/281/schwartz-pediatric-bedside-egfr-2009) | Medscape | `egfr_schwartz_bedside@2009` | js | no |
| [medscape-ckd-epi-crcys-2021](https://reference.medscape.com/calculator/863/egfr-using-ckd-epi-creatinine-cystatin-c-equation-2021) | Medscape | `egfr_ckd_epi_crcys@2021` | js | no |
| [stanford-rogers-qtc](https://rogerslab.stanford.edu/ep-tools/qtc-calculator/) | Stanford Rogers Lab EP Tools | `qtc_bazett@1920` | static | yes |
| [nhlbi-bmi](https://www.nhlbi.nih.gov/calculate-your-bmi) | NHLBI (NIH) | `bmi@quetelet` | static | yes |
| [cdc-adult-bmi](https://www.cdc.gov/bmi/adult-calculator/index.html) | CDC | `bmi@quetelet` | js | no |
| [inchcalculator-bmi](https://www.inchcalculator.com/bmi-calculator/) | Inch Calculator | `bmi@quetelet` | static | yes |
| [bmi-calculator-net](https://www.bmi-calculator.net/) | bmi-calculator.net | `bmi@quetelet` | static | yes |
| [hopkins-ldl-calculator](https://www.ldlcalculator.com/) | Johns Hopkins (ldlcalculator.com) | `ldl_martin_hopkins@2013` | unknown | no |
