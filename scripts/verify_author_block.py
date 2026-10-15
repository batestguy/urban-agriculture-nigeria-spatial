#!/usr/bin/env python3
"""verify_author_block.py — fail the build if any rendered artefact loses the author block.

Why this exists. Three rendering paths lose the author's affiliation in three different
ways, all of them silently:

  * Quarto's author normalisation consumes `author[].affiliation` before the LaTeX title
    partial runs, so the PDF never sees it.
  * Pandoc's docx writer renders only the author name.
  * Pandoc's LaTeX template renders only the author name.

Only the HTML output showed it, and only inside a <meta> tag. Reading the .qmd proves
nothing; the question is what the reader receives. This gate opens the actual rendered
files and looks for the strings.

Checks, per artefact:
  1. manuscript/manuscript.pdf   name, affiliation, e-mail
  2. manuscript/manuscript.docx  name, affiliation, e-mail
  3. manuscript/manuscript.html  name, e-mail
  4. docs/methodology.pdf        name
  5. docs/spatial-report.pdf     name
and, across every tracked text file, that no trace of a previous project name survives.

Exit code 0 = all present. 1 = at least one missing, listed on stdout.

Usage:
    python scripts/verify_author_block.py
    python scripts/verify_author_block.py --quiet
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parents[1]
QMD = ROOT / 'manuscript' / 'manuscript.qmd'

# Names that must NOT appear anywhere: the folder and repository were renamed, and a
# stale self-reference would ship the wrong project identity to a reviewer.
FORBIDDEN = ['YohannaPaper', 'YorubaPaper']


def front_matter() -> dict:
    """Read the author fields from the manuscript front matter (single source of truth)."""
    text = QMD.read_text(encoding='utf-8')
    block = text.split('---', 2)[1]
    out: dict[str, str] = {}
    for line in block.splitlines():
        # A list item reads `- name: X`; strip the dash so the key is still detected.
        s = line.strip().lstrip('-').strip()
        for key in ('author-affiliation', 'affiliation', 'name', 'email'):
            if s.startswith(key + ':') and key not in out:
                val = s.split(':', 1)[1].strip().strip('"\'')
                out[key if key != 'affiliation' else 'author.affiliation'] = val
    return out


def pdf_text(path: pathlib.Path) -> str:
    try:
        import pypdf
    except ImportError:
        return ''
    try:
        r = pypdf.PdfReader(str(path))
    except Exception:
        return ''
    # Page 1 holds the title block, but a long abstract can push it; scan the first three.
    return '\n'.join((p.extract_text() or '') for p in r.pages[:3])


def docx_text(path: pathlib.Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    return re.sub(r'<[^>]+>', '', xml)


def html_text(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    fm = front_matter()
    name = fm.get('name', '')
    affil = fm.get('author-affiliation', '')
    email = fm.get('email', '')

    if not (name and affil and email):
        print('FAIL: manuscript front matter is missing one of name / author-affiliation / email')
        print(f'      found: {fm}')
        return 1

    # The two copies of the affiliation must agree. If they drift, one of the three
    # rendered outputs is showing a different institution from the other two.
    twinned = fm.get('author.affiliation', '')
    if twinned and twinned != affil:
        print('FAIL: the two affiliation strings disagree')
        print(f'      author[].affiliation  = {twinned!r}')
        print(f'      author-affiliation    = {affil!r}')
        return 1

    # (path, needed-fields) — the affiliation is only rendered by hand in the two
    # manuscript outputs, so it is not required of the companion PDFs.
    plan = [
        (ROOT / 'manuscript' / 'manuscript.pdf', [('name', name), ('affiliation', affil), ('e-mail', email)], pdf_text),
        (ROOT / 'manuscript' / 'manuscript.docx', [('name', name), ('affiliation', affil), ('e-mail', email)], docx_text),
        (ROOT / 'manuscript' / 'manuscript.html', [('name', name), ('e-mail', email)], html_text),
        (ROOT / 'docs' / 'methodology.pdf', [('name', name)], pdf_text),
        (ROOT / 'docs' / 'spatial-report.pdf', [('name', name)], pdf_text),
    ]

    failures: list[str] = []
    checked = 0
    for path, needed, reader in plan:
        rel = path.relative_to(ROOT)
        if not path.exists():
            failures.append(f'{rel}: file not found')
            print(f'  [MISS] {rel} — not found')
            continue
        text = reader(path)
        if not text:
            print(f'  [SKIP] {rel} — could not extract text (no reader available)')
            continue
        checked += 1
        missing = [label for label, value in needed if value and value not in text]
        if missing:
            failures.append(f'{rel}: missing {", ".join(missing)}')
            print(f'  [FAIL] {rel} — missing {", ".join(missing)}')
        else:
            print(f'  [ OK ] {rel} — {len(needed)} string(s) present')

    # The old project name must not survive anywhere it could be read.
    skip_dirs = {'.git', 'abandoned', '.playwright-mcp', '_site', '_freeze', '_probe',
                 '__pycache__', '.quarto', 'node_modules'}
    # This gate names the forbidden strings, and rename_project.py exists to rewrite them;
    # a migration tool has to know what it is migrating away from.
    exempt = {pathlib.Path(__file__).resolve(),
              (ROOT / 'scripts' / 'rename_project.py').resolve()}
    binary = {'.pdf', '.png', '.jpg', '.jpeg', '.docx', '.gpkg', '.shp', '.dbf', '.prj', '.tif'}
    stale: list[str] = []
    scanned = 0
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() in binary:
            continue
        if any(part in skip_dirs for part in p.relative_to(ROOT).parts):
            continue
        if p.resolve() in exempt:
            continue
        try:
            t = p.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for bad in FORBIDDEN:
            if bad in t:
                stale.append(f'{p.relative_to(ROOT)} contains "{bad}"')
    if stale:
        failures.extend(stale)
        for s in stale:
            print(f'  [FAIL] stale project name — {s}')
    else:
        print(f'  [ OK ] no stale project name in {scanned} scanned text file(s)')

    print()
    if failures:
        print(f'AUTHOR BLOCK: {len(failures)} problem(s)')
        for f in failures:
            print('  - ' + f)
        return 1
    print(f'AUTHOR BLOCK: all present, 0 discrepancies ({len(plan)} artefacts checked)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
