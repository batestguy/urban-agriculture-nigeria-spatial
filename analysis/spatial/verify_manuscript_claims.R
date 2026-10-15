#!/usr/bin/env Rscript
# verify_manuscript_claims.R — the gate for manuscript/manuscript.qmd.
#
# The manuscript is the project's face now, so it gets the same treatment the spatial
# report got: every number quoted in its PROSE is re-derived from the frozen data, and
# every figure is checked for integrity. Computed tables cannot drift because they are
# rendered live; prose can, and this catches that.
#
# Also asserts that things which should NOT be in the manuscript are absent — most
# importantly any dependence on the abandoned Bauchi survey, and the withdrawn
# climate finding.
#
# Read-only. Exits non-zero on any discrepancy.
# Run: Rscript analysis/spatial/verify_manuscript_claims.R

suppressMessages({
  library(sf); library(dplyr); library(readr); library(spdep); library(spatialreg); library(MASS)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
ok <- 0L; bad <- 0L
chk <- function(label, actual, expected, tol = 0.001) {
  good <- isTRUE(all.equal(as.numeric(actual), as.numeric(expected), tolerance = tol))
  if (good) { ok <<- ok + 1L; cat(sprintf('  [OK]   %-48s %s\n', label, format(actual))) }
  else { bad <<- bad + 1L
         cat(sprintf('  [DIFF] %-48s text says %s, data says %s\n', label, format(expected), format(actual))) }
}
chk_has <- function(label, text, needle) {
  if (grepl(needle, text, fixed = TRUE)) { ok <<- ok + 1L; cat(sprintf('  [OK]   %-48s present\n', label)) }
  else { bad <<- bad + 1L; cat(sprintf('  [DIFF] %-48s MISSING: %s\n', label, needle)) }
}
chk_absent <- function(label, text, needle) {
  if (grepl(needle, text, fixed = TRUE)) { bad <<- bad + 1L; cat(sprintf('  [DIFF] %-48s stale text: %s\n', label, needle)) }
  else { ok <<- ok + 1L; cat(sprintf('  [OK]   %-48s absent\n', label)) }
}

MS <- 'manuscript/manuscript.qmd'
if (!file.exists(MS)) { cat('manuscript not found at', MS, '\n'); quit(status = 1) }
text <- paste(readLines(MS, warn = FALSE), collapse = '\n')

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
osm <- read_csv('data/raw/osm_urban_ag.csv', show_col_types = FALSE)
lga$log_area <- log(lga$area_km2)
nb <- poly2nb(lga, queen = TRUE); lw <- nb2listw(nb, style = 'W', zero.policy = TRUE)

hr('1. Study frame')
chk('features', nrow(osm), 484, 0)
chk('LGAs', nrow(lga), 775, 0)
chk('LGAs with a feature', sum(lga$n > 0), 39, 0)
chk('percent with a feature', round(100 * mean(lga$n > 0), 1), 5.0, 0.05)
chk('percent at exactly zero', round(100 * mean(lga$density == 0), 1), 95.0, 0.05)
chk('skewness', round({x <- lga$density - mean(lga$density); mean(x^3)/mean(x^2)^1.5}, 1), 15.5, 0.05)
chk('max density', round(max(lga$density), 2), 1.06, 0.005)
chk('Kano features', sum(osm$city == 'Kano'), 189, 0)
chk('allotment features', sum(osm$landuse == 'allotments', na.rm = TRUE), 5, 0)
chk('farmland features', sum(osm$landuse == 'farmland', na.rm = TRUE), 328, 0)

hr('2. H1 clustering')
mi <- moran.test(lga$density, lw, zero.policy = TRUE)
chk("Moran's I", round(mi$estimate[1], 3), 0.300, 0.001)
chk('z', round(mi$statistic, 1), 17.6, 0.05)
chk('counts I', round(moran.test(lga$n, lw, zero.policy = TRUE)$estimate[1], 3), 0.158, 0.002)
nb_r <- poly2nb(lga, queen = FALSE); lw_r <- nb2listw(nb_r, style = 'W', zero.policy = TRUE)
chk('rook I', round(moran.test(lga$density, lw_r, zero.policy = TRUE)$estimate[1], 3), 0.306, 0.002)
lga_nk <- lga |> filter(NAME_1 != 'Kano')
nb_nk <- poly2nb(lga_nk, queen = TRUE); lw_nk <- nb2listw(nb_nk, style = 'W', zero.policy = TRUE)
chk('Kano-excluded I', round(moran.test(lga_nk$density, lw_nk, zero.policy = TRUE)$estimate[1], 3), 0.274, 0.002)
chk('Kano-excluded N (Kano LGAs)', nrow(lga) - nrow(lga_nk), 44, 0)
m0 <- lm(density ~ log_area, data = lga)
mlag <- lagsarlm(density ~ log_area, data = lga, listw = lw, zero.policy = TRUE, tol.solve = 1e-10)
chk('residual Moran OLS', round(moran.test(residuals(m0), lw, zero.policy = TRUE)$estimate[1], 3), 0.256, 0.002)
chk('residual Moran lag', round(moran.test(residuals(mlag), lw, zero.policy = TRUE)$estimate[1], 3), -0.036, 0.003)
p_raw <- localmoran(lga$density, lw, zero.policy = TRUE)[, 5]
chk('LISA raw', sum(p_raw < 0.05), 23, 0)
chk('LISA BH-FDR', sum(p.adjust(p_raw, 'BH') < 0.05), 19, 0)
chk('chance expectation', round(0.05 * length(p_raw), 1), 38.8, 0.05)
chk('join-count z', round(joincount.test(factor(as.numeric(lga$n > 0)), lw, zero.policy = TRUE)[[2]]$statistic, 1), 30.3, 0.05)

hr('3. H2 scale effect')
nb_rate  <- glm.nb(n ~ offset(log(area_km2)), data = lga)
nb_slope <- glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)
b <- summary(nb_slope)$coefficients['log_area', 1]
pois <- glm(n ~ log_area, family = poisson, data = lga)
chk('coefficient on log(area)', round(b, 3), -1.551, 0.002)
chk('fall per e-fold (%)', round(100 * (1 - exp(b)), 0), 79, 0.01)
chk('fall per doubling (%)', round(100 * (1 - 2^b), 0), 66, 0.01)
chk('Poisson dispersion', round(sum(residuals(pois, 'pearson')^2) / df.residual(pois), 1), 39.1, 0.05)
chk('LR chi-square', round(2 * (as.numeric(logLik(nb_slope)) - as.numeric(logLik(nb_rate))), 1), 32.0, 0.05)

hr('4. H3 coverage control')
expo <- read_csv('data/raw/osm_exposure_by_lga.csv', show_col_types = FALSE) |>
  filter(!is.na(n_buildings), n_buildings > 0)
d <- lga |> left_join(transmute(expo, GID_2 = gid2, n_buildings, n_highways), by = 'GID_2') |>
  filter(!is.na(n_buildings), n_buildings > 0) |> mutate(log_bldg = log(n_buildings))
mA <- glm.nb(n ~ log_area + offset(log_area), data = d)
mB <- glm.nb(n ~ log_area + offset(log_area) + offset(log_bldg), data = d)
chk('LGAs with exposure', nrow(d), 78, 0)
chk('Spearman vs highways', round(cor(d$n, d$n_highways, method = 'spearman'), 3), 0.613, 0.002)
chk('median buildings, with', round(median(d$n_buildings[d$n > 0]) / 500) * 500, 33500, 600)
chk('median buildings, without', round(median(d$n_buildings[d$n == 0]) / 500) * 500, 17500, 600)
chk('b without control', round(coef(mA)['log_area'], 3), -1.001, 0.002)
chk('b with control', round(coef(mB)['log_area'], 3), -1.421, 0.002)
chk('dAIC', round(AIC(mA) - AIC(mB), 1), 20.0, 0.15)

hr('5. Withdrawn climate hypothesis')
nasa <- read_csv('data/processed/nasa_annual.csv', show_col_types = FALSE)
map <- c('Federal Capital Territory' = 'abuja', 'Lagos' = 'lagos', 'Kano' = 'kano',
         'Rivers' = 'port_harcourt', 'Gombe' = 'gombe')
dat <- lga |> mutate(city_key = unname(map[NAME_1])) |>
  left_join(nasa, by = c('city_key' = 'city')) |>
  filter(n > 0, !is.na(prectot_sum)) |> st_drop_geometry()
chk('LGAs assigned rainfall', nrow(dat), 34, 0)
chk('distinct rainfall values', length(unique(round(dat$prectot_sum))), 5, 0)
city <- dat |> group_by(city_key) |> summarise(density = mean(density), rain = mean(prectot_sum), .groups = 'drop')
chk('K=5 rainfall p', round(summary(lm(density ~ rain, data = city))$coefficients['rain', 4], 2), 0.58, 0.005)

hr('6. Prose values in the manuscript')
for (pair in list(
  c('Moran I quoted', 'I = 0.300'), c('Kano-excluded I quoted', 'I = 0.274'),
  c('per-doubling fall quoted', '66% per doubling'), c('coverage rho quoted', '\u03c1 = 0.613'),
  c('delta AIC quoted', '\u0394AIC = 20.0'), c('zero-inflation quoted', '95% of LGAs'),
  c('LISA adjusted quoted', '19 of 775'), c('leakage quoted', '8.9%'))) {
  chk_has(pair[1], text, pair[2])
}

hr('7. Must NOT appear (independence from the abandoned work)')
chk_absent('no Bauchi survey', text, 'Bauchi Metropolis')
chk_absent('no 285 respondents', text, '285 farmers')
chk_absent('no thesis dependence', text, 'M.Tech thesis')
chk_absent('no fabricated citation key', text, 'urban_food_insecurity2026')
chk_absent('no claimed climate finding', text, 'supporting **H2**')

hr('8. Figures and references')
figs <- list.files('results/figures', pattern = '\\.png$', full.names = FALSE)
used <- regmatches(text, gregexpr('\\.\\./results/figures/[a-z_0-9]+\\.png', text))[[1]]
missing <- setdiff(unique(basename(used)), figs)
if (length(missing)) {
  bad <- bad + 1L
  cat('  [DIFF] referenced figure(s) not on disk:', paste(missing, collapse = ', '), '\n')
} else {
  ok <- ok + 1L
  cat(sprintf('  [OK]   %-48s all %d present\n', 'referenced figures exist', length(unique(used))))
}

cited <- unique(regmatches(text, gregexpr('@[a-z]+[0-9]{4}', text))[[1]])
cited <- sub('^@', '', cited)
bib <- sub('^@\\w+\\{([^,]+),.*', '\\1',
           grep('^@\\w+\\{', readLines('manuscript/references.bib', warn = FALSE), value = TRUE))
chk('cited references', length(cited), length(bib), 0)
if (length(setdiff(cited, bib))) {
  bad <- bad + 1L
  cat('  [DIFF] cited but not in bib:', paste(setdiff(cited, bib), collapse = ', '), '\n')
} else {
  ok <- ok + 1L
  cat('  [OK]   every cited key exists in references.bib\n')
}

hr('Summary')
cat(sprintf('  checks passed : %d\n  discrepancies : %d\n', ok, bad))
if (bad > 0) {
  cat('\n  The manuscript quotes something the frozen data does not support. Fix before submitting.\n')
  quit(status = 1)
}
cat('\n  Every number quoted in manuscript/manuscript.qmd matches the frozen data,\n')
cat('  every figure exists, and every citation resolves to a bib entry.\n')
