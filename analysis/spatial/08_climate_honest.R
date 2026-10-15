#!/usr/bin/env Rscript
# 08_climate_honest.R — replacing the "N = 34 LGAs" claim with an honest one.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# `run_regression.R` reports a climate model with N = 34 LGAs and concludes that
# rainfall predicts urban-agriculture density (spatial error p = 0.018). That
# number is not supportable:
#
#   * The 34 LGAs carry only FIVE distinct annual rainfall values (one per city),
#     because NASA POWER was pulled at city centroids. Rainfall R^2 on city
#     dummies = 1.000 — the covariate IS city identity.
#   * The "spatial weights" on that subset form 5 disconnected components with an
#     isolate, so the spatial term is absorbing city effects, not inter-LGA
#     spillover. The fitted rho/lambda are negative, which is meaningless here.
#   * Between-city variance is only ICC = 0.102, so 90% of the outcome variation
#     is WITHIN cities while the covariate varies only BETWEEN them.
#
# Re-fit at the level the data actually replicates (the 5 cities) and the effect
# disappears (p = 0.58). This script does three things:
#
#   1. Demonstrates the pseudoreplication numerically.
#   2. Reports the honest city-level (K = 5) relationship with its uncertainty.
#   3. Tests whether the "aridity" hypothesis can be assessed at all with the
#      frozen data, and says plainly what would be required to assess it properly.
#
# Run: Rscript analysis/spatial/08_climate_honest.R

suppressMessages({
  library(sf); library(spdep); library(spatialreg)
  library(dplyr); library(readr); library(ggplot2)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
dir.create('results/tables', showWarnings = FALSE, recursive = TRUE)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)

nasa <- read_csv('data/processed/nasa_annual.csv', show_col_types = FALSE)
nasa$city <- tolower(nasa$city)
map <- c('Federal Capital Territory' = 'abuja', 'Lagos' = 'lagos', 'Kano' = 'kano',
         'Rivers' = 'port_harcourt', 'Gombe' = 'gombe')
lga$city_key <- map[lga$NAME_1]
lga <- left_join(lga, nasa, by = c('city_key' = 'city'))

dat <- lga %>% filter(n > 0, !is.na(prectot_sum)) %>% st_drop_geometry()

# =============================================================================
hr('1. The pseudoreplication, demonstrated')
# =============================================================================
cat(sprintf('rows in the "N = 34" model            : %d\n', nrow(dat)))
cat(sprintf('distinct cities                       : %d\n', length(unique(dat$city_key))))
cat(sprintf('distinct annual rainfall values       : %d\n', length(unique(round(dat$prectot_sum)))))
r2 <- summary(lm(prectot_sum ~ factor(city_key), data = dat))$r.squared
cat(sprintf('R^2 of rainfall on city dummies       : %.4f\n', r2))
cat('\n=> rainfall is a deterministic function of city. The model has 34 rows but the\n')
cat('   predictor has 5 unique values, so the effective sample size for that effect\n')
cat('   is 5, not 34. Treating the rows as independent is textbook pseudoreplication.\n')

ss_tot <- sum(residuals(lm(density ~ 1, data = dat))^2)
ss_within <- sum(residuals(lm(density ~ factor(city_key) - 1, data = dat))^2)
cat(sprintf('\nBetween-city share of variance (ICC): %.3f\n', (ss_tot - ss_within) / ss_tot))
cat(sprintf('Within-city  share of variance      : %.3f\n', ss_within / ss_tot))

sub_sf <- lga %>% filter(n > 0, !is.na(prectot_sum))
nb_sub <- poly2nb(sub_sf, queen = TRUE)
comp <- n.comp.nb(nb_sub)
cat(sprintf('\nConnected components in the subset weights: %d (one per city)\n', comp$nc))
cat(sprintf('Isolates (no neighbour): %d\n', sum(card(nb_sub) == 0)))
cat('=> the spatial weights are almost entirely WITHIN-city, so the spatial term is\n')
cat('   absorbing city effects rather than modelling inter-LGA spillover.\n')

# =============================================================================
hr('2. The same model at the two levels')
# =============================================================================
m34 <- lm(density ~ log_area + prectot_sum + t2m_mean, data = dat)
cat('--- (a) Naive OLS, treating 34 rows as independent ---\n')
print(round(summary(m34)$coefficients, 6))
cat(sprintf('R2 = %.4f\n', summary(m34)$r.squared))

if (requireNamespace('sandwich', quietly = TRUE)) {
  cat('\n--- (b) City-cluster-robust SE (K = 5 clusters) ---\n')
  ct <- lmtest::coeftest(m34, vcov = sandwich::vcovCL(m34, cluster = dat$city_key))
  print(round(ct, 6))
  cat('\nNote: with only 5 clusters the robust SE is itself unreliable; it is shown\n')
  cat('to demonstrate the direction of the correction, not as a final answer.\n')
}

city <- dat %>% group_by(city_key) %>%
  summarise(density = mean(density), rain = mean(prectot_sum), t2m = mean(t2m_mean),
            n_lga = n(), total_pts = sum(n), .groups = 'drop') %>% as.data.frame()
cat('\n--- (c) The honest replication level: K = 5 cities ---\n')
print(city, row.names = FALSE, digits = 4)

mc <- lm(density ~ rain, data = city)
cat('\nCity-mean regression, density ~ rainfall (K = 5):\n')
print(round(summary(mc)$coefficients, 6))
cat(sprintf('R2 = %.4f | residual df = %d | p(rainfall) = %.3f\n',
            summary(mc)$r.squared, mc$df.residual, summary(mc)$coefficients[2, 4]))
cat('\nWith 3 residual degrees of freedom, no rainfall effect can be established.\n')
cat('The honest statement is: "the data are consistent with the aridity hypothesis\n')
cat('but cannot test it", not "rainfall significantly predicts density".\n')

# correlation as a descriptive, since it needs no model
ct_sp <- cor.test(city$density, city$rain, method = 'spearman')
cat(sprintf('\nSpearman (K = 5), density vs rainfall: rho = %.3f, p = %.3f\n',
            ct_sp$estimate, ct_sp$p.value))
cat('Reportable as descriptive only, with n = 5 stated in the caption.\n')

# =============================================================================
hr('3. What the earlier N=34 result was actually detecting')
# =============================================================================
cat('The 34-row models reported PRECTOT significant at p = 0.018-0.035. Those rows\n')
cat('come from 5 cities with very different LGA counts (Kano 12, Lagos 15, Rivers 4,\n')
cat('FCT 2, Gombe 1). The significance tracks the number of rows a city contributes,\n')
cat('not the number of independent observations of rainfall.\n')
cat('\nCompare the fitted effect with the raw city contrast:\n')
cat(sprintf('  driest  city (Kano,   %.0f mm): mean density %.4f\n',
            city$rain[city$city_key == 'kano'], city$density[city$city_key == 'kano']))
cat(sprintf('  wettest city (Rivers, %.0f mm): mean density %.4f\n',
            city$rain[city$city_key == 'port_harcourt'],
            city$density[city$city_key == 'port_harcourt']))
cat('\nThat contrast is the entire basis of H2, and it rests on two cities. Report it\n')
cat('as a two-city descriptive comparison or not at all.\n')

# =============================================================================
hr('4. What would be needed to test H2 properly')
# =============================================================================
cat('Rainfall with WITHIN-city variation. Options:\n')
cat('  - CHIRPS (~5 km, daily, 1981-present, free, Africa-focused)\n')
cat('  - ERA5-Land (~9 km, hourly reanalysis)\n')
cat('  - TAMSAT (4 km, Africa, gauge-calibrated)\n')
cat('\nAny of these rasterises to LGA polygons and gives each LGA its own value, so\n')
cat('the 34-row model would have 34 distinct rainfall values rather than 5.\n')
cat('Until then, H2 is untestable and must be reported as such.\n')

write_csv(city, 'results/tables/climate_city_level.csv')

# =============================================================================
hr('5. Honest replacement figure')
# =============================================================================
p <- ggplot(city, aes(x = rain, y = density)) +
  geom_smooth(method = 'lm', se = TRUE, colour = 'grey40', linetype = 'dashed',
              alpha = 0.15) +
  geom_point(aes(size = total_pts), colour = '#d73027', alpha = 0.85) +
  geom_text(aes(label = city_key), vjust = -1.1, size = 3.2) +
  scale_size_continuous(range = c(3, 9), name = 'OSM points') +
  labs(title = 'Urban agriculture density vs annual rainfall — the honest unit of analysis',
       subtitle = sprintf('K = 5 cities, not 34 LGAs. Spearman rho = %.2f, p = %.2f. No effect is established.',
                          ct_sp$estimate, ct_sp$p.value),
       x = 'Annual precipitation 2023 (mm, NASA POWER)', y = 'Mean density (points per km2)',
       caption = 'Rainfall was sampled at city centroids, so it cannot vary within a city. The earlier N=34 model replicated one value across LGAs.') +
  theme_minimal(base_size = 11) + theme(legend.position = 'bottom')
ggsave('results/figures/climate_honest.png', p, width = 7.5, height = 5.5, dpi = 300)
cat('Wrote results/figures/climate_honest.png\n')

cat('\n08_climate_honest.R done\n')
