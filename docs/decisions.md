# Decision record

Canonical log of every decision taken on this manuscript's venue, submission and
manuscript-content choices. **Append, do not rewrite.** Each entry states the decision, the
evidence behind it, and what it supersedes — so a later reader can tell a considered choice from
an accident.

Handoffs (`docs/handoff-*.md`) summarise the current state and point here. This file is the
history; the handoffs are the snapshot.

Dates are the author's local dates. Where a decision was made by the author, say so; where it was
recommended by an assistant and accepted, say that too.

---

## D-01 · 2026-10-15/16 · AJLP&GS dropped — not Scopus-indexed

**Decision:** Do not submit to *African Journal on Land Policy and Geospatial Sciences*.

**Evidence:** Four independent sources agreed it is absent from Scopus — SCImago returns no
result for the title; DOAJ's API record for `2657-2664` carries no Scopus identifier; the
journal's own site lists DOAJ and Cairn, not Scopus; a search summary stated it is not indexed.
None disagreed.

**Status:** Final. Verified again on 2026-11-09 against Elsevier's serial-title API: ISSN
`2657-2664` returns HTTP 404.

**Recorded in:** `docs/venue-options.md` §0, `docs/submission-ajlpgs.md`.

---

## D-02 · 2026-10-16 · Town and Regional Planning selected

**Decision:** Target *Town and Regional Planning* (University of the Free State, ISSN 1012-280X).

**Reasoning:** Passed the Scopus gate on the journal's own accreditation page. No APC. The author
selected it.

**Status:** **Superseded by D-03.** TRP was never submitted to.

**Recorded in:** `docs/venue-options.md` header, `docs/submission-trp.md`.

---

## D-03 · 2026-10-18 · TRP abandoned — AI-policy conflict

**Decision:** Leave TRP for a venue with no AI policy. **Never submitted.**

**Reasoning (the author's, recorded first-person in commit `0bb1539`):** TRP's checklist requires
the author to attest that generative AI was used "limited to language editing and grammar support
only", and its policy bars AI from generating "methods, **analysis**, findings". The manuscript
declared that AI assisted with implementing and debugging the analysis pipeline. Those two
statements cannot both be true, so ticking the box would have been false.

**What did *not* happen — do not record it as a rejection:** TRP was never reached. The author
could not register because the portal's Google OAuth returned `401 invalid_client`, and he
emailed TRP on 17 Oct for help. He switched to TeMA on 18 Oct. Alna Beukes replied on **19 Oct**
— one day after the switch — offering to register him manually. So the TRP route was open and
being actively facilitated when the decision to leave was taken. The AI clause was the stated
reason for leaving, not a rejection, and not the only hurdle (TRP also demands proof of
postgraduate origin).

**Status:** Final. **The AI-clause reasoning did not travel to the next venue** — see D-09.

---

## D-04 · 2026-10-18 · TeMA selected; AI declaration removed

**Decision:** Target *TeMA — Journal of Land Use, Mobility and Environment* (Università di Napoli
Federico II). **Remove** the `# Declaration of Generative AI Use` section, on the ground that TeMA
publishes no AI policy — its `Format_TeMA_paper_2026.docx` has no AI clause and
`about/editorialPolicies` 404s — so there was no attestation to conflict with.

**Status:** Venue choice superseded by D-08. Declaration **restored** under D-09. The removal was
correct for that venue and wrong as a general policy; see D-09 for why.

**Consequential changes made for TeMA, still in force:** abstract cut to 200 words; APA
references (`csl: apa.csl`); ORCID `0009-0002-3302-9558` in the front matter and the author block;
`# Author's profile` section added (later removed, D-11).

---

## D-05 · 2026-10-19 · TeMA desk-rejected on scope

**Outcome:** *Not a decision — an event, recorded because it drove later choices.*

`redazione.tema@unina.it`, subject `[TeMA] Gatekeeper Decision`, 19 October 2026 at 12:04 PM:

> "Before starting the revision process, we conduct a preliminary assessment of the submitted
> manuscript to determine its alignment with the journal's objectives and scientific contents.
> We regret to inform you that, following evaluation, your proposal has been deemed **not fully
> aligned with the journal's aims and scopes**."

**Reading:** submitted 18 Oct, decided 19 Oct — under 24 hours. No reviewer saw it. This is a
scope screen at the gatekeeper stage, not an evaluation of the science. Nothing in the letter
criticises the data, method or argument. **There is nothing to revise and nothing to rebut.**

**Consequence:** the search that followed tested editorial *fit* against published evidence, which
no previous venue search had done.

---

## D-06 · 2026-11-09 · Scopus verified by API, not by summary

**Decision:** Verify every candidate venue's Scopus status against Elsevier's serial-title
endpoint, not against search summaries or SCImago.

**Instrument:** `https://api.elsevier.com/content/serial/title/issn/{ISSN}`. Keyless, one request
per ISSN, returns the same source records that back `scopus.com/sources`.

**Why it was needed:** `scopus.com` and `scimagojr.com` serve Cloudflare challenges to automated
browsing, so the previous search could not verify Scopus at all. Worse, `docs/venue-options.md` §2
recorded TeMA's SCImago SID as **21100830974** — flagged unverified, and indeed
`scopus.com/sourceid/21100830974` returns `?invalidSource=t`. It does not exist. TeMA's real
Scopus source is **21101185191**.

**Validation before trust — all four controls behaved correctly:** Nature `0028-0836` → indexed;
TeMA `1970-9889` → indexed; TRP `1012-280X` → indexed; AJLP&GS `2657-2664` → 404.

**Status:** Standing practice. Any future Scopus claim on this project goes through this check.

**Reproducing:** `.scratch/scopus_check.py` (promote to `scripts/` if it is needed again).

---

## D-07 · 2026-11-09 · "Free" means no cost to the author, not "fully open access"

**Decision:** Treat the constraint as *no fee payable by the author*, not *DOAJ-listed*.

**Reasoning:** OpenAlex records `apc_usd` for every journal, including subscription ones — but for
a hybrid title that figure is the price of the *optional* Open Access route. Land Use Policy shows
`$3,830`, which an author publishing through the subscription route does not pay. The previous
search filtered DOAJ on `has_apc:false`, which can only ever return fully-OA journals and therefore
structurally excluded every subscription title — including the ones that fit this paper best. That
is why earlier shortlists kept producing journals that were free but that a desk editor would not
want.

**Consequence:** two accepted categories — fully-OA with APC 0 (rare among good Scopus titles), and
subscription/hybrid with no author-side fee (the normal case for the best-fitting journals).

---

## D-08 · 2026-11-09 · African Geographical Review selected

**Decision:** Submit to *African Geographical Review* (Taylor & Francis, ISSN 1937-6812 /
2163-2642).

**Evidence — all three gates passed on the journal's own terms, not inference:**

- **Scopus:** confirmed by the D-06 instrument.
- **Cost:** the journal states, in its instructions for authors, **"There are no submission fees,
  publication fees or page charges for this journal."** Open Select is a post-acceptance choice.
- **Fit:** across its last 200 Crossref items, 8.5% concern Nigeria and 11.5% use spatial methods,
  and 48.5% concern Africa. It has published *"Auditing the spatial and temporal changes in urban
  cropland in Harare metropolitan Province"* — urban cropland mapping in an African city, which is
  this paper's exact subject. That is the test TeMA failed.

**Runners-up, and why not chosen:** *Land Use Policy* (strongest topical home — 62 of the last 100
Crossref results for OpenStreetMap land-use work in Africa are there — but higher review bar);
*Applied Geography*, *Habitat International*, *GeoJournal*, *Applied Spatial Analysis and Policy*
(all Scopus-indexed and free via subscription, weaker Nigeria fit); *Africa Spectrum* (genuinely
$0 APC and Scopus-indexed, but a social-science journal with nothing on urban agriculture — the
TeMA outcome in prospect).

**Nigerian venues — investigated and ruled out on evidence:** of 68 Nigerian journals in DOAJ,
only 3 charge no APC (economics, law, general science). Of 14 plausible Nigerian titles checked for
Scopus, 3 are indexed (Nigerian Journal of Technology; Journal of Agricultural Extension; Journal
of the Nigerian Society of Physical Sciences). **The intersection of both constraints is empty.**
Nigerian representation comes through the authorship, not the publisher.

**Status:** Acted on — submitted under D-15.

**Recorded in:** `docs/venue-search-2026-11-09.md`.

---

## D-09 · 2026-11-09 · AI declaration restored, naming tools with versions

**Decision:** Restore `# Declaration of Generative AI Use`, and name the tools and versions.

**Reasoning:** D-04 removed the declaration because TeMA has no AI policy. **That reasoning was
venue-specific and does not travel.** Taylor & Francis requires acknowledgement — "You must also
acknowledge the use of AI in any papers you write based on that research" — and explicitly lists
**"Coding assistance"** among permitted uses, which is a materially better position than TRP's
"language editing only" clause. Silence where disclosure is mandatory is a misrepresentation, not
a judgement call.

**The attestation problem, and why the box was not ticked at first:** the submission form requires
the declaration to disclose "the full name of the tool used (**with version number**)". The repo
recorded `Co-Authored-By: Claude <noreply@anthropic.com>` on two commits (2026-10-15) but **no
version number anywhere** — checked across git history, docs and commit messages. Ticking the box
against a version-less declaration would have been a false attestation, the same class of error as
the fabricated Scopus ID and the fabricated DOI this project has already been burned by. The box
was left unticked and the author was asked.

**Resolution:** the author supplied the tools and versions — **DeepSeek Flash 4.1 (build 1017)**
and **Opus 5.5**. The declaration was rewritten to name them, state how they were used and why,
and state explicitly that no generative tool produced data, a figure, a map, or an interpretation.
The box was then ticked.

**Status:** Final. Declared in the submitted manuscript.

---

## D-10 · 2026-11-09 · Trimmed to the journal's six-element ceiling

**Decision:** Reduce the article to **4 tables + 2 figures**; move the other 7 tables and 4 figures
to a separate supplementary file.

**Reasoning:** AGR asks that papers "limit the number of tables and/or figures to 6". The
manuscript carried 12 tables and 6 images — 18 elements, three times the request. The limit is
phrased as a request rather than a rule, but at 3× it would be noticed at the desk stage, which is
exactly where TeMA was lost.

**What stayed in the article** — the four tables and two figures carrying the central claims:
global Moran's I under four specifications; the negative binomial model with area as exposure; the
coverage-correction comparison (ΔAIC = 20.0); the ten most intensively cultivated LGAs; the
LISA-after-FDR map; the summary panel.

**What moved:** analysis frame; feature types; features by city; local clustering counts; the scale
coefficient in interpretable units; the coverage confound; the climate diagnostic; and the figures
for bounding-box leakage, density distribution, feature locations and the city-level climate
relationship.

**Check performed:** no prose promise was orphaned — there are no numbered "Table N"/"Figure N"
cross-references in the text, and every value quoted in the article is still reported in its text.
The supplementary file tabulates rather than extends the claims.

**Gates after the trim:** figures 2/2 placed with no orphans; format all checks passed; audit 114
checks, 0 discrepancies; 6,136 words against the 7,000 cap.

**Recorded in:** `manuscript/supplementary.qmd`; the article's own `# Supplementary Material`
section states what is in the separate file.

---

## D-11 · 2026-11-09 · Author's profile removed; Key Terms kept

**Decision:** Remove `# Author's profile`. **Keep** `# Key Terms and Definitions`.

**Reasoning — profile:** it was a TeMA template requirement with no place in a T&F geography
article, and it states the author's name and institution in the body, which is an identity leak in
the file that goes to double-anonymous reviewers.

**Reasoning — glossary:** AGR is format-free and read by a general geography audience; defining
*coverage bias*, *exposure offset*, *LISA* and *spatial autocorrelation* earns its few hundred
words. This reversed an earlier recommendation to cut it.

**Status:** Final.

---

## D-12 · 2026-11-09 · Declaration of Interest added

**Decision:** Add `# Declaration of Interest`.

**Reasoning:** AGR's required element order includes a "declaration of interest statement"; the
manuscript had none. It now states no competing financial interests, sole authorship, no funding,
and refers to the separate AI declaration.

**Status:** Final.

---

## D-13 · 2026-11-09 · Rendered artefacts stay unversioned, including the supplementary

**Decision:** Add `supplementary.docx` to `manuscript/.gitignore`, alongside `manuscript.docx`,
`manuscript-anonymised.docx`, `manuscript.pdf` and `manuscript.html`.

**Reasoning:** the repo already excludes rendered artefacts because the journal permits archiving
only the **published** version, so a public pre-publication copy would breach its terms; and
because they are large binaries that change on every render. `supplementary.docx` was simply not
covered by the existing patterns. The `.qmd` source is tracked and the binary is rebuildable.

**Status:** Final. The rebuilt artefacts remain on disk for upload, just untracked.

---

## D-14 · 2026-11-09 · `scripts/normalize_docx_meta.py` created

**Decision:** Add a script to normalise DOCX compatibility metadata after every render.

**Reasoning:** Quarto/pandoc writes `compatibilityMode val="14"` (Word 2010) into
`word/settings.xml`, and `reference.docx` carries `Application: Microsoft Macintosh Word` /
`AppVersion: 14.0000` in `docProps/app.xml`. Word therefore opened every rendered file in
[Compatibility Mode] — a banner that looks unpolished beside a submission. It is not a
file-format fault: the container is valid OOXML throughout. The script sets mode 15 and normalises
the app metadata, touching only those two parts, writing through a sibling temp file so a failure
cannot truncate a submission document. It is idempotent and has a `--check` mode.

**Run order — this matters:** `quarto render manuscript.qmd` → `quarto render supplementary.qmd` →
`fix_docx_trp.py --anonymise` → `normalize_docx_meta.py`. Re-rendering alone silently drops the
author block *and* the compatibility fix.

**Status:** Final, committed.

---

## D-15 · 2026-11-09 · Submitted to African Geographical Review

**Decision:** Submit. **Done** — the author authorised it in the session.

**Submission ID 260528906**, 9 November 2026 at 10:56. Confirmed by the journal's own
acknowledgement from `RAFG-peerreview@journals.tandf.co.uk`, not merely by the portal's success
page.

**Submitted:** Research Article; `manuscript.docx` (with author details);
`manuscript_anonymised.docx` (anonymous review copy, identity verified absent);
`supplementary.docx` (Supplementary Material - for review). 6,136 words, 200-word abstract, six
keywords. No fee. Open Select declined for now; it is offered post-acceptance.

**Judgement at the attestation:** the AI checkbox was ticked only after the declaration named the
tools with versions (D-09). Before that the box was left unticked and the author was asked, rather
than a version being invented to satisfy a form.

**Status:** In review. Queries to `RAFG-peerreview@journals.tandf.co.uk` with the ID in the
subject.

---

## D-16 · 2026-11-09 · `manuscript/TEMA-SUBMISSION.txt` left untracked

**Decision:** Do not delete; do not commit.

**Reasoning:** it is the copy-paste sheet for the abandoned TeMA submission (ID 14096). The
instruction was to commit and push, not to delete unrelated files. It sits untracked until the
author says otherwise.

**Status:** Open — awaiting the author's call.

---

## D-17 · 2026-11-13 · Correction: AGR returned the submission unreviewed; inbox recorded

**Not a decision — a correction of fact.** D-15's "Status: In review" was wrong from 10 November.

**Which inbox:** every AGR / Taylor & Francis message for this submission goes to the
corresponding-author address `jzbannister@atbu.edu.ng` (university Google Workspace mail). None
are in the author's personal Gmail — that account was searched across all folders including trash
on 2026-11-13 and holds nothing from the journal. Instrument: the university inbox read in the
browser on 2026-11-13, search `260528906`, three messages.

**What the inbox shows:**

| Received | From | Subject |
|---|---|---|
| 9 Nov 2026 | `RAFG-peerreview@journals.tandf.co.uk` | Submission received … (Submission ID: 260528906) |
| 10 Nov 2026, 05:43 (letter dated 09-Nov-2026) | AGR Editorial Office via `onbehalfof@manuscriptcentral.com` | 260528906 (African Geographical Review) - changes required to your submission |
| 13 Nov 2026, 00:53 | `RAFG-peerreview@journals.tandf.co.uk` | Incomplete submission to African Geographical Review, ID: 260528906 |

**The editorial office's reason, in substance:** the author's name was found in the anonymous
file; the journal runs double-blind review and needs a fully blinded document. The author is to
fix it and re-submit via the author dashboard ("Resume"). The 13 Nov message is a reminder that
the submission is still incomplete.

**Consequence:** the paper is **not in review**. It is back with the author, awaiting a corrected
anonymous file. D-15's claim "identity verified absent" in `manuscript_anonymised.docx` is
contradicted by the journal. Where the name survives in that file has **not yet been
investigated** — do not guess; text-extract the rendered artefact, including headers, footers,
document properties and comments, before re-uploading.

**Status:** Investigated and fixed in D-18; re-submission pending.

---

## D-18 · 2026-11-13 · Review copies scrubbed in every part; supplementary de-authored

**Where the identity was** (instrument: a scan of every zip part of the files as uploaded,
copies kept in `.scratch/pre-scrub/`):

- `manuscript-anonymised.docx` — body clean. Name in `docProps/core.xml` (`dc:creator`, the Word
  "Author" field); affiliation in `docProps/custom.xml` (`author-affiliation`). Pandoc writes both
  from the front matter; `fix_docx_trp.py --anonymise` only rewrites `word/document.xml`, and its
  own check only reads that part — so it truthfully reported "identity absent" about the one part
  it looked at.
- `supplementary.docx` — **not flagged by the journal, but also exposed**: the name was printed
  as a byline in the body, and in `docProps/core.xml`. It was uploaded as "for review".

**Decision:**

1. New `scripts/scrub_review_copies.py` empties `dc:creator` / `cp:lastModifiedBy`, drops author
   and identity-bearing custom properties, removes any body paragraph carrying identity, then
   scans every part of both review files for ten identity strings (name, name parts, e-mail,
   ORCID, affiliation, institution). `--check` verifies only. Added to the rebuild order after
   `fix_docx_trp.py --anonymise` and again as a final check after `normalize_docx_meta.py`.
2. `author:` removed from `manuscript/supplementary.qmd` — the supplementary has no named
   version, so the source should not carry the name at all.

**Verified 2026-11-13:** scrub → normalise → `--check`: 2 files, every part, 0 hits. Break-test:
the same check on the pre-scrub copies fails with 15 hits. Paragraph text diff: anonymised copy
283 → 283 paragraphs, only `docProps/core.xml` and `custom.xml` changed; supplementary 127 → 126,
the one removed paragraph is the byline. `verify_trp_format.py` passes; `verify_docx_figures.py`
2 figures placed; every XML part re-parses. `verify_author_block.py` shows only the two known
`.codewhale/state/` hits.

**Not verified:** the supplementary was not re-rendered from the edited `.qmd`; the uploaded file
is the post-processed 9 Nov render. The files were not opened in Word.

**Status:** Fixed locally; re-uploaded and re-submitted in D-19.

---

## D-19 · 2026-11-13 · Re-submitted to AGR with clean review files; data link withheld

**Done** — the author instructed the upload, the change to the data field, the submit, and the
acceptance of the T&F terms, each explicitly in the session.

**Portal changes (submission 260528906, author dashboard → Resume):**

- `manuscript_anonymised.docx` (Manuscript - anonymous) and `supplementary.docx` (Supplementary
  Material - for review) deleted and replaced with the D-18 scrubbed files, both shown "Added 13
  November 2026". `manuscript.docx` (with author details) untouched, still "Added 9 November".
- **Data-availability field** changed from the GitHub repository URL to "Public repository link
  withheld for double-blind review; to be provided on acceptance". Reason: the URL carries the
  GitHub username, and the public repo's `AGENTS.md` names the author and institution; whether
  the field reaches reviewers is unknown. The manuscript itself carries no data-availability
  statement and no repository link (verified by scan).
- All other fields carried over from 9 Nov unchanged; author-list confirmation answered "Yes".

**Confirmed:** portal page "Thank you for your submission … submission ID is 260528906", and a
new "Submission received" e-mail from `RAFG-peerreview@journals.tandf.co.uk` in
`jzbannister@atbu.edu.ng` on 13 Nov 2026, 03:46.

**Not verified:** the portal-generated anonymous PDF proof was opened (required to enable
Submit) but could not be read by the browser tool, so the portal's own rendering was not
inspected for identity — only the source files were.

**Status:** In review (re-submitted 13 Nov 2026). On acceptance, supply the repository link.

---

## Open decisions

Not yet made. Recorded so they are not silently forgotten.

1. **Folder rename.** `scripts/rename_folder.ps1` performs it and refuses to half-move from inside
   the source; run from `D:\` with nothing holding the folder. Pending since before 2026-10-15.
2. **GitHub licence detection** still reports none despite `LICENSE` and an SPDX identifier.
3. **Response to reviewers,** whenever AGR sends them — including whether the response letter names
   the AI tools again.
4. **Preprint or self-archive** — currently excluded by the journal's terms until publication.
5. **`manuscript/TEMA-SUBMISSION.txt`** — delete or commit (D-16). Currently untracked.
6. **Data link on acceptance** — the portal's data field was withheld for blind review (D-19);
   supply the repository URL (or a DOI) once the paper is accepted.

**Closed since first written:** `docs/venue-options.md` now records the outcome of all three
shortlisted venues, so it no longer announces a decision that was abandoned.

---

## Corrections this record exists to prevent

Three times on this project a confident claim turned out to be fabricated or misremembered. Each is
now pinned:

- **A cited source was fabricated** (pre-`4f5043c`). Fixed by generating `references.bib` from
  Crossref (`scripts/build_bib.py`) so an unresolvable DOI cannot enter the file.
- **TeMA's Scopus ID was invented** as 21100830974 by a search summary, and recorded as
  "unverified" in `docs/venue-options.md`. The real ID is 21101185191. See D-06.
- **TRP was described as a rejection** when it was a self-selected exit that never reached the
  journal. See D-03.

The pattern: a plausible claim, stated confidently, never checked against the thing itself. The
standing remedy is to verify at source and record the instrument.
