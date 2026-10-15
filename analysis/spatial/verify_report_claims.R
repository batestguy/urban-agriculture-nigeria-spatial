#!/usr/bin/env Rscript
# verify_report_claims.R — cross-check the hardcoded numbers in docs/spatial-report.qmd
# against values recomputed from the frozen data.
#
# The report computes most of its tables inline, so those cannot drift. But the prose
# quotes specific figures (in the abstract, the corrections register and the interpretation
# paragraphs). Those CAN drift as the data changes. This script checks every one.
#
# Read-only. Run: Rscript analysis/spatial/verify_report_claims.R

suppressMessages({
  library(sf); library(dplyr); library(readr); library(spdep); library(spatialreg); library(MASS)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
ok <- 0L; bad <- 0L
chk <- function(label, actual, expected, tol = 0.001) {
  good <- isTRUE(all.equal(as.numeric(actual), as.numeric(expected), tolerance = tol))
  if (good) { ok <<- ok + 1L; cat(sprintf('  [OK]   %-46s %s\n', label, format(actual))) }
  else { bad <<- bad + 1L
         cat(sprintf('  [DIFF] %-46s report says %s, data says %s\n',
                     label, format(expected), format(actual))) }
}
chk_txt <- function(label, text, needle) {
  hit <- grepl(needle, text, fixed = TRUE)
  if (hit) { ok <<- ok + 1L; cat(sprintf('  [OK]   %-46s \"%s\" present\n', label, needle)) }
  else { bad <<- bad + 1L
         cat(sprintf('  [DIFF] %-46s \"%s\" NOT found in report\n', label, needle)) }
}

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
osm <- read_csv('data/raw/osm_urban_ag.csv', show_col_types = FALSE)
lga$log_area <- log(lga$area_km2)

report <- paste(readLines('docs/spatial-report.qmd', warn = FALSE), collapse = '\n')

hr('1. Structural claims')
chk('OSM features', nrow(osm), 484, 0)
chk('LGAs', nrow(lga), 775, 0)
chk('LGAs with >=1 feature', sum(lga$n > 0), 39, 0)
chk('% of LGAs with a feature', round(100 * mean(lga$n > 0), 1), 5.0, 0.05)
chk('features reconcile', sum(lga$n), 484, 0)
chk('% LGAs at exactly zero', round(100 * mean(lga$density == 0), 1), 95.0, 0.05)
chk('skewness of density', round({x <- lga$density - mean(lga$density); mean(x^3)/mean(x^2)^1.5}, 1),
    15.5, 0.05)
chk('Kano features', sum(osm$city == 'Kano'), 189, 0)
chk('Abuja features', sum(osm$city == 'Abuja'), 32, 0)

hr('2. H1 clustering')
nb <- poly2nb(lga, queen = TRUE); lw <- nb2listw(nb, style = 'W', zero.policy = TRUE)
mi <- moran.test(lga$density, lw, zero.policy = TRUE)
chk("Moran's I (density)", round(mi$estimate[1], 3), 0.300, 0.001)
chk('  z', round(mi$statistic, 1), 17.6, 0.05)
chk("Moran's I (counts)", round(moran.test(lga$n, lw, zero.policy = TRUE)$estimate[1], 3), 0.158, 0.001)
lga_nk <- lga %>% filter(NAME_1 != 'Kano')
nb_nk <- poly2nb(lga_nk, queen = TRUE); lw_nk <- nb2listw(nb_nk, style = 'W', zero.policy = TRUE)
chk('Moran I, Kano excluded', round(moran.test(lga_nk$density, lw_nk, zero.policy = TRUE)$estimate[1], 3),
    0.274, 0.001)

m0 <- lm(density ~ log_area, data = lga)
mlag <- lagsarlm(density ~ log_area, data = lga, listw = lw, zero.policy = TRUE, tol.solve = 1e-10)
chk('residual Moran, OLS', round(moran.test(residuals(m0), lw, zero.policy = TRUE)$estimate[1], 3), 0.256, 0.001)
chk('residual Moran, lag', round(moran.test(residuals(mlag), lw, zero.policy = TRUE)$estimate[1], 3), -0.036, 0.001)
chk('negative fitted densities', sum(as.numeric(fitted(mlag)) < 0), 265, 0)

hr('3. LISA and point pattern')
p_raw <- localmoran(lga$density, lw, zero.policy = TRUE)[, 5]
chk('LISA raw p<0.05', sum(p_raw < 0.05), 23, 0)
chk('LISA after BH-FDR', sum(p.adjust(p_raw, 'BH') < 0.05), 19, 0)
chk('expected false positives', round(0.05 * length(p_raw), 1), 38.8, 0.05)
jc <- joincount.test(factor(as.numeric(lga$n > 0)), lw, zero.policy = TRUE)
chk('join-count z', round(jc[[2]]$statistic, 1), 30.3, 0.05)

hr('4. H3 count model')
nb_rate  <- glm.nb(n ~ offset(log(area_km2)), data = lga)
nb_slope <- glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)
co <- summary(nb_slope)$coefficients
chk('log(area) coefficient', round(co['log_area', 1], 3), -1.551, 0.001)
chk('IRR', round(exp(co['log_area', 1]), 3), 0.212, 0.001)
chk('LR chi-square', round(2 * (as.numeric(logLik(nb_slope)) - as.numeric(logLik(nb_rate))), 1), 32.0, 0.06)
# A doubling is 2^b, NOT exp(b). The fall per e-fold is 79%; per doubling it is 66%.
chk('fall per e-fold (exp(b))', round(100 * (1 - exp(co['log_area', 1])), 0), 79, 0.01)
chk('fall per doubling (2^b)', round(100 * (1 - 2^co['log_area', 1]), 0), 66, 0.01)

hr('5. H4 exposure control')
expo <- read_csv('data/raw/osm_exposure_by_lga.csv', show_col_types = FALSE) %>%
  filter(!is.na(n_buildings), n_buildings > 0)
d <- lga %>% left_join(transmute(expo, GID_2 = gid2, n_buildings, n_highways), by = 'GID_2') %>%
  filter(!is.na(n_buildings), n_buildings > 0) %>% mutate(log_bldg = log(n_buildings))
chk('LGAs with exposure', nrow(d), 78, 0)
chk('Spearman, highways', round(cor(d$n, d$n_highways, method = 'spearman'), 3), 0.613, 0.002)
chk('median buildings, with features',
    round(median(d$n_buildings[d$n > 0]) / 1000) * 1000, 33465, 600)
chk('median buildings, without',
    round(median(d$n_buildings[d$n == 0]) / 1000) * 1000, 17347, 600)
mA <- glm.nb(n ~ log_area + offset(log_area), data = d)
mB <- glm.nb(n ~ log_area + offset(log_area) + offset(log_bldg), data = d)
chk('area b, no control', round(coef(mA)['log_area'], 3), -1.001, 0.002)
chk('area b, with control', round(coef(mB)['log_area'], 3), -1.421, 0.002)
chk('dAIC', round(AIC(mA) - AIC(mB), 1), 20.0, 0.15)

hr('6. H2 withdrawal')
nasa <- read_csv('data/processed/nasa_annual.csv', show_col_types = FALSE)
map <- c('Federal Capital Territory' = 'abuja', 'Lagos' = 'lagos', 'Kano' = 'kano',
         'Rivers' = 'port_harcourt', 'Gombe' = 'gombe')
lg2 <- lga %>% mutate(city_key = unname(map[NAME_1])) %>% left_join(nasa, by = c('city_key' = 'city'))
dat <- lg2 %>% filter(n > 0, !is.na(prectot_sum)) %>% st_drop_geometry()
chk('rows in the old N=34 model', nrow(dat), 34, 0)
chk('distinct rainfall values', length(unique(round(dat$prectot_sum))), 5, 0)
city <- dat %>% group_by(city_key) %>% summarise(density = mean(density), rain = mean(prectot_sum), .groups = 'drop')
mc <- lm(density ~ rain, data = city)
chk('K=5 rainfall p', round(summary(mc)$coefficients['rain', 4], 3), 0.576, 0.002)

hr('7. Prose figures quoted in the report')
chk_txt('abstract quotes I = 0.300', report, "I = 0.300")
chk_txt('abstract quotes z = 17.6', report, "z = 17.6")
chk_txt('per-e-fold IRR quoted correctly', report, "incidence rate ratio of 0.212 per")
chk_txt('per-doubling fall quoted', report, "66% per doubling")
chk_txt('confound rho quoted', report, "ρ = 0.613")
chk_txt('delta AIC quoted', report, "ΔAIC = 20.0")
chk_txt('negative fits quoted', report, "265 of 775")
chk_txt('BH count quoted', report, "19 survive")
chk_txt('extent leak quoted', report, "8.9%")
# The following assert ABSENCE, which chk_txt() cannot express - it tests presence.
chk_absent <- function(label, needle) {
  if (grepl(needle, report, fixed = TRUE)) {
    bad <<- bad + 1L
    cat(sprintf('  [DIFF] %-46s stale text found: "%s"\n', label, needle))
  } else {
    ok <<- ok + 1L
    cat(sprintf('  [OK]   %-46s absent as required\n', label))
  }
}
chk_absent('withdrawn AIC not reintroduced', "132.45")
chk_absent('H2 not claimed as supported', "supporting **H2**")
chk_absent('no dependence on the thesis', "M.Tech thesis")
chk_absent('no thesis table citations', "Thesis Table")

# The IRR unit matters. b is the effect per e-fold increase in area; the effect
# per DOUBLING is 2^b. Quoting 0.212 as a per-doubling figure would overstate the
# decline, since 0.341 is the correct value.
chk('ratio per doubling of area', round(2^coef(nb_slope)['log_area'], 3), 0.341, 0.002)
chk_absent('IRR not mislabelled as per-doubling', "IRR = 0.212 means a doubling")

hr('8. Figure integrity')

# On 2026-10-15 a stray ggsave() in a draft of spatial-report.qmd, with no plot
# argument, silently saved the last-drawn plot (a histogram) over
# results/figures/lisa_fdr_map.png. The report then embedded a histogram under a
# caption claiming it was a LISA cluster map. Both the file and the caption were
# wrong, and nothing caught it.
#
# A figure's pixel dimensions are a cheap, reliable fingerprint of the code that
# produced it, because each generator declares its own width/height/dpi. Checking
# dimensions catches accidental overwrites between figures.
fig_expect <- list(
  list(f = 'results/figures/lisa_fdr_map.png',          w = 8,   h = 7,   dpi = 300, by = '07_lisa_fdr_pointpattern.R'),
  list(f = 'results/figures/osm_points.png',            w = 8,   h = 6,   dpi = 300, by = '03_maps.R'),
  list(f = 'results/figures/density_hist.png',          w = 7,   h = 4,   dpi = 300, by = '03_maps.R'),
  list(f = 'results/figures/count_model_diagnostics.png', w = 9, h = 4.2, dpi = 300, by = '06_count_models.R'),
  list(f = 'results/figures/climate_honest.png',        w = 7.5, h = 5.5, dpi = 300, by = '08_climate_honest.R'),
  list(f = 'results/figures/study_extent.png',          w = 8,   h = 6,   dpi = 300, by = '10_study_extent.R'),
  list(f = 'results/figures/summary_panel.png',         w = 12,  h = 9,   dpi = 300, by = '11_summary_figure.R'),
  list(f = 'results/figures/density_vs_rainfall.png',   w = 7,   h = 5,   dpi = 300, by = '04_extra_figs.R'),
  list(f = 'results/figures/climate_correlation.png',   w = 6,   h = 5,   dpi = 300, by = '04_extra_figs.R'),
  list(f = 'results/figures/density_by_state.png',      w = 6,   h = 4.5, dpi = 300, by = '04_extra_figs.R')
)

if (requireNamespace('png', quietly = TRUE)) {
  for (fe in fig_expect) {
    if (!file.exists(fe$f)) {
      bad <<- bad + 1L
      cat(sprintf('  [DIFF] %-42s missing\n', basename(fe$f)))
      next
    }
    d <- dim(png::readPNG(fe$f))
    ew <- round(fe$w * fe$dpi); eh <- round(fe$h * fe$dpi)
    # allow 2% for device rounding
    okw <- abs(d[2] - ew) <= 0.02 * ew
    okh <- abs(d[1] - eh) <= 0.02 * eh
    if (okw && okh) {
      ok <<- ok + 1L
      cat(sprintf('  [OK]   %-42s %dx%d px\n', basename(fe$f), d[2], d[1]))
    } else {
      bad <<- bad + 1L
      cat(sprintf('  [DIFF] %-42s is %dx%d px; %s declares %dx%d.\n',
                  basename(fe$f), d[2], d[1], fe$by, ew, eh))
      cat(sprintf('         The file was probably overwritten by another script.\n'))
    }
  }
} else {
  cat('  [SKIP] png package unavailable - figure integrity not checked\n')
}

# Guard against the specific bug: a ggsave with no plot argument in the report.
report_gs <- grep('ggsave', readLines('docs/spatial-report.qmd', warn = FALSE), value = TRUE)
if (length(report_gs) > 0) {
  bad <<- bad + 1L
  cat(sprintf('  [DIFF] docs/spatial-report.qmd contains %d ggsave() call(s). The report must\n', length(report_gs)))
  cat('         only INCLUDE figures, never regenerate them - a bare ggsave() saves the\n')
  cat('         last-drawn plot and silently corrupts another figure.\n')
} else {
  ok <<- ok + 1L
  cat('  [OK]   report contains no ggsave(); it only includes figures\n')
}

hr('Summary')
cat(sprintf('  checks passed : %d\n  discrepancies : %d\n', ok, bad))
if (bad > 0) {
  cat('\n  Review the [DIFF] lines above: the report quotes a value the frozen data no longer supports.\n')
  quit(status = 1)
}
cat('\n  Every number quoted in docs/spatial-report.qmd matches the frozen data.\n')
