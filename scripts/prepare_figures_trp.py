#!/usr/bin/env python3
"""prepare_figures_trp.py - produce the journal-format figures for submission.

Town and Regional Planning asks for figures as TIF or JPEG at 300 dpi, and requires that
diagrams, maps and photos be camera-ready with clear text (docs/trp-author-guidelines.md).

The R pipeline writes PNG at generous pixel sizes (the smallest is 1800x1350, which is 6x4.5
inches at 300 dpi), so the resolution is already sufficient. What the PNGs lack is *embedded*
DPI metadata — a 1800px image with no DPI tag is not a 300 dpi image as far as a typesetter's
software is concerned, it is a 1800-pixel image with unknown scaling. This script reads each
figure, writes a copy with the DPI recorded, and emits both requested formats:

    results/figures/submission/<name>-300dpi.jpg    (quality 95, no chroma loss worth seeing)
    results/figures/submission/<name>-300dpi.tif    (LZW, lossless, for maps with fine lines)

Only the figures the manuscript actually cites are converted. Adding a figure to the paper
means adding it here — the script reads the .qmd to decide, so the two cannot drift.

Requires Pillow. Run:
    python scripts/prepare_figures_trp.py
    python scripts/prepare_figures_trp.py --dpi 300 --format tif
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    from PIL import Image
except ImportError:
    print("FAIL: Pillow is required.  pip install Pillow  (or use the ds-general env)")
    raise SystemExit(1)

ROOT = pathlib.Path(__file__).resolve().parents[1]
QMD = ROOT / "manuscript" / "manuscript.qmd"
FIGDIR = ROOT / "results" / "figures"
OUTDIR = FIGDIR / "submission"


def cited_figures() -> list[str]:
    """Figure filenames the manuscript references, in citation order."""
    text = QMD.read_text(encoding="utf-8")
    seen: list[str] = []
    for name in re.findall(r"results/figures/([A-Za-z0-9_\-]+\.png)", text):
        if name not in seen:
            seen.append(name)
    return seen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--format", choices=("jpg", "tif", "both"), default="both")
    args = ap.parse_args()

    names = cited_figures()
    if not names:
        print("FAIL: no figures found in manuscript.qmd")
        return 1

    OUTDIR.mkdir(parents=True, exist_ok=True)
    print(f"figures cited by the manuscript: {len(names)}")
    print(f"writing to {OUTDIR.relative_to(ROOT)} at {args.dpi} dpi")
    print()

    failures = 0
    for name in names:
        src = FIGDIR / name
        if not src.exists():
            print(f"  [MISS] {name} - the manuscript cites it but results/figures/ has no such file")
            failures += 1
            continue

        im = Image.open(src).convert("RGB")
        w, h = im.size
        inches = (round(w / args.dpi, 2), round(h / args.dpi, 2))
        stem = src.stem

        written = []
        if args.format in ("jpg", "both"):
            dst = OUTDIR / f"{stem}-{args.dpi}dpi.jpg"
            im.save(dst, "JPEG", dpi=(args.dpi, args.dpi), quality=95, optimize=True)
            written.append((dst.name, dst.stat().st_size))
        if args.format in ("tif", "both"):
            dst = OUTDIR / f"{stem}-{args.dpi}dpi.tif"
            im.save(dst, "TIFF", dpi=(args.dpi, args.dpi), compression="tiff_lzw")
            written.append((dst.name, dst.stat().st_size))

        size_note = "  ".join(f"{n} ({s/1024:.0f} KB)" for n, s in written)
        print(f"  [OK]   {name:28s} {w}x{h} px = {inches[0]}x{inches[1]} in   {size_note}")

    print()
    if failures:
        print(f"{failures} figure(s) could not be converted.")
        return 1
    print("All cited figures converted. Both formats embed the DPI, which the source PNGs did not.")
    print("Attach the JPEG for the submission; keep the TIFF if the editor asks for lossless.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
