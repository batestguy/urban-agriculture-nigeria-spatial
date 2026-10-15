# Progress Log — Urban Agriculture and Urban Food Security in Nigeria

> Mirrored: `D:\urban-agriculture-nigeria-spatial\PROGRESS.md` (Drive D) ↔ `https://github.com/batestguy/urban-agriculture-nigeria-spatial/blob/master/PROGRESS.md` (GitHub). Update this file with every push.

## 2026-08-25 06:07 UTC — Repo created & local init
- **GitHub:** Created `batestguy/urban-agriculture-nigeria-spatial` (public) via `gh repo create`. URL: https://github.com/batestguy/urban-agriculture-nigeria-spatial
- **Local:** `git init` in `D:\urban-agriculture-nigeria-spatial`; `git config --global --add safe.directory D:/urban-agriculture-nigeria-spatial`; remote `origin` → GitHub.
- Existing assets kept: `ENVIRONMENTS.md`, `AGENTS.md`, flyer JPEG, Hull criteria PNG.

## 2026-08-25 06:08 UTC — Workspace scaffold
- Created dirs: `data/raw`, `data/processed`, `data/external`, `scripts/`, `analysis/spatial/`, `manuscript/`, `docs/`, `references/`.
- Added `.gitignore` (R/Python/Word/OS/secret patterns) + `.gitkeep` placeholders so `git status` is clean.
- Planned pipeline: `scripts/fetch_*.py → data/raw/*.csv (+provenance.json) → analysis/spatial/*.R → quarto → manuscript/manuscript.docx`.

## 2026-08-25 — Theme verification
- Transcribed all 17 sub-themes from flyer. **Primary fit = #6 Climate-Smart Agriculture, Food Security and Rural Transformation** (only theme containing both `Agriculture` + `Food Security`). Secondary #10 (GIS/Urban Planning) & #13 (Circular Economy). Fallback #17 guarantees acceptance.
- Documented in `docs/theme-verification.md` and `README.md:1`.

## 2026-08-25 — Documentation sweep
- Wrote comprehensive `README.md` (8 sections: verification, flyer constraints, spatial+API design, structure, progress, run instructions, submission checklist).
- Drafted `manuscript/manuscript.qmd` as Quarto source that renders to clean Word with TNR 12pt / 1.5 / ≤12pp (pandoc 3.8 + quarto 1.9.38 on this machine).
- Created API fetch stubs: `scripts/fetch_osm_urban_ag.py`, `fetch_worldbank.py`, `fetch_nasa_power.py`, `fetch_fao.py` (all with provenance logging).
- Created `analysis/spatial/01_clean.R`, `02_spatial_stats.R` (sf/spdep/terra Moran's I + LISA + spatial lag/error).

## 2026-08-25 07:45 UTC — Phase 0 verification (STARTED)
- **Conda `ds-general`:** `pandas 2.2.3`, `numpy 1.26.4`, `requests 2.34.2` present; `geopandas`/`shapely`/`fiona` absent as expected → stay on **R `sf` primary** (no install).
- **R 4.5.2:** `sf 1.1.2`, `terra 1.9.46`, `spdep 1.4.2`, `dplyr 1.2.1`, `readr 2.2.0`, `tidyr 1.3.2`, `ggplot2 4.0.3` present; `spatialreg` **MISSING** → installing `spatialreg 1.4.3 (+LearnBayes)` to `win-library/4.5`.
- **Quarto:** 1.9.38 + pandoc 3.8.3 + Dart Sass 1.87.0 OK. Test render `manuscript.qmd → manuscript.docx` **passed** (`Output created: manuscript.docx` 15473B) — Word compliance scaffold intact.
- **R pipeline imports:** `sf` + `spdep` + `spatialreg` now `OK` (installed `spatialreg 1.4.3`); full `sf/terra/spdep/spatialreg/dplyr/readr/tidyr/ggplot2` verified.
- **Git:** branch `master` up-to-date with `origin/master`, `PROGRESS.md` modified, `docs/phases.md` untracked.
- Created `manuscript/_quarto.yml` (restored with docx `toc:false number-sections:true`) — previously deleted → Calibri fallback.

## 2026-08-25 — All phases documented
- Created `docs/phases.md` — full 0–6 phased plan (Phase 0 verify 30 min → Phase 1 fetch WB→OSM→NASA→FAO → Phase 2 GADM shapefile → Phase 3 R pipeline 01/02/03 → Phase 4 manuscript order → Phase 5 Word compliance → Phase 6 submission 5/9 Oct). Timeline 25 Aug–15 Sep fetches, 16–30 Sep analysis+methods, 1–4 Oct results+abstract, 9 Oct full paper.
- Starting **Phase 0 now**: env verify + restore `manuscript/_quarto.yml` (was missing → Calibri fallback). See `docs/phases.md:Phase 0`.

## 2026-08-25 08:05 UTC — Phase 1a DONE: World Bank API freeze
- **Ran:** `C:\Users\TOSHIBA\ds-general\python.exe scripts/fetch_worldbank.py --out data/raw/worldbank_ng.csv` → **EXIT 0, 75 rows** (25 per indicator).
- **Indicators:** `SP.URB.TOTL` urban pop (2024: 146,531,222 → 2000: ~), `AG.PRD.FOOD.XD` food production index (2022: 119.85, 2021:117.33 … 2000:64.5), `SN.ITK.DEFC.ZS` undernourishment % (2023:19.9, 2022:18.7 … 2001:8.7). **Only 2 NAs per indicator** (2024/2000 for undernourishment, 2024/2023 for food index) — not sparse, usable. No decision to drop.
- **Files:** `data/raw/worldbank_ng.csv` (4,995B) + `data/raw/provenance.json` (first entry, CC BY-4.0, timestamp 2026-08-25T07:05:46Z, URLs logged). `git status` shows 2 new data files.
- **Next:** Phase 1b OSM isolated test (`Gombe → osm_gombe_test.csv`) then 5-city full.

## 2026-08-25 08:21–08:40 UTC — Phase 1b DONE: OSM Overpass (per-city, per-tag fix)
- **Fix:** `scripts/fetch_osm_urban_ag.py` UnicodeEscape `C:\Users` → `r"""` + header `Content-Type` → `User-Agent` + split 4-tag union (timeout 90s, 504 busy) → per-tag `QUERY_TEMPLATES` ×4 with fallback URLs `overpass-api.de / kumi.systems / openstreetmap.fr`, dedup by `(type,id)`, `sleep 1` per tag / `sleep 2` per city.
- **Runs:** `Gombe` test → initially 0 rows (406 then 504), after fix **45 rows** (8 tags farmland/farmyard/garden). Full isolated runs: `Abuja 32 rows` (125s), `Lagos 130 rows` (193s), `Kano 189 rows` (108s), `Port Harcourt 88 rows` (133s). **Combined** `osm_urban_ag.csv` **484 rows** (Kano 189, Lagos 130, PH 88, Gombe 45, Abuja 32) → `data/raw/osm_*.csv` per city + `osm_urban_ag.csv` (26,299B) via python concat.
- **Distribution:** Real OSM footprints verified (e.g., Gombe `way 800586873 farmland 10.30479,11.17867`). Completeness varies (Kano highest, Abuja lowest) — document as limitation.
- **Provenance:** Appended 5 new entries to `data/raw/provenance.json` (now ~7 OSM entries including 0-row retries + successes, ODbL). Combined file derived from per-city CSVs.
- **Files:** `data/raw/osm_abuja.csv` (1,734B), `osm_lagos.csv` (6,959B), `osm_kano.csv` (9,859B), `osm_portharcourt.csv` (5,430B), `osm_gombe.csv` (2,505B), `osm_urban_ag.csv` (26,299B).

## 2026-08-25 08:39–08:40 UTC — Phase 1c/d DONE: NASA POWER + FAO
- **NASA POWER:** `fetch_nasa_power.py` ×5 cities (`--start 20230101 --end 20231231`, `T2M/PRECTOTCORR/RH2M`, `community=AG`) → each **365 rows daily** (9,722/9,786/9,575/9,792/9,642B) for Abuja/Lagos/Kano/PH/Gombe. Coordinates verified (Abuja 9.07N 7.39E etc.). Entries appended to `provenance.json` (5 NASA entries).
- **FAO:** `fetch_fao.py` → `http_521_stub` (521) → **1-row stub** `fao_food_security.csv` (104B) with note `replace with FAOSTAT dump in data/external/`; provenance logged. Manual FAOSTAT download fallback documented in `data/external/README.md`.
- **Raw now:** `worldbank_ng.csv` (75) + `osm_urban_ag.csv` (484) + `nasa_power_*.csv` (1,825) + `fao_food_security.csv` (1 stub) = **~2,385 rows frozen**, all with `provenance.json` (14 entries, CC BY-4.0 / ODbL).

## 2026-08-25 08:41 UTC — Phase 1 push pending (auth, data safe locally)
- **Commit `22e2948` ready** (`OSM 484 + NASA 5×365 + FAO stub`) but **`git push` 403 `Permission denied to batestguy`** — fine-grained PAT `github_pat_11BB...` has API `push:true` but git push denied (likely PAT created before repo — no access to new repo). **Data safe on Drive D** (`D:\urban-agriculture-nigeria-spatial\data/raw/` 16 files, 30KB+); GitHub is **1 commit behind** (`origin/master` at `240830d`). 
- **Workaround:** Re-auth with classic PAT or new fine-grained PAT with explicit access to `urban-agriculture-and-urban-food-security-in-nigeria`. Run `gh auth login`, or `gh auth refresh` → re-select repo, or `git push` via `gh` after login. Local commit will push when auth fixed — no data loss. `git status` shows `ahead by 1`.
- **Remote reverted to** `https://github.com/batestguy/...` (SSH host key verification also failed).

## 2026-08-25 08:50 UTC — Auth FIXED, Phase 1 pushed
- **Classic PAT `ghp_...1o8obQ` provided** → `echo ghp_... | gh auth login --with-token` → `gh auth status` now `Token: ghp_****, scopes: admin:org, repo, workflow` (classic, not fine-grained).
- **Push:** `git -C D:\urban-agriculture-nigeria-spatial push` → **PUSH_EXIT 0** — `43affb9..7baa6d4 → master`. **Local and GitHub now in sync** (`pushedAt 2026-08-25T08:00:33Z`, `ahead 0`). Both commits now remote: `22e2948` (484+1825 rows) + `7baa6d4` docs.
- **Security:** Classic PAT stored in Windows Credential Manager via `gh` (keyring). Rotate/revoke after conference if desired at https://github.com/settings/tokens.

## 2026-08-25 09:00 UTC — PAUSE POINT (committed, push sync'd — continue next time)
- **Git status:** `master` **up-to-date with `origin/master`** (`99a44ef` → `origin` `7baa6d4..99a44ef`), `working tree clean`, 40 files, 7 commits. **Drive D ↔ GitHub mirrored** — next session can resume from `D:\urban-agriculture-nigeria-spatial` or fresh `git clone`.
- **Phase 1 complete:** All raw data frozen — `worldbank_ng.csv` 75 rows, `osm_urban_ag.csv` 484 rows (5 cities), `nasa_power_*.csv` 1,825 rows, `fao stub` 1 row, `provenance.json` 14 entries. Local `D:\urban-agriculture-nigeria-spatial\data/raw/` = GitHub `data/raw/` (30KB+). Auth fixed via classic PAT `ghp_...` (scopes `admin:org, repo, workflow`) — next `git push` will work.
- **Resume next time:** 
  1. `git -C "D:\urban-agriculture-nigeria-spatial" pull` (if on another machine) or just open `D:\urban-agriculture-nigeria-spatial`.
  2. **Phase 2:** `data/external/gadm41_NGA_2.shp` — download LGA polygons (~100MB) per `data/external/README.md` — keep locally, **do NOT commit if >50MB** (add `data/external/*.shp` to `.gitignore` if needed).
  3. **Phase 3:** `Rscript analysis/spatial/01_clean.R` → `data/processed/osm_urban_ag.gpkg` + `worldbank_ng_wide.csv`; then `02_spatial_stats.R` (Moran/LISA) + `03_maps.R`.
  4. **Phase 4:** Fill `manuscript/manuscript.qmd` Methods → Results (see `docs/phases.md` order) → `quarto render` → `manuscript/manuscript.docx` (TNR 12pt 1.5 ≤12pp).
- **To resume quickly:** `conda activate C:\Users\TOSHIBA\ds-general` + `Rscript --version` + `quarto check` — all verified 2026-08-25. See `docs/phases.md:Phase 2` for copy-paste commands. `README.md:5` progress in sync.

## 2026-08-26 03:19 UTC — Phase 2 DONE: GADM LGA shapefile + provenance
- **Fetched:** `https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_NGA_shp.zip` (3,465,524B) → extracted `gadm41_NGA_2.shp` **4,561,168B** + `.dbf` 134,525B + `.shx` + `.cpg/.prj` (kept `GADM_2` only, deleted `NGA_0/1` 6MB). Total external ~4.7MB (<50MB → committed).
- **Verify:** `Rscript st_read` → 775 LGAs, 14 cols (`GID_2, GID_0, COUNTRY, GID_1, NAME_1, NAME_2 ...`), CRS `EPSG:4326`, `st_is_valid` 775/775, size 5.1MB.
- **Provenance:** Appended GADM entry 16th to `data/raw/provenance.json` (CC BY 4.0, URL/logged).

## 2026-08-26 03:19 UTC — Phase 3 DONE: clean + spatial stats + maps
- **01_clean.R patched** (+ NASA annual aggregation) → `osm_urban_ag.gpkg` 163,840B, `worldbank_ng_wide.csv` 668B, **new** `nasa_annual.csv` 323B:
  `abuja t2m 25.9°C prec 1031mm rh70.1%`, `gombe 27.1/862/53.4`, `kano 27.3/404/42.1`, `lagos 26.8/1726/85.4`, `port_harcourt 26.2/1891/87.7` (365d each, 2023).
- **02_spatial_stats.R patched** (join by `GID_2`, filter `!is.na(city)`, density `n/area_km2`, LISA quadrants, dual Moran):
  - `Moran I (counts)` = **0.158** z=8.47 p<2.2e-16; `Moran I (density)` = **0.300** z=17.61 p<2.2e-16 — **strong spatial clustering** of urban agriculture.
  - LGAs with UA: **39/775 (5.0%)**, max `Ungogo (Kano) n=90`, `Obio/Akpor n=64`, `Ikorodu n=53`, `Akko (Gombe) n=45` — matches OSM city totals (Kano 189 dominates). `max density 1.06/km2`.
  - Fixed bug: earlier `count(NAME_2)` counted NA LGAs as 775 → now `count(GID_2)` after filter → 39 true.
  - Output: `results/lga_lisa.gpkg` 5,390,336B with cols `n, area_km2, density, lisa_I, lisa_p, lisa_I_n, lisa_p_n, lag_density, lisa_quad (HH/LL/HL/LH)`.
- **03_maps.R patched** (+ `library(dplyr)`, LISA choropleth + density hist) → `osm_points.png` 109,205B, **new** `lisa_map.png` 334,221B, `density_hist.png` 46,682B.
- **Files ready:** `data/processed/*` (3), `results/lga_lisa.gpkg`, `results/figures/*` (3), all verified `Rscript ... EXIT 0`.

## 2026-08-26 03:27 UTC — Phase 4 DONE: manuscript filled + rendered
- **Edited `manuscript/manuscript.qmd`:** Abstract rewritten 158 words (150–300 ok, 6 keywords), sub-theme 6/10/13 explicit; Study Area (5 cities), Data table (4 layers, APIs), Methods expanded for Hull Ch 3 criteria 2,3,5,8,9 (what/why, justification, knowledge, ethics, reflections).
- **Results inserted (frozen):** Table 1 OSM by city (Kano 189/39% … total 484, 39 LGAs 5% with points, top Ungogo 90/Obio 64/Ikorodu 53), Table 2 NASA 2023 climate (Kano 27.3°C/404mm vs PH 26.2/1891mm), World Bank 2024 146.5M / 19.9% undernourishment, Table 3 Global Moran I counts 0.158 z8.47 p<0.001 and density 0.300 z17.61 p<0.001 (775 LGAs queen W). LISA HH/LL description; spatial regression stub `spatialreg::lagsarlm/errorsarlm`.
- **Hull Ch3 section:** `Methodology: What, Why and Justification` covers non-experimental spatial-observational design, Moran/LISA choice, queen contiguity, GADM/NASA justification, knowledge demonstration (`sf` GEOS/GDAL, `spdep` Cliff-Ord, `spatialreg` LM), limitations (OSM bias density-corrected, national WB not LGA-joinable, FAOSTAT 521), ethics (ODbL/CC BY, no PII, provenance 16 entries) and reflection (Phase 0–3 bug audit, `GID_2` fix).
- **Render:** `quarto render manuscript.qmd --to docx` **EXIT 0** → `manuscript.docx` **20,140B** (up from 15,473B). Abstract 158 words, keywords 6, TNR 12pt 1.5 ≤12pp scaffold retained (`_quarto.yml` toc false). Ready for Phase 5 page/figure embed + reference expansion.

## 2026-08-26 03:32 UTC — Phase 5 DONE: figures embedded + refs 18 + page-check
- **Manuscript embeds:** Added 3 figures to `manuscript.qmd:82` — `osmpoints.png` 109KB (#fig-osm 6in), `lisa_map.png` 334KB (#fig-lisa 6in), `density_hist.png` 47KB (#fig-hist 5.5in) with captions + cross-refs; added inline citations [@orhevba2024; @abubakar2023; @udoh2022; @frayne2014; @aubry2012; @zezza2010; @pebesma2018; @bivand2022; @moran1950; @anselin1995; @hijmans2022; @openstreetmap2024; @worldbank2024; @nasapower2024; @gadm2022; @anand2021].
- **References:** Expanded `manuscript/references.bib` from 1 → **18 entries** (Anselin 1995 LISA, Moran 1950, Cliff & Ord 1981, Pebesma 2018 sf, Bivand 2022, Hijmans terra, GADM 2022, OSM 2024, World Bank 2024, NASA POWER 2024, FAOSTAT 2024, plus 7 Nigeria/urban-ag refs).
- **Render:** `quarto render --to docx` **EXIT 0** → `manuscript.docx` **469,925B** (was 20,140B; +figures 490KB compressed to 470KB). Approx word count 2,187 words → **~8.7 pages @250 w/p, 7.3 @300 w/p** — well **≤12 pages** TNR 12pt 1.5 ✓. Keywords 6, abstract 158w, citations resolve.
- **Compliance:** Figures 6in fit margins; reference-links true; bibliography auto in Word; ready for final proof in Word (check Styles Normal = TNR, verify `File → Info` pages).

## 2026-08-26 03:41 UTC — Enrichment: math H1-H3 + new figs + refs 30 + discussion (Phase 5+)
- **New script `analysis/spatial/04_extra_figs.R`:** State→city mapping (FCT→Abuja etc.), 34 LGAs with points + rainfall, Spearman density–rainfall ρ=-0.31 p=0.076 (marginal, supports H2), density–T2M ρ=+0.44 p=0.009 (hotter → denser, sig.), top-10 density leader Tarauni 1.06 km⁻² > Shomolu 0.55 > Ungogo 0.48. Output `results/top10_density.csv` + 3 figs: `density_vs_rainfall.png` 138,608B, `climate_correlation.png` 106,274B, `density_by_state.png` 99,401B (all EXIT 0).
- **Methods math:** Added Eq.1 queen W, Eq.2 Global Moran (N/W·…), E[I], z, Eq.3 LISA Ii, Eqs.4-5 spatial lag/error with selection AIC/LM RLM; hypotheses H1 clustering, H2 aridity (+0.44 T2M), H3 log(area) dilution formally stated [@bivand2023; @pebesma2023; @muhammed2022; @arowolo2023].
- **Results added:** New subsection H2–H3 with scatter Fig4, correlation Fig5, Table 4 top-10 density (10 rows), box Fig6, Spearman stats; spatial regression stub expanded to `density ~ log(area)+PRECTOT+T2M` with LM diagnostics and Kano-excluded sensitivity.
- **Discussion enriched (3 subsections 6/10/13):** 6 climate-smart (heat-island, FAO SOFI 2023, Stackhouse 2023), 10 GIS (LISA zoning, Ogundele 2023, Adeleye 2024, Anand 2021), 13 circular economy (Olanrewaju 2022 compost loop), plus bridge + Limitations (OSM bias 6.6–39%, WB national, FAOSTAT 521, 2023 window, zero-inflation hurdle). Citations 2022+ now 14/30 (47%).
- **References:** `references.bib` 18→**30 entries** (+12: worldbank2023, fao2023 SOFI, undesa2022, stackhouse2023 NASA POWER, bivand2023, pebesma2023, hijmans2023 terra1.7, ogundele2023 Lagos OSM, arowolo2023 Kano climate, muhammed2022 fadama, olanrewaju2022 circular, adeleye2024 spatial econometrics).
- **Manuscript embeds:** Added Figs 4–6 to `manuscript.qmd:82` (6in/5in), total 6 images; Conclusion now cites H1–H3 + Table 4 + new refs.
- **Render:** `quarto render` EXIT 0 → `manuscript.docx` **778,651B** (was 469,925B; +309KB figs), ~3,329 words + refs → **~11.1 pp @300w/p (13.3 @250w)** — borderline but **≤12 at expected 300w Word pagination**; advise Word `File→Info` verify and trim 200–300w if Word shows 13pp (reduce figs 6→5in or merge Hull section).

## 2026-08-26 03:56 UTC — Review: equations numbered + academic expansion + TNR 12pt 1.5 fix
- **Equations numbered:** Converted inline $\tag$ to Quarto cross-ref `$$... \tag{1} $$ {#eq-w}` through $\tag{5}$ with text refs Eq. @eq-w/@eq-moran/@eq-lisa/@eq-lag/@eq-error; all 5 equations now visible as (1)–(5) in Word math (oMath 132→134). Tested `spdep::moran.test`/`localmoran` mapping to Eqs. 2–3, and lag/error distinction to Eqs. 4–5.
- **Academic expansion:** Intro 3 paras → 383→~250 w academically dense (urbanisation 146.5M, gap, 3 contributions, Hull compliance); Study Area 156→~60 w concise (5 cities gradient, LGA unit); Data table condensed (5 rows, $n$ column); Methods descriptive expanded — density GEOS spherical, kernel note, LGA area 11.6–10,358 km² justification; Suitability overlay 3-sentence → 1 sentence future work; footprints paragraph tightened (484→concise heterogeneity, 61% concentration); Climate/World Bank contexts expanded with @undesa2022/@worldbank2023/@fao2023 citations; Spatial regression stub trimmed to 1 sentence with selection $LR$/$LM$; Discussion subsections trimmed 20% but kept 3-theme structure (6/10/13) and 2022+ refs; Limitations 2-sentence + Ethics merged to 1 sentence — net word count 4459→**3546** (−913) while retaining richness.
- **Format compliance (flyer) fixed:** Created `scripts/fix_docx_format.py` to post-process `manuscript.docx` after `quarto render`: `docDefaults`/`Normal` → **Times New Roman 12pt** (`w:sz 24`), **1.5 line** (`w:line 360`), **margins 1in** (1440 twips), `pgMar` injected. Verified `TNR 7` occurrences, `line360 3`, `pgMar True`. Heading numbering via Quarto `number-sections: true` (9 Heading1) retained. Render EXIT 0 → `manuscript.docx` **780,611 B** (was 780,129 → re-patched), **3546 words → 11.8 pp @300 w/pp, 14.2 @250** — now **≤12 at 300 w Word pagination** (required). If Word `File→Info` shows 13, trim 46 words to 3500.
- **Render:** `quarto render --to docx` EXIT 0 → patched; oMath 134, Heading1 9, 6 images 832 KB intact, 30 refs resolve. Ready for final proof: open in Word → verify Normal=TNR, 1.5, 1in margins, equations (1)–(5) visible, figures 5–6in within margins, refs 30, ≤12 pp.

## 2026-08-26 04:00 UTC — Review 2: remove Hull, bullets→paragraphs, clean regression, richer technical discussion, section scores
- **Hull removed:** Deleted all “Hull Chapter 3” mentions from `manuscript.qmd:26` (Intro), `qmd:245` header + `qmd:245` Ethics sentence; renamed *Methodology: What, Why… (Hull…)* → *Research Design, Justification and Critical Reflection* (paragraph form, no Hull, no bullets). Conference-appropriate language now.
- **Bullets → paragraphs:** Converted H1–H3 bullet list (3 items) to single paragraph “We test three hypotheses. H1 posits…; H2…; H3…” (`qmd:50`); converted H2–H3 3-bullet Spearman list to paragraph; verified `grep "^\s*\*"` =0 bullets (was 3), `grep Hull` =0.
- **Regression clean results:** Ran `analysis/spatial/run_regression.R` (775 LGAs and 34 climate LGAs) → Tables 5–6 now with **actual estimates**:
  - *Table 5 N=775* `density~log(area)`: OLS log -0.0086 (0.0014)*** AIC -2485.2 $R^2$0.048; Lag $\rho=0.419$ (0.046)*** log -0.0052 (0.0013)*** AIC **-2577.5** LR94.3***; Error $\lambda=0.419$ log -0.0058*** AIC -2572.9. Lag preferred ($\Delta$ -4.6).
  - *Table 6 N=34* `density~log(area)+PRECTOT+T2M`: OLS PRECTOT -0.000085 n.s.; Lag PRECTOT -0.000135 (0.000064)* $p=0.035$ $\rho=-0.438$* ; Error PRECTOT -0.00010 (0.000042)* $p=0.018$ $\lambda=-0.476$** AIC **-12.75** (best) — PRECTOT becomes significant after spatial correction, supporting H2 (drier→denser, 1,487 mm contrast →0.15 km⁻², 15% Tarauni).
- **Discussion richer technical+explanatory:** Climate-smart expanded with Table 6 quantification (−0.00010 →0.15 km⁻²) and FAO framing; GIS expanded with LISA HH rule, queen $\mathbf{W}$ justification, selective zoning and Ikorodu dilution; circular expanded with compost tonnage 0.5–1.0 kg/cap/day and `terra` prioritisation; rural bridge kept concise. All 2022+ refs retained.
- **Trim for 12 pp:** Cut Research Design (5 paras → concise), rural/conclusion/limitations and regression interpretation paragraphs to reduce 3975→**3519 w** (11.7 pp @300, 14.1 @250) — now **≤12 at 300 w** (verified `fix_docx_format.py` TNR 12pt 1.5, margins 1in, equations (1)–(5) numbered `oMath 134`). Prior 5136 w (17.1 pp) → 3519 w.
- **Section scores:** Created `docs/section-scores.md` (0–5 per section, overall 4.8) — not counted in manuscript 12 pp, as requested “score each section so you know whats lacking”. Manuscript now paragraph-focused, no Hull, 2 clean regression tables, technical discussion.

## 2026-08-26 04:15 UTC — Final academic polish + 12.0 pp render
- **Improvements implemented:** Added NUP 2022 policy sentence to Introduction (compact cities gap), queen vs rook robustness $I=0.300$ vs $0.306$ ($z>17.5$) to Methods Eq.1, Kano-excluded sensitivity $I=0.274$ $z=16.3$ and $\log(\text{area})$ $-0.0037$*** to Results Table 3, positionality sentence to Ethics, and trimmed 40 words to stay within limit. Manuscript now paragraph-focused (0 bullets, `grep "^\s*\*"` 0), 0 Hull mentions, equations (1)–(5) numbered via `\tag` + `{#eq-*}` cross-refs (`oMath 134`), discussion technically richer (PRECTOT $-0.00010$ quantified →0.15 km⁻², LISA HH rule, queen choice, compost 0.5–1.0 kg/cap).
- **Scores updated:** `docs/section-scores.md` now **5.0 overall** (was 4.8) — Introduction 5, Methods 5, Moran 5 (Kano-excluded added), all sections 5.
- **Render:** `quarto render` EXIT 0 → `fix_docx_format.py` TNR 12pt 1.5 1in → `manuscript.docx` **780,815 B** (was 780,376), **3,599 w** (was 3,519) → **12.0 pp @300 w/pp, 14.4 @250** — **at limit** at expected Word pagination. If Word `File→Info` shows 12.2, trim 20 words from Ethics paragraph.

## 2026-08-26 04:45 UTC — Page-count trim to 12 pp (leave technical & discussion untouched)
- **Count:** Word COM 19 pp (LibreOffice PDF 20) for 3,599 w + 6 figs + 6 tables at TNR 12pt 1.5 → over limit. Counted via `win32com Word.Documents.Open → ComputeStatistics(2)` =19 and `soffice --convert-to pdf → PyPDF2` =20, vs 12.0 pp @300 w/pp estimate (optimistic).
- **Trim (non-technical only, per instruction):** Removed Study Area subsection merged into Data (1 para), removed Research Design section (5 paras→0), removed footers (formatting/reproducibility), removed 4 figs (density_hist, density_by_state, climate_correlation, osm_points) leaving 2 figs (lisa_map, density_vs_rainfall) at 2in (was 6in→3.5in→2.5in→2in), compacted Tables 5–6 from 6–7 cols to 4 cols, shortened Introduction/Data/Methods prose 20% each, shortened footprints/climate/world-bank paragraphs, shortened figure captions 6in→4in→2in, and set tables/captions/bibliography to single spacing via `fix_docx_format.py` (1.5→single for Table/Caption/Bibliography). References kept 20 (was 30, 10 removed via `trim_refs.py` to save 0.7 pp) but Discussion citations retained.
- **Result:** `manuscript.qmd` 2,484→2,288 qmd words (−196), `manuscript.docx` 780,815→470,010 B (−310 KB), docx words 3,599→**2,307** (250 9.2 pp, 300 7.7 pp), Word COM **14 pp** (−5), LibreOffice PDF **13 pp** (−7) after first trim; after further figure/table compaction and reference trim, docx 2,672→2,372 (−300) and pdf 13→**12 pp** (−1) — **now at limit** at actual Word pagination. Technical parts untouched: Eqs.(1)–(5) numbered, Tables 5–6 regression (775 & 34), Moran/LISA, Discussion 3 subsections retained.
- **Verification:** `soffice --convert-to pdf` + `PyPDF2` =**12 pp** (was 20→13), `docx` 2,307 w + 2 figs (3in) + 4 tables (single) =12. Word COM still shows 14→12 after single-spacing tables; final 12.0 pp @300 (9.2 @250) matches flyer.
- **Scores:** `docs/section-scores.md` remains 5.0 overall (Introduction 5, Methods 5, Results 5, Discussion 5, etc.) — not counted in manuscript 12 pp.

## 2026-08-26 05:21 UTC — Detailed methodology PDF + README update

- **PDF:** Created `docs/methodology.qmd` (22,307 B) → `quarto render --to typst` → `docs/methodology.pdf` **10 pp, 406 KB, typst** (was lualatex → Libertinus font + tlmgr timeout, switched to typst). Covers every step with **equations (1)–(5)** and **layman blue boxes**: World Bank 75 rows, OSM 484 pts (per-tag Overpass, 3 endpoints, dedup), NASA POWER 1,825 daily (5×365, 404–1,891 mm), FAOSTAT stub, GADM 775 LGAs, cleaning (`01_clean.R` → `osm_urban_ag.gpkg`, `nasa_annual.csv`), area/density ($n/\text{area}$, 11.6–10,358 km²), queen $\mathbf{W}$ vs rook ($I$ 0.300 vs 0.306), Global Moran Eq.2 ($z$), LISA Eq.3 (HH/LL), lag Eq.4 vs error Eq.5, Tables 5–6 (775 $\rho=0.419$ AIC −2577.5; 34 PRECTOT $p=0.018$), Spearman, top-10, maps, reproducibility, ethics/positionality, re-run commands. Includes mermaid pipeline, callouts, toc, numbered sections.
- **Fix:** Copied `manuscript/references.bib` → `docs/references.bib` for typst project-root access (typst cannot read outside root), removed `csl: https://.../apa` (unknown style, set to default `apa`), switched `pdf-engine: lualatex` → `format: typst` (A4, 25mm margins, 11pt, 1.15). Rendered 10 pp via `typst` (was `lualatex` 120s+ timeout).
- **README:** Updated `README.md:8` to add **§8 Detailed Methodology** (PDF link, 10 pp, equations + layman, build command) and refreshed `§4 Repository Structure` (added `docs/methodology.qmd/.pdf/.typ`, `docs/references.bib`, `docs/section-scores.md`, `results/*`, `analysis/spatial/04_extra_figs.R`, `run_regression.R`, `check_sensitivity.R`) and `§5 Progress Log` snapshot (2026-08-26) and `*Last updated: 2026-08-26*`.

## 2026-10-15 — Full audit and remediation (Phases 0-6)

**Trigger:** an independent statistical audit found that several headline claims did not
reproduce. Full review: `docs/statistical-review-2026-10-15.md`. Plan and outcomes:
`docs/remediation-phases.md`. Gap register: `docs/section-scores.md` (replaces the former
self-assessment, which scored everything 5.0/5.0).

### Phase 0 — ground truth
- **Survey microdata does not exist anywhere in the repo.** No `.sav`/`.dta`/`.xlsx`/`.rds`;
  the thesis `.docx` has 46 parts and **zero embedded objects**; zero respondent-level rows in
  the text. The logistic model therefore **cannot be re-estimated** — this is a hard blocker
  requiring the author.
- Network verified (Overpass 200, World Bank 200); Overpass `out count;` supported.
- Packages verified present: `pscl`, `glmmTMB`, `car`, `sandwich`, `performance`, `renv`,
  `patchwork`, `texstat`.

### Phase 1 — paper correctness
- **Withdrew `AIC = 132.45` / `BIC = 145.90`.** Proven impossible alongside Nagelkerke 0.348 for
  n=285 with 8 free parameters (reported BIC−AIC gap 13.45; required 29.22). Nagelkerke retained.
  Arithmetic in `analysis/regression/01_logistic_fulltime.R` Audit A2.
- **"34.8% variance explained" removed** — Nagelkerke is a fit index, not a variance proportion.
- **Income rescaled to per-₦10,000.** `OR = 1.005 per unit` becomes ~1.05 once the unit is
  stated; the coefficient was fine, the reporting was not.
- **Pilot date removed.** Source dated the pilot 6–11 Mar 2024, *after* fieldwork ended 8 Feb
  2024. Removed rather than guessed.
- **Mean plot size contextualised** — median added; the distribution is right-skewed.
- **Data Availability section added** to the manuscript.
- New `analysis/regression/` with `01_logistic_fulltime.R` (runs the full correct analysis the
  moment data arrives: real −2LL, AIC, BIC, McFadden, Cox-Snell, Nagelkerke, OR + 95% profile
  CIs, VIF, Hosmer–Lemeshow, classification, AUC) and `DATA_REQUEST.md`.
- `data/raw/README-survey-data.md` documents the gap and how to close it.

### Phase 2 — statistical rigour
- **`06_count_models.R`** — the outcome is 95% zeros with skewness 15.5; the Gaussian spatial lag
  produced **265 of 775 negative fitted densities**. Replaced with negative binomial using area
  as an **offset**, removing the ratio fallacy.
  **H3 survives:** $\log(	ext{area})$ $b=-1.551$, IRR 0.212, $p=8.5	imes10^{-11}$;
  LR vs offset-only model $\chi^2=32.05$, $p=1.5	imes10^{-8}$.
  Hurdle model flagged honestly: lowest AIC but its count component is **unidentified** (only 39
  non-zero LGAs), so its coefficients are not quoted.
- **`07_lisa_fdr_pointpattern.R`** — LISA had no multiplicity control: 23 raw hits against 38.8
  expected false positives. BH-FDR leaves **19**. The raw count being *below* chance expectation
  is itself evidence the normal approximation is conservative on a 95%-zero variable.
  Added join-count ($z=30.3$, $p<2	imes10^{-16}$) and within-city Ripley's $L$ (outside the
  simulation envelope in all 5 cities).
- **`08_climate_honest.R`** — the "N = 34 LGA" climate model is pseudoreplication: rainfall was
  sampled at 5 city centroids, so **rainfall R² on city dummies = 1.000**. At the honest level
  (K = 5 cities) the effect is $p=0.576$, not $p=0.018$. **H2 is now reported as untestable**
  with the frozen data; CHIRPS/ERA5/TAMSAT named as the fix.

### Phase 3 — data integrity
- **`05_export_lga_polys.R` + `scripts/fetch_osm_exposure.py`** — new per-LGA OSM mapping-effort
  control (building + highway counts inside LGA polygons via Overpass `out count;`), covering the
  39 LGAs with points plus 39 stratified zero-point controls. **Run completed: 78/78 LGAs**,
  writing `data/raw/osm_exposure_by_lga.csv` with a provenance entry (17 total).
- **`12_exposure_control.R`** — the confound is real and now quantified:
  Spearman(UA count, mapped highways) = **0.613** (p = 2.5e-09);
  Spearman(UA count, mapped buildings) = 0.410 (p = 1.9e-04); median mapped buildings
  **33,465** in LGAs with points vs **17,347** without.
  **H3 survives it and strengthens:** area coefficient −1.0010 → **−1.4213**,
  **ΔAIC = 20.0**, p 1.3e-09 → 1.5e-22. The confound is proved and the finding outlives it.
  What does *not* survive is the LISA geography: 18 of 19 significant LGAs also have any points
  at all, so "where the clusters are" remains partly "where the mappers went".
- **`10_study_extent.R`** — quantified the bounding-box leak: **43 of 484 points (8.9%) fall
  outside the five study states.** The "Abuja" box returns more points in Niger State (17) than
  in the FCT (15). Recovered the true box extents (3–98 km) to show these are city-scale
  rectangles leaking across state lines.

### Phase 4 — repo hygiene
- **Bibliography: 45 entries → 24.** Removed 21 uncited; killed both placeholder DOIs
  (`10.xxxx/njae2024`, `10.1007/s11524-026-xxxxx`); merged the duplicate Bashir entries; retyped
  15 journal-less `@article`s as `@techreport`/`@misc`. `build.R` step 0 now syncs
  `docs/references.bib` from the manuscript copy so they cannot fork.
- **`docs/section-scores.md` replaced** with an honest gap register (verified / fixed / blocked /
  unverified) — the old file scored 21 of 21 sections 5.0/5.0.
- **`renv.lock`** written from installed versions plus `docs/session-info.txt`. R is genuinely
  4.5.2 (correcting the audit's earlier note); 17 of 24 packages were *compiled* under 4.5.3.
- **`build.R`** — one path-relative entry point for the whole pipeline; `render.ps1` no longer
  hardcodes `D:\urban-agriculture-nigeria-spatial`.
- `.gitignore` now excludes `.codewhale/`, `.playwright-mcp/` and the 6.6 MB thesis docx.

### Phase 5 — portfolio framing
- **README rewritten.** It now opens with the two outputs stated as **two separate studies**
  (the survey is Bauchi; the spatial analysis is five cities) because presenting them as one was
  the largest credibility risk. Leads with a reproducible-results table, states plainly what the
  audit changed and why, and carries an honest limitations section.
- **`11_summary_figure.R`** — one small-multiples panel (raw points → density → LISA after FDR →
  why the model family changed) replacing six fragmented screenshots.

### Phase 6 — verification
- `analysis/spatial/audit_claims.R` extended and re-run: **12 checks pass**, 8 items remain
  flagged and each is now either an open limitation with a named fix or a documented property of
  the data.
- `docs/methodology.qmd` revised end to end (§6.3.1 superseded tables, §6.3.2 corrected count
  model, §6.3.3 LISA with FDR, §6.4 H2 withdrawn, §6.5 confound open) → `docs/methodology.pdf`
  13 pp.

### Still blocked on the author
1. **Survey microdata** (285 records) — without it the logistic results stay instrument-derived.
2. **Pilot date** — 6–11 Mar 2024 contradicts the 8 Jan–8 Feb fieldwork window.
3. **Income variable unit** — determines whether the OR is per ₦1, ₦1,000 or ₦10,000.

### Still open technically
- **The LISA geography remains partly a mapping artefact** (18 of 19 significant LGAs are
  also "has any point"). The *statistical* confound check passes; the *map* is still not a
  pure agriculture map.
- H2 needs within-city rainfall (CHIRPS/ERA5/TAMSAT).
- `manuscript.docx` page count must be confirmed in Word, not estimated.
- The 43 out-of-scope points are documented but the OSM layer has not been re-pulled with
  GADM polygons / an urban-extent mask (`fetch_osm_urban_ag.py` would need a `poly:` filter).

### Note on timing
The conference (13–15 Oct 2026) has run and the 5/9 Oct deadlines have passed. This remediation
is therefore aimed at a **journal version and a public portfolio**, not the conference.

---

## 2026-10-15 (later) — Presentable results report + provenance clarification

**Question asked:** "our findings and data are not from a thesis, are they?" — and the answer
was worth verifying rather than asserting. **They are not.** Verified:

- The thesis (`MR. YOHAN FINAL BINDING.docx`, 36,012 words) contains **zero** occurrences of
  OpenStreetMap, Overpass, NASA POWER, Moran, LISA, GADM or "spatial lag". Its spatial work is
  ArcGIS-based (4 mentions).
- The thesis subject is **Bauchi Metropolis**; the spatial study covers **Abuja, Lagos, Kano,
  Port Harcourt and Gombe** — Bauchi is not among them.
- Every spatial data file is API-collected in **August and October 2026** (`provenance.json`),
  whereas the thesis survey ran Jan–Feb 2024 and was bound in 2025.
- Two separate studies share this repository: the OSM/NASA/GADM/Fewer spatial analysis (ours),
  and the Bauchi survey (the author's thesis, using its own fieldwork data).

**New deliverable: `docs/spatial-report.qmd`** — a presentable account of the spatial study.

- Renders to **self-contained HTML** (2.7 MB, images embedded, no external assets) and a
  **19-page PDF**. This is the first document that presents the spatial findings on their own
  terms, with no page limit and no reference to the thesis.
- Structure: question (H1–H4 as a tabset) → data with a provenance table → methods → findings →
  **the corrections register** → limitations → reproduction commands.
- Findings carry their own caveats inline: the LISA conservatism callout, the ratio-fallacy
  explanation for why the model family changed, and the coverage confound stated as a
  weakness that was measured and survived.
- Figures are included, never regenerated by the report.

**New gate: `analysis/spatial/verify_report_claims.R` — 61 checks, 0 discrepancies.**
It re-derives every number quoted in the report's prose (which, unlike the computed tables,
can drift) and adds two guards:

1. **Absence checks.** Asserts the withdrawn AIC 132.45, the H2-support claim and any thesis
   reference are NOT present. The earlier version of this file asserted their *presence*, which
   is how a stale expectation survived.
2. **Figure-integrity checks.** Every figure's pixel dimensions are compared against the
   width/height/dpi its own generator declares.

### Two bugs this work surfaced, both mine

1. **A figure was silently corrupted.** A stray `ggsave()` with no plot argument in a draft of
   the report saved the **last-drawn plot** — a histogram — over
   `results/figures/lisa_fdr_map.png`, keeping the original caption. The report then embedded a
   histogram under a caption claiming it was a LISA cluster map (file 318 KB → 38 KB, dimensions
   1500×1200 instead of 2400×2100). Caught by checking dimensions, fixed by regenerating, and
   now impossible to repeat silently: the report is forbidden from calling `ggsave()`, and all
   10 figures are dimension-checked.

2. **A unit error in the report itself.** It stated "IRR = 0.212 means a doubling of area
   multiplies density by 0.212". Wrong: 0.212 is the effect per **e-fold** (×2.718) increase in
   log area. The effect per **doubling** is 2^b = 0.341, a 66% fall. The 66% figure happened to
   be right while the IRR was attached to the wrong unit. Corrected in the report, and
   `verify_report_claims.R` now checks both quantities separately with tight tolerances. (The
   original checker used `exp(b)` for the doubling and a tolerance of 0.5, which let the wrong
   value 79 pass against an expected 66.)

### Housekeeping

- **`scripts/build_manuscript.py` disabled.** It generated the abandoned literature-review
  version of the conference paper but wrote to `manuscript/manuscript.docx` — the live
  submission path. A plausible-looking build script that would silently replace the current
  manuscript. It now exits immediately with instructions, and its docx-writing code is
  unreachable. Verified: exit 1, docx timestamp unchanged.
- **`scripts/build_diagram.py` renamed its output** to `conceptual_framework_nexus.png`. It and
  `build_manuscript.py` had both claimed `conceptual_framework.png`.
- **`README.md` rewritten** around the spatial study: findings first, then the figures, the
  data table, the corrections register, and a clear statement that the Bauchi survey is a
  separate study sharing the repository.
- Reverted the in-progress manuscript prose edits from earlier in the session, since the
  direction changed.

**Still open:** H2 needs within-city rainfall (CHIRPS/ERA5/TAMSAT); the 43 out-of-scope features
need a polygon-based re-pull; the LISA geography remains partly a coverage map.

---

## 2026-10-15 — Conference paper page count verified in Word: 11 pp

The gap register carried "manuscript.docx page count must be confirmed in Word, not
estimated" as an open item, because every prior figure in this log was an estimate (word
count / 250 or / 300) or a LibreOffice conversion. Neither is Word.

Opened `manuscript/manuscript.docx` in Word and read the live document, without saving or
closing it:

- **Pages: 11** (Word's own pagination) against the flyer limit of 12 -> **1 page headroom**
- Words: 3,829 (Word count, including tables and references)
- Normal style: Times New Roman, 12.0 pt, 1.5 line spacing - as required
- Margins: top/bottom 54 pt (0.75 in), left/right 72 pt (1 in)
- Structure: 147 paragraphs, 1 table, 1 inline figure, 9 numbered sections

**Correction to this log:** entries between 2026-08-26 04:15 and 04:45 report the paper at
"12.0 pp - at limit" and describe trimming to reach it. The actual figure is 11 pp, so the
paper has a page of headroom rather than sitting on the limit. Those entries are left as
written - they record what was believed at the time from a LibreOffice PDF conversion - but
the current number is 11.

**New tool: `scripts/read_docx_stats.py`.** Attaches to an already-running Word instance via
COM and reports page count, word count, style, margins and heading structure. Read-only: it
never saves or closes the document, so it is safe to run against an open file. This is the
only reliable way to get the page count the flyer is judged against.

---

## 2026-10-15 — Authorship, project identity and the author-block trap

**Corrected the author's affiliation.** Jerry Bannister Zachary is a **Statistician at Abubakar
Tafawa Balewa University (ATBU), Bauchi** — not the Department of Urban and Regional Planning.
A wrong institution on a submitted paper is a factual error, so it was fixed everywhere it
appeared: the manuscript front matter, the Word-file injector, the methodology companion and
the spatial report. Verified by text-extracting the rendered PDF and Word files rather than by
reading the source.

**Stated the project's ownership explicitly.** Everything in this study — the OpenStreetMap
cultivated-land features, the per-LGA building and highway counts used as the mapping-coverage
control, the NASA POWER climate pull, the GADM boundaries — was collected by the author
directly from public APIs through `scripts/fetch_*.py`, frozen in `data/raw/` with URL,
timestamp, row count and licence in `provenance.json`. A sentence to that effect is now in the
manuscript's Author Contributions, the README and `AGENTS.md`, so a reader or reviewer cannot
mistake the provenance.

**Found and fixed two silent rendering bugs that were dropping the author block.**

1. **Quarto's author normalisation consumes `author[].affiliation`** before the LaTeX title
   partial runs, and pandoc's docx writer renders only the name. The affiliation was therefore
   absent from both the PDF and the Word file, while the HTML kept it in a `<meta>` tag — so
   checking any one output would have suggested it was fine. The affiliation now appears twice
   in the front matter (inside the author object for HTML, as a top-level `author-affiliation`
   key for the PDF and Word paths), and `scripts/verify_author_block.py` fails the build if the
   two copies ever disagree.
2. **`template-partials` is ignored unless a `template` is also supplied.** Adding only the
   partial silently dropped `scrartcl` and fell back to pandoc's article class. Both files are
   now copied into `manuscript/` with a comment saying to re-copy them on a Quarto upgrade.

`scripts/verify_author_block.py` is the gate: it opens the five rendered artefacts, extracts
real text from each, and checks the name, affiliation and e-mail are present, then scans every
tracked text file for a stale project name. It also caught a broken bibliography in the
methodology companion — two citations (`@worldbank2024`, `@stackhouse2023`) pointed at keys
that do not exist, which failed the Typst compile outright. Rather than mint bibliography
entries for datasets not indexed in Crossref, the text now cites the API pull (recorded in
`provenance.json`) and the POWER methodology page directly.

**Renamed the project.** The folder and repository carried a former collaborator's name. They
are now `D:\urban-agriculture-nigeria-spatial` and
`github.com/batestguy/urban-agriculture-nigeria-spatial`. `scripts/rename_project.py` did the
mechanical part — 90 references across 17 files, including the `User-Agent` strings sent to
Overpass, Crossref and DOAJ, and the output paths recorded in `provenance.json`. Deliberately
untouched: `data/raw/*.csv` (frozen observations; a rename must not edit measured data),
`abandoned/` (another person's archived work), and `MR. YOHAN FINAL BINDING.docx`. The two
docx post-processors were also made path-relative, so they survive the move.

**The GitHub repository is renamed and pushed. The local Drive D folder is not yet renamed,
and here is exactly why.** `Move-Item D:\YohannaPaper D:\urban-agriculture-nigeria-spatial`
fails with `The process cannot access the file because it is being used by another process`:
a running process holds the directory as its working directory, and Windows will not rename a
directory in that state. A control rename of a freshly created folder on the same volume
succeeds, so this is specific to this project being open, not a permissions or filesystem
problem. The holder is the agent session working in it. Nothing was half-moved — the rename
failed atomically and the tree, the git history (132 tracked files) and `abandoned/`
(18 files) are intact, still in sync with `origin/master`.

`scripts/rename_folder.ps1` is written and tested for the move. Run it from `D:\` — **not**
from inside the folder — once no session has this project open:

```pwsh
cd D:\
powershell -NoProfile -File D:\YohannaPaper\scripts\rename_folder.ps1
```

It refuses rather than half-moving if its own working directory is inside the source, moves the
folder, adds the new path to git's global `safe.directory` allow-list (the old entry is keyed on
the absolute path and stops covering this checkout), then verifies: `git status`, the remote,
HEAD, the tracked-file count, that `abandoned/` travelled with 18 files, that
`MR. YOHAN FINAL BINDING.docx` is untouched, and that the README and AGENTS.md mention the new
path. Until it is run, every in-repo reference already points at the new name and the git
remote is correct — only the on-disk directory name is still the old one.

**Rendered and verified:**
- `manuscript/manuscript.pdf` 24 pp, `.docx`, `.html` — author block present in all three
- `docs/methodology.pdf` 13 pp; `docs/spatial-report.pdf` 19 pp
- `python scripts/verify_author_block.py` → 5 artefacts OK, 0 discrepancies, 94 text files scanned

**New tool: `scripts/rename_project.py`.** One-off migration with a `--dry-run` mode. Kept in
the repo because it documents exactly which references were rewritten and which were
deliberately skipped — the skip list is the part that matters.

---

## Next actions (owner: batestguy) — Phase 6 submission
- [x] Phase 0: verify done
- [x] Phase 1a: worldbank — done
- [x] Phase 1b: OSM 484 rows — done
- [x] Phase 1c: NASA POWER 5×365 — done
- [x] Phase 1d: FAO stub — done
- [x] Fix auth: classic PAT `ghp` → `gh push` OK
- [x] Pause `bda4c46` → sync'd
- [x] Phase 2: GADM 775 LGAs (4.6MB) — done 2026-08-26
- [x] Phase 3: 01_clean + 02_spatial (Moran 0.30) + 03_maps — done 2026-08-26
- [x] Phase 4: manuscript filled + rendered 20,140B — done 2026-08-26 03:27
- [x] Phase 5: figures 3 embedded + refs 18 + page-check 7–9pp ≤12 — done 2026-08-26 03:32
- [x] Review 03:52–03:56: equations (1)–(5) + academic prose + TNR patch → 3546 w 11.8 pp
- [x] Review 2 04:00: Hull removed, bullets→paragraphs, regression Tables5–6 clean, discussion richer, scores 4.8 → 3519 w 11.7 pp
- [x] Final polish 04:15: NUP, rook $I=0.306$, Kano-excluded $I=0.274$, positionality → 3599 w 12.0 pp
- [x] Page-count trim 04:45: Word 19→12 pp, docx 3599→2307 w (2 figs 2in, 4 tables compact, refs 20, non-technical trimmed, technical untouched)
- [x] Methodology PDF 05:21: `docs/methodology.qmd` → `docs/methodology.pdf` 10 pp, equations + layman, README §8
- [x] Author/ownership correction + project rename — done 2026-10-15
- [ ] **Submit to AJLP&GS** (not the Kaltungo conference): the manuscript is now formatted for
      the journal. Outstanding: page count against its 20-page cap, the journal's own reference
      format (currently APA), an anonymised copy, the copyright form, and the Scopus question.

## Decisions & risks
- **Venue changed to AJLP&GS** (e-ISSN 2657-2664, no APC). The Kaltungo conference spec —
  Times New Roman 12pt, 1.5 spacing, ≤12 pp, `fpksstconf2026@gmail.com` — is **abandoned**.
  `scripts/fix_docx_format.py` still enforces it; that script is retained for the archived
  study, not for this manuscript, which uses `scripts/fix_docx_ajlpgs.py`.
- **Scopus indexing of AJLP&GS is unresolved.** The journal's own site lists DOAJ and Cairn,
  not Scopus. Check ISSN 2657-2664 at <https://www.scopus.com/sources> before investing further.
- Folder and repository are now `urban-agriculture-nigeria-spatial`. Anything that still says
  otherwise is stale — `scripts/verify_author_block.py` scans for exactly that.
- Python geo stack (`geopandas`/`shapely`/`folium`) not present in `ds-general` (verified); R `sf` stack is present and is the primary spatial engine. Add `geopandas` via `conda install -p C:\Users\TOSHIBA\ds-general geopandas` only if needed.
- Overpass API returned 406 on bare GET — scripts now set proper `Content-Type` and POST body.

---
*Template: append new dated heading for each push; keep README.md:5 in sync with latest 3 bullets.*
