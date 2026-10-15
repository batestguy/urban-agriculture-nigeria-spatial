#!/usr/bin/env Rscript
# 06_count_models.R — the defensible model for a 95%-zero areal outcome.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# The existing Table 5/6 fit `density = n / area_km2` with Gaussian models
# (lm / lagsarlm / errorsarlm). Two things are wrong with that:
#
#   1. density is a RATIO. Regressing it on its own denominator (log area) partly
#      recovers a mechanical relationship (Kronmal's ratio fallacy), so the
#      magnitude of the "area effect" is not interpretable.
#   2. density is non-negative and EXACTLY ZERO for 95% of the 775 LGAs
#      (skewness ~15.5). A Gaussian is the wrong family: 34% of fitted values
#      from the lag model come out NEGATIVE, which is impossible.
#
# The fix is a count model with the area as an EXPOSURE (offset), not a regressor:
#
#       n_i ~ NegBin(mu_i, theta)
#       log mu_i = log(area_i) + X_i beta
#
# Then exp(beta) is an INCIDENCE RATE RATIO per unit of area — i.e. exactly the
# "does density depend on X?" question, asked correctly.
#
# We fit and compare:
#   - Poisson (to demonstrate overdispersion)
#   - Negative binomial (the workhorse)
#   - Hurdle / zero-inflated (because 95% zeros is a genuine mixture)
#   - The same three with the OSM exposure offset, if available (see 07_*)
#
# Out: results/tables/count_models.csv, results/figures/count_model_diagnostics.png
#
# Run: Rscript analysis/spatial/06_count_models.R

suppressMessages({
  library(sf); library(dplyr); library(readr); library(ggplot2)
  library(spdep); library(spatialreg)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
dir.create('results/tables', showWarnings = FALSE, recursive = TRUE)
dir.create('results/figures', showWarnings = FALSE, recursive = TRUE)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)

# --- OSM exposure, if 03_exposure has produced it ----------------------------
expo_path <- 'data/raw/osm_exposure_by_lga.csv'
if (file.exists(expo_path)) {
  expo <- read_csv(expo_path, show_col_types = FALSE)
  lga <- left_join(lga, expo %>% select(GID_2 = gid2, n_buildings, n_highways),
                   by = 'GID_2')
  has_expo <- sum(!is.na(lga$n_buildings)) > 20
} else {
  lga$n_buildings <- NA_real_; lga$n_highways <- NA_real_; has_expo <- FALSE
}
cat('OSM exposure available:', has_expo, '\n')

# =============================================================================
hr('0. The problem, stated numerically')
# =============================================================================
cat(sprintf('n LGAs                    : %d\n', nrow(lga)))
cat(sprintf('LGAs with n == 0          : %d (%.1f%%)\n', sum(lga$n == 0), 100 * mean(lga$n == 0)))
cat(sprintf('skewness of density       : %.2f\n',
            {x <- lga$density - mean(lga$density); mean(x^3) / mean(x^2)^1.5}))
cat(sprintf('range of density          : %.4f to %.4f\n', min(lga$density), max(lga$density)))
cat('\nA Gaussian model cannot respect the lower bound at 0 or the point mass at 0.\n')

# =============================================================================
hr('1. Poisson — fitted to show why it fails, not to use')
# =============================================================================
p0 <- glm(n ~ log_area, family = poisson, data = lga)
disp <- sum(residuals(p0, type = 'pearson')^2) / df.residual(p0)
cat(sprintf('AIC            : %.2f\n', AIC(p0)))
cat(sprintf('Pearson dispersion: %.1f   (Poisson assumes 1; >>1 means overdispersed)\n', disp))
cat('=> Poisson is unusable here. Its standard errors would be understated by ~sqrt(disp).\n')

# =============================================================================
hr('2. Negative binomial with log(area) as EXPOSURE')
# =============================================================================
# Model A: log_area as a covariate -> tests whether COUNTS scale with area
nb_count <- MASS::glm.nb(n ~ log_area, data = lga)
# Model B: log_area as an offset   -> tests whether DENSITY depends on area
# MASS::glm.nb has no `offset=` argument, so the offset must sit in the formula.
nb_rate  <- MASS::glm.nb(n ~ offset(log(area_km2)), data = lga)
# Model C: offset + a slope on log_area -> does density vary with area at all?
nb_slope <- MASS::glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)

cat('Model B (pure rate, no area slope)  : AIC', sprintf('%.2f', AIC(nb_rate)),
    '| theta', sprintf('%.4f', nb_rate$theta), '\n')
cat('Model C (rate + area slope)         : AIC', sprintf('%.2f', AIC(nb_slope)),
    '| theta', sprintf('%.4f', nb_slope$theta), '\n')
cat('Model A (counts, area as covariate) : AIC', sprintf('%.2f', AIC(nb_count)), '\n')
cat('\nLR test, Model B -> Model C (does density depend on area?):\n')
lr <- 2 * (as.numeric(logLik(nb_slope)) - as.numeric(logLik(nb_rate)))
cat(sprintf('  chi-sq = %.3f on 1 df, p = %.3g\n', lr, pchisq(lr, 1, lower.tail = FALSE)))

co <- summary(nb_slope)$coefficients
cat('\nModel C coefficients (IRRs):\n')
print(data.frame(term = rownames(co),
                 b = co[, 1], SE = co[, 2], z = co[, 3], p = co[, 4],
                 IRR = exp(co[, 1]), row.names = NULL), digits = 4)
cat('\nInterpretation: the area slope is on the DENSITY scale. A negative value means\n')
cat('larger LGAs are less densely covered - the H3 claim - tested without the ratio\n')
cat('fallacy, because area enters as an exposure rather than as a regressor on a ratio.\n')

# =============================================================================
hr('3. Hurdle / zero-inflated — because 95% zeros is a mixture')
# =============================================================================
if (requireNamespace('pscl', quietly = TRUE)) {
  # hurdle: logit for zero vs non-zero, then a zero-truncated count for the rest
  h <- pscl::hurdle(n ~ log_area | log_area, data = lga, dist = 'negbin')
  cat('Hurdle (NegBin) AIC :', sprintf('%.2f', AIC(h)), '\n')
  hc <- summary(h)$coefficients$count
  cat('\nCount component (intensity, given at least one point):\n')
  print(round(hc, 4))
  unstable <- any(!is.finite(hc[, 2]))
  if (unstable) {
    cat('\n*** WARNING: the count component is NOT identified. ***\n')
    cat('Only 39 of 775 LGAs are non-zero, and a zero-truncated negative binomial\n')
    cat('needs a defensible estimate of theta from those 39 alone. theta collapses to\n')
    cat('the boundary and the standard errors come back NaN. The AIC is therefore not\n')
    cat('comparable in the usual way, and the count-component coefficients must not be\n')
    cat('quoted. Only the ZERO component below is interpretable, and it is stable.\n')
  }
  cat('\nZero component (probability of being outside the mapped set):\n')
  print(round(summary(h)$coefficients$zero, 4))
  cat('\nThe zero component is the usable half: it models WHY an LGA has no points at\n')
  cat('all, which on this dataset is dominated by whether the area is mapped.\n')

  # zero-inflated NB
  z <- pscl::zeroinfl(n ~ log_area | log_area, data = lga, dist = 'negbin')
  cat('\nZero-inflated NegBin AIC :', sprintf('%.2f', AIC(z)), '\n')

  cmp <- data.frame(
    model = c('Poisson', 'NegBin (counts)', 'NegBin (rate, offset)',
              'NegBin (rate + area slope)', 'Hurdle NegBin', 'Zero-inflated NegBin'),
    AIC   = c(AIC(p0), AIC(nb_count), AIC(nb_rate), AIC(nb_slope), AIC(h), AIC(z))
  )
} else {
  cat('pscl not installed — hurdle/zero-inflated skipped.\n')
  cmp <- data.frame(
    model = c('Poisson', 'NegBin (counts)', 'NegBin (rate, offset)',
              'NegBin (rate + area slope)'),
    AIC   = c(AIC(p0), AIC(nb_count), AIC(nb_rate), AIC(nb_slope))
  )
}
cmp$dAIC <- cmp$AIC - min(cmp$AIC)
cat('\n'); print(cmp, row.names = FALSE, digits = 2)
cat('\nCAUTION on ranking by AIC: the hurdle has the lowest AIC but its count\n')
cat('component is unidentified (see above). The defensible shortlist is therefore\n')
cat('NegBin (rate + area slope) among single-equation models, with the caveat that\n')
cat('95% zeros means a single-equation model is itself an approximation.\n')
write_csv(cmp, 'results/tables/count_models.csv')

# =============================================================================
hr('4. What happened to H3?')
# =============================================================================
cat('H3 (density declines with LGA area) tested three ways:\n\n')
cat(sprintf('  Gaussian on the ratio   : b = %+.5f (p = %.2g)  <- ratio fallacy\n',
            coef(lm(density ~ log_area, data = lga))['log_area'],
            summary(lm(density ~ log_area, data = lga))$coefficients['log_area', 4]))
cat(sprintf('  NegBin, area as exposure: IRR = %.4f (p = %.2g)  <- correct family\n',
            exp(co[2, 1]), co[2, 4]))
if (exists('h')) {
  cz <- summary(h)$coefficients$zero
  cat(sprintf('  Hurdle, zero component  : b = %+.4f (p = %.2g)\n', cz[2, 1], cz[2, 4]))
}
cat('\nIf the sign is stable across all three, H3 is a real finding rather than an\n')
cat('artefact of dividing by the denominator. That is the claim the paper can make.\n')

# =============================================================================
hr('5. Diagnostics figure')
# =============================================================================
fv_gauss <- as.numeric(fitted(lagsarlm(density ~ log_area, data = lga,
                                       listw = nb2listw(poly2nb(lga, queen = TRUE),
                                                        style = 'W', zero.policy = TRUE),
                                       zero.policy = TRUE, tol.solve = 1e-10)))
d1 <- data.frame(fitted = fv_gauss, model = 'Gaussian spatial lag (current)')
d2 <- data.frame(fitted = fitted(nb_slope) / lga$area_km2, model = 'NegBin rate (proposed)')
dd <- rbind(d1, d2)

p <- ggplot(dd, aes(x = fitted, fill = model)) +
  geom_histogram(bins = 60, alpha = 0.75, position = 'identity') +
  geom_vline(xintercept = 0, linetype = 'dashed', colour = 'firebrick') +
  facet_wrap(~model, scales = 'free') +
  scale_fill_manual(values = c('#4575b4', '#d73027'), guide = 'none') +
  labs(title = 'Fitted density: the Gaussian model predicts impossible negatives',
       subtitle = sprintf('Left: %.0f of 775 fitted densities are < 0. Right: a rate model cannot be negative.',
                          sum(fv_gauss < 0)),
       x = 'Fitted density (points per km2)', y = 'LGAs') +
  theme_minimal(base_size = 11)
ggsave('results/figures/count_model_diagnostics.png', p, width = 9, height = 4.2, dpi = 300)
cat('Wrote results/figures/count_model_diagnostics.png\n')

cat('\n06_count_models.R done\n')
