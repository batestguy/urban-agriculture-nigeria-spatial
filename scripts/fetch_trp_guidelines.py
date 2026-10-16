#!/usr/bin/env python3
"""fetch_trp_guidelines.py - pull the Town and Regional Planning guidance pages as plain text.

Why this exists: docs/trp-author-guidelines.md is an extraction, and an extraction is only
trustworthy if it can be repeated. This script fetches the journal's own pages and prints the
body text, so the committed guidelines can be re-derived rather than taken on faith. It is the
venue's equivalent of data/raw/provenance.json.

It is a plain GET against the journal's public OJS site. No third-party packages: stdlib only,
so it runs under any interpreter including C:\\Python314. It writes nothing to disk.

Usage:
    python scripts/fetch_trp_guidelines.py                 # all pages
    python scripts/fetch_trp_guidelines.py --page AI       # one page

    --page accepts: abouttrp, accred, submissions, authors, AI, guidepoli, policies,
                    ethics, peerreview, conflicts, copyright

The two agreement PDFs are NOT fetched here; they are documents, not pages. Their public URLs
are recorded in docs/trp-author-guidelines.md and docs/submission-trp.md:

    .../libraryFiles/downloadPublic/115   Author agreement 2026 (PER)
    .../libraryFiles/downloadPublic/56    Publishing agreement (UFS-PER)
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request

BASE = "https://journals.ufs.ac.za/index.php/trp"
UA = "Mozilla/5.0 (compatible; research-metadata-check/1.0)"

PAGES = [
    "abouttrp",      # focus, scope, fees, open access, archiving
    "accred",        # accreditation and indexing  <- the Scopus evidence
    "submissions",   # author guidelines + submission checklist
    "authors",       # "Information for Authors" (portal text)
    "AI",            # AI and generative-AI use policy  <- the declaration constraint
    "guidepoli",     # guidelines-and-policies index
    "policies",      # editorial policies index
    "ethics",        # ethics and malpractice
    "peerreview",
    "conflicts",
    "copyright",
]

# Boilerplate that the OJS theme repeats on every page; trimmed from the tail.
_TAIL_MARKERS = ("Make a Submission", "openaccess")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", errors="replace")


def to_text(markup: str) -> str:
    """Minimal HTML to text: drop script/style, break on block tags, unescape entities."""
    s = re.sub(r"(?is)<script.*?</script>", " ", markup)
    s = re.sub(r"(?is)<style.*?</style>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|li|h[1-6]|tr)>", "\n", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return "\n".join(line.strip() for line in s.splitlines()).strip()


def trim(text: str) -> str:
    """Remove the shared site navigation and footer."""
    i = text.find("Skip to site footer")
    if i != -1:
        text = text[i + len("Skip to site footer"):]
    cut = len(text)
    for marker in _TAIL_MARKERS:
        j = text.rfind(marker)
        if 200 < j < cut:
            cut = j
    return text[:cut].strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Pull the Town and Regional Planning guidance pages as plain text."
    )
    ap.add_argument("--page", action="append", choices=PAGES,
                    help="fetch only this page (repeatable); default is all pages")
    args = ap.parse_args(argv)

    slugs = args.page or PAGES
    failures = 0
    for slug in slugs:
        url = f"{BASE}/{slug}"
        print("=" * 78)
        print(f"# /{slug}   <{url}>")
        print("=" * 78)
        try:
            print(trim(to_text(fetch(url))))
        except Exception as exc:  # noqa: BLE001 - report and continue, this is a probe
            failures += 1
            print(f"FAILED: {exc}")
        print()

    if failures:
        print(f"{failures} page(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
