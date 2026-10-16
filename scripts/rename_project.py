#!/usr/bin/env python3
"""rename_project.py - retarget every in-repo identifier at the new project name.

The study is Jerry Zachary Bannister's; the folder and repository previously carried
another person's name. This rewrites the self-references so the project is named after
the work and its author rather than a former collaborator:

    D:\\YohannaPaper                          -> D:\\urban-agriculture-nigeria-spatial
    batestguy/urban-agriculture-and-...-nigeria -> batestguy/urban-agriculture-nigeria-spatial
    User-Agent: YohannaPaper/1.0                -> urban-agriculture-nigeria-spatial/1.0

Deliberately NOT touched:
    data/raw/*.csv          frozen observations; a rename must not edit measured data
    abandoned/              another person's archived work, preserved verbatim
    MR. YOHAN FINAL BINDING.docx   a real filename belonging to its author

Usage:
    python scripts/rename_project.py --dry-run
    python scripts/rename_project.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parents[1]

NEW_SLUG = 'urban-agriculture-nigeria-spatial'
NEW_DIR = 'D:\\' + NEW_SLUG
NEW_URL_SLUG = 'batestguy/' + NEW_SLUG

# Longest first: the repository URL slug must be consumed before the bare folder name,
# or the second rule would leave a mangled `batestguy/urban-agriculture-nigeria-spatial`.
REPLACEMENTS = [
    ('batestguy/urban-agriculture-and-urban-food-security-in-nigeria', NEW_URL_SLUG),
    ('D:\\\\YohannaPaper', NEW_DIR.replace('\\', '\\\\')),   # JSON-escaped form
    ('D:\\YohannaPaper', NEW_DIR),
    ('D:/YohannaPaper', NEW_DIR.replace('\\', '/')),
    ('YohannaPaper', NEW_SLUG),
]

SKIP_DIRS = {'.git', 'abandoned', '.playwright-mcp', '_site', '_freeze',
             'node_modules', '__pycache__', '.quarto', '.Rproj.user'}

# data/ holds frozen measurements; a rename must never rewrite an observed value.
SKIP_SUFFIXES = {'.csv', '.gpkg', '.shp', '.dbf', '.prj', '.tif', '.png', '.jpg',
                 '.jpeg', '.docx', '.pdf', '.bib', '.lock'}

TEXT_SUFFIXES = {'.qmd', '.md', '.R', '.r', '.py', '.yml', '.yaml', '.json', '.ps1',
                 '.bat', '.cff', '.txt', '.Rmd', '.tex', '.typ', '.gitignore'}


def targets():
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.name in SKIP_DIRS:            # bare-dot names such as .gitignore
            continue
        if p.suffix.lower() in SKIP_SUFFIXES:
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.name != '.gitignore':
            continue
        if p.resolve() == pathlib.Path(__file__).resolve():
            continue                        # this script names the old path on purpose
        yield p


def rewrite(path: pathlib.Path, dry: bool) -> int:
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return 0
    new = text
    for old, repl in REPLACEMENTS:
        if old in new:
            new = new.replace(old, repl)
    if new == text:
        return 0
    n = sum(text.count(o) for o, _ in REPLACEMENTS)
    if not dry:
        path.write_text(new, encoding='utf-8', newline='')
    print(f'  {path.relative_to(ROOT)}  ({n} replacement(s))')
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    total = 0
    files = 0
    for p in targets():
        n = rewrite(p, args.dry_run)
        if n:
            files += 1
            total += n
    verb = 'would rewrite' if args.dry_run else 'rewrote'
    print(f'\n{verb} {total} reference(s) across {files} file(s)')

    # Anything left is worth seeing before the folder move. On a dry run this necessarily
    # lists every file, because nothing was written yet.
    if args.dry_run:
        return 0
    leftovers = []
    for p in targets():
        try:
            t = p.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        if 'YohannaPaper' in t:
            leftovers.append(str(p.relative_to(ROOT)))
    if leftovers:
        print('STILL CONTAINING the old name:')
        for f in leftovers:
            print('  ' + f)
    else:
        print('no remaining occurrences in scannable text files')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
