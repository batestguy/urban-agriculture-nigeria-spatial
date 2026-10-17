"""Build the small preview images the README embeds.

The README has to open fast: the published figures are 300 dpi exports in the
hundreds of kilobytes each, and GitHub serves them at whatever width the page
gives. This script downscales the figures the README uses into
`docs/figures/readme/`, at twice the display width so they stay crisp on
high-density screens.

It reads from `results/figures/` and writes only to `docs/figures/readme/`.
Nothing it produces is an analysis input.

Run:  python scripts/make_readme_figures.py
"""

from pathlib import Path

from PIL import Image  # noqa: F401  (type stub flags LANCZOS; v12.2.0 has it)

# Pillow moved the resampling enums to `Image.Resampling` in 9.1; keep working on
# whichever version is installed.
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "figures"
OUT = ROOT / "docs" / "figures" / "readme"

# (source file, output file, display width in CSS px)
FIGURES = [
    ("summary_panel.png", "summary-panel.png", 1000),
    ("lisa_fdr_map.png", "lisa-fdr.png", 460),
    ("count_model_diagnostics.png", "model-diagnostics.png", 700),
    ("osm_points.png", "osm-points.png", 460),
    ("study_extent.png", "study-extent.png", 460),
    ("climate_honest.png", "climate-honest.png", 700),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for src_name, out_name, width in FIGURES:
        src = SRC / src_name
        if not src.exists():
            raise SystemExit(f"missing source figure: {src}")
        with Image.open(src) as im:
            im = im.convert("RGB")
            target_w = width * 2
            ratio = target_w / im.width
            resized = im.resize(
                (target_w, max(1, round(im.height * ratio))), LANCZOS
            )
            dest = OUT / out_name
            resized.save(dest, "PNG", optimize=True)
            size_kb = dest.stat().st_size / 1024
            total += size_kb
            print(f"{out_name:<24} {resized.width}x{resized.height}  {size_kb:6.0f} KB")
    print(f"\n{len(FIGURES)} files, {total:.0f} KB total -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
