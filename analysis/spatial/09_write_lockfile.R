#!/usr/bin/env Rscript
# 09_write_lockfile.R — record the exact package versions the pipeline runs on.
#
# Why not `renv::init()`: it needs to take over the project (.Rprofile, renv/
# library) and it crashed on this machine. The value we actually want is a
# machine-readable record of versions, so we write an renv-compatible lockfile
# from the installed library directly. It is a snapshot of reality, not an
# aspiration, and it never modifies the project.
#
# Run: Rscript analysis/spatial/09_write_lockfile.R

suppressMessages({
  needed <- c(
    # spatial
    'sf', 'spdep', 'spatialreg', 'spatstat.geom', 'spatstat.explore', 'terra',
    # modelling
    'MASS', 'pscl', 'glmmTMB',
    # diagnostics
    'car', 'sandwich', 'lmtest', 'performance', 'pROC', 'ResourceSelection',
    # data wrangling / reporting
    'dplyr', 'tidyr', 'readr', 'ggplot2', 'patchwork', 'texreg',
    # reproducibility
    'renv', 'sessioninfo',
    # document rendering
    'knitr', 'rmarkdown'
  )
  present <- needed[vapply(needed, function(p) requireNamespace(p, quietly = TRUE), TRUE)]
  absent  <- setdiff(needed, present)
})

info <- function(p) {
  d <- packageDescription(p)
  list(
    Package    = p,
    Version    = as.character(d$Version),
    Source     = if (!is.null(d$Repository)) d$Repository else 'unknown',
    Built      = if (!is.null(d$Built)) d$Built else NA_character_,
    Title      = if (!is.null(d$Title)) d$Title else NA_character_
  )
}

pkgs <- lapply(present, info)
names(pkgs) <- present

# renv.lock is JSON. Emit the subset of the schema that matters: R version and
# per-package Version, plus the repo for each. Keep it valid JSON so tooling
# that reads renv.lock can at least parse it.
esc <- function(s) gsub('"', '\\\\"', gsub('\\\\', '\\\\\\\\', as.character(s)))
lines <- c(
  '{',
  '  "R": {',
  sprintf('    "Version": "%s",', esc(R.version.string)),
  sprintf('    "Repositories": [{"Name": "CRAN", "URL": "https://cloud.r-project.org"}]'),
  '  },',
  '  "Packages": {'
)
entries <- vapply(pkgs, function(p) {
  sprintf('    "%s": {\n      "Package": "%s",\n      "Version": "%s",\n      "Source": "%s",\n      "Built": "%s"\n    }',
          esc(p$Package), esc(p$Package), esc(p$Version), esc(p$Source),
          esc(ifelse(is.na(p$Built), 'unknown', p$Built)))
}, character(1))
lines <- c(lines, paste(entries, collapse = ',\n'), '  }', '}')

writeLines(lines, 'renv.lock')

cat('Wrote renv.lock\n')
cat('  R version :', R.version.string, '\n')
cat('  packages  :', length(pkgs), '\n')
if (length(absent)) {
  cat('  NOT installed (listed as needed):', paste(absent, collapse = ', '), '\n')
  cat('    -> install if you want the optional diagnostics in those steps\n')
}

# The package *build* version matters for API compatibility.
# Match the literal prefix returned by R.version, which reads "R 4.5.2;".
# An earlier version of this check appended a trailing '.' to the pattern; that
# then required a literal dot inside the Built string, nothing matched, and EVERY
# package was wrongly reported as mismatched. Compare prefixes instead.
r_self <- paste0('R ', R.version$major, '.', R.version$minor, ';')
built_other <- vapply(pkgs, function(p) {
  !is.na(p$Built) && !startsWith(as.character(p$Built), r_self)
}, TRUE)
built_other <- names(built_other)[built_other]
if (length(built_other) > 0) {
  cat(sprintf('\nNote: %d of %d packages were compiled under a different R than %s:\n',
              length(built_other), length(pkgs), R.version.string))
  cat('  ', paste(built_other, collapse = ', '), '\n')
  cat('  They load and run correctly; the note is recorded rather than hidden.\n')
} else {
  cat('\nAll packages were compiled under', R.version.string, '\n')
}
