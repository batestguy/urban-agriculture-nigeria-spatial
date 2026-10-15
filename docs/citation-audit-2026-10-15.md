# Citation audit — 15 October 2026

**Scope:** `manuscript/references.bib`, 24 entries, of which 25 keys are cited in `manuscript/manuscript.qmd`.
**Method:** every DOI resolved against the Crossref REST API (`scripts/verify_bib.py`); entries without a DOI listed for manual checking.
**Trigger:** a placeholder DOI (`10.xxxx/njae2024`) was found during the earlier audit, which suggested the bibliography had not been checked.

---

## Verdict

**A source used in the Introduction was fabricated.** It has been removed and replaced with a clearly-labelled placeholder for the author to fill.

Beyond that, the DOI-bearing entries are now in reasonable shape: **7 verified correct, 2 unresolvable, 15 with no identifier at all.** No entry currently asserts a DOI that resolves to the wrong paper.

---

## 1. The fabricated entry

The manuscript cited `urban_food_insecurity2026` in the Introduction, supporting the claim that
*nearly 7 in 10 urban households experienced moderate or severe food insecurity*.

The bib entry read:

```bibtex
@article{urban_food_insecurity2026,
  author  = {Ifeakachukwu, N. P. and Adebayo, A. B.},
  title   = {Urban food insecurity in {Nigeria}: A multilevel analysis of nationally representative data},
  journal = {Journal of Urban Health},
  year    = {2026},
  doi     = {10.1007/s11524-026-xxxxx},
  note    = {Nearly 7 in 10 urban households experienced moderate or severe food insecurity},
}
```

Four things are wrong with it:

| Problem | Evidence |
|---|---|
| The DOI is a placeholder | `10.1007/s11524-026-xxxxx` — the `xxxxx` is literal |
| A 2026 publication year | No such paper could be located |
| An invented co-author | No record of "Ifeakachukwu, N. P." on this topic was found |
| A precise empirical claim attached to it | "nearly 7 in 10" cannot be checked against a source that may not exist |

The citation has been **removed from the manuscript text** and the bib entry replaced by a
placeholder pointing the author at the National Bureau of Statistics. **The claim itself is now
unsupported and must be either sourced properly or deleted.**

### How this was nearly made worse

Attempting to repair it from web-search results produced a DOI —
`10.1007/s11524-023-00751-w` — that the search described as the correct 2023 paper by
"Adebayo et al.". Resolving that DOI directly through Crossref returned:

> **Optimizing Sanitation Network Upgrading Projects in Slum Areas** — Marzouk, Bahi, El-Anwar
> *Journal of Urban Health* 100: 811–833

A completely different paper. **The search summary was wrong, and applying it would have put a
second fabricated citation into the manuscript, this time with a DOI that resolves.** That bad
edit was reverted; nothing in the bib now rests on a web-search summary.

---

## 2. Corrections applied (Crossref-verified)

| Entry | Was | Now | Basis |
|---|---|---|---|
| `palinkas2013` | year 2013 | **year 2015** | Crossref: title matches, year is 2015. DOI/volume/pages correct. Key name kept stable for citation continuity |
| `tambol2025` | pages 4127 | **pages 2771** | The bib's own DOI resolves to this paper by Tambol et al. — only the page number was wrong |
| `adedeji2009` | 2(6): 112–123 | **2(5): 101–107** | Publisher PDF record |

## 3. Flagged as unresolvable (author must verify)

| Entry | DOI | Status |
|---|---|---|
| `sekabira2022` | `10.1007/s43615-022-00183-5` | Returns **404** in Crossref. Title, volume and pages are therefore unverified |
| `issifu2025` | `10.1016/j.landusepol.2025.107278` | Returns **404** in Crossref |

Neither can be fixed from here without a source that can be trusted.
An alternative DOI was tried for each and both also returned 404, which is why they are left
in place with an explicit `UNVERIFIED` note rather than changed again.

**Action:** open the publisher page for each, confirm the article number and DOI, and correct.

## 4. Fifteen entries have no DOI at all

Most are legitimately DOI-less: government policy documents (`nup2022`), institutional reports
(`fao2007`, `fao2024`, `oshinusi2024`), websites (`worldbank2024`, `noburn2026`, `nesg2024`,
`fewsnet2024`), and books (`krejcie1970`, `saidu2010`, `zeeuw2014`). These need checking by hand
against the cited URL or the printed copy.

Two deserve particular scrutiny:

- **`bashir2022`** — "Geospatial analysis of Bauchi metropolis growth", no journal, no publisher,
  no URL, no DOI. The manuscript relies on it for the study-area coordinates, rainfall and relief.
  It reads like a thesis or an unpublished report. **Verify it exists and is citable.**
- **`oshinusi2024`** — given as "University of Toronto Scholaris", which is not a recognisable
  publisher name; it may be a repository. The 60% organic-waste figure rests on it.

## 5. One further issue: the coordinates in the manuscript

While verifying `bashir2022`, an unrelated error surfaced in the manuscript text:

> "Bauchi Metropolis (10°16'30"–10°21'00"N, **90°48'00"–90°52'30"E** ...)"

A longitude of 90°E is in eastern China. Bauchi is at approximately **9.8°E**. The degree symbol
appears to have been transposed for a superscript. **This is a factual error in the manuscript
and should be corrected to 9°48'00"–9°52'30"E.**

## 6. How to re-run this audit

```pwsh
C:\Users\TOSHIBA\ds-general\python.exe scripts/verify_bib.py
```

It resolves every DOI through Crossref, compares title/year/volume/pages against the bib record,
and lists the DOI-less entries separately. Exit code is non-zero if any DOI is wrong or
unresolvable, so it can gate a submission.

---

## Honest summary

The bibliography was **not** in a submittable state. One entry was invented, two DOIs do not
resolve, one point number and one year were wrong, and the manuscript text contains a coordinate
error. Two of these (the invented entry, the wrong pages) have been fixed. Two require the
author's access to publisher records. The coordinate error is a one-character fix in the text
that has **not** been applied, because the earlier session reverted manuscript edits at the
author's direction and this one should be confirmed.

**Do not submit until sections 3, 4 and 5 are cleared.**
