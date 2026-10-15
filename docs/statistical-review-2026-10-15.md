# Statistical Review — YohannaPaper

**Reviewed:** 15 October 2026
**Reviewer:** independent audit, re-deriving every headline claim from the frozen data
**Scope:** `manuscript/manuscript.qmd`, `docs/methodology.qmd`, `analysis/spatial/*.R`, `README.md`, `docs/section-scores.md`
**Evidence:** `analysis/spatial/audit_claims.R` (read-only; re-run it yourself)

---

## Verdict

The **engineering discipline is genuinely good** and the **statistical inference does not
yet carry the weight the documentation puts on it**. The single most important distinction:

- The **spatial pipeline reproduces exactly.** Every number in `docs/methodology.qmd`
  Tables 5–6 came back to the digit. That is rare, and it is the foundation worth building on.
- The **conference paper's logistic model reports three fit statistics that cannot all be
  true simultaneously**, and its main result rests on a dataset that is not in the repository.
- The **"N = 34 LGAs" climate model is a five-city model in LGA clothing.** Its headline
  significant result does not survive at the level the data actually replicate.
- The **paper and the spatial analysis are two different studies.** The submitted manuscript
  contains no spatial analysis at all.

A statistician reviewing this repo will find the OSM/NASA/GADM work quickly and be impressed,
then read the paper, then find the logistic table, and stop trusting the rest. Fixing the
paper is what unlocks the value already banked in the pipeline.

---

## 1. What is genuinely strong — protect this

**1.1 Frozen-data provenance.** `data/raw/provenance.json` records source, URL, timestamp,
row count and licence for every pull. `data/raw/*.csv` are immutable; analysis reads only
frozen files. This is real reproducibility practice and most published Nigerian urban
agriculture work does not do it.

**1.2 The spatial regression is done correctly, and it reproduces.** Re-derived independently:

- Global Moran (density) `I = 0.2999`, `z = 17.613` — claimed 0.300 / 17.61 ✓
- Global Moran (counts) `I = 0.1584`, `z = 8.466` — claimed 0.158 / 8.47 ✓
- Rook contiguity `I = 0.3058` — claimed 0.306 ✓
- Spatial lag `AIC = −2577.50`, `ρ = 0.4192` — claimed −2577.5 / 0.419 ✓
- LR(OLS → lag) `= 94.249` — claimed 94.3 ✓
- OLS `AIC = −2485.25` — claimed −2485.2 ✓

**1.3 The spatial term does real work.** Residual Moran falls from **0.2557 (OLS) to −0.0355
(lag)**. That is a textbook-clean demonstration that the spatial specification removed the
dependence OLS left behind. Keep this; it is the strongest inferential result in the repo.

**1.4 Robustness checks are present and correct in spirit.** Queen-vs-rook, and the
Kano-excluded refit (`I = 0.274`) to show the result is not one state driving it. Both
reproduce.

**1.5 The figures are real.** 300 dpi, generated from committed scripts and committed data,
with no manual step. `lisa_map.png` and `density_vs_rainfall.png` are honest artefacts.

**1.6 The paper meets the conference format.** Abstract 286 words (limit 150–300), 5 keywords
(limit 6), all eight sampled wards sum to `n = 306` (`120+58+35+26+22+15+15+15`), and
`Krejcie & Morgan` for `N = 1500` does give 306. The sampling arithmetic is internally sound.

---

## 2. What breaks under scrutiny

### 2.1 CRITICAL — the paper's logistic fit statistics are mutually impossible

`manuscript/manuscript.qmd` Table 1 reports, for `n = 285` and 7 predictors:

> Nagelkerke R² = 0.348; AIC = 132.45; BIC = 145.90

These cannot coexist:

| Check | Arithmetic | Result |
|---|---|---|
| Null deviance for a binary outcome at 37.5% prevalence, `n = 285` | `−2(n₁ln p + n₀ln q)` | `377.09` |
| BIC−AIC gap implied by the reported pair | `k(ln n − 2) = 8(5.652 − 2)` | should be **29.22**, reported **13.45** |
| Free parameters implied by the reported gap | `13.45 / 3.652` | **≈ 3.7**, not 8 |
| Deviance implied by AIC 132.45 | `132.45 − 2(8)` | `116.45` → McFadden R² = **0.691** |
| Nagelkerke implied by that deviance | `0.691 / 0.734` | **≈ 0.82**, not 0.348 |
| AIC implied by Nagelkerke 0.348 | `−2LL ≈ 293` | **≈ 309**, not 132.45 |

Two of the three numbers are wrong. Tracing to source: the same triple appears verbatim in
`MR. YOHAN FINAL BINDING.docx` (Thesis Table 19) as SPSS output, so **this is inherited, not
introduced in the paper** — but the paper is what a reviewer reads.

Separately, `OR = 1.005 per unit income` is reported as a substantive finding, but the **unit
is never stated**. This matters enormously:

- If one unit = ₦1, then `OR` per +₦10,000 is `exp(0.005 × 10,000) = 5.2 × 10²¹` — absurd.
- If the variable is coded in **thousands of naira**, `OR` per +₦10,000 is `exp(0.05) = 1.051`
  — a sensible, modest effect.

The second is almost certainly the truth, which means the coefficient is fine and the
*reporting* is the defect: an odds ratio per unit of an unspecified scale cannot be
interpreted by a reader. State the coding and report the effect per ₦10,000.

Also note: several `b/SE` pairs do not reproduce their printed p-values (married:
`0.672/0.212 → p = 0.0015`, printed `0.010`; income: `0.005/0.002 → p = 0.0124`, printed
`0.020`). Small, but they are the kind of thing a methods reviewer checks first.

**Fix.** Re-run the model in R (`glm(fulltime ~ ., family = binomial)`), export the actual
`−2LL`, AIC, BIC, McFadden and Nagelkerke, and report those. Also report `exp(β)` with 95%
CIs and the rescaled income odds. Then state the pseudo-R² correctly — Nagelkerke is *not*
"34.8% of variance explained"; it is a likelihood-ratio-based analogue bounded by 1, and
calling it "variance explained" is a known misstatement.

### 2.2 CRITICAL — the "N = 34 LGA" climate model is a 5-city model

`docs/methodology.qmd` Table 6 presents `N = 34` LGAs and reports rainfall significant at
`p = 0.018` (spatial error) and `p = 0.035` (spatial lag), concluding H2 is supported.
Verified against the frozen data:

- The 34 LGAs map to **5 cities** and therefore to **5 distinct annual rainfall values**.
- Regressing rainfall on city dummies gives **R² = 1.000** — rainfall *is* city identity.
- The subset's spatial weights split into **5 connected components with 1 isolate**, i.e.
  the "neighbour" structure is almost entirely *within-city*.
- Between-city variance is only **ICC = 0.102** — 90% of the outcome variance is *within*
  cities, but the covariate varies only *between* them.

Consequence — refitting at the honest replication level:

| Specification | rainfall coefficient | p |
|---|---|---|
| Naive OLS, 34 rows | −0.000085 | 0.250 |
| Spatial lag, 34 rows | −0.000135 | 0.035 |
| Spatial error, 34 rows | −0.000100 | **0.018** ← the quoted result |
| Collapsed to **5 city means** | −0.0000438 | **0.576**, R² = 0.116 |

The significance is manufactured by treating 34 rows as independent observations of a
covariate that has 5 values. `ΔAIC = 0.36` between lag and error — the stated basis for
"error preferred" — is not evidence for anything. The estimated `ρ = −0.438` and
`λ = −0.476` are **negative** spatial dependence coefficients, which are substantively
meaningless in this setting and are correctly flagged in the document as an artefact but
then used anyway to support H2.

**Fix.** Either (a) drop the LGA-level climate model and report the 5-city relationship
openly as `K = 5` with the limitation stated, or (b) go get rainfall that actually varies
within cities (CHIRPS/ERA5 rasters at LGA level) and rerun. Option (b) is the one that
becomes a real paper.

### 2.3 HIGH — Gaussian regression on a ratio that is 95% zero

The outcome `density = n / area_km²` is non-negative, bounded at zero, and **exactly zero for
95.0% of the 775 LGAs**, with skewness 15.5. It is fitted with `lm` / `lagsarlm` /
`errorsarlm` — Gaussian models on a continuous scale.

Verified consequence: **265 of 775 fitted values (34.2%) are negative.** A negative
agricultural density is not a small numerical artefact; it means the model is not a
description of the data-generating process.

The correct family is a count model with the area exposure as an **offset**:

```
n_i ~ NegBin(μ_i);   log μ_i = log(area_i) + Xβ     # log(area) is an offset, not a regressor
```

Diagnostics from the frozen data:

- Poisson: dispersion **39.1** — grossly overdispersed, unusable.
- Negative binomial: `AIC = 571.6`, `θ = 0.0145`, `log_area` coefficient `−1.551`
  (`p = 8.5e−11`).

Note that a negative binomial of `n` on `log(area)` *without* an offset tests the
area–count relation, while the offset form tests whether **density** depends on area — the
latter is the actual H3 hypothesis. Both give a strong negative area effect, so **H3 survives
the correct specification**, which is good news. But the current `density ~ log(area)` fit also
partly exploits the mechanical correlation of a ratio with its own denominator (the classic
Kronmal ratio fallacy), so the reported magnitude is not trustworthy even though the sign is.

**Fix.** Refit as negative binomial with `offset(log(area))`; report IRR with CIs. If
anything spatial is still needed, use a spatial filter or a conditional autoregressive (CAR)
model on the counts, not Gaussian spatial lag on a ratio. Also report a **hurdle / zero-inflated**
variant and compare, because 95% zeros is a genuine mixture.

### 2.4 HIGH — 43 of 484 points are outside the five study cities, and the layer measures mapping, not farming

The OSM Overpass queries used **rectangular city bounding boxes**. The bounding boxes spill
across state lines. Verified: **43 points (8.9%) lie outside the five study states** —

| State | LGA | points |
|---|---|---|
| Ogun | Ifo | 13 |
| Niger | Suleja | 9 |
| Niger | Tafa | 8 |
| Ogun | Ado Odo/Ota | 8 |
| Ogun | Shagamu | 5 |

They are then **silently dropped** from the climate subset because they have no city key.
Worse, the "Abuja" box contributes **15 points in the FCT and 17 in Niger** — the majority of
"Abuja" points are not in Abuja.

More fundamentally, `landuse=farmland` inside a rectangle is not a measurement of *urban*
agriculture. The same tag covers ordinary rural farmland. And "Abuja 32 / Kano 189" is
substantially **an OSM mapping-effort gradient** — Kano is the best-mapped state in Nigerian
OSM — not an agriculture gradient. This confound is the single biggest threat to the
validity of everything downstream, including the spatial regressions.

**Fix.** (1) Replace bounding boxes with administrative or built-up-area masks (`city proper`
or `urban extent` polygons), and re-pull. (2) Add a **per-LGA OSM exposure control** — count
of buildings / roads / landuse features — and include it as an offset or covariate, so density
is interpreted *per unit of mapped environment* rather than per km². (3) Report the 43
out-of-scope points rather than dropping them silently. This one change converts the study from
"OSM is dense in Kano" to a defensible spatial analysis.

### 2.5 HIGH — the paper and the spatial analysis are two different studies

The submitted manuscript contains **zero** occurrences of `Moran`, `OSM`, `OpenStreetMap`,
`NASA`, `GADM`, `allotment` or `spatial lag`. (An automated scan flagged "LISA" — verbatim
inspection shows every hit is inside the word *professiona**lisa**tion*.)

The manuscript is a **Bauchi Metropolis survey** (`n = 285`, SPSS logistic regression, eight
wards, Jan–Feb 2024). The repo is a **five-city OSM spatial analysis**. `README.md` presents
these as one integrated "Spatial Statistics + API Data" project and §9 advertises them with
six screenshots; the paper a reviewer actually receives contains none of it.

This is the largest credibility risk in the repository. It reads as though the spatial work
was built to decorate a paper rather than to answer a question the paper asks.

**Fix.** Pick one of two honest framings, and make the README match:

- **Two outputs, stated as two outputs.** `README` says plainly: "Output A: conference paper
  (Bauchi survey). Output B: national spatial study (OSM/NASA/GADM, in preparation)." Both
  stand on their own. This is honest and still impressive.
- **One merged study.** Bring the spatial analysis *into* the paper as the site-selection or
  targeting layer for Bauchi. This is more work but is the stronger paper.

### 2.6 MEDIUM — LISA significance is reported without multiplicity control, and the test is uncalibrated here

`localmoran` was run on 775 LGAs; **23 are flagged at p < 0.05**, and the maps/discussion
treat "HH" clusters as a targeting tool. Two problems:

- With 775 tests at α = 0.05, chance alone yields ≈ **38.8** "significant" units. The 23
  observed is *below* the chance expectation, which signals that the normal approximation is
  **not calibrated** on a variable that is 95% zeros — the p-values are discrete and
  conservative. So LISA is not doing the work the discussion claims for it.
- No FDR or Bonferroni control is applied anywhere. (Bonferroni leaves 18, BH-FDR leaves 19 —
  so the conclusion is not dramatically different, but it must be *stated*.)

The substantive point, though, is that the "HH" set is largely *the same 39 LGAs that have any
points at all*, concentrated in Kano and Lagos. "High-density clusters in Kano and Lagos" and
"the places where OSM has data" are the same statement on this dataset — which loops back to §2.4.

**Fix.** Apply BH-FDR, report adjusted p-values, and state the OSM-completeness caveat
alongside the LISA result. Consider a **join-count test** or a **Ripley's K / point-process**
analysis on the 484 points, which is better suited to a point pattern than an areal
zero-inflated rate.

### 2.7 MEDIUM — internal inconsistencies in the manuscript

- **Fieldwork order is impossible.** Fieldwork is "8 Jan–8 Feb 2024"; the instrument "pilot
  [ran] 6–11 Mar 2024". The pilot postdates the main survey. A pilot must precede the
  instrument it validates. One of the two dates is wrong.
- **"Mean plot ≈ 0.5 ha"** — *I initially flagged this as inconsistent with "62.4% are
  < 1,800 m² (0.18 ha)" and that flag was wrong.* The distribution is right-skewed: the
  bottom three bands contribute ~1,863 m² to the mean, so a 13.7% tail averaging ~2.3 ha
  puts the mean at 0.5 ha quite legitimately. The genuine criticism is weaker but still
  real — the mean is tail-driven and **the median should be reported alongside it**. The
  median falls in the 540–1,800 m² band (50th percentile; 62.4% of farms are below
  1,800 m²). Report both and say the distribution is skewed.
- **Three different "87%"s** appear for related concepts: "87.4% subsistence", "87%
  home-consumed", "65% home food". They are different questions but read as contradictory.
  Label each explicitly.
- **README self-contradicts on references** — "20 refs" in §4/§7, "30 refs" in §8.

### 2.8 MEDIUM — reference hygiene

- `manuscript/references.bib` holds **45 entries**; the manuscript cites **24**. **21 entries
  are uncited** (`abubakar2023`, `adeleye2024`, `adesokan2023`, `arowolo2023`, `atukunda2021`,
  `bsadp2023`, `crciucg2014`, `fao2001`, `imf2023`, `lagosfoodbank2024`, `malabo2014`,
  `muhammed2022`, `ogundele2023`, `olanrewaju2022`, `orhevba2024`, `tinubu2025`, `ubah2025`,
  `udoh2022`, `un2030`, `worldbank2023`, `bashir2022b`).
- **Placeholder identifiers remain**: `doi = {10.xxxx/njae2024}` and
  `doi = {10.1007/s11524-026-xxxxx}`. A fabricated-looking DOI is worse than no DOI.
- **Duplicate entries**: `bashir2022` and `bashir2022b` are the same work.
- **15 `@article` entries have no `journal` field** (`nesg2024`, `feesnet2024`, `fao2023`,
  `fao2024`, `oshinusi2024`, `noburn2026`, `nup2022`, `tinubu2025`, `un2030`, `malabo2014`,
  `lagosfoodbank2024`, `worldbank2024`, `worldbank2023`, `bashir2022`, `bashir2022b`) — these
  will render incorrectly under APA. They should be `@techreport`, `@misc` or `@online`.
- **Two divergent bib files**: `manuscript/references.bib` (45) vs `docs/references.bib` (20).
  They will drift. Make one the source and symlink or copy at build time.

### 2.9 MEDIUM — `docs/section-scores.md` is a self-assigned 5.0/5.0 on all 21 rows

This file damages credibility more than it helps. It scores "Results — Regression Tables 5–6"
as 5/5 and "Methods" as 5/5 while §2.1–2.4 above document impossible fit statistics, a
five-city model presented as `N = 34`, a Gaussian fit to a 95%-zero ratio, and 8.9% of points
outside the study area. It also carries two contradictory word counts and two "Next:" lines
from different edits.

A statistician who reads it, then reads the tables, concludes the author cannot tell. **Delete
it or convert it to an honest gap register.** The audit script added in this review is a better
model: it states what passes and what is flagged.

### 2.10 MEDIUM — reproducibility gaps

- **The survey dataset is not in the repository.** The paper's central result (`n = 285`
  logistic regression) rests on data that is not present, not in `data/raw`, not anywhere.
  The provenance chain that is impeccable for the API layers stops exactly where the paper
  begins. This is the gap a recruiter or replicator will test first.
- **No environment lock.** No `renv.lock`, no `sessionInfo()` capture. The docs claim
  `R 4.5.2`; the installed packages report **built under R 4.5.3**. Package versions
  (`spdep 1.4.2`, `spatialreg 1.4.3`) are asserted in prose but not pinned in a file.
- **Build is not one command.** `render.ps1` / `render.bat` hardcode `D:\YohannaPaper`, so
  they fail on any other machine — which is precisely the audience for a public repo.
- **`MR. YOHAN FINAL BINDING.docx` (6.6 MB)** sits untracked in the repo root and appears to
  be the only carrier of the thesis source data. Either extract the survey data into
  `data/raw/` with a provenance entry, or move it to `data/external/` and document it.
- `data/raw/fao_food_security.csv` is a one-row stub (HTTP 521 at freeze time). It is
  documented as a stub, which is the right handling — but it is cited as a data source in the
  README data table without qualification.
- `.playwright-mcp/` and `.codewhale/` are untracked working artefacts; add them to `.gitignore`.

### 2.11 LOW — framing and rhetoric

- `README.md` §9 claims "(ii) compost circularity via `terra` suitability — both quantified",
  but `terra` is never used anywhere in the code. `ENVIRONMENTS.md` lists it as available;
  no script calls it.
- README §9 says "Spatial terms halve AIC vs OLS" — AIC is on a log-likelihood scale; it
  went from −2485.2 to −2577.5. "Halve" is meaningless for AIC. Say "ΔAIC = 92.3".
- README §9 says "The heterogeneity beyond city area is visually undeniable" — this is the
  OSM completeness gradient described in §2.4. Reframe.
- The README's "Why this repo is exceptional" section reads as self-congratulation. Let the
  audit script and the reproduced numbers do that work instead; it is far more convincing.

---

## 3. Reality check on timing

Today is **15 October 2026**. The conference ran **13–15 October 2026**; the abstract and full
paper deadlines were **5 and 9 October**. `PROGRESS.md` still lists Phase 6 submission as
unchecked.

If the paper was submitted, everything in §2 is now a **journal-version** or **portfolio**
agenda with no length limit — which is good news, because the fixes in §2.1–2.4 need room.
If it was not submitted, the time pressure is gone anyway. Either way, the highest-value work
now is correctness, not formatting.

---

## 4. The improvement plan

### Tier 1 — Correctness (do first; ~1 day)

1. **Re-run the logistic model in R** and replace Table 1 with real `−2LL`, AIC, BIC,
   McFadden, Nagelkerke. Report `OR` with 95% CIs. Rescale income to per-₦10,000.
2. **Commit the survey dataset** to `data/raw/` with a `provenance.json` entry, or state
   plainly in the README that it is restricted and give the access route.
3. **Delete or rewrite `docs/section-scores.md`** as a gap register.
4. **Fix the pilot/fieldwork date order** and the "mean plot" summary statistic.
5. **Clean the bibliography** — remove the 21 uncited entries, kill both placeholder DOIs,
   merge the duplicate Bashir entries, retype the 15 journal-less `@article` entries, and make
   `docs/references.bib` a copy rather than a fork.
6. **Reconcile README numbers** (refs 20 vs 30; density mean 0.62 vs 0.0055; "halve AIC").

### Tier 2 — Statistical rigour (~3–5 days; this is the tier that impresses statisticians)

7. **Refit the density model as negative binomial with `offset(log(area))`.** Compare against
   a hurdle/ZINB. Report IRRs. Demonstrate the sign of the area effect is stable across
   Gaussian, Poisson, NB and hurdle. *This turns H3 from a ratio artefact into a finding.*
8. **Re-pull OSM with administrative/urban-extent masks** instead of bounding boxes, and add a
   **per-LGA OSM exposure offset** (buildings/roads/landuse feature counts). Report how much
   of the spatial pattern survives. *This is the single highest-value change in the review.*
9. **Drop or demote the `N = 34` climate model.** Report the `K = 5` city-level relationship
   with its uncertainty stated honestly, or fetch CHIRPS/ERA5 rainfall at LGA resolution and
   rebuild it properly.
10. **Add LISA multiplicity control** (BH-FDR, adjusted p-values in the map legend) and a
    **join-count or Ripley's K** analysis on the point pattern.
11. **Add a `renv.lock`** and a `sessionInfo()` dump; make the build path-relative.
12. **Keep and extend `audit_claims.R`.** Re-run it after every change. A repo that ships its
    own adversarial audit is a strong signal.

### Tier 3 — Portfolio framing (the tier that impresses recruiters)

Recruiters do not read methods. They read the README for 30 seconds and click one artefact.
Optimise for that:

13. **Lead the README with the reproduced result, not the aspiration.** Replace §9's
    "exceptional" list with a short, falsifiable block:
    > `N = 775` LGAs. Global Moran `I = 0.300` (`z = 17.6`). OLS residual Moran `0.256` →
    > spatial lag `−0.036`. `ΔAIC = 92.3`. Negative-binomial refit confirms area effect
    > (`IRR` CI reported). 8.9% of points found outside study extent and re-scoped.
    > Every number re-derivable with `Rscript analysis/spatial/audit_claims.R`.

    The last line is the one that gets you hired.
14. **State the two studies as two studies** (§2.5) so the repo's claims equal the repo's contents.
15. **Add one genuinely well-designed figure** — a small-multiples panel: points → density →
    LISA → residual Moran before/after. One image that tells the whole spatial story beats six
    that each tell a fragment.
16. **Fix the build so `git clone && Rscript analysis/spatial/audit_claims.R` works on a clean
    machine.** Test it in a fresh directory. This is the demo that converts.
17. **Write the honest limitations paragraph in the README**, not just the paper. "OSM
    completeness is a confound; we control for it with an exposure offset" is a sentence that
    signals statistical maturity far more than "why this repo is exceptional".

---

## 5. Summary judgement

**Currently:** a well-engineered data pipeline wrapped around a paper whose headline statistics
do not hold, presented as though the two are one body of work.

**After Tier 1:** internally consistent and honest. Submittable anywhere.

**After Tier 2:** a genuinely strong spatial analysis of urban agriculture in Nigeria. The
negative-binomial refit, the OSM exposure control and the honest `K = 5` climate treatment
would each individually put this ahead of most work in the area.

**After Tier 3:** a portfolio piece that demonstrates, rather than asserts, statistical
competence — because the repository audits itself and the audit passes.

The distance between here and there is not large. Most of the machinery is already correct;
what is missing is the willingness to let the data overrule the story that was written about it.

---

*Evidence for every claim above: `analysis/spatial/audit_claims.R`. Re-run before and after
any change.*
