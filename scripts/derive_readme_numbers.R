# scripts/derive_readme_numbers.R
#
# Re-derive the small set of numbers the README quotes that are not already
# sitting verbatim in a results table, and write them to
# results/tables/readme_numbers.csv so that scripts/verify_readme_claims.py
# can check the README against a file rather than against a hard-coded literal.
#
# Run from the repository root:  Rscript scripts/derive_readme_numbers.R

suppressPackageStartupMessages({
  library(sf)
  library(MASS)
})

lga <- st_read("results/lga_lisa.gpkg", quiet = TRUE)
lga$log_area <- log(lga$area_km2)

# Area as an exposure offset: a model of counts becomes a model of density.
m_rate  <- glm.nb(n ~ offset(log(area_km2)), data = lga)
m_slope <- glm.nb(n ~ log_area + offset(log(area_km2)), data = lga)
lr <- 2 * as.numeric(logLik(m_slope) - logLik(m_rate))
b  <- as.numeric(coef(m_slope)["log_area"])

pois <- glm(n ~ log_area + offset(log(area_km2)), family = poisson, data = lga)
disp <- sum(residuals(pois, type = "pearson")^2) / df.residual(pois)

out <- data.frame(
  quantity = c("log_area_slope", "lr_chi2", "fall_per_doubling_pct",
               "poisson_dispersion", "negbin_theta"),
  value = c(
    sprintf("%.3f", b),
    sprintf("%.1f", lr),
    sprintf("%.0f", 100 * (1 - 2^b)),
    sprintf("%.1f", disp),
    sprintf("%.3f", m_slope$theta)
  )
)

dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)
write.csv(out, "results/tables/readme_numbers.csv", row.names = FALSE)
print(out)
