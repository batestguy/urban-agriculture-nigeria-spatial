# Spec: Urban Agriculture and Urban Food Security in Nigeria — Literature Review Rewrite

> **Date:** 2026-08-26
> **Author:** Yohanna (batestguy)
> **Status:** Spec — not yet implemented
> **Replaces:** `manuscript/manuscript.qmd` (spatial statistics paper, 484 OSM pts, Moran's I, LISA, lag/error regression)

---

## 1. What This Document Is

This spec defines the **complete rewrite** of the conference paper from a spatial-statistics-heavy approach to a **pure literature review and policy analysis** with no original data analysis, no equations, no regression, and no methods section.

The old paper (`manuscript/manuscript.qmd`) had: 5 equations, Moran's I, LISA, spatial lag/error regression, 484 OSM footprints, NASA POWER climate, World Bank indicators, GADM shapefiles, R spatial pipeline (`sf`, `spdep`, `spatialreg`), and 6 figures.

The new paper has **none of that**. It is a Nigeria-focused literature review on climate-smart urban farming practices, with policy recommendations for local government zoning, composting/circular economy, and national/international frameworks.

---

## 2. Paper Metadata

| Field | Value |
|---|---|
| **Title** | To be determined — must include "Urban Agriculture" and "Food Security" and "Nigeria" |
| **Subtitle** | Conference line: Federal Polytechnic Kaltungo — 2nd Annual National Multidisciplinary Conference 2026 |
| **Sub-themes** | Primary: #6 Climate-Smart Agriculture, Food Security and Rural Transformation; Secondary: #10 GIS & Urban Planning, #13 Circular Economy & Environmental Sustainability |
| **Author** | Yohanna — batestguy (presenting author) |
| **Abstract** | 150–300 words, ≤6 keywords, MS Word format |
| **Body** | Times New Roman 12pt, 1.5 line spacing, ≤12 pages |
| **Keywords (max 6)** | Suggested: urban agriculture, food security, climate-smart agriculture, Nigeria, circular economy, urban planning (to be finalized in abstract) |
| **Bibliography** | ~30 references, Nigeria-focused, no stats papers (Moran, Anselin, Bivand, Pebesma — all removed) |
| **Figures/Tables** | 1–2 tables + 1 conceptual diagram (no spatial maps, no scatter plots) |
| **Word count** | 3,500–4,000 words (fits ≤12 pp at TNR 12pt 1.5 with figures) |
| **Submission** | Abstract deadline: 5 Oct 2026; Full paper deadline: 9 Oct 2026 |
| **Submit to** | `fpksstconf2026@gmail.com` |
| **Fee** | ₦13,000 physical / ₦10,000 virtual / ₦5,000 students — First Bank Plc, School Of Science Conference Fpk, 2047116096 |

---

## 3. Complete Clean Break — What Is Removed

The following elements from the current manuscript are **entirely removed** and must not appear in the rewrite:

- **All 5 equations** (weight matrix, Global Moran's I, LISA, spatial lag, spatial error)
- **All spatial statistics** (Moran's I = 0.300, LISA, AIC, LR, LM diagnostics, Spearman correlations)
- **All R code references** (`sf`, `spdep`, `spatialreg`, `terra`, `dplyr`)
- **All data source descriptions** (OSM Overpass API, NASA POWER, World Bank WDI, GADM shapefiles, FAOSTAT)
- **All data tables** (Tables 1–6: OSM by city, NASA climate, Moran's I, top-10 density, regression results)
- **All spatial figures** (LISA choropleth, density scatter, correlation heatmap, density histogram, OSM points map, density by state)
- **Methods section** entirely
- **All stats references** (`moran1950`, `anselin1995`, `bivand2023`, `pebesma2023`, `hijmans2023`, `bivand2022`, `pebesma2018`)
- **Results section entirely** (no "Results" heading)
- **`fix_docx_format.py`** output pipeline (new paper should still comply with TNR 12pt 1.5 but no R/Python needed)
- **All technical jargon**: LISA, queen contiguity, weight matrix, spatial autocorrelation, zero-inflation, GEOS, GDAL, PROJ, etc.

---

## 4. New Paper Structure

### Proposed Section Outline (3,500–4,000 words)

```
Abstract (150–300 words)
Keywords (≤6)

1. Introduction (~500–600 words)
   - Urban agriculture definition and global context
   - Nigeria's urbanisation challenge (population, food insecurity stats)
   - Gap: under-documented urban farming in Nigerian cities
   - Paper objectives: review climate-smart practices, propose policy interventions

2. Conceptual Framework (~300–400 words)
   - The urban agriculture–food security–climate-smart nexus
   - Include 1 conceptual diagram (Figure 1) showing the framework
   - Link to sub-themes 6, 10, 13

3. Literature Review (~1,500–1,800 words)

   3.1 Urban Agriculture in Nigeria: Current State
       - Types: peri-urban fadama, rooftop gardens, vacant-lot farming, community gardens
       - Geographic patterns: Kano, Lagos, Abuja, Port Harcourt, Gombe
       - Scale: estimates from literature (e.g., % of urban food from local production)
       - Challenges: land tenure, water access, contamination, market access

   3.2 Climate-Smart Practices in Urban Agriculture (sub-theme 6)
       - Composting organic waste → soil amendment
       - Rainwater harvesting and drip irrigation
       - Shade nets and heat-tolerant crop varieties
       - Rooftop and vertical farming adaptations
       - Case studies from Nigerian cities (cite literature)

   3.3 Circular Economy and Waste-to-Resource (sub-theme 13)
       - Organic waste generation in Nigerian cities
       - Composting as circular loop (tonnage estimates, compost quality)
       - Linkage to sanitation and public health
       - Precedents: Ibadan, Kano, Lagos composting initiatives

   3.4 Urban Planning and Zoning for Agriculture (sub-theme 10)
       - Land-use conflicts: agriculture vs housing vs industry
       - Zoning frameworks: international examples (Portland, Kampala, Dar es Salaam)
       - Nigerian context: NUP 2022 (National Urban Policy), state-level planning
       - Protected fadama lands and peri-urban buffer zones

   3.5 Urban-Rural Linkages and Food Systems
       - Shortened supply chains from peri-urban farms to urban markets
       - Rural–urban seed and compost exchange
       - Price buffering: urban agriculture as shock absorber
       - Link to sub-theme 6 (Rural Transformation)

4. Discussion (~600–800 words)

   4.1 Climate-Smart Agriculture: Opportunities for Nigerian Cities
       - Synthesize evidence from §3.2 and §3.3
       - Quantify potential: e.g., composting X tons/day could supply Y hectares
       - Barriers: awareness, initial cost, land ownership

   4.2 Policy Recommendations
       - Recommendation 1: LGA-level zoning to protect urban farmland
       - Recommendation 2: Municipal composting programs (link to circular economy)
       - Recommendation 3: Integration into NUP 2022 and state development plans
       - Recommendation 4: Urban agriculture extension services
       - Link each to sub-themes 6, 10, 13

   4.3 Limitations and Future Research
       - This paper is a literature review; no original empirical data
       - Gaps in Nigerian urban agriculture literature (geographic, crop-specific)
       - Need for LGA-level food security data (DHS, NLSS)
       - Future: empirical studies using open data (OSM, satellite imagery, climate APIs)

5. Conclusion (~300–400 words)
   - Restate: urban agriculture is a viable climate-smart food security strategy
   - Nigeria's opportunity: climate-smart practices + circular economy + zoning
   - Call to action for policymakers and researchers

References (30 entries)
```

---

## 5. Policy Areas to Cover

### 5.1 Local Government Zoning (Sub-theme 10)
- How LGAs can designate and protect urban agricultural land
- Zoning as a tool to prevent urban sprawl over farmland
- Case studies from Nigerian cities (if available in literature)
- International examples adapted to Nigerian context
- Link to NUP 2022 compact-cities agenda

### 5.2 Composting & Circular Economy (Sub-theme 13)
- Organic waste generation in Nigerian cities (tonnage estimates from literature)
- Composting as a circular loop: waste → soil → food → waste
- Compost quality and application rates (kg/capita/day from literature)
- Case studies: Ibadan, Kano, Lagos composting programs
- Health and sanitation co-benefits

### 5.3 National/International Policy (Sub-theme 6)
- National Urban Policy (NUP) 2022 — compact cities and food systems
- SDG 2 (Zero Hunger) and SDG 11 (Sustainable Cities) alignment
- AU Malabo Declaration on agriculture
- FAO urban agriculture guidelines
- How Nigeria's policy frameworks should prioritize urban agriculture

---

## 6. References — Direction

**Replace** all 30 current references (stats-heavy) with **Nigeria-focused agriculture/food-security/policy** references. Target ~30 references.

### Categories to Source

| Category | Example Sources | Target Count |
|---|---|---|
| Nigerian urban agriculture studies | Orhevba 2024, Abubakar 2023, Udoh 2022, Muhammed 2022, Ogundele 2023 | 8–10 |
| Food security & nutrition in Nigeria | FAO SOFI 2023, WHO Nigeria, NLSS/DHS reports | 5–6 |
| Climate-smart agriculture | FAO CSA guidelines, IPCC AR6 WGII Ch5, Stackhouse NASA POWER | 4–5 |
| Circular economy & composting | Olanrewaju 2022, UNEP circular economy, World Bank waste reports | 3–4 |
| Urban planning & zoning | NUP 2022, UN-Habitat, Adeleye 2024 | 4–5 |
| International urban agriculture | UNDP, WHO urban food systems, Molnar 2014, Bakker 2016 | 3–4 |

**Keep** from current refs: `orhevba2024`, `abubakar2023`, `udoh2022`, `muhammed2022`, `olanrewaju2022`, `ogundele2023`, `arowolo2023`, `adeleye2024`, `fao2023`, `worldbank2023`, `worldbank2024`, `undesa2022`.

**Remove**: `moran1950`, `anselin1995`, `bivand2023`, `pebesma2023`, `hijmans2023`, `bivand2022`, `pebesma2018`, `moran1950`, `gadm2022`, `nasapower2024`, `openstreetmap2024`.

---

## 7. Figures and Tables

### 7.1 Conceptual Diagram (Figure 1)
- **Content:** Urban Agriculture ↔ Food Security ↔ Climate-Smart Practices nexus
- **Elements:** Urban agriculture (inputs: land, water, waste; outputs: food, income, resilience), Climate-smart practices (composting, rainwater, shade, varieties), Food security outcomes (availability, access, utilization, stability), Policy enablers (zoning, NUP 2022, SDGs)
- **Format:** Conceptual flowchart or systems diagram (not a map)
- **Size:** 5–6 inches width, single column or full page

### 7.2 Summary Table(s)
- **Table 1:** Key Statistics on Urban Agriculture in Nigerian Cities (city, estimated area/population, main crops, key challenges — from literature)
- **Table 2 (optional):** Policy Frameworks Relevant to Urban Agriculture in Nigeria (policy, year, key provisions, relevance to urban agriculture)

---

## 8. Writing Style

- **Academic but accessible** — this is a multidisciplinary conference, not a statistics journal
- **Paragraph-focused** — no bullet points, no numbered lists in the body
- **Nigerian context throughout** — cite Nigerian studies, use Nigerian city names, reference Nigerian policies
- **No equations** — describe concepts in plain language
- **No R/Python/code references** — no mention of `sf`, `spdep`, `terra`, `conda`, `quarto`, etc.
- **No "Results" section** — this is a review, not an empirical study
- **Sub-theme alignment** — explicitly tie sections to sub-themes 6, 10, 13 in text

---

## 9. Format Compliance (Unchanged from Flyer)

| Requirement | Spec |
|---|---|
| Font | Times New Roman 12pt |
| Spacing | 1.5 line spacing |
| Margins | 1 inch (2.54 cm) all sides |
| Length | ≤12 pages |
| Abstract | 150–300 words, ≤6 keywords |
| Format | MS Word (.docx) |
| Submission email | `fpksstconf2026@gmail.com` |
| Abstract deadline | 5 Oct 2026 |
| Full paper deadline | 9 Oct 2026 |
| Fee | ₦13,000 / ₦10,000 / ₦5,000 — First Bank Plc, 2047116096 |

---

## 10. Build Pipeline

The current pipeline is:
```
R scripts → results/ → manuscript.qmd → quarto render → fix_docx_format.py → manuscript.docx
```

The new pipeline simplifies to:
```
manuscript.qmd (pure Quarto markdown) → quarto render → manuscript.docx
```

- No R scripts needed (remove `analysis/spatial/` dependency)
- No `fix_docx_format.py` needed (Quarto docx output with `_quarto.yml` for TNR 12pt 1.5)
- Keep `manuscript/_quarto.yml` with TNR 12pt 1.5 settings
- Figures created as separate image files (conceptual diagram, tables as images if needed)

### Files to Keep
- `manuscript/manuscript.qmd` — **rewrite completely** (current content replaced)
- `manuscript/_quarto.yml` — update if needed
- `manuscript/references.bib` — **rewrite completely** (stats refs replaced with ag refs)
- `WhatsApp Image 2026-08-24 at 9.23.15 PM.jpeg` — conference flyer
- `ENVIRONMENTS.md`, `AGENTS.md`, `README.md`, `PROGRESS.md`

### Files That Become Optional/Archived
- `analysis/spatial/*.R` — no longer needed for the paper (keep for archival)
- `data/raw/*.csv` — no longer used in paper (keep for archival)
- `results/*` — no longer used (keep for archival)
- `docs/methodology.qmd` / `docs/methodology.pdf` — stats methodology doc, no longer relevant
- `docs/section-scores.md` — old scores, no longer relevant
- `scripts/fix_docx_format.py` — no longer needed

---

## 11. Differences from Current Manuscript

| Aspect | Current (Statistics) | New (Literature Review) |
|---|---|---|
| **Core approach** | Original spatial analysis | Literature review + policy |
| **Data** | 484 OSM pts, NASA, World Bank, GADM | None — cite published literature |
| **Methods** | Moran's I, LISA, lag/error regression | No methods section |
| **Equations** | 5 formal equations | None |
| **Results** | 6 tables, 6 figures with stats | 1–2 summary tables, 1 conceptual diagram |
| **References** | 30 (stats + Nigeria) | ~30 (Nigeria agriculture/food/policy) |
| **Stats refs** | Moran, Anselin, Bivand, Pebesma | Removed |
| **R/Python code** | Referenced throughout | Not mentioned |
| **Sub-themes** | 6, 10, 13 (same) | 6, 10, 13 (same) |
| **Word count** | 3,599 → 2,307 (trimmed) | 3,500–4,000 |
| **Pages** | 12 pp (at limit) | ≤12 pp |

---

## 12. Open Questions for Implementation

1. **Title** — needs to be finalized. Options:
   - "Climate-Smart Urban Agriculture and Food Security in Nigeria: A Literature Review and Policy Analysis"
   - "Urban Agriculture and Food Security in Nigeria: Toward Climate-Smart Practices and Circular Economy"
   - "Bridging Knowledge Frontiers: Urban Agriculture, Food Security and Climate-Smart Practices in Nigerian Cities"

2. **Conceptual diagram** — to be created. Options:
   - Simple flowchart (boxes + arrows)
   - Venn diagram (three overlapping circles)
   - Systems map (feedback loops)

3. **Source of Nigerian urban agriculture literature** — need to identify and read ~15–20 Nigerian studies. Key starting points:
   - Orhevba et al. 2024 (already in refs)
   - Abubakar et al. 2023 (already in refs)
   - Ogundele et al. 2023 (Lagos OSM — note: remove OSM method, keep findings)
   - Muhammed et al. 2022 (fadama)
   - New: need to search for additional Nigerian urban agriculture, food security, and climate-smart agriculture studies

4. **Tables** — content TBD based on literature:
   - Table 1: Summary of urban agriculture in Nigerian cities (from literature)
   - Table 2 (optional): Policy frameworks

---

*This spec replaces the spatial statistics approach entirely. The paper will be a Nigeria-focused literature review on climate-smart urban farming practices with policy recommendations, fitting within 12 pages at TNR 12pt 1.5.*
