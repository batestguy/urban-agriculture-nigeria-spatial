"""Remove the author's identity from every file reviewers see, and prove it is gone.

Why this exists (docs/decisions.md D-17, D-18)
----------------------------------------------
On 10 Nov 2026 African Geographical Review returned submission 260528906 unreviewed: the
author's name was found in the anonymous file. The body text was clean -- `fix_docx_trp.py
--anonymise` strips the byline and checks `word/document.xml` -- but the name survived in
`docProps/core.xml` (the "Author" field Word shows under File > Info) and the affiliation in
`docProps/custom.xml`. The supplementary file, also uploaded "for review", carried the name in
its body and its properties. The earlier check only ever looked at one part of one file.

This script therefore scans EVERY part of each review file, not just the document body.

Usage
-----
    python scripts/scrub_review_copies.py           # scrub, then verify
    python scripts/scrub_review_copies.py --check   # verify only; exit 1 on any hit

Rebuild order (see AGENTS.md):
    quarto render manuscript.qmd -> quarto render supplementary.qmd
    -> python scripts/fix_docx_trp.py --anonymise
    -> python scripts/scrub_review_copies.py
    -> python scripts/normalize_docx_meta.py
    -> python scripts/scrub_review_copies.py --check
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "manuscript"

# The files that go to reviewers. The NAMED manuscript.docx is deliberately absent.
REVIEW_FILES = [MS / "manuscript-anonymised.docx", MS / "supplementary.docx"]

PARA = r"<w:p[ >].*?</w:p>"


def front_matter() -> dict[str, str]:
    qmd = (MS / "manuscript.qmd").read_text(encoding="utf-8")
    block = qmd.split("---", 2)[1]
    out: dict[str, str] = {}
    for line in block.splitlines():
        s = line.strip().lstrip("-").strip()
        for key in ("author-affiliation", "name", "email", "orcid"):
            if s.startswith(key + ":") and key not in out:
                out[key] = s.split(":", 1)[1].strip().strip("\"'")
    return out


def needles() -> list[str]:
    fm = front_matter()
    name = fm.get("name", "")
    found = [fm.get(k, "") for k in ("name", "email", "author-affiliation", "orcid")]
    # Each name part on its own: "Bannister" alone identifies the author.
    found += [p for p in name.split() if len(p) > 3]
    # The institution, but NOT "Tafawa Balewa" alone: that is also a Bauchi LGA name and may
    # legitimately appear in the data.
    found += ["Abubakar Tafawa Balewa University", "ATBU", "atbu.edu.ng"]
    out = sorted({n for n in found if n}, key=len, reverse=True)
    if not name or not out:
        raise SystemExit("FAIL: could not read the author identity from manuscript.qmd")
    return out


def hits(path: pathlib.Path, ns: list[str]) -> list[str]:
    report = []
    with zipfile.ZipFile(path) as z:
        for part in z.namelist():
            text = z.read(part).decode("utf-8", errors="replace")
            for n in ns:
                flags = 0 if n == "ATBU" else re.I
                if re.search(re.escape(n), text, flags):
                    report.append(f"{path.name}: {part}: '{n}'")
    return report


def scrub_core(xml: str) -> str:
    for tag in ("dc:creator", "cp:lastModifiedBy"):
        xml = re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}></{tag}>", xml, flags=re.S)
    return xml


def scrub_custom(xml: str, ns: list[str]) -> str:
    def drop(m: re.Match) -> str:
        prop = m.group(0)
        name = re.search(r'name="([^"]*)"', prop)
        key = name.group(1).lower() if name else ""
        if key.startswith("author") or key in ("email", "orcid") or any(
                n.lower() in prop.lower() for n in ns):
            return ""
        return prop
    xml = re.sub(r"<property\b.*?</property>", drop, xml, flags=re.S)
    # pids must stay unique; they need not be contiguous.
    return xml


def scrub_body(xml: str, ns: list[str]) -> tuple[str, int]:
    removed = 0

    def strip(m: re.Match) -> str:
        nonlocal removed
        text = re.sub(r"<[^>]+>", "", m.group(0))
        if any(n.lower() in text.lower() for n in ns if n != "ATBU") or "ATBU" in text:
            removed += 1
            return ""
        return m.group(0)
    return re.sub(PARA, strip, xml, flags=re.S), removed


def rewrite(path: pathlib.Path, ns: list[str]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    changed: list[str] = []
    try:
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                text = None
                if item.filename == "docProps/core.xml":
                    text = scrub_core(data.decode("utf-8"))
                elif item.filename == "docProps/custom.xml":
                    text = scrub_custom(data.decode("utf-8"), ns)
                elif item.filename == "word/document.xml":
                    text, n = scrub_body(data.decode("utf-8"), ns)
                    if n:
                        changed.append(f"{n} body paragraph(s)")
                if text is not None and text.encode("utf-8") != data:
                    if item.filename != "word/document.xml":
                        changed.append(item.filename)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
        with zipfile.ZipFile(tmp) as check:
            if check.testzip() is not None or not check.namelist():
                raise zipfile.BadZipFile("archive failed to verify after rewrite")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"scrubbed {path.name}: {', '.join(changed) if changed else 'nothing to remove'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; do not modify")
    args = ap.parse_args()
    ns = needles()

    missing = [p for p in REVIEW_FILES if not p.exists()]
    if missing:
        print("FAIL: missing " + ", ".join(p.name for p in missing))
        return 1
    if not args.check:
        for p in REVIEW_FILES:
            rewrite(p, ns)

    problems = [h for p in REVIEW_FILES for h in hits(p, ns)]
    if problems:
        print(f"FAIL: {len(problems)} identity hit(s) in review files:")
        for h in problems:
            print("  " + h)
        return 1
    print(f"PASS: {len(REVIEW_FILES)} review files, every part scanned for "
          f"{len(ns)} identity strings, 0 hits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
