# Remediation Phases — post-review work plan

**Created:** 15 October 2026
**Source:** `docs/statistical-review-2026-10-15.md`
**Companion gate:** `analysis/spatial/audit_claims.R` (re-run after every phase)

> **Context.** The conference deadlines (5/9 Oct 2026) have passed and the conference
> (13–15 Oct 2026) has run. This remediation is therefore aimed at a **journal version and a
> public portfolio**, with no page limit. The priority order is *correctness → rigour →
> presentation*, and no phase may introduce a claim that `audit_claims.R` cannot reproduce.

---

## Phase 0 — Ground truth audit ✅ COMPLETE (15 Oct 2026)

**Goal:** establish what is achievable before committing to a plan.

| Question | Answer | Evidence |
|---|---|---|
| Does the survey microdata exist? | **NO** | No `.sav`/`.dta`/`.xlsx`/`.rds` anywhere in the tree; thesis `.docx` has 46 parts and **zero** embedded objects; **zero** long numeric runs (no respondent-level rows) |
| Can the logistic model be re-run? | **NO — blocked** | Needs respondent-level data; only summary tables survive in `MR. YOHAN FINAL BINDING.docx` |
| Does the thesis hold full SPSS output? | **NO** | `Omnibus`, `Model Summary`, `Variables in the Equation`, `Hosmer`, `Cox & Snell`, `Wald`, `Exp(B)` all absent — only Nagelkerke is mentioned, twice |
| Is there network access? | **YES** | Overpass HTTP 200; World Bank HTTP 200; `.fr` endpoint healthy |
| Does Overpass support cheap aggregate counts? | **YES** | `out count;` returns `{"total": "7"}` — per-LGA exposure is feasible |
| Are the analysis packages available? | **YES** | `pscl 1.5.9`, `glmmTMB 1.1.15.2`, `performance 0.18.2`, `car 3.1.5`, `renv 1.3.0`, `texreg 1.40`, `patchwork 1.3.2` |

**Consequence:** Tier-1 item 1 of the review (re-run the logistic model) **cannot be executed**.
It is replaced by Phase 1B: a runnable, documented re-analysis pipeline plus an explicit,
honest treatment of the unreproducible statistics in the manuscript. **Nothing is invented.**

---

## Phase 1 — Paper correctness
**Goal:** every number in the manuscript is either reproducible or explicitly flagged.

- **1A — Unreproducible statistics.** Remove the mutually impossible `AIC = 132.45` /
  `BIC = 145.90` pair and the "34.8% variance explained" phrasing from `manuscript.qmd`.
  Retain Nagelkerke = 0.348 (the only plausible value of the three) and describe it correctly.
  Add a footnote stating the exact AIC/BIC require the analytic dataset.
- **1B — Re-analysis pipeline.** New `analysis/regression/` with a script that runs the full
  logistic model correctly — real `−2LL`, AIC, BIC, McFadden, Nagelkerke, OR with 95% CIs,
  VIF, Hosmer–Lemeshow, classification — the moment the data is supplied. Ships with a data
  request spec.
- **1C — Income scale.** Report OR per ₦10,000, not per ₦1.
- **1D — Internal inconsistencies.** Pilot date vs fieldwork order; mean vs median plot size;
  the three different "87%"s.
- **1E — Data provenance note.** `data/raw/README-survey-data.md` documenting the gap and the
  route to closing it.

## Phase 2 — Statistical rigour
**Goal:** the inference matches the data-generating process.

- **2A — Count models.** Negative binomial with `offset(log(area))`; hurdle (zero-inflated)
  comparison; IRR with CIs. Demonstrates H3 survives correct specification.
- **2B — LISA multiplicity.** Benjamini–Hochberg FDR, adjusted p-values, plus a join-count
  test and Ripley's K on the point pattern — tests suited to a sparse point process.
- **2C — Climate model honesty.** Retire the `N = 34` framing; report the `K = 5` city-level
  relationship with its true uncertainty across all five cities.
- **2D — Update `docs/methodology.qmd`** to match 2A–2C.

## Phase 3 — Data integrity
**Goal:** separate urban agriculture from OSM mapping effort.

- **3A — Exposure counts.** Per-LGA OSM building and highway counts via Overpass `out count;`
  (39 LGAs with points + a matched control sample of zero-point LGAs).
- **3B — Exposure-controlled models.** Re-fit with OSM exposure as covariate/offset; report
  how much of the spatial pattern survives.
- **3C — Out-of-scope points.** Document the 43 points (8.9%) outside the five study states
  and re-scope the analysis boundary.

## Phase 4 — Repo hygiene
- **4A** Bibliography: drop 21 uncited entries, kill both placeholder DOIs, merge the Bashir
  duplicate, retype the 15 journal-less `@article` entries, unify the two divergent `.bib` files.
- **4B** Replace `docs/section-scores.md` with an honest gap register.
- **4C** `renv.lock` + `sessionInfo()`; record the R-version mismatch (4.5.2 claimed vs 4.5.3 built).
- **4D** Path-relative build scripts; `.gitignore` for `.codewhale/`, `.playwright-mcp/`.

## Phase 5 — Portfolio framing
- **5A** README rewrite: lead with reproducible results, not aspiration.
- **5B** Two-studies framing so repo claims equal repo contents.
- **5C** One small-multiples figure: points → density → LISA → residual Moran.
- **5D** Honest limitations section in the README.

## Phase 6 — Verification
- Re-run `audit_claims.R`; confirm every remaining claim reproduces.
- Confirm a clean-clone path works.
- Record results in `PROGRESS.md`.

---

## Hard blockers (cannot be cleared by an agent)

| Blocker | Why | What unblocks it |
|---|---|---|
| Survey microdata (285 respondents) | Never committed; not recoverable from any artefact in the tree | The author supplying the SPSS/Excel file or the original questionnaires |
| R 4.5.2 vs 4.5.3 | Different install than documented | Not material; pin what is actually installed |

**No claim in this remediation is filled in from inference. Where data is absent, the output
says so.**
