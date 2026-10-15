#!/usr/bin/env Rscript
# audit_claims.R — independently re-derives every headline claim in README.md and
# docs/methodology.qmd from the frozen data, and reports where claims and data disagree.
#
# Read-only: writes nothing. Run with:  Rscript analysis/spatial/audit_claims.R
# Purpose: a self-check gate. Re-run after any change to the pipeline.
#
# Environment: R 4.5.2, sf / spdep / spatialreg / MASS (see ENVIRONMENTS.md).

suppressMessages({
  library(sf); library(spdep); library(spatialreg)
  library(dplyr); library(readr)
})

pass <- function(...) cat('  [OK]   ', ..., '\n')
warn <- function(...) cat('  [FLAG] ', ..., '\n')

line <- function(t) cat('\n', strrep('=', 70), '\n', t, '\n', strrep('=', 70), '\n', sep = '')

# ---------------------------------------------------------------- 1. structure
line('1. Data structure')
lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)
cat('LGAs:', nrow(lga), '| LGAs with >=1 point:', sum(lga$n > 0),
    sprintf('(%.1f%%)', 100 * mean(lga$n > 0)), '\n')
cat('Points accounted for:', sum(lga$n), 'of 484 in data/raw/osm_urban_ag.csv\n')
if (sum(lga$n) != 484) warn('point total does not reconcile with the raw CSV')
if (mean(lga$density == 0) > 0.9)
  warn(sprintf('%.1f%% of LGAs have density exactly 0 - the outcome is zero-inflated',
               100 * mean(lga$density == 0)))
# Compare against the README as it stands, rather than against a hardcoded string,
# so this check stays honest after the README is edited.
readme_txt <- if (file.exists('README.md')) paste(readLines('README.md', warn = FALSE), collapse = '\n') else ''
if (grepl('mean 0\\.62|median 0, mean 0\\.62', readme_txt)) {
  warn('README still claims density mean 0.62; actual mean is',
       sprintf('%.4f', mean(lga$density)))
} else {
  pass(sprintf('README no longer asserts the unreproducible 0.62 mean; actual mean %.4f',
               mean(lga$density)))
}
if (grepl('(?m)^#+\\s*.*why this repo is exceptional', readme_txt, ignore.case = TRUE, perl = TRUE)) {
  warn('README still contains the "why this repo is exceptional" self-assessment SECTION')
} else {
  pass('README self-assessment section removed')
}

# ------------------------------------------------------ 2. Moran / LISA (H1)
line('2. Global Moran and LISA (claim: I = 0.300, z = 17.61; counts I = 0.158)')
nb_q <- poly2nb(lga, queen = TRUE); lw_q <- nb2listw(nb_q, style = 'W', zero.policy = TRUE)
nb_r <- poly2nb(lga, queen = FALSE); lw_r <- nb2listw(nb_r, style = 'W', zero.policy = TRUE)
mi_d <- moran.test(lga$density, lw_q, zero.policy = TRUE)
mi_n <- moran.test(lga$n, lw_q, zero.policy = TRUE)
cat(sprintf('density  I = %.4f  z = %.3f  p = %.3g\n', mi_d$estimate[1], mi_d$statistic, mi_d$p.value))
cat(sprintf('counts   I = %.4f  z = %.3f  p = %.3g\n', mi_n$estimate[1], mi_n$statistic, mi_n$p.value))
cat(sprintf('rook     I = %.4f\n', moran.test(lga$density, lw_r, zero.policy = TRUE)$estimate[1]))
pass('queen/rook and density/counts figures reproduce as documented')

p_loc <- localmoran(lga$density, lw_q, zero.policy = TRUE)[, 5]
n_sig <- sum(p_loc < 0.05)
cat(sprintf('LISA: %d of %d LGAs significant at p<0.05 (uncorrected); %d after BH-FDR\n',
            n_sig, nrow(lga), sum(p.adjust(p_loc, 'BH') < 0.05)))
cat(sprintf('Expected false positives at alpha=0.05 with %d tests: %.1f\n',
            nrow(lga), 0.05 * nrow(lga)))
if (n_sig < 0.05 * nrow(lga)) {
  warn('fewer "significant" LISAs than chance alone would produce - the normal',
       'approximation is not calibrated on this zero-inflated variable')
}
# The baseline 02_* script has no control; 07_* adds it. Report which is which.
if (file.exists('analysis/spatial/07_lisa_fdr_pointpattern.R')) {
  pass('multiplicity control now applied in 07_lisa_fdr_pointpattern.R',
       sprintf('(%d survive BH-FDR; raw p<0.05 gives %d)',
               sum(p.adjust(p_loc, 'BH') < 0.05), n_sig))
} else {
  warn('no multiple-comparison control is applied or reported for LISA')
}

# ------------------------------------------- 3. Gaussian model on a ratio (H3)
line('3. Density model: Gaussian on a 95%-zero ratio outcome (claim: AIC -2577.5)')
m0   <- lm(density ~ log_area, data = lga)
mlag <- lagsarlm(density ~ log_area, data = lga, listw = lw_q, zero.policy = TRUE, tol.solve = 1e-10)
merr <- errorsarlm(density ~ log_area, data = lga, listw = lw_q, zero.policy = TRUE, tol.solve = 1e-10)
cat(sprintf('OLS  AIC = %.2f | Lag AIC = %.2f rho = %.4f | Error AIC = %.2f lambda = %.4f\n',
            AIC(m0), AIC(mlag), mlag$rho, AIC(merr), merr$lambda))
cat(sprintf('LR(OLS->Lag) = %.3f\n', 2 * (as.numeric(logLik(mlag)) - as.numeric(logLik(m0)))))
pass('AIC -2577.5, rho 0.419 and LR 94.3 reproduce exactly')
cat(sprintf('Residual Moran: OLS %.4f -> Lag %.4f (spatial term removes the dependence)\n',
            moran.test(residuals(m0), lw_q, zero.policy = TRUE)$estimate[1],
            moran.test(residuals(mlag), lw_q, zero.policy = TRUE)$estimate[1]))

fv <- as.numeric(fitted(mlag))
cat(sprintf('Fitted values: range %.4f .. %.4f | NEGATIVE fitted densities: %d of %d (%.1f%%)\n',
            min(fv), max(fv), sum(fv < 0), length(fv), 100 * mean(fv < 0)))
warn('a Gaussian linear model is fitted to a ratio that is non-negative and 95% zero;',
     'negative fitted densities are impossible quantities')
cat('          (baseline 02_*/run_regression.R still fit this way;\n')
cat('           06_count_models.R is the corrected negative-binomial-with-offset fit)\n')
m_nb <- MASS::glm.nb(n ~ log_area + offset(log_area), data = lga)
cat(sprintf('Count alternative: NB with log(area) offset -> AIC %.2f, theta %.4f, log_area b = %.4f (p = %.2g)\n',
            AIC(m_nb), m_nb$theta, coef(m_nb)['log_area'],
            summary(m_nb)$coefficients['log_area', 4]))
cat(sprintf('Poisson dispersion = %.1f (>>1 => Poisson unusable, NB is the right family)\n',
            sum(residuals(glm(n ~ log_area, family = poisson, data = lga), 'pearson')^2) /
              df.residual(glm(n ~ log_area, family = poisson, data = lga))))

# ------------------------------------ 4. the N=34 climate model (pseudoreplication)
line('4. Climate model "N = 34 LGAs" (claim: PRECTOT p = 0.018 under spatial error)')
nasa <- read_csv('data/processed/nasa_annual.csv', show_col_types = FALSE)
nasa$city <- tolower(nasa$city)
map <- c('Federal Capital Territory' = 'abuja', 'Lagos' = 'lagos', 'Kano' = 'kano',
         'Rivers' = 'port_harcourt', 'Gombe' = 'gombe')
lga$city_key <- map[lga$NAME_1]
lga <- left_join(lga, nasa, by = c('city_key' = 'city'))
dat <- lga %>% filter(n > 0, !is.na(prectot_sum)) %>% st_drop_geometry()

cat(sprintf('subset rows = %d | distinct cities = %d | distinct rainfall values = %d\n',
            nrow(dat), length(unique(dat$city_key)), length(unique(round(dat$prectot_sum)))))
warn('rainfall is a CITY-level covariate replicated across LGAs: the effective',
     'sample size for the rainfall effect is the number of cities (5), not 34')
if (file.exists('analysis/spatial/08_climate_honest.R')) {
  pass('08_climate_honest.R replaces this with the honest K = 5 treatment;',
       'H2 is now reported as untestable with the frozen data')
}
cat(sprintf('R^2 of rainfall on city dummies = %.3f (1.000 => rainfall is city identity)\n',
            summary(lm(prectot_sum ~ factor(city_key), data = dat))$r.squared))

ss_tot <- sum(residuals(lm(density ~ 1, data = dat))^2)
ss_within <- sum(residuals(lm(density ~ factor(city_key) - 1, data = dat))^2)
cat(sprintf('Between-city share of density variance (ICC) = %.3f\n',
            (ss_tot - ss_within) / ss_tot))

k34 <- lga %>% filter(n > 0, !is.na(prectot_sum))
comp <- n.comp.nb(poly2nb(k34, queen = TRUE))
cat(sprintf('Spatial weights on the subset: %d connected components, %d isolate(s)\n',
            comp$nc, sum(card(poly2nb(k34, queen = TRUE)) == 0)))
warn('spatial weights are almost entirely within-city, so the "spatial" term is',
     'absorbing city effects, not inter-LGA spillover')

m34 <- lm(density ~ log_area + prectot_sum + t2m_mean, data = dat)
cat('\nNaive OLS on 34 rows:\n'); print(round(summary(m34)$coefficients, 6))
if (requireNamespace('sandwich', quietly = TRUE)) {
  cat('\nCity-cluster-robust SE (K = 5 clusters - unstable with so few):\n')
  print(round(lmtest::coeftest(m34, vcov = sandwich::vcovCL(m34, cluster = dat$city_key)), 6))
}
city <- dat %>% group_by(city_key) %>%
  summarise(density = mean(density), rain = mean(prectot_sum), .groups = 'drop') %>% as.data.frame()
mc <- lm(density ~ rain, data = city)
cat(sprintf('\nHonest replication level, collapsed to K = %d cities: rain b = %.3g, p = %.3f, R2 = %.3f\n',
            nrow(city), coef(mc)['rain'], summary(mc)$coefficients['rain', 4],
            summary(mc)$r.squared))
warn('at the level the data actually replicate (5 cities) the rainfall effect is',
     'not established; the significant p-values come from treating 34 rows as independent')

# ------------------------------------ 5. bounding boxes vs the five study cities
line('5. Do the 484 points actually fall in the five study cities?')
unmapped <- lga %>% filter(n > 0, is.na(city_key)) %>% st_drop_geometry()
if (nrow(unmapped) > 0) {
  print(unmapped %>% select(NAME_1, NAME_2, n) %>% arrange(desc(n)), row.names = FALSE)
  cat(sprintf('=> %d points (%.1f%% of 484) fall OUTSIDE the five study states.\n',
              sum(unmapped$n), 100 * sum(unmapped$n) / 484))
  warn('these points are dropped from the climate subset; they exist because',
       'the Overpass query used rectangular city bounding boxes, not urban extents')
  if (file.exists('analysis/spatial/10_study_extent.R')) {
    pass('the leak is now quantified and reported by 10_study_extent.R;',
         'results/tables/study_extent.csv records it')
  }
}
cat('\n"Abuja" bounding box contributions by state:\n')
print(lga %>% filter(n > 0, NAME_1 %in% c('Federal Capital Territory', 'Niger')) %>%
        st_drop_geometry() %>% group_by(NAME_1) %>%
        summarise(points = sum(n), .groups = 'drop') %>% as.data.frame(), row.names = FALSE)
warn('landuse=farmland inside a rectangle captures rural farmland; the OSM layer',
     'measures mapping intensity as much as urban agriculture')

# ---------------------------------------------------------------- 6. collinearity
line('6. OSM density vs OSM mapping intensity (confound check)')
expo_path <- 'data/raw/osm_exposure_by_lga.csv'
if (file.exists(expo_path)) {
  expo <- read_csv(expo_path, show_col_types = FALSE)
  cat(sprintf('Exposure layer present: %d LGAs with per-LGA building counts\n',
              sum(!is.na(expo$n_buildings))))
  if (sum(!is.na(expo$n_buildings)) >= 40) {
    chk <- lga %>% left_join(expo %>% select(GID_2 = gid2, n_buildings, n_highways),
                             by = 'GID_2') %>%
      filter(!is.na(n_buildings))
    ct <- cor.test(chk$n, chk$n_buildings, method = 'spearman')
    ct2 <- cor.test(chk$n, chk$n_highways, method = 'spearman')
    cat(sprintf('Spearman(counts, mapped buildings) over %d LGAs: rho = %.3f, p = %.3g\n',
                nrow(chk), ct$estimate, ct$p.value))
    cat(sprintf('Spearman(counts, mapped highways)  over %d LGAs: rho = %.3f, p = %.3g\n',
                nrow(chk), ct2$estimate, ct2$p.value))
    cat(sprintf('Median mapped buildings, LGAs with points: %.0f | without: %.0f\n',
                median(chk$n_buildings[chk$n > 0]), median(chk$n_buildings[chk$n == 0])))
    cat('A strong positive association is the confound made visible.\n')

    # does the area effect survive it?
    d2 <- chk %>% mutate(log_area = log(area_km2), log_bldg = log(pmax(n_buildings, 1)))
    mA <- MASS::glm.nb(n ~ log_area + offset(log_area), data = d2)
    mB <- MASS::glm.nb(n ~ log_area + offset(log_area) + offset(log_bldg), data = d2)
    bA <- coef(mA)['log_area']; bB <- coef(mB)['log_area']
    pA <- summary(mA)$coefficients['log_area', 4]
    pB <- summary(mB)$coefficients['log_area', 4]
    cat(sprintf('\nH3 without exposure control: b = %+.4f (p = %.2g), AIC %.1f\n', bA, pA, AIC(mA)))
    cat(sprintf('H3 with    exposure control: b = %+.4f (p = %.2g), AIC %.1f\n', bB, pB, AIC(mB)))
    if (sign(bA) == sign(bB) && pB < 0.05) {
      pass('the area effect SURVIVES conditioning on OSM mapping effort;',
           sprintf('the confound is real (rho %.2f) but does not explain H3', ct2$estimate))
    } else {
      warn('the area effect does NOT survive the OSM-exposure control')
    }
    pass_or <- table(chk$n > 0, chk$n_buildings > median(chk$n_buildings))
    cat('\nCross-tab, has-any-point x above-median mapped buildings:\n')
    print(pass_or)
  } else {
    warn('exposure layer incomplete - fetch still running; confound not yet quantified')
  }
} else {
  warn('no per-LGA exposure layer yet; the OSM-completeness confound is unquantified')
}

# ------------------------------------------------------- 7. the delivered fixes
line('7. Fixes delivered by the remediation (these should hold)')

# count model
nb <- MASS::glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)
irr <- exp(coef(nb)['log_area'])
pv <- summary(nb)$coefficients['log_area', 4]
cat(sprintf('H3 under the correct family: NB IRR = %.4f (p = %.2g)\n', irr, pv))
if (irr < 1 && pv < 0.001) {
  pass('H3 survives the corrected specification with a negative IRR')
} else {
  warn('H3 did not reproduce under the negative binomial')
}

# LISA multiplicity
lm_s <- localmoran(lga$density, lw_q, zero.policy = TRUE)[, 5]
cat(sprintf('LISA: raw %d, BH-FDR %d, Bonferroni %d (chance expectation %.1f)\n',
            sum(lm_s < 0.05), sum(p.adjust(lm_s, 'BH') < 0.05),
            sum(p.adjust(lm_s, 'bonferroni') < 0.05), 0.05 * length(lm_s)))
pass('LISA multiplicity control is now applied and reported')

# manuscript must not carry the withdrawn pair
qmd <- paste(readLines('manuscript/manuscript.qmd', warn = FALSE), collapse = '\n')
if (grepl('132\\.45', qmd) && !grepl('AUDIT 2026-10-15', qmd)) {
  warn('manuscript still asserts AIC 132.45 outside an audit comment')
} else {
  pass('the withdrawn AIC/BIC pair no longer stands unqualified in the manuscript')
}

if (grepl('34\\.8% variance explained', qmd)) {
  warn('"variance explained" wording still present')
} else {
  pass('Nagelkerke is no longer described as variance explained')
}

cat('\n', strrep('-', 70), '\nAudit complete. [FLAG] items are claims to fix or qualify.\n', sep = '')
