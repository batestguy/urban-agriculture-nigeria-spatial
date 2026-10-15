#!/usr/bin/env Rscript
# 10_study_extent.R — where the study area actually is, and what fell outside it.
#
# WHY THIS SCRIPT EXISTS
# ----------------------
# The OSM layer was pulled with RECTANGULAR city bounding boxes. Rectangles leak
# across administrative lines, and `landuse=farmland` inside a rectangle includes
# ordinary rural farmland. Two consequences the earlier documentation did not state:
#
#   1. 43 of 484 points (8.9%) fall in states outside the five study states.
#      They were silently dropped from the climate subset (no city key) and simply
#      never mentioned.
#   2. The "Abuja" box contributes 15 points in the FCT and 17 in Niger - so the
#      MAJORITY of "Abuja" points are not in Abuja.
#
# This script quantifies the extent problem, reports it, and writes the artefact
# that a re-pull would use. It does NOT re-pull (that needs the network and is
# driven by scripts/fetch_osm_urban_ag.py with an admin-mask option).
#
# Out: results/tables/study_extent.csv, results/figures/study_extent.png
#
# Run: Rscript analysis/spatial/10_study_extent.R

suppressMessages({
  library(sf); library(dplyr); library(readr); library(ggplot2)
})

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')
dir.create('results/tables', showWarnings = FALSE, recursive = TRUE)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
osm <- st_read('data/processed/osm_urban_ag.gpkg', quiet = TRUE)

STUDY_STATES <- c('Federal Capital Territory', 'Lagos', 'Kano', 'Rivers', 'Gombe')

# =============================================================================
hr('1. Points by state, against the declared study states')
# =============================================================================
pts_state <- st_join(osm, lga[, c('GID_2', 'NAME_1')], left = TRUE) %>%
  st_drop_geometry() %>%
  count(city, NAME_1, name = 'points') %>%
  arrange(city, desc(points))
print(as.data.frame(pts_state), row.names = FALSE)

in_scope <- pts_state %>% filter(NAME_1 %in% STUDY_STATES)
out_scope <- pts_state %>% filter(!NAME_1 %in% STUDY_STATES | is.na(NAME_1))

cat(sprintf('\nPoints inside the five study states : %d\n', sum(in_scope$points)))
cat(sprintf('Points OUTSIDE them                 : %d (%.1f%% of %d)\n',
            sum(out_scope$points), 100 * sum(out_scope$points) / nrow(osm), nrow(osm)))

cat('\nOut-of-scope breakdown:\n')
print(as.data.frame(out_scope), row.names = FALSE)

# =============================================================================
hr('2. The bounding-box leak, shown per city')
# =============================================================================
leak <- pts_state %>%
  mutate(in_study = NAME_1 %in% STUDY_STATES) %>%
  group_by(city) %>%
  mutate(share_in = points / sum(points)) %>%
  ungroup() %>%
  filter(!in_study)
if (nrow(leak) == 0) {
  cat('No leakage detected.\n')
} else {
  cat('Each row is a state that the named city\'s bounding box captured:\n\n')
  print(as.data.frame(leak %>% select(city, leaked_into = NAME_1, points, share_of_city = share_in)),
        row.names = FALSE, digits = 3)
  cat('\nThe Abuja box is the clearest case: it returns more points in Niger State\n')
  cat('than in the Federal Capital Territory itself, so "Abuja" in the earlier\n')
  cat('documentation does not mean "in Abuja".\n')
}

# =============================================================================
hr('3. What a corrected extent would look like')
# =============================================================================
# Reconstruct the city-level bounding boxes from the coordinates, so the geometry
# of the problem is explicit rather than asserted.
# NOTE: st_coordinates() inside a grouped summarise() returns coordinates for the
# WHOLE layer, not the current group, which silently gave every city an identical
# box spanning the entire dataset. Split, compute per group, then bind.
bb <- do.call(rbind, lapply(split(osm, osm$city), function(g) {
  xy <- st_coordinates(g)
  data.frame(city = g$city[1],
             xmin = min(xy[, 1]), xmax = max(xy[, 1]),
             ymin = min(xy[, 2]), ymax = max(xy[, 2]),
             n = nrow(g))
}))
bb <- bb[order(bb$city), ]
bb$span_km_x <- round((bb$xmax - bb$xmin) * 111.32, 0)
bb$span_km_y <- round((bb$ymax - bb$ymin) * 110.54, 0)
cat('Recovered bounding boxes (degrees), with span in km:\n')
print(bb, row.names = FALSE, digits = 3)

cat('\nA corrected pull would replace each box with either:\n')
cat('  (a) the GADM level-2 polygons of the target LGAs (exact, already available), or\n')
cat('  (b) an urban-extent mask (e.g. GHS-SMOD or a built-up raster) intersected\n')
cat('      with those polygons, so peri-urban and rural farmland are excluded.\n')
cat('\nThese are city-scale boxes (3-98 km across), not regional ones. The leak happens\n')
cat('because a generous rectangle around a city near a state boundary necessarily\n')
cat('crosses it: Abuja sits against Niger, Lagos against Ogun. Even inside the\n')
cat('correct state, landuse=farmland remains ordinary farmland as well as urban\n')
cat('agriculture, so the extent fix alone does not make the layer a UA measure.\n')
cat('\nOption (a) is free and immediate: data/external/gadm41_NGA_2.shp already holds\n')
cat('the polygons, and scripts/fetch_osm_urban_ag.py would need only a poly: filter\n')
cat('instead of a bbox: filter - the same mechanism fetch_osm_exposure.py already uses.\n')

write_csv(pts_state, 'results/tables/study_extent.csv')
cat('\nWrote results/tables/study_extent.csv\n')

# =============================================================================
hr('4. Figure: declared scope vs realised scope')
# =============================================================================
d <- pts_state %>%
  mutate(scope = ifelse(NAME_1 %in% STUDY_STATES, 'Inside study states', 'LEAKED - outside'))
p <- ggplot(d, aes(x = reorder(paste(city, NAME_1, sep = ' / '), points),
                   y = points, fill = scope)) +
  geom_col() +
  coord_flip() +
  scale_fill_manual(values = c('Inside study states' = '#4575b4',
                               'LEAKED - outside' = '#d73027'), name = NULL) +
  labs(title = 'Bounding-box leakage in the OSM layer',
       subtitle = sprintf('%d of %d points (%.1f%%) fall outside the five declared study states',
                          sum(out_scope$points), nrow(osm),
                          100 * sum(out_scope$points) / nrow(osm)),
       x = 'City bounding box / state the point actually falls in',
       y = 'OSM features',
       caption = 'Rectangles leak across state lines, and landuse=farmland inside a rectangle includes rural farmland.') +
  theme_minimal(base_size = 10) + theme(legend.position = 'bottom')
ggsave('results/figures/study_extent.png', p, width = 8, height = 6, dpi = 300)
cat('Wrote results/figures/study_extent.png\n')

cat('\n10_study_extent.R done\n')
