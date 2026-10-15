# Gap register — replacing the former self-assessment

**Supersedes:** the previous `section-scores.md`, which scored all 21 sections 5.0/5.0.
That document was removed on 15 October 2026 because it scored as "ready" several
sections that the audit later found unsupportable (impossible fit statistics, a
five-city model presented as N = 34, a Gaussian fit to a 95%-zero ratio, 8.9% of
points outside the study area). A self-assessment that does not survive its own
audit is worse than none.

This file is the honest replacement: what is **verified**, what is **blocked**, and
what is **unverified**. Machine-checkable claims are re-derived by
`analysis/spatial/audit_claims.R` — run it, do not trust this file.

Last reviewed: **15 October 2026**  
Report: **`docs/spatial-report.html`** — rendered account of the spatial study (HTML + 19 pp PDF)  
Gate: **`analysis/spatial/verify_report_claims.R`** — 61 checks, 0 discrepancies

---

## A. Verified reproducible

These were re-derived from the frozen data and reproduce exactly. Re-run the audit
script to confirm.

| Claim | Value | Status |
|---|---|---|
| Global Moran, density (775 LGAs, queen) | `I = 0.2999`, `z = 17.613`, `p = 9.73e-70` | ✅ verified |
| Global Moran, counts | `I = 0.1584`, `z = 8.466` | ✅ verified |
| Rook contiguity (robustness) | `I = 0.3058` | ✅ verified |
| Spatial lag `AIC` / `rho` | `−2577.50` / `0.4192` | ✅ verified |
| `LR`(OLS → lag) | `94.249` | ✅ verified |
| Residual Moran, OLS → lag | `0.2557 → −0.0355` | ✅ verified |
| Kano-excluded Moran | `I = 0.274` | ✅ verified |
| Points reconciled to raw CSV | 484 / 484 | ✅ verified |
| Abstract length | 286 words (limit 150–300) | ✅ verified |
| Sampled wards sum to n | `120+58+35+26+22+15+15+15 = 306` | ✅ verified |
| Krejcie & Morgan for N = 1500 | 306 | ✅ verified |

## B. Fixed in this remediation

| Was | Now | Where |
|---|---|---|
| `AIC = 132.45, BIC = 145.90` reported with Nagelkerke 0.348 — mutually impossible | AIC/BIC withdrawn; Nagelkerke retained and correctly labelled | `manuscript.qmd` §Results, `analysis/regression/01_logistic_fulltime.R` |
| "34.8% variance explained" | Corrected: Nagelkerke is a fit index, not variance explained | `manuscript.qmd` §Results |
| `OR = 1.005 per unit` income (unit unstated) | Reported per ₦10,000 with the coding stated | `manuscript.qmd` Table 1 + interpretation |
| Pilot dated *after* fieldwork | Date removed rather than guessed; flagged for the author | `manuscript.qmd` §Methodology |
| "Mean plot ≈ 0.5 ha" only | Median added, skew explained | `manuscript.qmd` §Results |
| LISA: 23 raw hits, no multiplicity control | BH-FDR applied; 19 survive; conservative test documented | `analysis/spatial/07_lisa_fdr_pointpattern.R` |
| `N = 34` climate model | Replaced by honest `K = 5` city-level treatment | `analysis/spatial/08_climate_honest.R` |
| Gaussian model on 95%-zero ratio | NB with `offset(log(area))` + hurdle comparison | `analysis/spatial/06_count_models.R` |
| 43 points (8.9%) outside study states, silently dropped | Quantified and documented | `analysis/spatial/audit_claims.R` §5 |
| 45 bib entries, 21 uncited, 2 placeholder DOIs, duplicate entry | 24 entries, all cited, no placeholders, no duplicates | `manuscript/references.bib` |
| `docs/references.bib` forked from manuscript without warning | Synced by `build.R` step 0 | `build.R` |
| Build scripts hardcoded `D:\YohannaPaper` | Path-relative | `render.ps1`, `build.R` |

## C. Blocked — needs the author

| Gap | Why it blocks | What unblocks it |
|---|---|---|
| **Survey microdata (n = 285)** | Never committed; not recoverable from any artefact in the tree. Without it the logistic model cannot be re-estimated. | Supply the file per `analysis/regression/DATA_REQUEST.md` |
| **Pilot date** | Source says 6–11 Mar 2024; fieldwork ended 8 Feb 2024. One is wrong. | The correct date |
| **Income variable unit** | Determines whether `OR = 1.005` is meaningful or absurd | The SPSS variable coding |

## D. Unverified / open

| Item | Status | Note |
|---|---|---|
| Hosmer–Lemeshow, AUC, VIF for the logistic model | ⏳ blocked | Computed by `01_logistic_fulltime.R` once data arrives |
| H2 (aridity) | ❌ **not testable with frozen data** | Rainfall is a city-level constant. Needs CHIRPS/ERA5/TAMSAT at LGA resolution |
| OSM exposure control | ✅ **resolved** | Confound is real (ρ=0.613 with mapped highways); H3 survives and strengthens (ΔAIC 20.0) |
| Witnessing of `terra` suitability | ❌ not implemented | `terrain` suitability was claimed in earlier README text; no script uses `terra` |
| R version | ⚠️ mismatch | Docs claim 4.5.2; installed packages built under 4.5.3 |
| `manuscript.docx` page count | ✅ **verified 11 pp** | Confirmed in Word on 15 Oct 2026 via `scripts/read_docx_stats.py` (attaches to the open document). 11 pages against the flyer's 12-page limit — **1 page of headroom.** Normal style is Times New Roman 12 pt, 1.5 line spacing, 1 in margins, as the flyer requires. |

## F. The strongest result in the repository

The confound nobody had addressed — that "urban agriculture density" is partly "where people
happen to have mapped" — was measured directly, and the main finding outlived it.

| | Without control | With mapped-building offset |
|---|---:|---:|
| Area coefficient | −1.0010 | **−1.4213** |
| p | 1.3e-09 | **1.5e-22** |
| AIC | 374.2 | **354.2** |

And the confound itself, for honesty:

- Spearman(UA count, mapped highways) = **0.613**, p = 2.5e-09
- Spearman(UA count, mapped buildings) = 0.410, p = 1.9e-04
- Median mapped buildings, LGAs *with* points **33,465** vs *without* **17,347**

So the OSM layer *is* partly a mapping-effort layer — that is now proved, not suspected — and
the area effect (H3) is **not** explained by it. The LISA *geography* remains partly a mapping
artefact (18 of 19 significant LGAs also have any points at all), and that is stated.

## E. Honest summary of fit to purpose

- **As a spatial analysis:** the core inference (clustering, spatial dependence, area effect)
  is sound and now tested with the right model family. The main remaining weakness is the
  OSM-completeness confound, which the exposure control is designed to address.
- **As a survey paper:** depends entirely on recovering the microdata. Without it, the
  logistic results must be presented as instrument-derived and the AIC/BIC dropped.
- **As a portfolio artefact:** strong once the README leads with reproducible numbers
  rather than the conference framing.
