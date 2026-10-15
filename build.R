#!/usr/bin/env Rscript
# build.R — one entry point for the whole reproducible pipeline.
#
# Fixes the portability problem in render.ps1 / render.bat, which hardcoded
# D:\YohannaPaper and therefore failed for anyone who cloned the repo.
# Everything here is path-relative: clone anywhere, run this, get the same outputs.
#
# Usage:
#   Rscript build.R              # full pipeline
#   Rscript build.R --audit      # only re-verify the headline claims
#   Rscript build.R --from 2     # resume from step 2
#
# Steps
#   0  sync docs/references.bib from manuscript/references.bib (one source of truth)
#   1  clean + join frozen API layers            -> data/processed/
#   2  Moran / LISA (baseline)                   -> results/lga_lisa.gpkg
#   3  maps                                      -> results/figures/
#   4  extra figures + top-10                    -> results/figures/, results/
#   5  spatial lag / error (as published)        -> console
#   6  LISA multiplicity + point-pattern tests   -> results/tables/
#   7  count models (NB / hurdle, the fix)       -> results/tables/
#   8  honest city-level climate treatment       -> results/tables/
#   9  study extent + bounding-box leak          -> results/tables/, figures
#  10  OSM exposure control (the confound)       -> results/tables/
#  11  one small-multiples summary figure        -> results/figures/
#  12  sensitivity (queen/rook, Kano excluded)   -> console
#  13  claim audit (the gate)                    -> console, exits non-zero on FLAG
#  14  report verification (61 checks)           -> console, exits non-zero on DIFF
#
# The OSM exposure fetch is Python (scripts/fetch_osm_exposure.py) and needs the
# network; it is NOT part of the default run because the analysis must work offline
# from frozen data. Run it explicitly when refreshing the exposure layer.

args <- commandArgs(trailingOnly = TRUE)
only_audit <- '--audit' %in% args
from_step <- 0L
if ('--from' %in% args) {
  i <- which(args == '--from')
  if (length(args) > i) from_step <- as.integer(args[i + 1])
  if (is.na(from_step)) from_step <- 0L
}

SCRIPTS <- c(
  'analysis/spatial/01_clean.R',
  'analysis/spatial/02_spatial_stats.R',
  'analysis/spatial/03_maps.R',
  'analysis/spatial/04_extra_figs.R',
  'analysis/spatial/run_regression.R',
  'analysis/spatial/07_lisa_fdr_pointpattern.R',
  'analysis/spatial/06_count_models.R',
  'analysis/spatial/08_climate_honest.R',
  'analysis/spatial/10_study_extent.R',
  'analysis/spatial/12_exposure_control.R',
  'analysis/spatial/11_summary_figure.R',
  'analysis/spatial/check_sensitivity.R',
  'analysis/spatial/audit_claims.R',
  'analysis/spatial/verify_report_claims.R'
)

# --- step 0: one bibliography -----------------------------------------------
hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')

if (from_step <= 0) {
  hr('0. Bibliography: manuscript/references.bib -> docs/references.bib')
  src <- 'manuscript/references.bib'; dst <- 'docs/references.bib'
  if (file.exists(src)) {
    # typst cannot read outside its project root, so docs/ needs its own copy.
    # Copying (rather than forking) keeps one source of truth.
    if (!file.exists(dst) || !identical(readLines(src), readLines(dst))) {
      file.copy(src, dst, overwrite = TRUE)
      cat('synced', src, '->', dst, '\n')
    } else {
      cat('already in sync\n')
    }
  } else cat('WARNING:', src, 'not found\n')
}

# --- independent scripts ------------------------------------------------------
rscript_cmd <- file.path(R.home('bin'), if (.Platform$OS.type == 'windows') 'Rscript.exe' else 'Rscript')
if (!file.exists(rscript_cmd)) rscript_cmd <- 'Rscript'

run_one <- function(s) {
  hr(sprintf('Running %s', s))
  if (!file.exists(s)) { cat('MISSING - skipped\n'); return(NA_integer_) }
  out <- system2(rscript_cmd, shQuote(s), stdout = TRUE, stderr = TRUE)
  cat(out, sep = '\n'); cat('\n')
  rc <- attr(out, 'status'); if (is.null(rc)) 0L else as.integer(rc)
}

# The chain is expressed as independent scripts on purpose: each opens the frozen
# data, does one job, and writes one artefact. Nothing is held in memory between
# steps, so a single failure does not poison the rest.
plan <- c(1L, 2L, 3L, 4L, 5L, 6L, 7L, 8L, 9L, 10L, 11L, 12L, 13L, 14L)
names(plan) <- SCRIPTS

if (only_audit) {
  plan <- plan[c('analysis/spatial/audit_claims.R',
                 'analysis/spatial/verify_report_claims.R')]
  from_step <- 13
}

status <- integer(0)
for (i in seq_along(plan)) {
  step <- plan[[i]]
  if (step < from_step) next
  status[names(plan)[i]] <- run_one(names(plan)[i])
}

hr('Build summary')
for (nm in names(status)) {
  cat(sprintf('  [%s] %s\n', ifelse(is.na(status[[nm]]) || status[[nm]] != 0, 'FAIL', ' OK '), nm))
}

hr('Rendering documents')
cat('The manuscript and methodology render via Quarto (path-relative):\n\n')
cat('  quarto render docs/spatial-report.qmd --to html    # the results report\n')
cat('  quarto render docs/spatial-report.qmd --to pdf\n')
cat('  quarto render manuscript/manuscript.qmd --to docx  # the separate Bauchi survey paper\n')
cat('  quarto render docs/methodology.qmd --to typst\n\n')
cat('Then, if Word styling needs enforcing:\n\n')
cat('  python scripts/fix_docx_format.py\n')

if (any(status != 0, na.rm = TRUE)) {
  cat('\nOne or more steps failed. See output above.\n')
  quit(status = 1)
}
cat('\nAll steps completed.\n')
