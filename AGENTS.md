# AGENTS.md — urban-agriculture-nigeria-spatial

## What this repo is
- **A spatial study of urban agriculture in Nigeria, by Jerry Bannister Zachary** (Statistician,
  Abubakar Tafawa Balewa University, Bauchi; `jzbannister@atbu.edu.ng`). Manuscript:
  *Where urban agriculture concentrates in Nigerian cities* — targeting the **African Journal on
  Land Policy and Geospatial Sciences** (AJLP&GS, e-ISSN 2657-2664, no APC).
- Everything in this repo is the author's own work. All layers used in the analysis —
  OpenStreetMap cultivated-land features, the per-LGA mapping-coverage control, NASA POWER
  climate, GADM boundaries — were collected directly from public APIs by the author, and the
  pulls are frozen in `data/raw/` with `provenance.json` recording URL, timestamp, row count
  and licence for each. No third party supplied or contributed any layer.
- **Git:** `D:\urban-agriculture-nigeria-spatial` is the clone on Drive D, mirrored to
  **GitHub `batestguy/urban-agriculture-nigeria-spatial`** (public). Remote `origin` is set;
  local = the Drive D copy. Every push mirrors Drive D → GitHub.
- Windows 11, `D:\urban-agriculture-nigeria-spatial` is the project root. OpenCode reports
  workspace root as `/` but it maps to `D:\` on this machine.
- `abandoned/` holds a **separate, retired** Bauchi survey paper from a former collaborator's
  M.Tech thesis. It shares no data with this study. Do not treat it as current work, and do not
  edit it — it is archived for recoverability only. Note that its author's name is different
  from this project's author; that is intentional.

## Structure — verified 2026-10-15
- `ENVIRONMENTS.md` — sole routing reference for all 10 interpreters. **Source of truth** for
  which env to use. Not a package inventory; for pinned lists run `conda list -p <prefix>`.
- `manuscript/manuscript.qmd` — the manuscript source. Renders to HTML, PDF and Word.
  `title.tex` + `template.tex` are Quarto partials copied locally to fix the author block
  (see below). `references.bib` is **generated** — never hand-edit it.
- `docs/methodology.qmd` — the technical companion (equations + plain-English boxes).
  `docs/spatial-report.qmd` — the earlier report version of the same analysis.
  `docs/ajlpgs-author-guidelines.md` — the journal's own guidelines, verbatim.
  `docs/submission-ajlpgs.md` — gap analysis and submission package.
- `build.R` — one entry point, 15 path-relative pipeline steps. `Rscript build.R --audit` runs
  only the three verification gates.
- `analysis/spatial/*.R` — clean → Moran/LISA → maps → count models → exposure control →
  sensitivity → the gates. `analysis/regression/` belongs to the archived study.
- `data/raw/` frozen API pulls + `provenance.json`; `data/processed/` cleaned layers;
  `results/` figures, tables, `lga_lisa.gpkg`.
- `scripts/fetch_*.py` — the API harvests. `scripts/build_bib.py` regenerates
  `references.bib` from Crossref. `scripts/verify_bib.py` re-checks every DOI.
  `scripts/fix_docx_ajlpgs.py` enforces journal typography **and injects the author block**.
  `scripts/verify_author_block.py` fails if any rendered file lost the author's name,
  affiliation or e-mail.

## Two rendering traps that cost real time — read before editing the front matter
1. **Quarto's author normalisation eats `author[].affiliation`.** It never reaches the LaTeX
   title partial or pandoc's docx writer, so the affiliation is silently absent from the PDF
   and the Word file while the HTML keeps it in a `<meta>` tag. The affiliation therefore
   appears **twice** in `manuscript.qmd`: inside the author object (for HTML) and as a
   top-level `author-affiliation` key (for `title.tex` and the docx injector).
   `scripts/verify_author_block.py` fails the build if the two copies disagree.
2. **`template-partials` alone is ignored.** Quarto only honours it when a `template` is also
   supplied; without one the render silently loses `scrartcl` and falls back to pandoc's
   article class. Both files are copied from
   `C:\Program Files\Quarto\share\formats\pdf\pandoc\` — re-copy them on a Quarto upgrade.

Never verify the author block by reading the `.qmd`. Text-extract the rendered artefact:
`python scripts/verify_author_block.py`.

## Environment — activation traps
Use `ENVIRONMENTS.md:9-23` task→env table. Defaults:

| Task | Activate |
|---|---|
| Generic/unsure | `conda activate C:\Users\TOSHIBA\ds-general` |
| Causal inference | `conda activate causality-handbook` |
| Deep learning / RL | `conda activate homl3` |
| Bayesian (Python) | `conda activate bap3` |
| Bayesian (R, preferred) | R 4.5.2 |
| Time-series | `conda activate prophet-env` |
| Stats/tidyverse/papers | R 4.5.2 |
| Web API / no DS deps | `C:\Users\TOSHIBA\appdev-env\Scripts\activate` (venv) |

Gotchas (`ENVIRONMENTS.md:77-92`):
- `ds-general` is a **prefix env** at `C:\Users\TOSHIBA\ds-general`. `conda activate ds-general`
  and `conda list -n ds-general` **fail**; use `conda activate C:\Users\TOSHIBA\ds-general` /
  `conda list -p C:\Users\TOSHIBA\ds-general`. Habitually use `-p <prefix>`.
- `appdev-env` is a **venv, not conda**. Interpreter is
  `C:\Users\TOSHIBA\appdev-env\Scripts\python.exe`; no `python.exe` at folder root.
  `conda activate` won't work.
- **numpy split:** 1.x in `bap3`/`homl3`/`ds-general`/`causality-handbook` (1.24–1.26) vs 2.x in
  `prophet-env`/`mlops-env`/`base`/system (2.4–2.5). **pandas split:** 3.0 in
  `causality-handbook`/`prophet-env`/`base`/system vs 2.1–2.2 in others. Expect API breaks.
- Python 3.14 (`appdev-env`, `C:\Python314`) has few scientific wheels — don't use for numeric work.
- Never install into `base` (19 GB incl. 3.6 GB shared `pkgs` cache). R has one install: 4.5.2, 1027 pkgs.

## Tooling
- `quarto 1.9.38` is global (any env). Node 24.15.0 / npm 11.16.0 / pnpm 10.33.2 / git 2.53.0 /
  uv 0.11.28 / conda 26.1.1+mamba.
- No formatter/linter/CI configured in this folder. If you add code, create its own
  `pyproject.toml`/`requirements` and document the env explicitly.

## Workflow for agents
- Read `ENVIRONMENTS.md` before choosing an interpreter. Verify with `conda list -p <prefix>` if unsure.
- Keep paper artifacts in `D:\urban-agriculture-nigeria-spatial`; do not scatter into `D:\` or
  `C:\Users\TOSHIBA\`.
- Use `pwsh` with absolute Windows paths; quote paths with spaces. Prefer
  `workdir: D:\urban-agriculture-nigeria-spatial` over `cd`.
- If you initialize git, do so inside `D:\urban-agriculture-nigeria-spatial` explicitly
  (`git init`), not at `D:\`.
- **Do not hand-edit `manuscript/references.bib`.** It is generated from Crossref by
  `scripts/build_bib.py`. A fabricated citation in a previous bibliography is why the generator
  exists: an unresolvable DOI cannot enter the file.
- **`scripts/fix_docx_format.py` is retained but enforces an abandoned conference spec**
  (Times New Roman, 1.5, 1 inch). It is a working tool for a different target. The AJLP&GS
  spec is `scripts/fix_docx_ajlpgs.py`.
- **Before reporting a number, run the gate that checks it.** `Rscript build.R --audit` re-derives
  every headline figure from the frozen data. Editing the prose to satisfy a test is the wrong
  direction: the test asserts what the data says.
