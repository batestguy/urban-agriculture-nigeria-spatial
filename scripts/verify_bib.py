"""verify_bib.py - check every DOI in references.bib against Crossref.

Motivation
----------
references.bib contained a placeholder DOI (10.xxxx/njae2024) and a placeholder
article number (s11524-026-xxxxx). Those were removed on 2026-10-15, but removal
only cleaned the FORM of the file. It did not establish that the remaining
citations exist, or that their volume, pages and co-authors are right.

Sampling four entries by hand found three wrong:
  issifu2025   DOI 10.1016/j.landusepol.2025.107278 -> actual ...107483
  khumalo2024  v16 p1882, authors Mahachi/Mavodza -> actual 16(15) 6482, Ngidi/Ojo
  tambol2025   DOI 10.1038/s41598-024-82813-w p4127 -> actual s41598-025-10858-2, 10858
  ogundele2023 title and pages both wrong (entry since removed as uncited)

So this script checks all of them. For each DOI it queries the Crossref REST API
and compares the returned title, year, volume and page/article number against the
.bib record, reporting any mismatch.

Network: Crossref API only (api.crossref.org). No auth needed.
Run:     python scripts/verify_bib.py [path/to/references.bib]
"""
from __future__ import annotations

import json
import re
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "manuscript" / "references.bib"
API = "https://api.crossref.org/works/"
UA = {"User-Agent": "urban-agriculture-nigeria-spatial-bibcheck/1.0 (mailto:jzbannister@atbu.edu.ng)"}


def entries(text: str) -> list[dict]:
    out = []
    for block in re.split(r"\n(?=@)", text):
        m = re.match(r"@(\w+)\{([^,]+),", block)
        if not m:
            continue
        def field(name: str) -> str | None:
            fm = re.search(rf"(?m)^\s*{name}\s*=\s*\{{(.+?)\}}\s*,?\s*$", block)
            return re.sub(r"\s+", " ", fm.group(1)).strip() if fm else None
        out.append({
            "type": m.group(1), "key": m.group(2), "raw": block,
            "title": field("title"), "year": field("year"),
            "volume": field("volume"), "pages": field("pages"),
            "journal": field("journal"), "doi": field("doi"),
            "author": field("author"), "url": field("url"),
        })
    return out


def crossref(doi: str) -> dict | None:
    try:
        req = urllib.request.Request(API + urllib.parse.quote(doi), headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["message"]
    except Exception:
        return None


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main() -> int:
    if not BIB.exists():
        print("no bib at", BIB); return 1
    ents = entries(BIB.read_text(encoding="utf-8"))
    with_doi = [e for e in ents if e["doi"]]
    without = [e for e in ents if not e["doi"]]

    print(f"{len(ents)} entries: {len(with_doi)} with a DOI, {len(without)} without\n")
    print("=" * 78)
    print("DOI-BEARING ENTRIES - verified against Crossref")
    print("=" * 78)

    bad, unverified = [], []
    for e in with_doi:
        msg = crossref(e["doi"])
        if msg is None:
            unverified.append(e)
            print(f"\n?? {e['key']}: DOI did not resolve -> {e['doi']}")
            continue

        ct = (msg.get("title") or [""])[0]
        cy = None
        for f in ("published-print", "published-online", "issued"):
            if msg.get(f, {}).get("date-parts"):
                cy = msg[f]["date-parts"][0][0]; break
        cv = msg.get("volume")
        cp = msg.get("page") or msg.get("article-number")
        ca = ", ".join(
            f"{a.get('family','')}" for a in (msg.get("author") or [])[:3]
        )

        problems = []
        if e["title"] and norm(e["title"])[:40] not in norm(ct) and norm(ct)[:40] not in norm(e["title"]):
            problems.append(f"title\n      bib : {e['title']}\n      real: {ct}")
        if e["year"] and cy and str(cy) != e["year"]:
            problems.append(f"year bib {e['year']} vs real {cy}")
        if e["volume"] and cv and norm(str(e["volume"])) != norm(str(cv)):
            problems.append(f"volume bib {e['volume']} vs real {cv}")
        if e["pages"] and cp and norm(str(e["pages"])) not in norm(str(cp)) and norm(str(cp)) not in norm(str(e["pages"])):
            problems.append(f"pages bib {e['pages']} vs real {cp}")

        if problems:
            bad.append(e)
            print(f"\nXX {e['key']}  ({e['doi']})")
            for p in problems:
                print(f"     {p}")
            print(f"      real authors: {ca}")
        else:
            print(f"\nOK {e['key']}  ({e['doi']})")
            print(f"     {ct[:70]}")

        time.sleep(0.4)  # be polite to Crossref

    print("\n" + "=" * 78)
    print("ENTRIES WITHOUT A DOI - need manual checking")
    print("=" * 78)
    for e in without:
        kind = "URL only" if e["url"] else "no identifier at all"
        print(f"\n-- {e['key']}  [{e['type']}, {kind}]")
        print(f"     {str(e['title'])[:72]}")
        if e["journal"]:
            print(f"     {e['journal']} vol {e['volume']} p{e['pages']}")

    print("\n" + "=" * 78)
    print(f"SUMMARY: {len(with_doi) - len(bad) - len(unverified)} DOI(s) verified good, "
          f"{len(bad)} wrong, {len(unverified)} unresolvable, {len(without)} without a DOI")
    print("=" * 78)
    return 1 if (bad or unverified) else 0


if __name__ == "__main__":
    raise SystemExit(main())
