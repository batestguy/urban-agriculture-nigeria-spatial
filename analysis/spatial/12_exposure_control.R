#!/usr/bin/env Rscript
# 12_exposure_control.R — does the spatial pattern survive conditioning on mapping effort?
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# `landuse=farmland` inside a rectangular city bounding box measures how much of a
# place OpenStreetMap contributors have mapped, at least as much as it measures
# urban agriculture. Kano is the best-mapped state in Nigerian OSM and also has the
# most "urban agriculture" points (189 of 484). Those two facts are not separable
# without an independent measure of mapping effort.
#
# `scripts/fetch_osm_exposure.py` supplies that measure: per-LGA counts of
# `way["building"]` and `way["highway"]` inside the LGA polygon. This script then
# asks the question that matters:
#
#     Given how much of this LGA is mapped at all, is urban agriculture
#     unusually present or absent?
#
# Implementation: negative binomial at the LGA level with the mapped-building count
# as an OFFSET alongside area, so the model predicts UA features per unit of
# *mapped environment* rather than per km².
#
# Requires: data/raw/osm_exposure_by_lga.csv (may be partial; handled honestly)
#
# Run: Rscript analysis/spatial/12_exposure_control.R

suppressMessages({
  library(sf); library(dplyr); library(readr); library(MASS)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
dir.create('results/tables', showWarnings = FALSE, recursive = TRUE)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)

expo_path <- 'data/raw/osm_exposure_by_lga.csv'
if (!file.exists(expo_path)) {
  cat('No exposure file. Run: python scripts/fetch_osm_exposure.py\n')
  quit(status = 0)
}

expo <- read_csv(expo_path, show_col_types = FALSE)
expo <- expo %>% filter(!is.na(n_buildings), n_buildings > 0)
cat(sprintf('Exposure layer: %d LGAs with building counts (%d with points, %d controls)\n',
            nrow(expo), sum(expo$n > 0), sum(expo$n == 0)))

expo_ex <- expo[, c('gid2', 'n_buildings', 'n_highways')]
names(expo_ex) <- c('GID_2', 'n_buildings', 'n_highways')

d <- lga %>% left_join(expo_ex, by = 'GID_2') %>%
  filter(!is.na(n_buildings), n_buildings > 0) %>%
  mutate(log_bldg = log(n_buildings))

# =============================================================================
hr('1. The confound, made visible')
# =============================================================================
ct <- cor.test(d$n, d$n_buildings, method = 'spearman')
cat(sprintf('Spearman(UA feature count, mapped buildings) : rho = %.3f, p = %.3g  (n = %d)\n',
            ct$estimate, ct$p.value, nrow(d)))
ct2 <- cor.test(d$n, d$n_highways, method = 'spearman')
cat(sprintf('Spearman(UA feature count, mapped highways)  : rho = %.3f, p = %.3g\n',
            ct2$estimate, ct2$p.value))

cat('\nCross-tab: has any UA feature  x  above-median mapped buildings\n')
tab <- table(UA_points = d$n > 0, High_mapping = d$n_buildings > median(d$n_buildings))
print(tab)
ch <- suppressWarnings(chisq.test(tab))
cat(sprintf('\nchi-square = %.2f on 1 df, p = %.4f\n', ch$statistic, ch$p.value))

cat(sprintf('\nMedian mapped buildings - LGAs WITH UA points : %.0f\n',
            median(d$n_buildings[d$n > 0])))
cat(sprintf('Median mapped buildings - LGAs WITHOUT points : %.0f\n',
            median(d$n_buildings[d$n == 0])))
cat('\nIf the second number is far below the first, the "urban agriculture" layer is\n')
cat('partly an artefact of where contributors have mapped.\n')

# =============================================================================
hr('2. Does the area effect survive conditioning on mapping effort?')
# =============================================================================
cat('Model A (as elsewhere): NB, area offset only\n')
mA <- glm.nb(n ~ log_area + offset(log_area), data = d)
cat(sprintf('  log_area b = %+.4f (p = %.3g) | AIC %.2f\n',
            coef(mA)['log_area'], summary(mA)$coefficients['log_area', 4], AIC(mA)))

cat('\nModel B: NB, area offset + mapped-building offset\n')
mB <- glm.nb(n ~ log_area + offset(log_area) + offset(log_bldg), data = d)
cat('  (two offsets: predicts UA per unit of area AND per unit of mapped environment)\n')
coB <- summary(mB)$coefficients
print(round(coB, 4))
cat(sprintf('\n  log_area b = %+.4f (p = %.3g) | AIC %.2f\n',
            coB['log_area', 1], coB['log_area', 4], AIC(mB)))
cat(sprintf('  IRR for log_area (density scale) = %.4f\n', exp(coB['log_area', 1])))

cat('\nModel C: NB, area offset only, restricted to LGAs with points (n = 39-ish)\n')
d_pos <- d %>% filter(n > 0)
mC <- glm.nb(n ~ log_area + offset(log_area), data = d_pos)
cat(sprintf('  log_area b = %+.4f (p = %.3g) | n = %d\n',
            coef(mC)['log_area'], summary(mC)$coefficients['log_area', 4], nrow(d_pos)))

# =============================================================================
hr('3. Verdict')
# =============================================================================
bA <- coef(mA)['log_area']; bB <- coef(mB)['log_area']
pA <- summary(mA)$coefficients['log_area', 4]
pB <- summary(mB)$coefficients['log_area', 4]

cat(sprintf('Area effect without exposure control : b = %+.4f (p = %.3g)\n', bA, pA))
cat(sprintf('Area effect WITH exposure control    : b = %+.4f (p = %.3g)\n', bB, pB))
cat(sprintf('Change in the coefficient             : %+.1f%%\n',
            100 * (bB - bA) / abs(bA)))

if (pB < 0.05 && sign(bB) == sign(bA)) {
  cat('\n=> The area effect SURVIVES conditioning on mapping effort.\n')
  cat('   Larger LGAs remain less densely covered even once we control for how much\n')
  cat('   of each LGA is mapped. H3 is not an artefact of OSM completeness.\n')
} else if (sign(bB) != sign(bA)) {
  cat('\n=> The area effect REVERSES once mapping effort is controlled.\n')
  cat('   The earlier estimate was confounded by OSM coverage.\n')
} else {
  cat('\n=> The area effect does NOT survive: once mapping effort is accounted for,\n')
  cat('   it is no longer distinguishable from zero. The earlier result was confounded.\n')
}

cat(sprintf('\nn = %d LGAs. %s\n', nrow(d),
            if (nrow(d) < 70) 'PARTIAL exposure run - re-run fetch_osm_exposure.py to completion and rerun.' else ''))

# =============================================================================
hr('4. Reporting artefact')
# =============================================================================
out <- data.frame(
  model = c('Area offset only', 'Area + building offsets', 'With-points subset'),
  n     = c(nrow(d), nrow(d), nrow(d_pos)),
  log_area_b = c(bA, bB, coef(mC)['log_area']),
  p          = c(pA, pB, summary(mC)$coefficients['log_area', 4]),
  AIC        = c(AIC(mA), AIC(mB), AIC(mC))
)
print(out, row.names = FALSE, digits = 4)
write_csv(out, 'results/tables/exposure_control.csv')
write_csv(d %>% st_drop_geometry() %>%
            transmute(GID_2, NAME_1, NAME_2, n, area_km2,
                      density, n_buildings, n_highways),
          'results/tables/exposure_merged.csv')
cat('\nWrote results/tables/exposure_control.csv and exposure_merged.csv\n')

cat('\n12_exposure_control.R done\n')
