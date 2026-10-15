# Phases — Urban Agriculture and Urban Food Security in Nigeria

> Conference: Federal Polytechnic Kaltungo, 13–15 Oct 2026 — Abstract **5 Oct**, Full paper **9 Oct** (TNR 12pt 1.5 ≤12pp → `fpksstconf2026@gmail.com`)
> Repo: `batestguy/urban-agriculture-and-urban-food-security-in-nigeria` | Local: `D:\YohannaPaper` (Drive D ↔ GitHub mirror)
> Pipeline: `scripts/fetch_*.py → data/raw/*.csv (+provenance.json) → analysis/spatial/*.R → quarto → manuscript/manuscript.docx`
> Status: Logged in `PROGRESS.md` after each phase, mirrored to `README.md:5`.

---

## Phase 0 — Environment & Repo Verification (30 min) ⬅ STARTING NOW
**Goal:** Confirm interpreters before any fetch; unblock Word rendering.
**Do:**
- `conda list -p C:\Users\TOSHIBA\ds-general` — verify `requests`, `pandas 2.2.3`, confirm `geopandas` **missing** (stay on R `sf` primary; only `conda install -p ... geopandas` if later needed).
- `Rscript -e "packageVersion(c('sf','terra','spdep','spatialreg','dplyr','readr','tidyr','ggplot2'))"` — `spatialreg` split from `spdep` 1.2+; install if absent. Known installed: `sf 1.1.2`, `terra 1.9.46`, `spdep 1.4.2`.
- `quarto check` — expect 1.9.38 + pandoc 3.8.
- `git -C D:\YohannaPaper status` + `remote -v` — branch `master` tracks `origin/master`.
- **Create missing `manuscript/_quarto.yml`** with docx `reference-doc` TNR config (was deleted; without it pandoc defaults to Calibri).
**Outputs:** Verified env, `_quarto.yml` restored, ready for fetches. **Risk:** `numpy 1.x vs 2.x` / `pandas 2.x vs 3.0` split — pin all Python fetches to `ds-general`.
**Push:** `chore: verify envs, add quarto docx template`

## Phase 1 — API Data Acquisition (Ordered by Reliability)
**1a World Bank (5 min, safest first):** `fetch_worldbank.py --out data/raw/worldbank_ng.csv` (`SP.URB.TOTL, AG.PRD.FOOD.XD, SN.ITK.DEFC.ZS` 2000-2024). If `SN.ITK.DEFC.ZS` >50% NA → drop as outcome.
**1b Overpass OSM (isolated, riskiest):** test single city `fetch_osm_urban_ag.py --city Gombe --out osm_gombe_test.csv` then 4 more. Overpass POST `landuse=allotments/farmland/farmyard + leisure=garden` for Abuja/Lagos/Kano/Port Harcourt/Gombe bboxes. Mitigations for 406: User-Agent, alternate endpoint `overpass.kumi.systems`, single-tag split, or Geofabrik PBF fallback. Completeness bias → normalize to density/km².
**1c NASA POWER (loop 5 cities):** `fetch_nasa_power.py --city Abuja --start 20230101 --end 20231231` (loop all; decide consistent window e.g. 2020-2024). Verify `CITY_COORDS` lat/lon order.
**1d FAO (expect stub):** `fetch_fao.py` likely 403 → manual FAOSTAT FS dump to `data/external/faostat_food_security.csv`.
**End check:** `data/raw/provenance.json` has 4+ entries with `timestamp_utc/url/license`; `data/raw/*.csv` 4-7 files; `data/processed/` still empty.
**Push:** `data: freeze WB+OSM (+NASA POWER)`

## Phase 2 — Spatial Prerequisites — GADM Shapefile (Parallel with 1)
- Download `gadm41_NGA_2.shp` (LGA level 2, 774 LGAs, 50-120MB) from `gadm.org` or HDX COD-AB → place as `data/external/gadm41_NGA_2.shp` (name expected by `02_spatial_stats.R:8`). Verify `sf::st_read` + `NAME_2` + `st_is_valid`. **If >50MB, do NOT commit** — add `data/external/*.shp` to `.gitignore`, keep locally, note URL/SHA256 in provenance.
**Push:** `docs: GADM LGA shapefile local, gitignore large file`

## Phase 3 — Analysis Pipeline (After 1+2)
**3.1 `Rscript analysis/spatial/01_clean.R`:** Reads `osm_urban_ag.csv` + `worldbank_ng.csv` → writes `data/processed/osm_urban_ag.gpkg` + `worldbank_ng_wide.csv`. Patch to also aggregate NASA POWER annual means. Validate CRS 4326, no NA lat/lon.
**3.2 `Rscript analysis/spatial/02_spatial_stats.R`:** Needs GADM; `poly2nb queen → nb2listw → moran.test + localmoran → results/lga_lisa.gpkg` (`lisa_I`, `lisa_p`). Gap: `lga$n` raw counts → must compute `density = n / st_area`; national World Bank can't join to LGA → Moran on density itself or source NLSS/DHS subnational proxy (document as limitation). Regression `lagsarlm/errorsarlm` stub needs covariates `density ~ rainfall + temp + popdensity`.
**3.3 `Rscript analysis/spatial/03_maps.R`:** `osm_points.png` + need `lisa_map.png` choropleth + suitability overlay (`terra` weighted).
**Push:** `analysis: clean, Moran/LISA, maps`

## Phase 4 — Manuscript Writing (Abstract→Methods→Results→Discussion)
**Order:** Methods first (Hull Ch3 criteria, before numbers) → Data/Study Area (after provenance) → Abstract draft by 28 Sep (`abstract.docx` for email, mirror exact sub-theme phrase `Climate-Smart Agriculture, Food Security and Rural Transformation`) → Results 1-2 Oct (replace Table1/Fig1/Table2 placeholders with actual `moran.test`/LISA/regression) → Discussion/Conclusion (link to #10/#13, Urban-vs-Rural bridge, 2 policy levers) → Ethics/Reflections → References (expand from 1 to 15-20).
**Push:** `manuscript: methods+results draft`

## Phase 5 — Word Compliance & Rendering (Continuous, Final 7-9 Oct)
- Restore `manuscript/_quarto.yml` with `reference-doc` TNR 12pt template; `quarto render manuscript.qmd --to docx` → open in Word → verify **TNR 12pt, 1.5 spacing, ≤12 pages** (`File → Info`), table/figure captions within margins, references resolve. If >12pp → trim suitability overlay to paragraph, shrink figures 6×4in, collapse tables.
- Checklist: abstract 150-300w word count, ≤6 keywords, Styles Normal = TNR, refs `{#refs}`, ethics present, reproducibility note `data/raw/provenance.json`.
**Push:** `manuscript: page-limit trim`

## Phase 6 — Submission (5 Oct Abstract → 9 Oct Full Paper)
- **5 Oct:** email `abstract.docx` to `fpksstconf2026@gmail.com` + pay fee `First Bank 2047116096` (Physical ₦13k / Virtual ₦10k).
- **9 Oct:** email `manuscript/manuscript.docx`. Tag push `submit: abstract` / `submit: full paper TNR12pt 1.5 ≤12pp`.
- Git cadence: commit after each phase (≥6 pushes); every push mirrors Drive D → GitHub.

---

## Timeline
- **25 Aug–15 Sep:** Phases 0-1-2 (API freezes + GADM) — 3 weeks, most risk.
- **16-30 Sep:** Phases 3-4 (analysis + methods/data writing).
- **1-4 Oct:** Fill results, draft abstract, render test.
- **5 Oct:** Abstract deadline.
- **6-8 Oct:** Polish discussion, page trim, final render.
- **9 Oct:** Full paper deadline.

## Risks Register
| Risk | Trigger | Mitigation |
|---|---|---|
| Overpass 406/Timeout | POST returns 406/timeout | User-Agent, endpoint switch, single-tag split, Geofabrik PBF fallback |
| geopandas missing | Not in ds-general | Stay on R sf primary |
| GADM >50MB | .shp 80-120MB | .gitignore, keep local, note provenance |
| ≤12pp overflow | 14-15pp render | Trim overlay, shrink figures/tables |
| spatialreg missing | `lagsarlm` not found | `install.packages('spatialreg')` |
| national vs LGA mismatch | WB national only | Moran on density, or NLSS/DHS proxy |
| FAO 403 stub | fenixservices 403 | Manual FAOSTAT CSV to data/external |
| OSM completeness bias | Gombe n≈0 | Density/km² + sensitivity without Lagos |

---
*Next executable (Phase 0): `conda list -p C:\Users\TOSHIBA\ds-general | Select-String "requests|geopandas|pandas|numpy"` → `Rscript -e "packageVersion(...)"` → `quarto check` → `git status`.*
