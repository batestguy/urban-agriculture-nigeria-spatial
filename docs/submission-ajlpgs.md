# AJLP&GS submission — formatting gap analysis

**Journal:** African Journal on Land Policy and Geospatial Sciences (ISSN 2657-2664)
**Guidelines source:** `docs/ajlpgs-author-guidelines.md` — extracted verbatim from the journal's
own `AuthorGuidelines_AJLP&GS-EN.docx`, downloaded 15 October 2026.
**Manuscript today:** `manuscript/manuscript.qmd` → HTML / PDF / Word.

---

## Read this before formatting

**The Scopus question is unresolved and may disqualify this venue.** The journal's own website
lists DOAJ and Cairn under "Indexed In" and does **not** list Scopus. Check
<https://www.scopus.com/sources> for ISSN 2657-2664 before investing effort. The formatting work
below is worth doing regardless — it is the house style of a land-policy journal and would be
close to what any similar venue wants — but a Scopus requirement changes the target.

---

## What the guidelines require, and where this manuscript differs

| Requirement | Journal asks for | Manuscript today | Action |
|---|---|---|---|
| **Title length** | 6–10 words | 17 words | **Shorten** |
| **Subtitle** | 4–6 words | 20 words | **Shorten or drop** |
| **Font** | Cambria throughout | default Quarto serif | **Set Cambria** |
| **Body size** | 12 pt, justified | default | **Set** |
| **Line spacing** | 1.2 multiple | default | **Set** |
| **Page limit** | ≤ 20 pages incl. references, figures | 22 pages | **Trim ~2 pages** |
| **Margins** | top 2, bottom 1.5, left/right 1.5 (cm) | default | **Set** |
| **Abstract** | Structured, ≤ 500 words, **no equations, no references**, single-spaced, Cambria 10 pt | ~330 words, unstructured | **Restructure** into Context/Goal/Methods/Results |
| **Keywords** | 6, Cambria 10 pt bold label | 6 | minor |
| **Figures** | Numbered with Arabic numerals, embedded in text | embedded, captioned | minor |
| **Tables** | Cambria 10 pt, interline 1.2, no space before/after | live-rendered | **Set** |
| **References** | **Alphabetical, specific format, all in one list** | APA via CSL | **Swap CSL or reformat** |
| **Additional reading** | 3–6 suggestions | absent | **Add** |
| **Key terms and definitions** | 3–5 terms with definitions | absent | **Add** |
| **Funding** | Required section; "NO FUNDING" if none | absent | **Add** |
| **Author contributions** | Required section | absent | **Add** |
| **Acknowledgments** | Section (optional) | absent | consider |
| **Anonymisation** | **Remove author names and affiliations from first page** for review | author block present | **Maintain two versions** |

### The two that need real thought, not just formatting

**1. The abstract is structured, and must not carry equations or references.**
The guidelines name the parts explicitly: *Context and background*, *Goal and Objectives*,
*Methodology*, *Results*. Up to 500 words. This suits the paper well — the structure maps almost
exactly onto what it already says, and the extra room over a typical 250-word limit lets the
method and the coverage-control result both be stated properly. The current abstract mentions no
equations or citations, so it complies already.

**2. References must follow the journal's own format, not APA.**
The required forms are given in the guidelines with examples. A CSL style for
"Author (YYYY). Title. Journal, Volume(Issue), pp.xx–yy" is close to APA but not identical —
the journal uses `pp.` and an ampersand-plus-semicolon convention for three or more authors.
Either find a matching CSL or post-process. **`references.bib` must not be hand-edited**: it is
generated from Crossref by `scripts/build_bib.py`, and that guarantees the metadata is right.
Change the rendering style, never the source data.

---

## Two things the guidelines do NOT mention

**AI use.** The author guidelines say nothing about generative AI, and the journal is not a
COPE member. Absence of a policy is permission by default, but it also means there is no
disclosure mechanism. Recommendation: include the declaration in the manuscript anyway, in the
Author Contributions section. Volunteering it is safer than being asked.

**No APC is confirmed by DOAJ, and the journal does not mention fees.** Consistent with a
diamond open-access model.

---

## The submission package

1. **Anonymised manuscript** — author names and affiliations removed from the first page, as the
   submission process explicitly instructs. This is the file you upload.
2. **Named final version** — same file with authors restored, submitted separately as the
   guidelines describe.
3. **Copyright form** — `AJLP&GS_COPYRIGHT_FORM.docx`, downloadable from the submissions page at
   `revues.imist.ma/index.php/AJLP-GS/about/submissions`. The checklist states it must be
   returned to the Editor; submissions that do not meet the requirements may be sent back.
4. **Cover letter** — not requested, but the checklist says submissions not adhering to the
   guidelines may be returned. A short note confirming compliance saves a round trip.

---

## What is unchanged

Nothing about the analysis changes. The findings, the verification gates, the figures and the
citation base all stay as they are. This is presentation work only.

`Rscript build.R --audit` still has to pass (175 checks) after any reformatting, and it will —
the checks run against the frozen data, not against the layout.
