"""Remove preview images from docs/figures/readme/ that nothing embeds.

An image in a repository README is a claim that it is on the page. A leftover
one is worse than none: it implies a figure the README no longer shows.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
FIGDIR = ROOT / "docs" / "figures" / "readme"

referenced = set(re.findall(r"docs/figures/readme/([\w.-]+\.png)", README))
removed = []
for png in sorted(FIGDIR.glob("*.png")):
    if png.name not in referenced:
        png.unlink()
        removed.append(png.name)

for name in sorted(referenced - {p.name for p in FIGDIR.glob("*.png")}):
    print(f"[MISSING] the README embeds {name}, which is not in {FIGDIR}")
print("removed:", ", ".join(removed) if removed else "nothing")
print("referenced:", len(referenced))
