"""normalize_docx_meta.py - make rendered DOCX files open as Word 2013+ documents.

Why this exists
---------------
Quarto/pandoc writes `compatibilityMode val="14"` (Word 2010) into word/settings.xml,
and the project's reference.docx carries `Application: Microsoft Macintosh Word`,
`AppVersion: 14.0000` in docProps/app.xml. Word therefore opens every rendered
manuscript in [Compatibility Mode]: features are greyed out in the UI and the title
bar carries a banner that looks unpolished next to a submission.

It is not a file-format problem. The container is valid OOXML throughout (verified:
[Content_Types].xml, word/document.xml with the 2006/wordprocessingml namespace, 18
parts). It is purely the declared compatibility level. Setting it to 15 (Word 2013+)
turns the banner off and changes no layout, because the document already uses the
modern feature set pandoc emits.

What it changes
---------------
  word/settings.xml   compatibilityMode 14 -> 15
  docProps/app.xml    Application / AppVersion / Company normalised to this project

Nothing else is touched: styles, fonts, tables, figures and the author block are
byte-identical afterwards, so the format and figure gates stay valid.

Usage
-----
    python scripts/normalize_docx_meta.py                 # all rendered docx
    python scripts/normalize_docx_meta.py --check         # report only, exit 1 if wrong
    python scripts/normalize_docx_meta.py path\\to\\file.docx

Run AFTER scripts/fix_docx_trp.py, which rewrites the docx and would otherwise undo
this pass. It is safe (idempotent) to run more than once.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_MODE = "15"
APP_NAME = "Microsoft Office Word"
APP_VERSION = "16.0000"

DEFAULT_TARGETS = [
    ROOT / "manuscript" / "manuscript.docx",
    ROOT / "manuscript" / "manuscript-anonymised.docx",
    ROOT / "manuscript" / "supplementary.docx",
]

COMPAT_RE = re.compile(
    r'(<w:compatSetting w:name="compatibilityMode"[^>]*?w:val=")(\d+)(")'
)


def _norm_app(xml: str) -> str:
    xml = re.sub(r"<Application>[^<]*</Application>",
                 f"<Application>{APP_NAME}</Application>", xml)
    xml = re.sub(r"<AppVersion>[^<]*</AppVersion>",
                 f"<AppVersion>{APP_VERSION}</AppVersion>", xml)
    if "<Application>" not in xml:
        xml = xml.replace("</Properties>",
                          f"<Application>{APP_NAME}</Application>"
                          f"<AppVersion>{APP_VERSION}</AppVersion></Properties>")
    return xml


def inspect(path: Path) -> tuple[str | None, str | None]:
    with zipfile.ZipFile(path) as z:
        settings = z.read("word/settings.xml").decode("utf-8", "replace")
        app = z.read("docProps/app.xml").decode("utf-8", "replace")
    m = COMPAT_RE.search(settings)
    av = re.search(r"<AppVersion>([^<]*)</AppVersion>", app)
    return (m.group(2) if m else None), (av.group(1) if av else None)


def rewrite(path: Path) -> bool:
    """Rewrite the two metadata parts in place. Returns True if anything changed."""
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
        order = z.namelist()

    settings = parts["word/settings.xml"].decode("utf-8")
    app = parts["docProps/app.xml"].decode("utf-8")

    new_settings = COMPAT_RE.sub(lambda m: m.group(1) + TARGET_MODE + m.group(3), settings)
    new_app = _norm_app(app)

    if new_settings == settings and new_app == app:
        return False

    parts["word/settings.xml"] = new_settings.encode("utf-8")
    parts["docProps/app.xml"] = new_app.encode("utf-8")

    # Write to a sibling temp file, then replace, so a failure cannot truncate
    # the submission document. mkstemp keeps its own handle open on Windows, so
    # close it first and use a plain path.
    fd, tmp = tempfile.mkstemp(suffix=".docx", dir=str(path.parent))
    os.close(fd)
    Path(tmp).unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
            for name in order:
                out.writestr(name, parts[name])
        shutil.move(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return True


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="docx files (default: the rendered set)")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if wrong")
    args = ap.parse_args(argv[1:])

    targets = [Path(p) for p in args.paths] if args.paths else DEFAULT_TARGETS

    bad = 0
    for path in targets:
        if not path.exists():
            print(f"  [SKIP] {path.name} - not present")
            continue
        mode, appver = inspect(path)
        ok = mode == TARGET_MODE
        if args.check:
            mark = "OK  " if ok else "FAIL"
            print(f"  [{mark}] {path.name:32} compatMode={mode} appVersion={appver}")
            if not ok:
                bad += 1
            continue

        changed = rewrite(path)
        mode2, appver2 = inspect(path)
        note = "updated" if changed else "already clean"
        print(f"  [{note:13}] {path.name:32} compatMode={mode2} appVersion={appver2}")
        if mode2 != TARGET_MODE:
            bad += 1

    if args.check:
        print(f"\nCOMPAT MODE: {'all clean' if bad == 0 else f'{bad} file(s) wrong'}")
        return 0 if bad == 0 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
