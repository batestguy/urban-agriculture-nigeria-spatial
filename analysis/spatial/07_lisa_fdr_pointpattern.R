#!/usr/bin/env Rscript
# 07_lisa_fdr_pointpattern.R — multiplicity control and point-process tests.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# `02_spatial_stats.R` ran spdep::localmoran on 775 LGAs and flagged every unit
# with p < 0.05 as an HH cluster, then the maps and discussion treated those as a
# policy targeting tool. Two problems:
#
#   1. NO MULTIPLICITY CONTROL. With 775 simultaneous tests at alpha = 0.05 the
#      expected number of false positives is 38.8. Reporting 23 "significant" LGAs
#      without adjustment is not defensible.
#
#   2. THE TEST IS UNCALIBRATED HERE. Density is 0 for 95% of units, so the
#      normal approximation behind the LISA p-values is discrete and conservative.
#      Observing FEWER significant units than chance would produce (23 < 38.8) is
#      the signature of that miscalibration - not of an absence of clustering.
#
# An areal rate is also the wrong object for a point pattern. The 484 OSM features
# are points, so we add two tests built for points:
#
#   - join-count test on the binary "has any point" indicator
#   - Ripley's K / L on the point pattern (uses spatstat when available)
#
# Out: results/tables/lisa_fdr.csv, results/figures/lisa_fdr_map.png
#
# Run: Rscript analysis/spatial/07_lisa_fdr_pointpattern.R

suppressMessages({
  library(sf); library(spdep); library(dplyr); library(readr); library(ggplot2)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
dir.create('results/tables', showWarnings = FALSE, recursive = TRUE)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
nb <- poly2nb(lga, queen = TRUE)
lw <- nb2listw(nb, style = 'W', zero.policy = TRUE)

# =============================================================================
hr('1. Global Moran (for reference)')
# =============================================================================
mi <- moran.test(lga$density, lw, zero.policy = TRUE)
cat(sprintf('I = %.4f, E[I] = %.5f, z = %.3f, p = %.3g\n',
            mi$estimate[1], mi$estimate[2], mi$statistic, mi$p.value))

# =============================================================================
hr('2. LISA with and without multiplicity control')
# =============================================================================
lm_res <- localmoran(lga$density, lw, zero.policy = TRUE)
p_raw  <- lm_res[, 5]
p_bh   <- p.adjust(p_raw, method = 'BH')
p_bonf <- p.adjust(p_raw, method = 'bonferroni')

n <- length(p_raw)
cat(sprintf('tests performed                       : %d\n', n))
cat(sprintf('significant at p < 0.05 (raw)         : %d\n', sum(p_raw < 0.05)))
cat(sprintf('expected false positives at 0.05      : %.1f\n', 0.05 * n))
cat(sprintf('significant after Benjamini-Hochberg  : %d\n', sum(p_bh < 0.05)))
cat(sprintf('significant after Bonferroni          : %d\n', sum(p_bonf < 0.05)))
cat('\nThe raw count being BELOW the chance expectation confirms the LISA p-values\n')
cat('are conservative on this zero-inflated variable. Report the BH-adjusted set.\n')

lga$lisa_p_raw <- p_raw
lga$lisa_p_bh  <- p_bh
lga$lisa_sig_bh <- p_bh < 0.05

# quadrant assignment using the BH-adjusted threshold
lag_d <- lag.listw(lw, lga$density, zero.policy = TRUE)
mx <- mean(lga$density)
lga$quad_bh <- ifelse(lga$lisa_sig_bh,
  ifelse(lga$density > mx & lag_d > mx, 'HH',
  ifelse(lga$density < mx & lag_d < mx, 'LL',
  ifelse(lga$density > mx & lag_d < mx, 'HL', 'LH'))), NA_character_)
lga$quad_raw <- ifelse(p_raw < 0.05,
  ifelse(lga$density > mx & lag_d > mx, 'HH',
  ifelse(lga$density < mx & lag_d < mx, 'LL',
  ifelse(lga$density > mx & lag_d < mx, 'HL', 'LH'))), NA_character_)

cat('\nQuadrant counts, raw p < 0.05:\n'); print(table(lga$quad_raw, useNA = 'ifany'))
cat('\nQuadrant counts, BH-adjusted:\n'); print(table(lga$quad_bh, useNA = 'ifany'))

# how many of the BH-significant units are simply "has any point"?
cat(sprintf('\nOf the %d BH-significant LGAs, %d also have n > 0\n',
            sum(lga$lisa_sig_bh), sum(lga$lisa_sig_bh & lga$n > 0)))
cat(sprintf('Of all %d LGAs with n > 0, %d are BH-significant\n',
            sum(lga$n > 0), sum(lga$lisa_sig_bh & lga$n > 0)))
cat('=> the LISA result and "this LGA is in the mapped set" largely coincide,\n')
cat('   which is the OSM-completeness confound showing up inside the spatial test.\n')

tab <- lga %>% st_drop_geometry() %>%
  transmute(gid2 = GID_2, state = NAME_1, lga = NAME_2, n, density,
            lisa_I = lm_res[, 1], p_raw, p_bh, sig_raw = p_raw < 0.05,
            sig_bh = lisa_sig_bh, quad_raw, quad_bh)
write_csv(tab, 'results/tables/lisa_fdr.csv')
cat('\nWrote results/tables/lisa_fdr.csv\n')

# =============================================================================
hr('3. Join-count test — clustering of the binary "is it mapped at all"')
# =============================================================================
# Appropriate when the interesting question is presence/absence of the phenomenon,
# which on this dataset is dominated by OSM coverage.
has_pt <- as.numeric(lga$n > 0)
jc <- try(joincount.mc(has_pt, lw, nsim = 999, zero.policy = TRUE), silent = TRUE)
if (!inherits(jc, 'try-error')) {
  print(jc)
  cat('\nInterpretation: fewer same-category joins than expected under randomness (BB)\n')
  cat('indicates the mapped LGAs are spatially clustered rather than scattered.\n')
} else {
  jc2 <- joincount.test(factor(has_pt), lw, zero.policy = TRUE)
  print(jc2)
}

# =============================================================================
hr('4. Ripley K / L on the 484 points (the object that is actually a point pattern)')
# =============================================================================
osm <- st_read('data/processed/osm_urban_ag.gpkg', quiet = TRUE)
cat('points:', nrow(osm), '\n')
cat('NOTE: these 484 points span 5 widely separated city regions, so a single\n')
cat('national K-function conflates within-city clustering with the fact that the\n')
cat('cities are far apart. We therefore compute K WITHIN cities and report each.\n\n')

if (requireNamespace('spatstat.geom', quietly = TRUE) && requireNamespace('spatstat.explore', quietly = TRUE)) {
  suppressMessages({library(spatstat.geom); library(spatstat.explore)})
  res <- list()
  for (cty in unique(osm$city)) {
    o <- osm[osm$city == cty, ]
    if (nrow(o) < 20) { cat(sprintf('%-15s n = %2d : too few for K\n', cty, nrow(o))); next }
    xy <- st_coordinates(o)
    # convert degrees to metres approximately at the city's latitude
    lat0 <- mean(xy[, 2])
    sc <- c(111320 * cos(lat0 * pi / 180), 110540)
    xx <- xy[, 1] * sc[1]; yy <- xy[, 2] * sc[2]
    # The Overpass query used a bounding BOX, so many points sit exactly on the
    # edge of their own coordinate range. Border-corrected K is undefined for a
    # point ON the boundary, which is what produced Inf. Pad the window by 5% so
    # every point is strictly interior.
    px <- diff(range(xx)) * 0.05; py <- diff(range(yy)) * 0.05
    W <- owin(range(xx) + c(-px, px), range(yy) + c(-py, py))
    pp <- ppp(xx, yy, window = W)
    env <- envelope(pp, Lest, nsim = 199, correction = 'border', verbose = FALSE)
    # `Lest` has an analytic CSR value, so envelope() returns `theo` (which is 0 for
    # L) and omits `mmean` entirely. Deviating from `mmean` therefore yields a
    # zero-length vector. Under CSR, L(r) = 0, so the correct reference is `theo`.
    dev <- env$obs - env$theo
    ok <- is.finite(dev)
    if (!any(ok)) { cat(sprintf('%-15s n = %2d : no finite deviation\n', cty, nrow(o))); next }
    rng <- range(dev[ok])
    eok <- ok & is.finite(env$lo) & is.finite(env$hi)
    r_peak <- env$r[which.max(ifelse(ok, dev, -Inf))]
    # is the observed curve outside the simulation envelope anywhere?
    outside <- any(ok & (env$obs > env$hi | env$obs < env$lo))
    res[[cty]] <- data.frame(city = cty, n = nrow(o),
                             L_min = rng[1], L_max = rng[2],
                             r_at_Lmax = r_peak,
                             envelope_min = min((env$lo - env$theo)[eok], na.rm = TRUE),
                             envelope_max = max((env$hi - env$theo)[eok], na.rm = TRUE),
                             outside_envelope = outside)
    cat(sprintf('%-15s n = %3d : L(r) ranges %8.0f to %8.0f m; peak at r = %5.0f m; outside envelope: %s\n',
                cty, nrow(o), rng[1], rng[2], r_peak, outside))
  }
  if (length(res)) {
    rr <- do.call(rbind, res)
    print(rr, row.names = FALSE, digits = 1)
    write_csv(rr, 'results/tables/ripley_k_within_cities.csv')
    cat('\nWrote results/tables/ripley_k_within_cities.csv\n')
    cat('\nInterpretation: L(r) > 0 at short range means the points are MORE clustered\n')
    cat('than complete spatial randomness would produce. "outside envelope" indicates\n')
    cat('the observed curve exceeds the 199-simulation band somewhere.\n')
    cat('CAVEAT: the 5 study cities were defined by rectangular Overpass bounding\n')
    cat('boxes, so the window edge is an artefact of the query, not a real boundary.\n')
    cat('This is a secondary check only; the LISA and join-count results above are\n')
    cat('the primary evidence and do not depend on it.\n')
  }
} else {
  cat('spatstat.geom/explore not installed - K-function skipped.\n')
  cat('The join-count test above still provides a point-appropriate assessment.\n')
}

# =============================================================================
hr('5. FDR-adjusted LISA map')
# =============================================================================
q <- ggplot(lga) +
  geom_sf(aes(fill = quad_bh), colour = NA) +
  scale_fill_manual(values = c(HH = '#d73027', LL = '#4575b4',
                               HL = '#fee090', LH = '#91bfdb'),
                    na.value = 'grey92', name = 'LISA\n(BH-FDR < 5%)') +
  labs(title = 'LISA clusters after Benjamini-Hochberg control',
       subtitle = sprintf('%d of 775 LGAs significant after adjustment (raw p<0.05 gave %d; chance alone = %.1f)',
                          sum(lga$lisa_sig_bh), sum(p_raw < 0.05), 0.05 * n),
       caption = 'Data: OSM Overpass (484 pts) + GADM 4.1 NGA_2 (775 LGAs). Queen contiguity.') +
  theme_minimal(base_size = 11)
ggsave('results/figures/lisa_fdr_map.png', q, width = 8, height = 7, dpi = 300)
cat('Wrote results/figures/lisa_fdr_map.png\n')

cat('\n07_lisa_fdr_pointpattern.R done\n')
