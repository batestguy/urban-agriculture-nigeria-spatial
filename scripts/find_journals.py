"""find_journals.py - candidate venues from the DOAJ API.

DOAJ is an authoritative, queryable registry. It records, per journal: publisher,
APC (amount and currency), licence, peer-review model, and preservation. This script
queries it for journals in the paper's subject areas that charge NO article
processing fee, and prints what the registry actually says.

What this CANNOT tell you
-------------------------
DOAJ does not record Scopus indexing. Scopus status must be checked against the
official Scopus source list, which is updated monthly. Any claim about Scopus
indexing that does not come from that list is a guess.

Run: C:\\Users\\TOSHIBA\\ds-general\\python.exe scripts/find_journals.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://doaj.org/api/search/journals/"

# Subject terms chosen to match the paper: spatial analysis, geographic information,
# urban and land-use planning, agriculture and food security, African regional scope.
# DOAJ's subject vocabulary differs from common usage, so title-based queries are
# more reliable here - subject-term queries returned 0 matches for both
# "Geographic information systems" and "Remote sensing".
#
# Caveat on the APC field: DOAJ records what journals declare. It can be stale or
# unset. Always confirm fees on the journal's own page before submitting.
QUERIES = [
    ('GIS / geospatial in the title, no APC',
     '(bibjson.title:"GIS" OR bibjson.title:"geospatial" OR bibjson.title:"geoinformatics") AND bibjson.apc.has_apc:false'),
    ('Remote sensing / earth observation, no APC',
     '(bibjson.title:"remote sensing" OR bibjson.title:"earth observation") AND bibjson.apc.has_apc:false'),
    ('Urban / regional planning, no APC',
     '(bibjson.title:"urban" OR bibjson.title:"regional") AND bibjson.title:"planning" AND bibjson.apc.has_apc:false'),
    ('Land in the title, no APC',
     'bibjson.title:"land" AND bibjson.apc.has_apc:false'),
    ('Africa in the title, no APC',
     'bibjson.title:"Africa" AND bibjson.apc.has_apc:false'),
    ('Food security / agriculture, no APC',
     '(bibjson.title:"food security" OR bibjson.title:"agriculture") AND bibjson.apc.has_apc:false'),
]


def q(query: str, page_size: int = 20):
    url = BASE + urllib.parse.quote(query, safe='') + f"?pageSize={page_size}"
    req = urllib.request.Request(url, headers={"User-Agent": "urban-agriculture-nigeria-spatial/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def show(res: dict) -> None:
    b = res.get("bibjson", {})
    apc = b.get("apc", {})
    lic = (b.get("license") or [{}])[0].get("type", "?")
    pub = (b.get("publisher") or {}).get("name", "?")
    country = (b.get("publisher") or {}).get("country", "?")
    weeks = b.get("publication_time_weeks", "?")
    issns = ", ".join([b.get("pissn") or "", b.get("eissn") or ""]).strip(", ")
    print(f"    {b.get('title','?')}")
    print(f"      publisher : {pub} ({country})")
    print(f"      ISSN      : {issns or 'n/a'}")
    print(f"      APC       : {'NONE' if not apc.get('has_apc') else apc.get('max')}")
    print(f"      licence   : {lic}  |  review: {(b.get('editorial') or {}).get('review_process')}")
    print(f"      time      : ~{weeks} weeks  |  OA since {b.get('oa_start')}")


def main() -> int:
    for label, query in QUERIES:
        print("=" * 78)
        print(label)
        print("=" * 78)
        try:
            data = q(query)
        except Exception as e:
            print("    FAILED:", type(e).__name__, e); continue
        print(f"    {data.get('total', 0)} journals match\n")
        for res in data.get("results", [])[:10]:
            show(res)
            print()
        time.sleep(0.5)
    print("=" * 78)
    print("DOAJ records APC and licence, NOT Scopus indexing. Verify indexing at")
    print("https://www.scopus.com/sources (or the monthly source-list download).")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
