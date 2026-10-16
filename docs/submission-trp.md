# Town and Regional Planning — submission gap analysis

**Journal:** Town and Regional Planning (ISSN 1012-280X print / 2415-0495 online),
University of the Free State — Diamond Open Access, no APC.
**Guidelines source:** `docs/trp-author-guidelines.md` — verbatim extraction from the journal's
own site, fetched **2026-10-16**.
**Venue status:** **selected.** It passes the Scopus gate that dropped AJLP&GS (see
`docs/venue-options.md`).
**Manuscript today:** `manuscript/manuscript.qmd` → HTML / PDF / Word (Times New Roman, not yet).

---

## Headline: this is a **reformat and restructure**, not a reformat alone

AJLP&GS wanted a *formatting* change. Town and Regional Planning wants a formatting change **and
a different section architecture, a different abstract shape, and a different referencing
system**. The analysis, the findings and the 175 verification checks are untouched by all of it.

Three things are comfortable:

- **Word count fits.** The rendered `.docx` holds **5,312 words excluding references**, against a
  4,000–8,000 window. There is room to *add* the required literature-review section and still sit
  mid-range.
- **The title is already compliant.** "Where urban agriculture concentrates in Nigerian cities"
  is 8 words and informative.
- **No anonymised copy is required.** That was an AJLP&GS requirement; TRP does not ask for one.

---

## The one item that is a policy conflict, not a formatting task

**TRP's AI policy is stricter than the disclosure this manuscript currently makes.**

The journal's submission checklist requires the author to confirm:

> It confirms that any use of generative AI tools (e.g. ChatGPT) has been **limited to language
> editing and grammar support only. AI has not been used to generate substantive content,
> analysis, or data.**

The AI policy adds that AI "may not be used to generate substantive content such as problem
statements, literature reviews, methods, **analysis**, findings, policy recommendations, or
interpretations."

The manuscript's existing declaration (Section 10 today) says:

> An AI coding assistant was used during preparation of this work. Its role was to assist with
> **implementing and debugging the analysis pipeline**, writing the verification scripts, and
> **drafting and editing the prose.**

Those two statements do not sit together. The manuscript discloses that AI helped build the code
that performs the analysis; the checklist asks the author to attest that AI was used **only** for
language editing. **Ticking that box would be false**, and the declaration is the honest document.
This is the author's call, not something to paper over by softening the declaration:

- **Option A — declare fully and let the editor judge.** The policy's own §1 says AI "can assist
  with language editing and **routine tasks**", and the analytical *decisions* — the design, the
  model choice, the interpretation — are the author's. Argue the disclosure fits the policy's
  intent and accept the risk of rejection under §5.
- **Option B — ask the editor first.** A short enquiry stating exactly what the AI did and asking
  whether pipeline-implementation assistance falls under permitted "routine tasks". Costs one
  round trip; removes the risk.
- **Option C — reconsider the venue.** If the disclosure is not acceptable to the journal, the
  shortlist in `docs/venue-options.md` still stands.

**Recommendation: Option B**, and say so in the Comments to the Editor rather than hiding it. This
is phrased in the manuscript's favour already — the reproducibility machinery the AI helped write
is what makes the paper's numbers verifiable, which is the journal's own stated value.

---

## Formatting gaps (mechanical)

| Requirement | Journal asks for | Manuscript today | Action |
|---|---|---|---|
| Body font | Times New Roman 12 pt | Cambria 12 pt | **Change** |
| Line spacing | single | 1.2 multiple | **Change** |
| Paragraphs | start on a new line, **not indented** | Quarto default | **Set** |
| Table text | Times New Roman 10 pt, single spacing | Cambria 10 pt, 1.2 | **Change** |
| Table borders | ½ pt | default | set |
| Figures | **TIF or JPEG, 300 dpi** | PNG (2100–3600 px) | **Convert** |
| File format | MS Word | `.docx` ✓ | none |
| Headings | Arabic, max 3 levels (1 / 1.1 / 1.1.1) | numbered ✓ | none |
| In-text citations | Harvard `(Author, 1999: 12)` | APA author–date | **Convert** |
| Reference list | inhouse Harvard, **surnames capitalised** | APA | **Convert** |
| References | DOI for every source; URL + visit date for web sources | DOIs resolved ✓ | add visit dates |

### The referencing system is the largest mechanical job

TRP wants `HEALEY, P. 2026. Collaborative planning. London: McGraw-Hill.` — surname in capitals,
alphabetical, DOIs present. The manuscript renders APA from `manuscript/references.bib` via
`apa.csl`. The honest path is a **TRP-flavoured Harvard CSL file** driving the same generated
`.bib`, not hand-edited references — `references.bib` is generated by `scripts/build_bib.py` and
must not be hand-edited.

---

## Structural gaps (the real work)

TRP prescribes a section architecture for a research article:

```
1. Introduction
2. Literature review      <- MISSING today
3. Study area             <- exists, but buried inside "Data"
4. Methods                <- exists, but subsections do not match
5. Results
6. Discussion
7. Conclusion
   Declaration of AI Use  <- before the references
   References
```

Where the manuscript stands now: `1 Introduction / 2 Data (incl. Study area) / 3 Methods /
4 Results / 5 Discussion / 6 Conclusion / … / 13 References`.

Three specific mismatches:

1. **There is no literature-review section.** The Introduction does prior-work work inline. TRP
   wants a distinct section that "identif[ies] international research on similar topics and
   indicate[s] a clear gap". The material exists — the introduction already cites the
   single-city survey tradition and the VGI-coverage literature — but it needs to be split out
   and, on TRP's instruction, broadened to international work on urban agriculture and
   volunteered geographic information. **Room to grow: the word budget allows ~800–1,200 words
   here at no cost elsewhere.**
2. **The study area must be its own section, after the literature review, and must not sit in the
   methodology.** Today it is §2.1 inside "Data", before Methods — close, but it needs to be
   promoted to a top-level section in the right place.
3. **The methods subsections do not match the journal's five.** TRP names: *Research design*;
   *Population, sampling, and response rate*; *Data collection*; *Data analysis and how to
   interpret the results*; *Limitations*. The manuscript has *Density and zero-inflation* /
   *Spatial weights* / *Models* / *Software and reproducibility*. The mapping is not one-to-one:
   **"population, sampling, and response rate" is survey language and has no natural analogue in
   a census of mapped features** — the honest treatment is a subsection that says plainly that
   the study has no sampling frame or response rate because it analyses a complete extract, and
   explains what plays the equivalent role. This is a place to be candid, not to invent a
   response rate that does not exist.

Also: **articles must be written in third person.** The manuscript uses first person throughout
("We ask three questions", "We selected five cities"). This is a search-and-revise pass, not a
rewrite.

---

## Submission package (owner: the author)

| Item | Status |
|---|---|
| Manuscript `.docx`, TRP style | **to produce** (reformat + restructure) |
| `Declaration of AI Use` before references | exists; rename, relocate, restate per policy §2.2 |
| ORCID iD | **required — author to supply** |
| Author Agreement (form 115) signed | **author to complete** |
| Publishing Agreement (form 56) signed | **author to complete** |
| Comments to the Editor: origin of article | say **independent work**; no institutional proof needed |
| Suggested referees (optional, 3, outside own institution) | optional |
| Cover note | not requested; a short compliance note saves a round trip |

---

## What does not change

Nothing scientific. The frozen data, the five figures, the 19 references, the 175 verification
checks and every headline number stay as they are. `Rscript build.R --audit` must still pass
after any reformatting, and it will — it checks the data, not the layout.

## Verification obligations after the reformat

1. `Rscript build.R --audit` → 175 checks, 0 discrepancies.
2. `python scripts/verify_author_block.py` → author block present in every rendered artefact.
3. A TRP-specific typography check (Times New Roman / single spacing / margins) reading the
   rendered `.docx`, mirroring what `scripts/fix_docx_ajlpgs.py` did for the old spec.
4. Word's own `ComputeStatistics` for the page count, as before — and a word count excluding
   references checked against 4,000–8,000.
