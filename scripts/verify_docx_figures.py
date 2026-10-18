"""verify_docx_figures.py - every figure in the source must be placed in the DOCX.

Why this exists
---------------
The R gates check that figure FILES exist in results/figures/ and that their pixels match
their generators. None of them ever opened the rendered Word file to ask whether the
figures were actually placed in it. On 2026-10-18 that gap produced a false alarm: a stale
DOCX carried six media files but only one drawing, and the manuscript was reported as
missing five of its six figures. The document was fine; the check was absent.

This closes the gap. It reads manuscript/manuscript.qmd, finds every figure it declares
(both `![...](path){#id}` markdown images and `fig.cap=` chunk options), and asserts that:

  1. the DOCX contains at least as many placed images (a:blip / r:embed) as the source
     declares,
  2. no image is an orphan - every word/media file is referenced by a drawing,
  3. every figure caption appears in the document text.

Exit status is non-zero on any failure, and it names what is missing.

Usage
-----
    python scripts/verify_docx_figures.py
    python scripts/verify_docx_figures.py --docx manuscript/manuscript-anonymised.docx

Requires the rendered DOCX on disk. Run it after rendering and after
scripts/fix_docx_trp.py, which rewrites the file.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QMD = ROOT / "manuscript" / "manuscript.qmd"
DEFAULT_DOCX = ROOT / "manuscript" / "manuscript.docx"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
A_BLIP = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"


def declared_figures() -> list[tuple[str, str]]:
    """Return (id_or_chunk, caption) for every figure the source declares."""
    src = QMD.read_text(encoding="utf-8")
    out: list[tuple[str, str]] = []

    # Markdown images with an identifier:  ![Caption](path){#fig-id}
    for m in re.finditer(r"^!\[([^\]]+)\]\(([^)]+)\)(?:\{([^}]*)\})?", src, re.M):
        caption, _path, attrs = m.group(1), m.group(2), m.group(3) or ""
        ident = ""
        idm = re.search(r"#(fig-[\w-]+)", attrs)
        if idm:
            ident = idm.group(1)
        out.append((ident or caption[:40], caption))

    # Chunk figures: fig.cap="..." inside a ```{r chunk, ...} header
    for m in re.finditer(r"^```\{r[^}]*?fig\.cap\s*=\s*\"([^\"]+)\"[^}]*\}", src, re.M):
        out.append(("chunk-fig", m.group(1)))

    return out


def normalise(s: str) -> str:
    """Fold the characters pandoc/Word substitute, so caption matching is on words."""
    return (
        s.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u00a0", " ")
        .replace("\u2009", " ")
    )


def docx_text_and_images(path: Path) -> tuple[str, list[str], list[str]]:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
    text = "\n".join(
        "".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p")
    )
    # Only blips that actually carry an embed id count as placed images.
    placed = [b.get(R_EMBED) for b in root.iter(A_BLIP)]
    placed = [p for p in placed if p]
    return text, placed, media


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", default=str(DEFAULT_DOCX))
    args = ap.parse_args()

    docx = Path(args.docx)
    if not docx.exists():
        print(f"FAIL: {docx} not found. Render first:\n"
              f"  quarto render manuscript/manuscript.qmd --to docx\n"
              f"  python scripts/fix_docx_trp.py --anonymise")
        return 2

    figs = declared_figures()
    if not figs:
        print("FAIL: no figures found in the source; the parser is wrong, not the document")
        return 2

    text, placed, media = docx_text_and_images(docx)
    flat = normalise(text)
    flat_words = re.sub(r"\s+", " ", flat)

    failures: list[str] = []

    print(f"=== {docx.name} ===")
    print(f"figures declared in source : {len(figs)}")
    print(f"images placed in document  : {len(placed)}")
    print(f"media files in package     : {len(media)}")

    if len(placed) < len(figs):
        failures.append(f"only {len(placed)} of {len(figs)} declared figures are placed")
        print(f"  [FAIL] placed images ({len(placed)}) < declared figures ({len(figs)})")
    else:
        print(f"  [OK]   every declared figure has a placed image")

    # Orphan media: an image in the package that no drawing points at.
    rel_names = set()
    with zipfile.ZipFile(docx) as z:
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', rels):
        rel_names.add(m.group(1))
    orphans = rel_names - set(placed)
    if orphans:
        failures.append(f"{len(orphans)} orphaned image(s) never referenced by a drawing")
        print(f"  [FAIL] orphaned media: {sorted(orphans)}")
    else:
        print("  [OK]   no orphaned media")

    # Captions
    print()
    print("figure captions:")
    for ident, cap in figs:
        probe = re.sub(r"\s+", " ", normalise(cap).strip())
        # Match on the first sentence-fragment; Word may reflow or truncate later words.
        probe = probe.split(". ")[0][:70].strip()
        ok = probe in flat_words
        print(f"  [{'OK' if ok else 'FAIL'}] {ident}: {probe[:64]}")
        if not ok:
            failures.append(f"caption missing from document: {probe[:60]}")

    print()
    if failures:
        print(f"{len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"DOCX FIGURES: all {len(figs)} figures placed, captions present, no orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
