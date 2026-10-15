# Where Does Urban Agriculture Concentrate in Nigerian Cities?

> **A spatial analysis of 484 OpenStreetMap features across 775 Local Government Areas.**
> Study design, data collection and analysis: **Jerry Bannister Zachary**, Statistician,
> Abubakar Tafawa Balewa University (ATBU), Bauchi — <jzbannister@atbu.edu.ng>.
> All data collected by the author through public APIs in 2026. Every number reproducible
> from frozen data.

**Read the manuscript:** [HTML](manuscript/manuscript.html) · [PDF](manuscript/manuscript.pdf) · [Word](manuscript/manuscript.docx) — 24 pages, 19 cited references.

```pwsh
Rscript build.R --audit    # 175 verification checks; exits non-zero on any disagreement
Rscript build.R            # full 15-step pipeline from frozen data
```

## Author and ownership

This study is the work of **Jerry Bannister Zachary**, Statistician, Abubakar Tafawa Balewa
University (ATBU), Bauchi — <jzbannister@atbu.edu.ng>.

Every layer used in the analysis is the author's own. The OpenStreetMap cultivated-land
features, the per-LGA building and highway counts that serve as the mapping-coverage control,
the NASA POWER climate pull and the GADM administrative boundaries were all obtained by the
author directly from public APIs through the scripts in `scripts/`, and each pull is frozen in
`data/raw/` with its URL, timestamp, row count and licence in `data/raw/provenance.json`.
No third party supplied or contributed any dataset used here.

`abandoned/` holds an unrelated, retired survey paper from a different author's M.Tech thesis.
It shares no data with this study, and it is kept only so that it remains recoverable.

Three gates re-derive every number from the raw data and compare it with what the text
claims: `audit_claims.R` (61), `verify_report_claims.R` (61), `verify_manuscript_claims.R`
(53). All 175 pass. Every cited DOI is resolved against the Crossref registry before it can
enter the bibliography, and `scripts/verify_author_block.py` fails if any rendered output has
lost the author's name, affiliation or e-mail.

**Declaration of generative AI use.** An AI coding assistant was used in preparing this work:
implementing and debugging the analysis pipeline, writing the verification scripts, and
drafting and editing prose. Research design, data collection, analytical decisions and
interpretation are the author's. Every numerical result is independently re-derived from the
frozen data by committed scripts, and every reference was resolved against Crossref. The
author takes full responsibility for the content.

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
│                               title.tex + template.tex fix the LaTeX author block
├── docs/venue-options.md       where to submit, AI-policy guidance, checklist
├── docs/spatial-report.qmd     earlier report version of the same analysis
├── abandoned/                  retired Bauchi survey paper, kept recoverable
├── build.R                     one entry point, 15 pipeline steps, path-relative
├── analysis/
│   ├── spatial/                01 clean · 02 Moran/LISA · 03 maps · 04 extra figs
│   │                           05 LGA polygons · 06 count models · 07 LISA FDR + point pattern
│   │                           08 honest climate · 10 study extent · 11 summary figure
│   │                           12 exposure control · audit_claims.R · verify_report_claims.R
│   └── regression/             survey logistic re-analysis (separate study; see below)
├── data/raw/                   frozen API pulls + provenance.json
├── data/processed/             cleaned layers
├── results/                    figures/, tables/, lga_lisa.gpkg
├── scripts/
│   ├── fetch_*.py              the API harvests (the author's own data collection)
│   ├── build_bib.py            regenerate references.bib from Crossref
│   ├── verify_bib.py           re-check every DOI
│   ├── fix_docx_ajlpgs.py      AJLP&GS typography + inject the author block
│   ├── verify_author_block.py  fail if any output lost the author block
│   └── rename_project.py       one-off migration of the project name
└── renv.lock                   exact package versions
```

## Reproducing

```pwsh
Rscript build.R --audit                            # all three verification gates (175 checks)
Rscript build.R                                    # full pipeline, 15 steps
cd manuscript; quarto render manuscript.qmd --to html   # also --to pdf / --to docx
python scripts/fix_docx_ajlpgs.py  # AJLP&GS typography + author block into the Word file
python scripts/verify_author_block.py              # author present in every rendered output

python scripts/verify_bib.py     # re-check every DOI in references.bib against Crossref
python scripts/build_bib.py      # regenerate references.bib from Crossref metadata
python scripts/find_journals.py  # candidate venues from the DOAJ API
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

## Submitting

Target venue: **African Journal on Land Policy and Geospatial Sciences** (ISSN 2657-2664,
no APC). The manuscript has been reformatted to that journal's template.

- [docs/submission-ajlpgs.md](docs/submission-ajlpgs.md) - gap analysis and submission package
- [docs/ajlpgs-author-guidelines.md](docs/ajlpgs-author-guidelines.md) - the journal's own
  guidelines, extracted verbatim from its template file
- [docs/venue-options.md](docs/venue-options.md) - shortlist and AI-policy guidance

> **Open question: Scopus indexing.** The journal's own site lists DOAJ and Cairn under
> "Indexed In" and does **not** list Scopus. Verify ISSN 2657-2664 at
> <https://www.scopus.com/sources> before submitting if Scopus recognition matters to you.

Two points worth stating plainly, because they are easy to get wrong:

- **Scopus indexing is not verifiable from this repository.** Check any candidate at
  <https://www.scopus.com/sources> or against the monthly source-list download. Search
  results and journal homepages are not the authority.
- **Almost every reputable journal permits AI-assisted writing**, provided it is disclosed
  and no AI is listed as an author (the COPE position, followed by most publishers). The
  constraint is disclosure, not permission. Identify the minority that ban AI-generated text
  outright and avoid them.

`scripts/find_journals.py` queries the DOAJ API for journals in the paper's subject areas
that charge no article processing fee, and prints their publisher, licence, peer-review model
and typical time to publication — all from the registry rather than from a summary.

## Archived work

`abandoned/` holds an earlier conference paper on a Bauchi Metropolis farmer survey, drawn from
a separate M.Tech thesis, together with its analysis, figures and build scripts. It shares no
data with this study — different cities, different unit of analysis, different method — and the
survey microdata were never deposited. It is preserved for recoverability and documented in
`abandoned/README.md`, but it no longer represents this project. It is a different author's
work; nothing in `abandoned/` is part of the study this repository documents.

## History

Audited 15 October 2026. The full statistical review is in
`docs/statistical-review-2026-10-15.md`, the remediation plan in `docs/remediation-phases.md`,
and the open-gaps register in `docs/section-scores.md`.
