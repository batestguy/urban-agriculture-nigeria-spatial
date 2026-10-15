# Where Does Urban Agriculture Concentrate in Nigerian Cities?

> **A spatial analysis of 484 OpenStreetMap features across 775 Local Government Areas.**
> All data collected by the author through public APIs in 2026. Every number reproducible
> from frozen data.

**Read the manuscript:** [HTML](manuscript/manuscript.html) · [PDF](manuscript/manuscript.pdf) · [Word](manuscript/manuscript.docx) — 22 pages, 19 cited references, every number verified.

```pwsh
Rscript analysis/spatial/verify_manuscript_claims.R   # 53 checks against the manuscript
Rscript analysis/spatial/audit_claims.R               # claim-by-claim audit of the analysis
Rscript build.R                                        # whole pipeline from frozen data
```

---

## The finding in three lines

- Urban agriculture is **strongly clustered** across Nigerian LGAs — Moran's I = 0.300
  (z = 17.6, p < 1e-69). Excluding Kano entirely leaves I = 0.274, so it is not one state.
- **Density falls by about 66% per doubling of LGA area** (negative binomial with area as an
  exposure offset, p = 8.5e-11). Small LGAs concentrate cultivation; large ones dilute it.
- **That survives the obvious objection.** OpenStreetMap coverage is uneven, and the strongest
  criticism of this work is that it measures mapping effort rather than agriculture. The
  confound is real (ρ = 0.613 between features and mapped highways) — and the area effect gets
  *stronger* under control (ΔAIC = 20.0).

## What the study does

Four hypotheses, tested on openly available spatial data for five cities spanning Nigeria's
agro-ecological gradient (Abuja, Lagos, Kano, Port Harcourt, Gombe).

| | Question | Method | Outcome |
|---|---|---|---|
| **H1** | Is cultivation clustered? | Moran's I, LISA with BH-FDR, join-count, Ripley's L | **Yes** — I = 0.300; clusters in every city |
| **H2** | Does aridity drive it? | City-level regression (K = 5) | **Untestable** — rainfall was sampled at city centroids; see below |
| **H3** | Does density fall as area grows? | Negative binomial, area as offset | **Yes** — 66% fall per doubling, p = 8.5e-11 |
| **H4** | Does it survive coverage correction? | Per-LGA OSM building/highway counts as a second offset | **Yes** — strengthens under control, ΔAIC = 20.0 |

## Figures

![Summary panel: raw points → density → LISA clusters → model diagnostics](results/figures/summary_panel.png)

*One panel, four steps: the 484 features, density normalised by area, LISA clusters after FDR
control, and why the model family had to change.*

| Figure | What it shows |
|---|---|
| [LISA clusters after FDR control](results/figures/lisa_fdr_map.png) | 19 LGAs significant after Benjamini–Hochberg; raw p<0.05 gave 23 against 38.8 expected false positives |
| [Model diagnostics](results/figures/count_model_diagnostics.png) | The superseded Gaussian model predicts **265 of 775 negative densities**; a rate model cannot |
| [Mapping-coverage confound](results/figures/study_extent.png) | 43 of 484 features (8.9%) fall outside the study states — the "Abuja" box returns more points in Niger than in the FCT |
| [Honest climate unit](results/figures/climate_honest.png) | The rainfall question at K = 5 cities, where no effect is established |
| [Feature locations](results/figures/osm_points.png) | The 484 features across the five cities |

## Data

| Layer | Source | Records | Licence |
|---|---|---|---|
| Cultivated land features | OpenStreetMap Overpass API | 484 | ODbL © OpenStreetMap contributors |
| Mapping-coverage control | OpenStreetMap Overpass (aggregate counts) | 78 LGAs | ODbL |
| Agro-climate | NASA POWER, 2023 daily | 1,825 days | Public domain |
| Administrative boundaries | GADM v4.1 | 775 LGAs | CC BY 4.0 |
| National context | World Bank Indicators | 75 rows | CC BY 4.0 |

Every pull is recorded in `data/raw/provenance.json` with URL, timestamp, row count and
licence. Analysis reads only the frozen files and never the network. The one networked step is
refreshing the coverage control: `python scripts/fetch_osm_exposure.py`.

## What the audit changed

This work audited itself before publication, and four findings altered the analysis. They are
recorded because a result that has survived scrutiny is worth more than one that has not.

1. **Wrong model family.** Density is exactly zero for 95% of LGAs and strictly non-negative.
   An ordinary Gaussian spatial model produced 265 impossible negative fitted densities.
   → Replaced with a negative binomial using area as an **offset**, which also removes the
   ratio fallacy of regressing a ratio on its own denominator.
2. **No multiplicity control.** LISA flagged 23 LGAs at raw p < 0.05 against 38.8 expected
   false positives across 775 tests. → Benjamini–Hochberg applied; 19 survive. The raw count
   falling *below* chance expectation is reported as evidence the test is conservative, not as
   an absence of clustering.
3. **Pseudoreplication.** A climate model with "N = 34 LGAs" carried only **five distinct
   rainfall values** (rainfall R² on city dummies = 1.000). → H2 withdrawn as untestable and
   reported at K = 5.
4. **Uncontrolled coverage confound.** → Per-LGA building and highway counts collected; the
   confound confirmed and the finding shown to survive it.

Separately, **a figure was silently corrupted**: a stray `ggsave()` overwrote the LISA map with
a histogram while keeping the original caption. `verify_report_claims.R` now checks every
figure's pixel dimensions against its generator and refuses to let the report call `ggsave()`.

## Repository layout

```
├── manuscript/manuscript.qmd    the manuscript source → HTML, PDF, Word
├── docs/spatial-report.qmd     earlier report version of the same analysis
├── build.R                     one entry point, 13 pipeline steps, path-relative
├── analysis/
│   ├── spatial/                01 clean · 02 Moran/LISA · 03 maps · 04 extra figs
│   │                           05 LGA polygons · 06 count models · 07 LISA FDR + point pattern
│   │                           08 honest climate · 10 study extent · 11 summary figure
│   │                           12 exposure control · audit_claims.R · verify_report_claims.R
│   └── regression/             survey logistic re-analysis (separate study; see below)
├── data/raw/                   frozen API pulls + provenance.json
├── data/processed/             cleaned layers
├── results/                    figures/, tables/, lga_lisa.gpkg
└── renv.lock                   exact package versions
```

## Reproducing

```pwsh
Rscript analysis/spatial/verify_report_claims.R   # 61 checks against the report
Rscript analysis/spatial/audit_claims.R           # claim-by-claim audit
Rscript build.R                                   # full pipeline
quarto render manuscript/manuscript.qmd --to html # the manuscript
```

Environment: R 4.5.2 (`sf`, `spdep`, `spatialreg`, `spatstat`, `MASS`) with Python 3.12
(`pandas 2.2.3`) for the API harvest. Exact versions in `renv.lock`; full dump in
`docs/session-info.txt`. Seventeen of twenty-four packages were compiled under R 4.5.3 — they
run correctly and the discrepancy is recorded rather than hidden.

## Limitations

- **OpenStreetMap is volunteered and uneven.** The coverage control addresses this directly for
  the area effect; it cannot make the layer complete.
- **`farmland` is not `allotments`.** Only 5 of 484 features are formally designated allotments.
  This measures cultivated land within city regions, not statutory urban agriculture.
- **The study extent is rectangular.** 43 features lie outside the five intended states.
- **H2 is untestable** with city-centroid rainfall. CHIRPS, ERA5-Land or TAMSAT would fix it.
- **Cross-sectional, and not causal.** The models describe where cultivation is recorded.
- **The LISA geography remains partly a coverage map.** 18 of the 19 significant LGAs also
  have any feature at all. The statistical confound check passes; the *map* is still not a pure
  agriculture map.

## Archived work

`abandoned/` holds an earlier conference paper on a Bauchi Metropolis farmer survey, drawn from
a separate M.Tech thesis, together with its analysis, figures and build scripts. It shares no
data with this study — different cities, different unit of analysis, different method — and the
survey microdata were never deposited. It is preserved for recoverability and documented in
`abandoned/README.md`, but it no longer represents this project.

## History

Audited 15 October 2026. The full statistical review is in
`docs/statistical-review-2026-10-15.md`, the remediation plan in `docs/remediation-phases.md`,
and the open-gaps register in `docs/section-scores.md`.
