#!/usr/bin/env Rscript
# 05_export_lga_polys.R — export simplified LGA polygons for the Overpass exposure query.
#
# Why: the OSM point layer conflates *urban agriculture* with *OSM mapping effort*
# (Kano is the best-mapped state in Nigerian OSM). To separate the two we need an
# independent per-LGA measure of how much of the environment is mapped.
# Overpass `out count;` gives that cheaply, but needs a polygon filter, so we export
# simplified WGS84 rings here and let scripts/fetch_osm_exposure.py do the HTTP.
#
# Output: data/processed/lga_polys_for_overpass.csv  (gid2, state, lga, n, poly)
# Read-only with respect to the frozen raw data.

suppressMessages({library(sf); library(dplyr); library(readr)})

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)

# --- which LGAs get queried -------------------------------------------------
# (a) every LGA that holds at least one OSM point (the analysis set), and
# (b) a stratified control sample of LGAs with zero points from the same states,
#     so the exposure measure has variation to work with.
with_pts <- lga %>% filter(n > 0)

set.seed(20261015)
zero_ctl <- lga %>%
  filter(n == 0, NAME_1 %in% unique(with_pts$NAME_1)) %>%
  group_by(NAME_1) %>%
  slice_sample(n = 6) %>%          # 6 controls per state -> 30 controls
  ungroup()

sel <- bind_rows(with_pts, zero_ctl) %>%
  mutate(kind = ifelse(n > 0, 'has_points', 'control')) %>%
  arrange(NAME_1, desc(n))

cat(sprintf('Selected %d LGAs: %d with points, %d controls across %d states\n',
            nrow(sel), sum(sel$n > 0), sum(sel$n == 0), length(unique(sel$NAME_1))))

# --- simplify so the Overpass `poly:` string stays small ---------------------
# ~0.002 deg (~200 m) keeps urban shape while cutting vertex count hard.
simp <- st_simplify(st_geometry(sel), dTolerance = 0.002, preserveTopology = TRUE)
simp <- st_make_valid(simp)   # stays an sfc, so simp[[i]] indexes geometries

poly_string <- vapply(seq_len(nrow(sel)), function(i) {
  g <- simp[i]
  if (length(g) == 0 || all(st_is_empty(g))) return(NA_character_)
  g <- tryCatch(st_cast(g, 'POLYGON', warn = FALSE), error = function(e) g)
  g <- st_make_valid(g)
  if (length(g) == 0) return(NA_character_)
  keep <- which(!st_is_empty(g))
  if (length(keep) == 0) return(NA_character_)
  g <- g[keep]
  a <- as.numeric(st_area(st_sfc(g)))
  g <- g[[which.max(a)]]                       # largest polygon part
  m <- st_coordinates(g)[, c('Y', 'X'), drop = FALSE]   # Overpass wants lat lon
  if (nrow(m) > 1 && isTRUE(all.equal(unname(m[1, ]), unname(m[nrow(m), ])))) {
    m <- m[-nrow(m), , drop = FALSE]           # drop duplicated closing vertex
  }
  if (nrow(m) < 3) return(NA_character_)
  paste(sprintf('%.5f %.5f', m[, 1], m[, 2]), collapse = ' ')
}, character(1))

out <- sel %>%
  st_drop_geometry() %>%
  transmute(gid2 = GID_2, state = NAME_1, lga = NAME_2, n = n, kind = kind,
            n_vertices = lengths(strsplit(poly_string, ' ')) / 2, poly = poly_string)

if (anyNA(out$poly)) {
  cat('Dropping', sum(is.na(out$poly)), 'LGA(s) whose polygon collapsed below 3 vertices\n')
  out <- out %>% filter(!is.na(poly))
}

dir.create('data/processed', showWarnings = FALSE, recursive = TRUE)
write_csv(out, 'data/processed/lga_polys_for_overpass.csv')
cat(sprintf('Wrote data/processed/lga_polys_for_overpass.csv (%d rows; median %d vertices)\n',
            nrow(out), as.integer(median(out$n_vertices))))
