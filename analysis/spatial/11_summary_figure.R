#!/usr/bin/env Rscript
# 11_summary_figure.R — one panel that tells the whole spatial story.
#
# The earlier README advertised six separate screenshots. A reader learns more
# from one small-multiples panel that shows the analysis sequence and where it
# corrected itself than from six fragments. Four panels:
#
#   (1) the 484 points, by city          - the raw input
#   (2) density per LGA (log scale)      - normalising by area
#   (3) LISA clusters after BH-FDR       - where the clustering is
#   (4) fitted density, Gaussian vs NB   - why the model family had to change
#
# Out: results/figures/summary_panel.png
#
# Run: Rscript analysis/spatial/11_summary_figure.R

suppressMessages({
  library(sf); library(spdep); library(spatialreg)
  library(dplyr); library(ggplot2); library(patchwork)
})

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
osm <- st_read('data/processed/osm_urban_ag.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)

nb <- poly2nb(lga, queen = TRUE)
lw <- nb2listw(nb, style = 'W', zero.policy = TRUE)

# --- panel 1: raw points -----------------------------------------------------
p1 <- ggplot() +
  geom_sf(data = lga, fill = 'grey96', colour = 'grey80', linewidth = 0.08) +
  geom_sf(data = osm, aes(colour = city), size = 0.7, alpha = 0.8, show.legend = 'point') +
  scale_colour_brewer(palette = 'Set1', name = NULL) +
  labs(title = '1. Raw input', subtitle = sprintf('%d OSM features in 5 city boxes', nrow(osm))) +
  theme_minimal(base_size = 9) +
  theme(legend.position = 'bottom', legend.key.height = unit(8, 'pt'),
        legend.text = element_text(size = 6.5)) +
  guides(colour = guide_legend(nrow = 2, override.aes = list(size = 1.6)))

# --- panel 2: density ---------------------------------------------------------
# A continuous fill legend collided with its own tick labels and the map was
# almost entirely one colour, which hides the actual finding: 95% of LGAs are
# exactly zero. Discrete classes say that directly.
lga$dens_class <- cut(lga$density,
  breaks = c(-Inf, 0, 0.01, 0.1, Inf),
  labels = c("0 (95% of LGAs)", "0 - 0.01", "0.01 - 0.1", "> 0.1"),
  right = TRUE)
p2 <- ggplot(lga) +
  geom_sf(aes(fill = dens_class), colour = "grey85", linewidth = 0.05) +
  scale_fill_manual(values = c("0 (95% of LGAs)" = "grey93",
                               "0 - 0.01" = "#9ecae1",
                               "0.01 - 0.1" = "#3182bd",
                               "> 0.1" = "#08519c"),
                    name = "Points per km2", drop = FALSE) +
  labs(title = "2. Normalised by area",
       subtitle = sprintf("95%% of LGAs are exactly zero; max %.2f km-2", max(lga$density))) +
  theme_minimal(base_size = 9) +
  theme(legend.position = "bottom", legend.key.size = unit(8, "pt"),
        legend.text = element_text(size = 6.5),
        legend.title = element_text(size = 7)) +
  guides(fill = guide_legend(nrow = 2))

# --- panel 3: LISA ------------------------------------------------------------
# Panel 3 must show the SAME test the report recommends. `lga_lisa.gpkg` stores
# lisa_quad computed at the raw p < 0.05 threshold (23 LGAs). The defensible
# figure is the Benjamini-Hochberg adjusted set (19), so recompute it here rather
# than reusing a column that would overstate the result.
lm_s <- localmoran(lga$density, lw, zero.policy = TRUE)
p_bh <- p.adjust(lm_s[, 5], method = 'BH')
lag_d <- lag.listw(lw, lga$density, zero.policy = TRUE)
mx <- mean(lga$density)
quad_bh <- ifelse(p_bh < 0.05,
  ifelse(lga$density > mx & lag_d > mx, 'HH',
  ifelse(lga$density < mx & lag_d < mx, 'LL',
  ifelse(lga$density > mx & lag_d < mx, 'HL', 'LH'))), NA_character_)
lga$lisa_lab <- factor(ifelse(is.na(quad_bh), 'not significant', quad_bh),
                       levels = c('HH', 'LL', 'HL', 'LH', 'not significant'))
p3 <- ggplot(lga) +
  geom_sf(aes(fill = lisa_lab), colour = NA) +
  scale_fill_manual(
    values = c(HH = '#d73027', LL = '#4575b4', HL = '#fee090', LH = '#91bfdb',
               'not significant' = 'grey92'),
    name = NULL, drop = FALSE) +
  labs(title = '3. Where the clustering is',
       subtitle = sprintf('LISA after BH-FDR: %d of 775 LGAs significant (raw p<0.05 gave %d)',
                         sum(!is.na(quad_bh)), sum(lm_s[, 5] < 0.05)),
       caption = 'grey = not significant') +
  theme_minimal(base_size = 9) +
  theme(legend.position = 'bottom', legend.key.size = unit(8, 'pt'),
        legend.text = element_text(size = 6.5),
        plot.caption = element_text(size = 6.5, colour = 'grey45', hjust = 0)) +
  guides(fill = guide_legend(nrow = 1))

# --- panel 4: model family ----------------------------------------------------
fv_gauss <- as.numeric(fitted(lagsarlm(density ~ log_area, data = lga, listw = lw,
                                       zero.policy = TRUE, tol.solve = 1e-10)))
nb_slope <- MASS::glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)
fv_nb <- fitted(nb_slope) / lga$area_km2
n_neg <- sum(fv_gauss < 0)

dd <- rbind(
  data.frame(fitted = fv_gauss, model = 'Gaussian spatial lag (the earlier model)'),
  data.frame(fitted = fv_nb,    model = 'Negative binomial, area offset (the fix)')
)
dd$sign <- ifelse(dd$fitted < 0, 'impossible (< 0)', 'admissible (>= 0)')

p4 <- ggplot(dd, aes(x = fitted, fill = sign)) +
  geom_histogram(bins = 90, alpha = 0.9, position = 'stack') +
  annotate('rect', xmin = -Inf, xmax = 0, ymin = -Inf, ymax = Inf,
           fill = '#d73027', alpha = 0.07) +
  geom_vline(xintercept = 0, linetype = 'dashed', colour = 'grey20', linewidth = 0.4) +
  facet_wrap(~model, scales = 'free_x') +
  scale_fill_manual(values = c('impossible (< 0)' = '#d73027',
                               'admissible (>= 0)' = '#4575b4'), name = NULL) +
  labs(title = '4. Why the model family changed',
       subtitle = sprintf('%d of 775 Gaussian fitted values are negative; a rate model cannot be',
                          n_neg),
       x = 'Fitted density (points per km2)', y = 'LGAs') +
  theme_minimal(base_size = 9) +
  theme(strip.text = element_text(size = 7.5), legend.position = 'bottom',
        legend.text = element_text(size = 6.5))

panel <- (p1 | p2) / (p3 | p4) +
  plot_annotation(
    title = 'Urban agriculture in Nigerian OpenStreetMap: from raw points to a defensible model',
    subtitle = 'Each panel is reproducible from analysis/spatial/*.R against the frozen data in data/raw/.',
    caption = 'Data: OSM Overpass (ODbL) + GADM v4.1 + NASA POWER. Run analysis/spatial/audit_claims.R to verify every number.',
    theme = theme(plot.title = element_text(size = 13, face = 'bold'),
                  plot.subtitle = element_text(size = 9.5),
                  plot.caption = element_text(size = 7.5, colour = 'grey40'))
  )

ggsave('results/figures/summary_panel.png', panel, width = 12, height = 9, dpi = 300)
cat('Wrote results/figures/summary_panel.png\n')
cat(sprintf('Panel 4 shows %d of %d Gaussian fitted values below zero.\n', n_neg, length(fv_gauss)))
cat(sprintf('Panel 3 shows %d BH-significant LGAs (raw p<0.05 would have shown %d).\n',
            sum(!is.na(quad_bh)), sum(lm_s[, 5] < 0.05)))
