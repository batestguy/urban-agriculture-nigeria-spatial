"""find_references.py - build a citation base from Crossref, not from search summaries.

WHY THIS EXISTS
---------------
A fabricated citation reached the previous manuscript because a plausible-looking
reference was never checked against an authoritative record. Web-search summaries
describe papers in prose and can be wrong in ways that are hard to detect; one such
summary supplied a DOI that resolved to an entirely different article.

Crossref is the authoritative registry. This script therefore does two things:

  1. SEARCH: for each topic the manuscript needs, ask Crossref for real records and
     print their actual metadata. Nothing is paraphrased.
  2. RESOLVE: take a list of candidate DOIs and print exactly what they are, so a
     citation can be confirmed or rejected before it is written into a .bib file.

Output is for human review. This script does not write references.bib - a person
decides what to keep, then the .bib is generated from the verified metadata.

Run: C:\\Users\\TOSHIBA\\ds-general\\python.exe scripts/find_references.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = {"User-Agent": "YohannaPaper-refbuild/1.0 (mailto:jzbannister@atbu.edu.ng)"}
API = "https://api.crossref.org/works"

# ---------------------------------------------------------------------------
# 1. Topic searches. Crossref ranks by relevance; we print what actually exists.
# ---------------------------------------------------------------------------
TOPICS = [
    "controlling the false discovery rate practical powerful approach multiple testing",
    "local indicators of spatial association LISA",
    "notes on continuous stochastic phenomena Moran",
    "modelling spatial patterns Ripley",
    "how good is volunteered geographical information OpenStreetMap Ordnance Survey",
    "completeness inequalities global urban building data OpenStreetMap",
    "climate hazards infrared precipitation with stations CHIRPS",
    "urban agriculture Nigeria food security city",
    "urban and peri-urban agriculture profitability sustainability FAO",
    "regression analysis of count data Cameron Trivedi",
    "spatial point patterns methodology applications R",
]

# ---------------------------------------------------------------------------
# 2. Candidate DOIs to resolve. These are CLAIMS until Crossref confirms them.
# ---------------------------------------------------------------------------
DOI_CANDIDATES = [
    "10.1093/biomet/37.1-2.17",                     # Moran 1950?
    "10.1111/j.1538-4632.1995.tb00338.x",           # Anselin 1995?
    "10.1111/j.2517-6161.1995.tb02031.x",           # Benjamini & Hochberg 1995?
    "10.1111/j.2517-6161.1977.tb01615.x",           # Ripley 1977?
    "10.1068/b35097",                               # Haklay 2010?
    "10.1038/s41467-023-39698-6",                   # Zhang et al 2023?
    "10.1038/sdata.2015.66",                        # Funk et al 2015?
    "10.1017/CBO9781139013567",                     # Cameron & Trivedi 2013?
    "10.4060/cc3017en",                             # FAO SOFI 2023?
    "10.1080/19376812.2022.2041054",                # Ogundele Lagos UA? (claimed)
    "10.1016/j.landusepol.2025.107278",             # issifu 2025? (404 before)
    "10.1007/s43615-022-00183-5",                   # sekabira 2022? (404 before)
]


def _get(url: str, timeout: int = 40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def meta(m: dict) -> dict:
    year = None
    for f in ("published-print", "published-online", "issued"):
        if m.get(f, {}).get("date-parts"):
            year = m[f]["date-parts"][0][0]
            break
    return {
        "doi": m.get("DOI"),
        "title": (m.get("title") or ["?"])[0],
        "authors": [f"{a.get('family','')}, {a.get('given','')[:1]}." for a in (m.get("author") or [])[:4]],
        "year": year,
        "journal": (m.get("container-title") or ["?"])[0],
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "page": m.get("page") or m.get("article-number"),
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    }


def show(d: dict, indent: str = "    ") -> None:
    print(f"{indent}DOI     : {d['doi']}")
    print(f"{indent}Title   : {d['title'][:88]}")
    print(f"{indent}Authors : {'; '.join(d['authors']) if d['authors'] else '(none listed)'}")
    print(f"{indent}Source  : {d['journal'][:60]}  ({d['year']})  "
          f"vol {d['volume']} iss {d['issue']} p{d['page']}")
    print(f"{indent}Type    : {d['type']}  |  {str(d['publisher'])[:40]}")


def main() -> int:
    print("#" * 78)
    print("# PART 1 - TOPIC SEARCHES: what actually exists for each topic")
    print("#" * 78)
    for topic in TOPICS:
        print(f"\n=== {topic[:70]}")
        url = f"{API}?rows=3&select=DOI,title,author,container-title,volume,issue,page,issued,published-print,published-online,type,publisher&query.bibliographic=" + urllib.parse.quote(topic)
        try:
            items = _get(url)["message"]["items"]
        except Exception as e:
            print(f"    FAILED: {type(e).__name__} {e}")
            continue
        if not items:
            print("    (no results)")
        for m in items:
            show(meta(m), indent="    ")
            print()
        time.sleep(0.5)

    print("\n" + "#" * 78)
    print("# PART 2 - CANDIDATE DOIs: confirm or reject before citing")
    print("#" * 78)
    ok, bad = 0, 0
    for doi in DOI_CANDIDATES:
        print(f"\n=== {doi}")
        try:
            m = _get(f"{API}/{urllib.parse.quote(doi)}")["message"]
            show(meta(m))
            ok += 1
        except Exception as e:
            print(f"    DOES NOT RESOLVE: {type(e).__name__} {e}")
            bad += 1
        time.sleep(0.5)

    print(f"\n{'=' * 78}")
    print(f"{ok} DOI(s) resolved, {bad} did not. Only resolved DOIs may be cited.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
