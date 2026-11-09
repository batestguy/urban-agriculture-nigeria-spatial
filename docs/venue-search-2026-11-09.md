# Venue search — Scopus + no author APC, after TeMA desk rejection

**Compiled 9 November 2026.** Supersedes the shortlist in `docs/venue-options.md`, which is
kept as the historical record of how TeMA was selected.

## 1. Why redo the search at all

On **19 October 2026, 12:04 PM**, TeMA — *Journal of Land Use, Mobility and Environment* —
desk-rejected the manuscript at the gatekeeper stage. Verbatim, from
`redazione.tema@unina.it`, subject `[TeMA] Gatekeeper Decision`:

> "Before starting the revision process, we conduct a preliminary assessment of the submitted
> manuscript to determine its alignment with the journal's objectives and scientific contents.
> We regret to inform you that, following evaluation, your proposal has been deemed **not fully
> aligned with the journal's aims and scopes**."

No reviewer comments exist, because no reviewer saw it. Submitted 18 Oct, decided 19 Oct —
under 24 hours. **Nothing in the letter criticises the data, the method, or the argument.**

This is the third venue outcome in this project and the third non-scientific failure:

| Venue | Outcome | Cause |
|---|---|---|
| AJLP&GS | dropped | not Scopus-indexed |
| Town and Regional Planning | abandoned | AI-disclosure policy conflict |
| TeMA | desk-rejected | editorial scope mismatch |

Every prior selection optimised *eligibility criteria* (Scopus, no APC, AI policy). Editorial
**fit** was the one criterion never tested against evidence. This search tests it.

## 2. A correction to the repository's own record

`docs/venue-options.md` §2 records TeMA's SCImago SID as **21100830974**, flagged as
unverified. It is wrong. Loading `scopus.com/sourceid/21100830974` returns
`?invalidSource=t` — no such source. TeMA's actual Scopus record is
**sourceId 21101185191**, confirmed from Elsevier's serial-title API. The document's warning
that search summaries invent Scopus IDs was correct, and it caught its own example.

## 3. How Scopus was verified this time

**Instrument:** `https://api.elsevier.com/content/serial/title/issn/{ISSN}` — Elsevier's
serial-title endpoint. It returns the same source records that back `scopus.com/sources`,
needs no API key, and answers per-ISSN in one request. This is a substantive advance on the
previous search, which could not verify Scopus at all because `scimagojr.com` and
`scopus.com` were Cloudflare-blocked to the tooling then in use.

**Validation against known controls (all passed):**

- TeMA `1970-9889` → INDEXED, sourceId 21101185191
- Nature `0028-0836` → INDEXED, sourceId 21206
- Town and Regional Planning `1012-280X` → INDEXED, sourceId 21101123414
- AJLP&GS `2657-2664` → HTTP 404, confirming the earlier Scopus rejection

The verifier is `.scratch/scopus_check.py`; promote to `scripts/` if this recurs.

**Limits, stated honestly:**

- `scopus.com/sources` "Download Scopus Source List" is **gated behind a free Scopus account**.
  The API was used instead; it is the same record set.
- **Taylor & Francis and ScienceDirect serve Cloudflare challenges** to automated browsing.
  Their author-guidance pages could not be read directly. Claims about those journals' fees
  below rest on DOAJ, OpenAlex and structural reasoning — not on the publisher's own page.

## 4. The finding that reframes the constraint

The author's requirement is "Scopus-indexed and free". These two are usually compatible, but
the reason is **not** the one the earlier search assumed.

OpenAlex records `apc_usd` for *every* journal, including subscription ones. For a hybrid
Elsevier journal that number is **the price of the optional Open Access route**, not a fee the
author must pay. Land Use Policy shows `apc_usd = $3,830`; an author publishing there through
the subscription route pays **nothing**.

So "free" splits into two genuinely different categories:

- **Fully OA, APC = 0.** Free *and* the article is open to read. Rare among good Scopus
  journals. Africa Spectrum is one.
- **Subscription / hybrid.** Free *to publish*; the article sits behind a paywall unless the
  author elects OA and pays. This is the normal case for the best-fitting journals, and it
  satisfies "no cost to me".

The earlier search used DOAJ's `has_apc:false` filter, which **can only ever return fully-OA
journals**. That filter structurally excluded every subscription journal — including the ones
that fit this paper best. That is why the shortlist kept producing journals that were free but
editors would not want the paper.

## 5. Nigerian venues — the honest answer

The author asked for Nigerian journals to be considered. They were checked, and the result is
unwelcome but clear.

**Nigerian journals in DOAJ (68 total).** Of these, only **3 have no APC**:

- Ilorin Journal of Economic Policy — `2449-0512` — CC BY
- Journal of Sustainable Development Law and Policy — `2467-8406` — CC BY-NC-ND
- The Proceedings of the Nigerian Academy of Science — `0794-7976` — CC BY-NC-ND

**Scopus status of 14 plausible Nigerian titles checked: 3 indexed.**

- Nigerian Journal of Technology — `0331-8443` — **INDEXED**
- Journal of Agricultural Extension — `1119-944X` — **INDEXED**
- Journal of the Nigerian Society of Physical Sciences — `2714-2817` — **INDEXED**
- Not found: Nigerian Agricultural Journal, Nigerian Journal of Soil Science, Arid Zone Journal
  of Engineering, J. Applied Sciences & Environmental Management, Nigerian Journal of
  Geography and Environment, Annals of the Social Science Academy of Nigeria, Savanna, Journal
  of Environmental Design, and four others.

**Intersection of the three constraints is empty.** The three Scopus-indexed Nigerian titles
are in technology, agricultural extension and physical sciences — none is a venue for a
spatial-analysis paper on urban agriculture. The three APC-free Nigerian titles are in
economics, law and general science.

Nigerian venue representation would have to come from the *authorship*, not the publisher. That
is already true — the author is at ATBU Bauchi — and it is a genuine strength with every
international journal below.

## 6. Verified candidate table

Two cohorts. Scopus verified by API on 9 Nov 2026 unless marked.

### Cohort A — fit-first, free to publish via subscription route

| Journal | ISSN | Scopus | Cost to author | Fit evidence |
|---|---|---|---|---|
| **African Geographical Review** | 1937-6812 | YES | free (subscription) | 8.5% Nigeria, 11.5% spatial; publishes *urban cropland mapping* |
| **Land Use Policy** | 0264-8377 | YES | free (subscription) | **62 hits** on OSM/land-use/Africa — dominant |
| Applied Geography | 0143-6228 | YES | free (subscription) | 27% spatial, 3% Africa |
| Habitat International | 0197-3975 | YES | free (subscription) | peri-urban agriculture coverage |
| GeoJournal | 0343-2521 | YES | free (subscription) | 27% spatial, 11.5% Africa, 3% Nigeria |
| Applied Spatial Analysis and Policy | 1874-463X | YES | free (subscription) | 35.5% spatial — highest methods density |

### Cohort B — fully OA, APC = 0, Scopus-indexed

| Journal | ISSN | Scopus | APC | Fit |
|---|---|---|---|---|
| Africa Spectrum | 0002-0397 | YES | **0** (CC BY, DOAJ) | Africa 64.5%, Nigeria 9.5% — but social science, 0% urban ag |
| Modern Africa | 2336-3274 | YES | 0 (DOAJ) | Africa studies, weak spatial |
| Journal of Central European Agriculture | 1332-9049 | YES | 0 (DOAJ) | wrong region |
| Bijdragen tot de Taal-, Land- en Volkenkunde | 0006-2294 | YES | 0 (DOAJ) | Southeast Asia focus |

### Cohort C — checked and rejected

Journal of Land Use Science — Scopus YES but **DOAJ records APC $2,195**: not free.
Urban Science — Scopus YES, APC $1,930. Land — $3,137. Frontiers in Sustainable Cities —
$1,418. Journal of Urban Management — $1,200. All fail the free test.
Frontiers of Urban and Rural Planning — **not in Scopus** (404), as `venue-options.md`
predicted. International Journal of Environment and Geoinformatics, Journal of Geospatial
Surveying, GIS Odyssey, Geoinformatics FCE CTU, Journal of Urban and Landscape Planning — all
404, so the entire no-APC GIS cohort fails the Scopus gate.

## 7. Recommendation

**First choice: African Geographical Review** (Taylor & Francis, `1937-6812`).

The evidence is a direct match rather than an inference from a scope statement. A recent
article in it is *"Auditing the spatial and temporal changes in urban cropland in Harare
metropolitan Province"* — an urban-cropland spatial analysis in an African city, which is this
paper's subject. Another recent article maps urban heat across Sub-Saharan African cities.
17 of its last 200 items concern Nigeria. It is subscription, so publishing costs nothing.
Its 2-year mean citation rate is modest (~2.6), which is the trade for fit.

**Second choice: Land Use Policy** (Elsevier, `0264-8377`).

The topical home. 62 of the last 100 Crossref results for OpenStreetMap-based land-use work in
Africa are in this journal, and it recently published *"Urban agriculture as a land-use policy
instrument for protecting peri-urban agricultural land"*. Higher prestige, harder review, free
via the subscription route.

**Cheapest true-OA option: Africa Spectrum** — genuinely $0 APC and Scopus-indexed, but a
social-science journal that has published nothing on urban agriculture. Likely to repeat the
TeMA outcome.

## 8. What is not yet verified

- **Taylor & Francis and Elsevier author-guidance pages could not be read** — Cloudflare.
  Confirm on the journal page: no submission fee, no page charges on the subscription route,
  and the journal's own AI policy.
- **AI policies were not read per-journal.** Publisher-level policy at T&F, Elsevier, Springer
  and SAGE is the near-universal *permit with disclosure* form (see `docs/venue-options.md`),
  which is materially more permissive than TRP's "language editing only" clause that forced
  the venue change. But the specific clause must be read before submitting, because that is
  precisely the mistake that ended the TRP attempt.
- **No live fit-test against a specific editor's interests.** The Crossref sampling shows what
  each journal *has published*. It does not predict one editor's desk decision — which is what
  TeMA just demonstrated.

## 9. Reproducing this

```bash
# Scopus status for any ISSN (keyless)
python .scratch/scopus_check.py 1937-6812 0264-8377

# DOAJ no-APC listing (existing script)
C:\Users\TOSHIBA\ds-general\python.exe scripts/find_journals.py

# Nigerian venues
python .scratch/ng_all.py
python .scratch/ng_scopus.py

# Editorial fit via Crossref sampling
python .scratch/fit_check.py
python .scratch/topic_journals.py

# APC / OA status via OpenAlex
python .scratch/openalex_venues.py
```
