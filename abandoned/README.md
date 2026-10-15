# Abandoned — Bauchi Metropolis survey paper

**Archived:** 15 October 2026
**Status:** Abandoned as the project's output. Preserved, not deleted.

---

## Why this folder exists

The project originally aimed at a conference paper built on a field survey of 285 urban farmers
in Bauchi Metropolis, drawn from the author's M.Tech thesis. On 15 October 2026 the author
decided that work would no longer represent the project. The repository's face is now the
spatial study (`manuscript/`).

Nothing here was deleted. Everything is recoverable, and **it remains in the git history** —
this is a move, not a purge.

---

## What is here

| Path | What it is |
|---|---|
| `manuscript/manuscript.qmd` | The conference paper source (Bauchi survey, 285 farmers) |
| `manuscript/manuscript.docx` | Its rendered output — 11 pages, Times New Roman 12pt, 1.5 spacing |
| `manuscript/references.bib` | Its bibliography, 24 entries |
| `manuscript/fig1-conceptual-framework.png` | Its Figure 1 (integration framework) |
| `analysis/01_logistic_fulltime.R` | Re-analysis pipeline for its logistic model |
| `analysis/DATA_REQUEST.md` | Column spec for the survey microdata |
| `docs/README-survey-data.md` | Record that the survey microdata is not in the repository |
| `docs/phases.md` | Original conference submission plan |
| `docs/theme-verification.md` | Conference sub-theme fit analysis |
| `docs/urban-ag-literature-review-spec.md` | A proposed — never implemented — full rewrite as a literature review |
| `scripts/build_manuscript.py` | Disabled generator for the literature-review variant |
| `scripts/build_diagram.py` | Produces the nexus review diagram |
| `scripts/compact_tables.py` | Table compaction used for the 12-page limit |
| `results/conceptual_framework.png` / `.md` | The nexus review diagram |
| `paper-archive/hull-chapter3-criteria.png` | Dissertation marking screenshot |
| `paper-archive/conference-flyer.jpeg` | Conference call for papers |

## The unarchived original

**`MR. YOHAN FINAL BINDING.docx`** (6.6 MB) — the author's M.Tech thesis — sits at the
repository root and is gitignored. It was deliberately **not** moved or touched.

It is the author's own thesis: 36,012 words, years of primary fieldwork, and the only record of
the survey that generated the Bauchi results. It is not an artefact of this project and nothing
here supersedes it. Anyone reviving the paper would need it.

## Open items if this work is ever resumed

Recorded in `docs/citation-audit-2026-10-15.md` and inherited by these files:

- The survey microdata (285 respondents) was never deposited. Without it the logistic model
  cannot be re-estimated. `analysis/DATA_REQUEST.md` specifies the required columns.
- The pilot date (6–11 March 2024) post-dates the fieldwork window (8 Jan – 8 Feb 2024).
  One of the two is wrong.
- The reported `AIC = 132.45` / `BIC = 145.90` pair is impossible alongside Nagelkerke = 0.348
  at n = 285 with 8 free parameters. AIC/BIC are withdrawn in the archived manuscript text;
  only Nagelkerke is retained.
- One citation (`urban_food_insecurity2026`) was **fabricated** — placeholder DOI, invented
  co-author, a 2026 date for a paper that does not exist. It was removed from
  `manuscript/manuscript.qmd` and replaced with a labelled placeholder.
- Two DOIs in `references.bib` return 404 in Crossref (`sekabira2022`, `issifu2025`).
- `bashir2022` has no DOI, URL, journal or publisher, yet the study-area coordinates rest on it.
- The study-area coordinate in the manuscript reads 90°48′E; Bauchi is at approximately 9.8°E.

**If this paper is ever revived, none of those items should be inherited silently.**
