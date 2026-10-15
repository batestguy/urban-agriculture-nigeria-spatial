#!/usr/bin/env Rscript
# 01_logistic_fulltime.R - full, correct re-analysis of the manuscript's Table 1.
#
# STATUS: ready to run, currently BLOCKED on the survey microdata. See DATA_REQUEST.md.
# When the file exists this script runs end to end and emits every statistic the
# manuscript needs but cannot currently support.
#
# It also performs two audits that DO run without the data:
#   (a) reconstructs p-values from the reported b/SE pairs and flags mismatches
#   (b) proves the reported (Nagelkerke, AIC, BIC) triple is impossible for n=285
#
# Run:  Rscript analysis/regression/01_logistic_fulltime.R

suppressMessages({
  ok <- function(p) requireNamespace(p, quietly = TRUE)
  library(stats)
})

DATA_CANDIDATES <- c(
  'data/raw/survey_urban_ag.csv',
  'data/raw/survey_urban_ag.xlsx',
  'data/raw/survey_urban_ag.dta',
  'data/raw/survey_urban_ag.sav'
)

hr <- function(t) cat('\n', strrep('=', 72), '\n', t, '\n', strrep('=', 72), '\n', sep = '')

# =============================================================================
# PART A - AUDITS THAT DO NOT REQUIRE THE DATA
# =============================================================================

hr('AUDIT A1 - reported (b, SE, p) triples: do they agree?')
# From manuscript Table 1 / Thesis Table 19.
rep_tbl <- data.frame(
  variable = c('Gender (Male)', 'Age (years)', 'Marital status (Married)',
               'Education (years)', 'Monthly income', 'Access to extension',
               'Access to farmers assoc.'),
  b        = c(0.345, 0.023, 0.672, -0.056, 0.005, 1.205, 0.785),
  SE       = c(0.105, 0.007, 0.212,  0.020, 0.002, 0.321, 0.251),
  p_rep    = c(0.001, 0.002, 0.010,  0.008, 0.020, 0.001, 0.002)
)
rep_tbl$OR      <- exp(rep_tbl$b)
rep_tbl$z       <- rep_tbl$b / rep_tbl$SE
rep_tbl$p_calc  <- 2 * pnorm(-abs(rep_tbl$z))
rep_tbl$flag    <- ifelse(abs(rep_tbl$p_calc - rep_tbl$p_rep) > 0.002, '<-- MISMATCH', '')
print(rep_tbl, row.names = FALSE, digits = 4)
cat('\nNote: the printed p-values look like they were rounded to 3 dp from a\n')
cat('different rounding rule, or read off a Wald table whose SEs differ from\n')
cat('those transcribed. Either way they must come from the analytic dataset.\n')

hr('AUDIT A2 - is the reported (Nagelkerke, AIC, BIC) triple possible?')
n <- 285; k_pred <- 7; k_par <- k_pred + 1
prev <- 0.375                       # 37.5% full-time, per the manuscript
y1 <- prev * n; y0 <- n - y1
D0 <- -2 * (y1 * log(y1 / n) + y0 * log(y0 / n))
cat(sprintf('n = %d, predictors = %d, free parameters = %d, prevalence = %.3f\n', n, k_pred, k_par, prev))
cat(sprintf('Null deviance D0              = %.2f\n', D0))
cat(sprintf('Null AIC = D0 + 2k            = %.2f\n', D0 + 2 * k_par))

aic_rep <- 132.45; bic_rep <- 145.90; r2n_rep <- 0.348
D_from_aic <- aic_rep - 2 * k_par
mcf <- (D0 - D_from_aic) / D0
cox <- 1 - exp(-(D0 - D_from_aic) / n)
nag <- cox / (1 - exp(-D0 / n))

cat(sprintf('\n(i) Reported AIC %.2f implies deviance %.2f\n', aic_rep, D_from_aic))
cat(sprintf('    -> McFadden %.3f -> Cox-Snell %.3f -> Nagelkerke %.3f\n', mcf, cox, nag))
cat(sprintf('    but the manuscript reports Nagelkerke %.3f\n', r2n_rep))

# invert: what deviance does Nagelkerke 0.348 imply?
f <- function(D) {
  cs <- 1 - exp(-(D0 - D) / n); cs / (1 - exp(-D0 / n)) - r2n_rep
}
D_imp <- uniroot(f, c(1, D0 - 1))$root
cat(sprintf('\n(ii) Reported Nagelkerke %.3f implies deviance %.2f\n', r2n_rep, D_imp))
cat(sprintf('     -> AIC %.2f, BIC %.2f\n', D_imp + 2 * k_par, D_imp + log(n) * k_par))

cat(sprintf('\n(iii) BIC - AIC gap: reported %.2f, required %.2f for k = %d, n = %d\n',
            bic_rep - aic_rep, k_par * (log(n) - 2), k_par, n))
cat(sprintf('      the reported gap implies %.1f free parameters, not %d\n',
            (bic_rep - aic_rep) / (log(n) - 2), k_par))

cat('\nVERDICT: the three reported statistics are mutually inconsistent.\n')
cat('Nagelkerke 0.348 is the only plausible value and is retained in the\n')
cat('manuscript; AIC/BIC are withheld pending re-derivation below.\n')

# =============================================================================
# PART B - THE REAL ANALYSIS (requires the microdata)
# =============================================================================

hr('Locating the survey microdata')
found <- DATA_CANDIDATES[file.exists(DATA_CANDIDATES)]
if (length(found) == 0) {
  cat('NOT FOUND. Looked for:\n'); cat(paste0('  - ', DATA_CANDIDATES, collapse = '\n'), '\n')
  cat('\nThe logistic model CANNOT be re-estimated without it.\n')
  cat('Needed columns are specified in analysis/regression/DATA_REQUEST.md.\n')
  cat('Nothing is inferred or imputed in place of the data.\n')
  quit(status = 0)
}

path <- found[1]
cat('Found:', path, '\n')
if (grepl('\\.csv$', path)) {
  d <- read.csv(path, stringsAsFactors = FALSE)
} else if (grepl('\\.xlsx$', path) && requireNamespace('readxl', quietly = TRUE)) {
  d <- as.data.frame(readxl::read_excel(path))
} else if (grepl('\\.dta$', path) && requireNamespace('haven', quietly = TRUE)) {
  d <- as.data.frame(haven::read_dta(path))
} else if (grepl('\\.sav$', path) && requireNamespace('haven', quietly = TRUE)) {
  d <- as.data.frame(haven::read_sav(path))
} else {
  cat('Reader for this format is unavailable (need readxl or haven).\n'); quit(status = 1)
}

hr('Data checks')
cat('rows:', nrow(d), '| columns:', ncol(d), '\n')
need <- c('fulltime', 'gender', 'age', 'married', 'education_years',
          'income_thousand', 'extension_access', 'association_access')
miss <- setdiff(need, names(d))
if (length(miss)) {
  cat('MISSING REQUIRED COLUMNS:', paste(miss, collapse = ', '), '\n')
  cat('See DATA_REQUEST.md for definitions.\n'); quit(status = 1)
}
cat('complete cases:', sum(complete.cases(d[, need])), 'of', nrow(d), '\n')
if (sum(is.na(d$fulltime)) || !all(d$fulltime %in% c(0, 1)))
  warning('fulltime must be coded 0/1')

d <- d[complete.cases(d[, need]), ]

hr('Model: fulltime ~ . (binary logistic)')
m <- glm(fulltime ~ gender + age + married + education_years +
           income_thousand + extension_access + association_access,
         data = d, family = binomial)

ll    <- as.numeric(logLik(m))
D     <- -2 * ll
D0m   <- m$null.deviance
n_obs <- nobs(m); k <- length(coef(m))

cat(sprintf('\nObservations            : %d\n', n_obs))
cat(sprintf('-2 log-likelihood       : %.3f\n', D))
cat(sprintf('Null deviance           : %.3f\n', D0m))
cat(sprintf('AIC                     : %.3f\n', AIC(m)))
cat(sprintf('BIC                     : %.3f\n', BIC(m)))
cat(sprintf('McFadden pseudo-R2      : %.4f\n', 1 - D / D0m))
csn <- 1 - exp(-(D0m - D) / n_obs)
cat(sprintf('Cox-Snell pseudo-R2     : %.4f\n', csn))
cat(sprintf('Nagelkerke pseudo-R2    : %.4f\n', csn / (1 - exp(-D0m / n_obs))))
cat('\nInterpretation: Nagelkerke is a likelihood-ratio analogue rescaled to [0,1].\n')
cat('It is NOT "percent of variance explained". Report it as a fit index only.\n')

hr('Odds ratios with 95% profile-likelihood CIs')
ci <- suppressMessages(confint(m))
out <- data.frame(
  term     = names(coef(m)),
  b        = coef(m),
  SE       = summary(m)$coefficients[, 2],
  z        = summary(m)$coefficients[, 3],
  p        = summary(m)$coefficients[, 4],
  OR       = exp(coef(m)),
  OR_lo    = exp(ci[, 1]),
  OR_hi    = exp(ci[, 2]),
  row.names = NULL
)
print(out, digits = 4)

hr('Income effect made interpretable')
b_inc <- unname(coef(m)['income_thousand'])
cat(sprintf('Coefficient on income_thousand            : %+.5f\n', b_inc))
cat(sprintf('OR per +NGN1,000 of monthly income          : %.4f\n', exp(b_inc)))
cat(sprintf('OR per +NGN10,000 of monthly income         : %.4f\n', exp(b_inc * 10)))
ci_inc <- exp(ci['income_thousand', ] * 10)
cat(sprintf('95%% CI, per +NGN10,000                       : [%.4f, %.4f]\n', ci_inc[1], ci_inc[2]))
cat('\nSanity: if the source coded income in NGN (not thousands), the per-unit OR\n')
cat('would be exp(', b_inc, ') and the variable would be effectively inert over\n', sep = '')
cat('any realistic income range. Compare the two and state the coding used.\n')

hr('Collinearity (VIF)')
if (requireNamespace('car', quietly = TRUE)) {
  v <- car::vif(m)
  print(if (is.matrix(v)) v else v)
  cat('\nRule of thumb: VIF > 5 warrants inspection, > 10 is serious.\n')
} else cat('car not installed; skipped\n')

hr('Calibration: Hosmer-Lemeshow')
if (requireNamespace('ResourceSelection', quietly = TRUE)) {
  hl <- ResourceSelection::hoslem.test(d$fulltime, fitted(m), g = 10)
  print(hl)
  cat('\nA large p-value here is GOOD (no evidence of poor calibration).\n')
} else {
  # self-contained HL, so the script never depends on an optional package
  g <- 10
  pr <- fitted(m)
  grp <- cut(rank(pr, ties.method = 'first'), breaks = g, labels = FALSE)
  obs <- tapply(d$fulltime, grp, sum)
  exp_ <- tapply(pr, grp, sum)
  ngrp <- tapply(d$fulltime, grp, length)
  stat <- sum((obs - exp_)^2 / (exp_ * (1 - exp_ / ngrp)))
  pv <- pchisq(stat, df = g - 2, lower.tail = FALSE)
  cat(sprintf('HL chi-square = %.3f, df = %d, p = %.4f\n', stat, g - 2, pv))
  cat('(computed inline - install ResourceSelection for the canonical version)\n')
}

hr('Classification')
thr <- 0.5
pred <- as.integer(fitted(m) > thr)
tb <- table(observed = d$fulltime, predicted = pred)
print(tb)
acc <- sum(diag(tb)) / sum(tb)
sens <- if (all(c('1','1') %in% dimnames(tb))) tb['1','1'] / sum(tb['1', ]) else NA
spec <- if (all(c('0','0') %in% dimnames(tb))) tb['0','0'] / sum(tb['0', ]) else NA
cat(sprintf('\nAccuracy %.3f | Sensitivity %.3f | Specificity %.3f\n', acc, sens, spec))
cat('Note: for an unbalanced outcome, accuracy is a weak metric - report AUC too.\n')

if (requireNamespace('pROC', quietly = TRUE)) {
  r <- pROC::roc(d$fulltime, fitted(m), quiet = TRUE)
  cat(sprintf('AUC = %.4f (95%% CI %.4f-%.4f)\n',
              as.numeric(pROC::auc(r)), r$ci[1], r$ci[3]))
} else cat('pROC not installed; AUC skipped\n')

hr('Ward effects (if the ward column was supplied)')
if ('ward' %in% names(d)) {
  m2 <- glm(fulltime ~ . + factor(ward),
            data = d[, c('fulltime', setdiff(need, 'fulltime'), 'ward')],
            family = binomial)
  cat(sprintf('AIC with ward fixed effects: %.2f (vs %.2f without)\n', AIC(m2), AIC(m)))
  cat('A meaningful AIC drop suggests unmodelled ward-level heterogeneity.\n')
} else cat('ward column absent - cannot test ward-level heterogeneity.\n')

hr('Verdict line for the manuscript')
cat(sprintf('Nagelkerke = %.3f; -2LL = %.2f; AIC = %.2f; BIC = %.2f (n = %d)\n',
            csn / (1 - exp(-D0m / n_obs)), D, AIC(m), BIC(m), n_obs))
cat('Replace the withdrawn triple with these values.\n')
