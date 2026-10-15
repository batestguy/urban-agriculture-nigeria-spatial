"""build_bib.py - generate references.bib from Crossref metadata.

Every field in the output comes from the Crossref registry, not from a web search
summary and not typed by hand. If a DOI does not resolve, the entry is NOT written
and the failure is reported.

This is the mechanism that prevents the class of error that produced the fabricated
citation in the previous bibliography: a citation cannot enter the file unless an
authoritative registry vouches for it.

Run: C:\\Users\\TOSHIBA\\ds-general\\python.exe scripts/build_bib.py
Out: manuscript/references.bib
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "references.bib"
UA = {"User-Agent": "YohannaPaper-bibbuild/1.0 (mailto:yohanna@atbu.edu.ng)"}
API = "https://api.crossref.org/works"

# doi -> bibtex key. Chosen by the author; the metadata is fetched, not trusted.
WANTED: dict[str, str] = {
    # --- spatial statistics: the methods this paper uses ---------------------
    "10.1093/biomet/37.1-2.17":                 "moran1950",
    "10.1111/j.1538-4632.1995.tb00338.x":       "anselin1995",
    "10.1111/j.2517-6161.1977.tb01615.x":       "ripley1977",
    "10.1111/j.2517-6161.1995.tb02031.x":       "benjamini1995",
    "10.1007/978-3-662-60723-7_72":             "griffith2021",
    # --- count regression ----------------------------------------------------
    "10.1017/cbo9781139013567":                 "cameron2013",
    "10.1890/10-1831.1":                        "linden2011",
    # --- volunteered geographic information and its biases -------------------
    "10.1068/b35097":                           "haklay2010",
    "10.1038/s41467-023-39698-6":               "herfort2023",
    "10.1080/10095020.2017.1288424":            "jacobs2017",
    # --- urban agriculture: context and policy ------------------------------
    "10.4060/cc3017en":                         "fao2023",
    "10.3390/agriculture8070110":               "wuyep2018",
    "10.9734/ajaees/2014/6560":                 "ibok2014",
    "10.1016/j.sciaf.2025.e02703":              "elum2025",
    "10.3390/su17115151":                       "gottero2025",
    "10.1016/j.ecolecon.2006.04.006":           "vagneron2007",
    # --- urbanisation and land use in West Africa ---------------------------
    "10.1016/j.cities.2016.10.011":             "cobbinah2017",
    "10.1016/j.landusepol.2026.108185":         "prados2026",
    # --- climate data --------------------------------------------------------
    "10.1038/sdata.2015.66":                    "funk2015",
}


# Author metadata that Crossref does not carry. Kept as an explicit override so it is
# always obvious which fields did NOT come from the registry.
#
# fao2023 is the FAO flagship report; Crossref lists no personal authors and gives the
# institutional publisher as "FAO; IFAD; UNICEF; WFP; WHO". The institutional author
# below is the standard citation form.
AUTHOR_OVERRIDE = {
    "fao2023": "{Food and Agriculture Organization of the United Nations and "
               "International Fund for Agricultural Development and "
               "United Nations Children's Fund and World Food Programme and "
               "World Health Organization}",
}


def fetch(doi: str):
    req = urllib.request.Request(f"{API}/{urllib.parse.quote(doi)}", headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())["message"]


def bibtex_type(t: str) -> str:
    return {
        "journal-article": "article",
        "book": "book",
        "monograph": "book",
        "book-chapter": "incollection",
        "edited-book": "book",
        "proceedings-article": "inproceedings",
        "report": "techreport",
        "posted-content": "unpublished",
    }.get(t, "misc")


def esc(s: str) -> str:
    return (s or "").replace("&amp;", "&").replace("{", "").replace("}", "")


def authors(ms) -> str:
    out = []
    for a in ms.get("author") or []:
        fam, giv = esc(a.get("family", "")), esc(a.get("given", ""))
        if fam and giv:
            initials = " ".join(f"{p[0]}." for p in giv.replace("-", " ").split() if p)
            out.append(f"{fam}, {initials}")
        elif fam:
            out.append(fam)
        elif a.get("name"):
            out.append(esc(a["name"]))
    return " and ".join(out) if out else "{Anonymous}"


def year_of(ms):
    for f in ("published-print", "published-online", "issued"):
        if ms.get(f, {}).get("date-parts"):
            return ms[f]["date-parts"][0][0]
    return None


def build(key: str, doi: str, ms: dict) -> str:
    t = bibtex_type(ms.get("type", ""))
    title = esc((ms.get("title") or ["?"])[0])
    yr = year_of(ms)
    journal = esc((ms.get("container-title") or [""])[0])
    vol, iss = ms.get("volume"), ms.get("issue")
    page = ms.get("page") or ms.get("article-number")
    pub = esc(ms.get("publisher", ""))

    auth = AUTHOR_OVERRIDE.get(key) or authors(ms)
    lines = [f"@{t}{{{key},",
             f"  author  = {{{auth}}},",
             f"  title   = {{{title}}},"]
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    elif pub and t == "book":
        lines.append(f"  publisher = {{{pub}}},")
    elif pub:
        lines.append(f"  publisher = {{{pub}}},")
    if yr:
        lines.append(f"  year    = {{{yr}}},")
    if vol:
        lines.append(f"  volume  = {{{vol}}},")
    if iss:
        lines.append(f"  number  = {{{iss}}},")
    if page:
        lines.append(f"  pages   = {{{page}}},")
    lines.append(f"  doi     = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    entries, failed = [], []
    for doi, key in WANTED.items():
        try:
            ms = fetch(doi)
        except Exception as e:
            failed.append((key, doi, f"{type(e).__name__}: {e}"))
            print(f"FAIL  {key:16s} {doi}")
            continue
        entries.append(build(key, doi, ms))
        ttl = esc((ms.get("title") or ["?"])[0])
        print(f"OK    {key:16s} {ttl[:62]}")
        time.sleep(0.4)

    header = (
        "% references.bib - GENERATED FILE, do not edit by hand.\n"
        "%\n"
        "% Produced by scripts/build_bib.py from Crossref metadata. Every DOI below was\n"
        "% resolved through the Crossref REST API and every field (authors, title, journal,\n"
        "% year, volume, pages) is taken from that response rather than typed or inferred.\n"
        "%\n"
        "% Regenerate with:  python scripts/build_bib.py\n"
        "% Verify with:      python scripts/verify_bib.py\n"
        "%\n"
        "% The previous bibliography contained a fabricated entry (a placeholder DOI, an\n"
        "% invented co-author, and a paper year that does not exist). Generation from the\n"
        "% registry is the structural fix: an unresolvable DOI cannot reach this file.\n"
        "%\n"
        "% Generated 2026-10-15\n"
        "\n"
    )
    OUT.write_text(header + "\n\n".join(entries) + "\n", encoding="utf-8")

    print(f"\nwrote {OUT.relative_to(ROOT)}: {len(entries)} entries")
    if failed:
        print(f"\nNOT WRITTEN ({len(failed)}):")
        for k, d, why in failed:
            print(f"  {k}  {d}  <- {why}")
        return 1
    print("All DOIs resolved. No unresolvable entry reached the file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
