# Urban Agriculture and Urban Food Security in Nigeria

Two separate pieces of work share this repository. They are stated as two, because that is
what they are — an earlier version of this README presented them as one integrated study,
and they are not.

| | Output A | Output B |
|---|---|---|
| **What** | Field survey of urban farmers, Bauchi Metropolis | National spatial analysis of urban agriculture in OpenStreetMap |
| **Unit** | 285 farmers in 8 wards | 775 Local Government Areas, 5 cities |
| **Method** | Binary logistic regression (SPSS, thesis) | Moran's I, LISA, spatial lag/error, negative binomial |
| **Status** | Manuscript complete; **microdata not deposited** | Analysis complete and reproducible from frozen data |
| **Where** | `manuscript/manuscript.qmd` | `analysis/spatial/`, `results/` |

---

## Reproducible results (Output B)

Every number below is re-derived from the frozen data by
`analysis/spatial/audit_claims.R`. Run it — do not take this table on trust.

```pwsh
Rscript analysis/spatial/audit_claims.R     # re-verifies every claim in this README
Rscript build.R --audit                      # same thing, via the build entry point
```

| Result | Value |
|---|---|
| OSM features analysed | 484 across 5 city bounding boxes |
| LGAs assessed (GADM v4.1) | 775 |
| Global Moran's I, density (queen) | **0.300**, z = 17.61, p < 1e-69 |
| Global Moran's I, counts | 0.158, z = 8.47 |
| Rook contiguity (robustness) | I = 0.306 |
| Residual Moran, OLS → spatial lag | **0.256 → −0.036** |
| Spatial lag ΔAIC vs OLS | 92.3 (AIC −2485.2 → −2577.5), LR = 94.2 |
| LISA, Benjamini–Hochberg adjusted | 19 of 775 significant (raw p<0.05 → 23) |
| H3 (density declines with area), negative binomial | IRR = 0.212, p = 8.5e-11 |
| H3 under OSM-exposure control | **irr = 0.241, p = 1.5e-22** — survives and strengthens (ΔAIC = 20) |
| OSM confound, quantified | Spearman(counts, mapped highways) = **0.613**, p = 2.5e-09 |
| Join-count, "has any mapping" indicator | z = 30.3, p < 2e-16 |
| Points outside the five declared study states | 43 (8.9%) |

### What changed after audit, and why

This repository audits itself. Four findings from that audit changed the analysis:

- **The Gaussian model was wrong for the outcome.** Density is exactly zero for 95% of LGAs
  (skewness 15.5). Fitting a Gaussian spatial lag produced **265 of 775 negative fitted
  densities** — impossible quantities. Replaced with a negative binomial using area as an
  *offset* rather than a regressor, which also removes the ratio fallacy of regressing a
  ratio on its own denominator.
- **The "N = 34 LGA" climate model was pseudoreplication.** The 34 LGAs carried only **5
  distinct rainfall values** (rainfall R² on city dummies = 1.000). At the level the data
  actually replicate — 5 cities — the rainfall effect is p = 0.58, not p = 0.018. H2 is now
  reported as **untestable with the frozen data**.
- **LISA had no multiplicity control.** 23 raw hits against 38.8 expected false positives.
  Benjamini–Hochberg is now applied; the raw count being *below* chance expectation is itself
  evidence the normal approximation is conservative on a 95%-zero variable.
- **43 points were outside the study area.** Rectangular city bounding boxes leaked across
  state lines — the "Abuja" box returns more points in Niger State (17) than in the FCT (15).

A fifth finding is the one this repo is currently working on: **OSM density measures mapping effort as much as
it measures agriculture.** Kano is the best-mapped state in Nigerian OSM and also has the most
"urban agriculture" points. `scripts/fetch_osm_exposure.py` collected per-LGA building and highway counts
for all 78 target LGAs (39 with points plus 39 stratified controls), and
`analysis/spatial/12_exposure_control.R` conditions on them.

**The confound is real and quantified.** UA feature counts correlate with mapped highways
(Spearman 0.613, p = 2.5e-09) and with mapped buildings (0.410, p = 0.00019). LGAs *with* UA points have a
median of 33,465 mapped buildings; LGAs *without* have 17,347 — nearly double. Presence of a UA point and
"this place is mapped at all" are not independent facts.

**The area effect survives it, and strengthens.** Adding the mapped-building count as a second offset
improves the model rather than undermining it: coefficient −1.001 → −1.421, **ΔAIC = 20.0**,
p = 1.3e-09 → 1.5e-22. Larger LGAs remain less densely covered even once we control for how much of each
LGA is mapped, so **H3 is not an artefact of OSM completeness.** This is the most important robustness
result in the repository — the confound is real, and the finding outlives it.

What the exposure control does *not* rescue is the LISA geography: 18 of the 19 significant LGAs are
also LGAs with any points at all, so "where the clusters are" remains partly "where the mappers went".

![Summary of the spatial analysis](results/figures/summary_panel.png)

*One panel, four steps: raw OSM points → density normalised by area → LISA clusters after
FDR control → why the model family had to change.*

---

## Output A — the survey paper

`manuscript/manuscript.qmd` → `manuscript/manuscript.docx`. Times New Roman 12pt, 1.5 spacing,
286-word abstract, 5 keywords. A disciplined extract of the M.Tech thesis *Framework for the
Integration of Urban Agriculture in Bauchi Metropolis* (ATBU, July 2025), covering Objectives
2 and 4: existing practices, and determinants of full-time participation.

**The microdata is not in this repository.** The logistic model in Table 1 rests on 285
respondent records that appear nowhere in the tree — the thesis `.docx` contains 46 parts and
zero embedded objects. See `data/raw/README-survey-data.md`.

Consequences, all of which are reflected in the manuscript:

- The reported `AIC = 132.45` / `BIC = 145.90` pair is **internally impossible** alongside
  Nagelkerke = 0.348 for n = 285 with 8 free parameters (the implied BIC−AIC gap is 13.45;
  the required gap is 29.22). AIC and BIC are **withdrawn**; Nagelkerke is retained and
  correctly labelled as a fit index rather than "variance explained".
- `OR = 1.005` per unit of income is reported **per ₦10,000** with the coding stated, because
  the unit was never specified and the interpretation swings by 21 orders of magnitude.
- `analysis/regression/01_logistic_fulltime.R` runs the full correct analysis — real −2LL,
  AIC, BIC, McFadden, Cox-Snell, Nagelkerke, odds ratios with 95% profile CIs, VIF,
  Hosmer–Lemeshow, classification table, AUC — the moment the data is supplied.
  Required columns: `analysis/regression/DATA_REQUEST.md`.

---

## Repository layout

```
├── build.R                     single entry point; path-relative, runs the whole pipeline
├── render.ps1                  renders the two documents
├── renv.lock                   exact package versions actually used
├── analysis/
│   ├── spatial/                01 clean · 02 Moran/LISA · 03 maps · 04 extra figs
│   │                           05 LGA polys · 06 count models · 07 LISA FDR + point pattern
│   │                           08 honest climate · 09 lockfile · 10 study extent
│   │                           11 summary figure · audit_claims.R (the gate)
│   └── regression/             01 logistic re-analysis + DATA_REQUEST.md
├── data/
│   ├── raw/                    frozen API dumps + provenance.json + survey-data README
│   ├── processed/              cleaned layers
│   └── external/               GADM v4.1 boundaries (775 LGAs)
├── manuscript/                 manuscript.qmd → manuscript.docx
├── docs/                       methodology.qmd/pdf · statistical review · gap register
├── results/                    tables/, figures/, lga_lisa.gpkg
└── scripts/                    fetch_*.py (Python 3.12, ds-general) · build helpers
```

## Reproducing

```pwsh
# 1. Verify every claim in this README
Rscript analysis/spatial/audit_claims.R

# 2. Or run the whole pipeline
Rscript build.R

# 3. Render the documents
quarto render manuscript/manuscript.qmd --to docx
quarto render docs/methodology.qmd --to typst
```

Data is **frozen** — analysis reads only `data/raw/*.csv` and never the network, so results are
stable. Refreshing the exposure layer is the one networked step:
`python scripts/fetch_osm_exposure.py`.

## Environment

R 4.5.2 (`sf`, `spdep`, `spatialreg`, `spatstat`, `MASS`, `pscl`, `car`, `sandwich`) and
Python 3.12 (`pandas 2.2.3`, `requests 2.34.2`) in `ds-general`. Exact versions: `renv.lock`;
full dump: `docs/session-info.txt`. 17 of 24 packages were compiled under R 4.5.3 — they load
and run correctly, and the discrepancy is recorded rather than hidden.

## Limitations

- **OSM completeness confound.** Real and now measured: UA counts correlate with mapped highways at
  ρ = 0.613. The area effect (H3) survives the control; the LISA *geography* does not fully.
- **`landuse=farmland` ≠ urban agriculture.** Inside a city rectangle it also captures rural
  farmland. A corrected pull would use GADM polygons or an urban-extent mask.
- **H2 (aridity) is untestable** with city-centroid rainfall. Needs CHIRPS/ERA5/TAMSAT at LGA
  resolution.
- **The survey microdata is unavailable**, so the logistic results are instrument-derived.
- **The two outputs are unrelated.** The survey is Bauchi; the spatial analysis is five cities.
  They are not a single study and are not presented as one.

## Provenance and licence

Frozen API pulls are recorded in `data/raw/provenance.json` with URL, timestamp, row count and
licence for every entry. Sources: OpenStreetMap Overpass (ODbL © OpenStreetMap contributors),
GADM v4.1 (CC BY 4.0), World Bank Indicators (CC BY 4.0), NASA POWER (public domain).

## History

This repository was audited on **15 October 2026**; the findings are in
`docs/statistical-review-2026-10-15.md`, the remediation plan in `docs/remediation-phases.md`,
and the current open-gaps register in `docs/section-scores.md`. The audit discovered the four
modelling errors listed above, and the earlier version of this README — which advertised six
figures, "why this repo is exceptional", and statistics that did not reproduce — was replaced.

Original context: the work was prepared for the Federal Polytechnic Kaltungo 2nd Annual
National Multidisciplinary Conference (13–15 October 2026), sub-theme 6. The conference
deadlines have passed; this is now maintained as a journal and portfolio artefact.
