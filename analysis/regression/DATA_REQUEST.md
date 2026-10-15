# =============================================================================
# DATA REQUEST - survey microdata (analysis/regression/)
# =============================================================================
# Status: BLOCKED. The analytic dataset behind manuscript Table 1 does not exist
# anywhere in this repository. See docs/statistical-review-2026-10-15.md s2.1 and
# data/raw/README-survey-data.md.
#
# The model reported in the manuscript (Nagelkerke = 0.348, AIC = 132.45,
# BIC = 145.90) is internally impossible, and the exact values cannot be
# re-derived without the respondent-level data. 01_logistic_fulltime.R runs the
# whole analysis correctly as soon as a file with the columns below is placed in
# data/raw/.
#
# ---------------------------------------------------------------------------
# REQUIRED FILE:  data/raw/survey_urban_ag.csv   (or .sav / .xlsx / .dta)
# ONE ROW PER ANALYSED RESPONDENT. Expected n = 285 (306 administered, 21 non-returns).
# ---------------------------------------------------------------------------
#
#  column              type      values                          notes
#  ------------------  --------  ------------------------------  -------------------------
#  id                  integer   unique                          may be dropped before deposit
#  fulltime            integer   1 = full-time, 0 = part-time   DEPENDENT VARIABLE
#  gender              integer   1 = male, 0 = female            (or "Male"/"Female")
#  age                 integer   years                           continuous
#  married             integer   1 = married, 0 = otherwise      collapsed from 4 categories
#  education_years     integer   years of formal schooling       continuous
#  income_thousand     numeric   monthly income in NGN '000     <- UNIT MUST BE CONFIRMED
#  extension_access    integer   1 = yes, 0 = no                 binary
#  association_access  integer   1 = yes, 0 = no                 binary
#
#  OPTIONAL (strengthen the paper materially if available):
#    ward              text      one of the 8 sampled wards      enables ward fixed effects
#    farm_size_m2      numeric   plot area in m^2                enables size as a control
#    tenure            text      owned/freehold/squatting/...    enables tenure analysis
#    irrigation        integer   1 = yes, 0 = no                 enables dry-season analysis
#
# ---------------------------------------------------------------------------
# WHY `income_thousand` IS THE CRITICAL UNKNOWN
# ---------------------------------------------------------------------------
# The manuscript reports OR = 1.005 "per unit" of monthly income. The unit is
# never stated, and the interpretation swings enormously:
#
#   unit = NGN 1        -> OR per +NGN10,000 = exp(0.005 * 10,000) = 5.2e21   absurd
#   unit = NGN 1,000    -> OR per +NGN10,000 = exp(0.005 * 10)     = 1.051    plausible
#
# The second is almost certainly correct (SPSS coding in thousands is conventional
# in this literature), which means the coefficient is fine and the REPORTING was
# the defect. 01_logistic_fulltime.R reports per-NGN10,000 regardless, and prints
# the implied per-unit scale so the assumption is visible rather than hidden.
#
# ---------------------------------------------------------------------------
# WHAT THE SCRIPT PRODUCES (all currently missing or unverifiable)
# ---------------------------------------------------------------------------
#   - real -2 log-likelihood, AIC, BIC          (replaces the impossible pair)
#   - McFadden, Cox-Snell, Nagelkerke pseudo-R2 (with correct interpretation)
#   - odds ratios with 95% profile CIs          (currently point estimates only)
#   - variance inflation factors                (collinearity check)
#   - Hosmer-Lemeshow goodness of fit           (calibration)
#   - classification table, sensitivity, specificity, AUC
#   - AN AUDIT: recomputes the reported b/SE -> p and reports mismatches
#   - A VERDICT: tests whether the reported (Nagelkerke, AIC, BIC) triple is
#     internally consistent, reproducing the arithmetic in the review
# =============================================================================
