# AGENTS.md — urban-agriculture-nigeria-spatial

## What this repo is
- **A spatial study of urban agriculture in Nigeria, by Jerry Zachary Bannister** (Statistician,
  Abubakar Tafawa Balewa University, Bauchi; `jzbannister@atbu.edu.ng`). Manuscript:
  *Where urban agriculture concentrates in Nigerian cities*.
- **Status: RE-SUBMITTED, in review.** *African Geographical Review* (Taylor & Francis, ISSN
  1937-6812 / 2163-2642), **submission ID 260528906**. First submitted 9 November 2026, returned
  unreviewed 10 November because the author's name was in the anonymous file's properties,
  re-submitted with scrubbed files on 13 November 2026 (D-17 … D-19). **All journal mail goes to
  `jzbannister@atbu.edu.ng`**, not the personal Gmail — check that inbox for status. The current
  state is `docs/handoff-2026-11-13.md`; **every decision behind it
  is `docs/decisions.md` (D-01 … D-19)**
  — read that before changing the venue, the declarations, or the table/figure count.
- **Venue history, and the two traps in it.** AJLP&GS was dropped on a Scopus check and never
  submitted. Town and Regional Planning was abandoned over its AI clause and **never submitted** —
  do not record it as a rejection. TeMA **did** receive the manuscript and desk-rejected it on
  **scope** on 19 Oct 2026, in under 24 hours, without a reviewer: a scope screen, not an
  evaluation, and nothing to revise in response.
- **The AI declaration is REQUIRED and must not be removed.** TeMA had no AI policy, so it was
  deleted on 2026-10-18; that reasoning was venue-specific. Taylor & Francis requires
  acknowledgement and counts coding assistance as a permitted use. The declaration names **DeepSeek
  Flash 4.1 (build 1017)** and **Opus 5.5**, as the submission form's attestation demands, and
  states that no generative tool produced data, a figure, a map or an interpretation. Never tick an
  AI attestation against a declaration that omits the tool names and versions — ask the author.
- **Current manuscript constraints** (AGR): **APA** references (`csl: apa.csl`, not the inhouse
  Harvard in `manuscript/trp-harvard.csl`); **200-word** abstract, **4–6** keywords; **7,000 words**
  including references (currently 6,136); **no more than 6 tables and figures combined** — the
  article carries 4 tables and 2 figures, and anything further goes to `manuscript/supplementary.qmd`.
  The holdover script `scripts/fix_docx_trp.py` is still the one to use, despite its name: it
  produces TNR 12 pt single-spaced and injects the author block, and
  `scripts/verify_trp_format.py` still gates it.
- **Author's name: `Jerry Zachary Bannister`** (family name *Bannister*), as given by ORCID
  `0009-0002-3302-9558`. Corrected from "Jerry Bannister Zachary" on 2026-10-16 — an earlier
  commit had it as "Ibrahim Yohanna". Do not reintroduce either spelling: the ORCID record is
  the authority, and the identity gate scans for stale names.
- Everything in this repo is the author's own work. All layers used in the analysis —
  OpenStreetMap cultivated-land features, the per-LGA mapping-coverage control, NASA POWER
  climate, GADM boundaries — were collected directly from public APIs by the author, and the
  pulls are frozen in `data/raw/` with `provenance.json` recording URL, timestamp, row count
  and licence for each. No third party supplied or contributed any layer.
- **Git:** mirrored to **GitHub `batestguy/urban-agriculture-nigeria-spatial`** (public). Remote
  `origin` is set; local = the Drive D copy. Every push mirrors Drive D → GitHub.
- **Path trap — the folder has not been renamed yet.** The repository is *named*
  `urban-agriculture-nigeria-spatial` and every in-repo reference uses that name, but the
  on-disk directory **still carries a different name**; the rename is pending.
  `scripts/rename_folder.ps1` performs the move and refuses to half-move if its own working
  directory is inside the source. It must be run from `D:\` with no session holding the folder
  open. **Until it is run, trust the directory shown in the workspace context for anything the
  filesystem resolves — not the name used inside these files.** This bullet deliberately does
  not spell the old name, which is why it needs no edit when the rename lands. Windows 11;
  OpenCode reports the workspace root as `/` but it maps to `D:\` on this machine.
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
  `docs/trp-author-guidelines.md` — **Town and Regional Planning's guidelines, submission
  checklist and full AI policy, verbatim** — retained as the **previous** target's record.
  `docs/submission-trp.md` — the gap analysis for that venue, including the AI-policy conflict
  (now marked resolved by the venue change).
  `docs/venue-search-2026-11-09.md` — the search that selected AGR, with the Scopus verification
  instrument and the fit evidence. Supersedes the shortlist in `docs/venue-options.md`.
  `docs/decisions.md` — **the canonical decision log (D-01 … D-16).** Append, never rewrite.
  `docs/venue-options.md` — the earlier shortlist and the evidence behind each choice; §2 is TeMA.
  Its header still announces TRP as the decision and does not record TeMA's rejection — treat
  `docs/decisions.md` as authoritative where they differ.
  `docs/ajlpgs-author-guidelines.md` / `docs/submission-ajlpgs.md` — the **dropped** venue's
  guidelines and gap analysis, kept because the reasoning and much of the work are reusable.
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
  (Times New Roman, 1.5, 1 inch). `scripts/fix_docx_ajlpgs.py` enforces the **dropped** AJLP&GS
  spec (Cambria 12, 1.2, cm margins). Neither matches the current target. **`fix_docx_trp.py`
  is the one to use**: it enforces Times New Roman 12 pt single-spaced and it injects the author
  block including the ORCID. Its name is a holdover from the previous venue; the style it produces
  is still correct.
- **`scripts/normalize_docx_meta.py` must run after `fix_docx_trp.py` on every render.** Quarto
  writes `compatibilityMode 14` (Word 2010) into every DOCX and `reference.docx` carries a Mac Word
  2010 stamp, so Word opens the file in [Compatibility Mode]. The script sets mode 15 and
  normalises the app metadata, touching only `word/settings.xml` and `docProps/app.xml`. Full
  rebuild order: `quarto render manuscript.qmd` → `quarto render supplementary.qmd` →
  `python scripts/fix_docx_trp.py --anonymise` → `python scripts/scrub_review_copies.py` →
  `python scripts/normalize_docx_meta.py` → `python scripts/scrub_review_copies.py --check`.
  Re-rendering alone silently drops the author block and the compatibility fix.
- **Anonymity is checked in EVERY part of the review files, not just the body text.** The first
  AGR submission was returned because the author's name sat in the Word "Author" property while
  the body was clean (D-18). `scrub_review_copies.py --check` scans every part of
  `manuscript-anonymised.docx` and `supplementary.docx`; never upload either unless it passes.
- **Rendered DOCX/PDF/HTML are deliberately untracked** (`manuscript/.gitignore`, including
  `supplementary.docx`). The journal permits archiving only the published version, and they are
  large binaries that change on every render. The `.qmd` sources are tracked and rebuild them.
- **Before reporting a number, run the gate that checks it.** `Rscript build.R --audit` re-derives
  every headline figure from the frozen data. Editing the prose to satisfy a test is the wrong
  direction: the test asserts what the data says.
