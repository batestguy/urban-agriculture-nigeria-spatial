# Survey data provenance — status and gap

**Status: NOT DEPOSITED.** Written 15 October 2026.

## What this directory contains

| File | What it is |
|---|---|
| `worldbank_ng.csv` | World Bank Indicators API, 3 indicators × 2000–2024 |
| `nasa_power_*.csv` | NASA POWER daily agro-climate, 5 cities × 365 days (2023) |
| `osm_*.csv` | OpenStreetMap Overpass features, 5 city bounding boxes |
| `osm_exposure_by_lga.csv` | Per-LGA OSM mapping-effort counts (analysis control) |
| `fao_food_security.csv` | One-row stub — FAOSTAT API returned HTTP 521 at freeze time |
| `provenance.json` | URL, timestamp, row count and licence for every pull above |

## What this directory does NOT contain

**The farmer survey microdata** underlying Table 1 of `manuscript/manuscript.qmd`
(n = 285, binary logistic regression on full-time participation).

This is a genuine gap, not an oversight in this file. The dataset appears nowhere in
the repository:

- no `.sav`, `.dta`, `.xlsx`, `.rds` or respondent-level `.csv` exists in the tree
- `MR. YOHAN FINAL BINDING.docx` (the thesis) contains **46 parts and zero embedded
  objects** — no attached spreadsheet, no data appendix
- it contains **zero long numeric runs**, i.e. no respondent-level rows in the text
- the full SPSS tables (`Omnibus`, `Model Summary`, `Wald`, `Exp(B`, `Hosmer`) are
  absent; only Nagelkerke is mentioned

## Why this matters

The manuscript reports `Nagelkerke = 0.348`, `AIC = 132.45`, `BIC = 145.90` for
n = 285 with 7 predictors. Those three numbers **cannot all be true**:

- an 8-free-parameter model at n = 285 requires a BIC−AIC gap of
  `8 × (ln 285 − 2) = 29.22`; the reported gap is 13.45, implying ~3.7 parameters
- AIC 132.45 implies deviance 116.45 → Nagelkerke ≈ 0.82, not 0.348
- Nagelkerke 0.348 implies deviance 293.07 → AIC ≈ 309.07, BIC ≈ 338.29

The manuscript now retains only Nagelkerke (the plausible value) and withdraws
AIC/BIC pending re-derivation.

## How to close the gap

1. Place the analytic file at **`data/raw/survey_urban_ag.csv`** (or `.xlsx` / `.dta` / `.sav`).
2. Required columns and coding are specified in **`analysis/regression/DATA_REQUEST.md`**.
   The critical unknown is the **unit of the income variable** — if it is coded in
   thousands of naira (conventional in this literature) then `OR = 1.005 per unit`
   is really `OR ≈ 1.05 per ₦10,000`, and the coefficient is fine while the reporting
   was the defect.
3. Run:

```pwsh
Rscript analysis/regression/01_logistic_fulltime.R
```

It emits real `−2LL`, AIC, BIC, McFadden/Cox-Snell/Nagelkerke, odds ratios with 95%
profile CIs, VIF, Hosmer–Lemeshow, a classification table and AUC — everything Table 1
needs and currently lacks.

## Ethics note

The survey collected **verbal informed consent** with **no personal identifiers
retained**. Depositing respondent-level records should therefore respect those terms:
either publish with consent, or publish a synthetic/perturbed demonstration dataset
plus the analysis code. `01_logistic_fulltime.R` runs against either.

## If the data cannot be recovered

The paper is still publishable. What it must then do:

- report the logistic model as **instrument-derived**, citing the thesis as the source
  of the estimates, and state plainly that the analytic dataset is not available
- drop AIC/BIC entirely (they cannot be verified)
- keep Nagelkerke, correctly labelled as a fit index rather than variance explained
- lead on the parts that ARE reproducible: the practice profile (§Results), which is
  fully documented, and the companion spatial study
