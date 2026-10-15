#!/usr/bin/env Rscript
# check_sensitivity.R - robustness of the headline spatial results.
#
# FIXED 2026-10-15: the climate section called `lm(density ~ log_area + ...)` on `lga`,
# but `log_area` was only ever created on the Kano-excluded subset `lga_nkano`. In a
# fresh R session (which is how build.R runs it) the object did not exist and the script
# died with "object 'log_area' not found". `log_area` is now derived once, up front.
#
# CHANGED 2026-10-15: the Kano-excluded *climate* refit is no longer reported as
# evidence. It shares the pseudoreplication defect documented in
# analysis/spatial/08_climate_honest.R (rainfall is a 5-valued city constant), so a
# Kano-excluded variant of it inherits the same problem. The section is retained only
# to demonstrate that the defect persists under the exclusion, and is labelled as such.
#
# Run: Rscript analysis/spatial/check_sensitivity.R

library(sf); library(spdep); library(spatialreg); library(dplyr); library(readr)

lga <- st_read('results/lga_lisa.gpkg', quiet = TRUE)
lga$log_area <- log(lga$area_km2)          # <- derived once, for every later use

nb_q <- poly2nb(lga, queen = TRUE);  lw_q <- nb2listw(nb_q, style = 'W', zero.policy = TRUE)
nb_r <- poly2nb(lga, queen = FALSE); lw_r <- nb2listw(nb_r, style = 'W', zero.policy = TRUE)

cat('queen\n'); print(moran.test(lga$density, lw_q, zero.policy = TRUE))
cat('rook\n');  print(moran.test(lga$density, lw_r, zero.policy = TRUE))

# --- Kano excluded: is the clustering one state's doing? ----------------------
lga_nkano <- lga %>% filter(NAME_1 != 'Kano')
nb_nk <- poly2nb(lga_nkano, queen = TRUE)
lw_nk <- nb2listw(nb_nk, style = 'W', zero.policy = TRUE)
cat('Kano excluded N', nrow(lga_nkano), '\n')
print(moran.test(lga_nkano$density, lw_nk, zero.policy = TRUE))
m0 <- lm(density ~ log_area, data = lga_nkano)
print(summary(m0))
mlag <- lagsarlm(density ~ log_area, data = lga_nkano, listw = lw_nk, zero.policy = TRUE)
print(summary(mlag))

# --- climate, Kano excluded: retained to show the defect persists --------------
nasa <- read_csv('data/processed/nasa_annual.csv', show_col_types = FALSE)
nasa$city <- tolower(nasa$city)
state_to_city <- c('Federal Capital Territory' = 'abuja', 'Lagos' = 'lagos',
                   'Kano' = 'kano', 'Rivers' = 'port_harcourt', 'Gombe' = 'gombe')
lga$city_key <- state_to_city[lga$NAME_1]
lga <- left_join(lga, nasa, by = c('city_key' = 'city'))

dat <- lga %>% filter(n > 0, !is.na(prectot_sum), NAME_1 != 'Kano')
cat('\nclimate Kano excluded N', nrow(dat), '\n')
cat('distinct cities in this subset:', length(unique(dat$city_key)),
    '| distinct rainfall values:', length(unique(round(dat$prectot_sum))), '\n')

if (nrow(dat) >= 10) {
  m0c <- lm(density ~ log_area + prectot_sum + t2m_mean, data = dat %>% st_drop_geometry())
  print(summary(m0c))
  cat('\nWARNING: this refit is NOT evidence for H2. Excluding Kano leaves',
      length(unique(dat$city_key)), 'cities, so rainfall still has only',
      length(unique(round(dat$prectot_sum))), 'unique values while the model claims',
      nrow(dat), 'independent rows.\n')
  cat('The exclusion tests nothing about the climate effect; it only reproduces the\n')
  cat('pseudoreplication in a smaller sample. See 08_climate_honest.R.\n')

  city <- dat %>% group_by(city_key) %>%
    summarise(density = mean(density), rain = mean(prectot_sum), .groups = 'drop') %>%
    as.data.frame()
  mc <- lm(density ~ rain, data = city)
  cat(sprintf('\nKano-excluded city-level regression (K = %d): rain p = %.3f\n',
              nrow(city), summary(mc)$coefficients['rain', 4]))
}
