#!/usr/bin/env python3
"""fix_docx_ajlpgs.py - enforce the AJLP&GS author-guideline formatting on the manuscript.

Separate from scripts/fix_docx_format.py, which enforces the (now abandoned) conference
spec: Times New Roman 12pt, 1.5 spacing, 1-inch margins. This journal wants something
different, so overwriting that script would lose a working tool.

Per docs/ajlpgs-author-guidelines.md (extracted from the journal's own template):
    Font          Cambria, throughout
    Body          12 pt, justified
    Line spacing  1.2 multiple  -> w:line = 288 (240 * 1.2)
    Margins       top 2 cm, bottom 1.5 cm, left 1.5 cm, right 1.5 cm
                  (Word stores twips: 1 cm = 567 twips)
    Abstract      Cambria 10 pt, single spaced
    Table text    Cambria 10 pt, interline 1.2, no space before or after

The journal also requires the submitted file to be ANONYMISED (author names and
affiliations removed from the first page). That is produced separately, not here:
this script always writes the NAMED version, so the two cannot be confused.

Run: python scripts/fix_docx_ajlpgs.py
"""
from __future__ import annotations

import pathlib
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / 'manuscript' / 'manuscript.docx'

FONT = 'Cambria'
CM = 567          # twips per cm
LINE_12 = 288     # 240 * 1.2

MARGINS = dict(top=2 * CM, bottom=int(1.5 * CM), left=int(1.5 * CM), right=int(1.5 * CM))


def patch_rfonts(xml: str, font: str = FONT) -> str:
    """Replace any theme-based font reference with an explicit one."""
    repl = (f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" '
            f'w:eastAsia="{font}" />')
    xml = re.sub(r'<w:rFonts[^>]*?(?:Theme|theme)[^>]*?/>', repl, xml)
    xml = re.sub(r'<w:rFonts[^>]*?/>',
                 lambda m: m.group(0) if font in m.group(0) else repl, xml)
    return xml


# ---------------------------------------------------------------------------
# Inject the author's affiliation and e-mail into the Word file.
#
# Pandoc's docx template renders ONLY the author name and silently drops the
# affiliation and e-mail; Quarto's author normalisation makes the affiliation
# unavailable to the template at all. The journal's author block requires all
# three, so the source alone cannot produce a compliant Word file. The missing
# lines are appended to the paragraph that holds the author's name.
#
# The three strings are READ FROM THE MANUSCRIPT FRONT MATTER rather than repeated
# here, so the paper and the Word file cannot drift apart. E-mail
# is read from `author[].email`, the affiliation from the top-level
# `author-affiliation` key (see the note beside it in manuscript.qmd).
# scripts/verify_author_block.py re-checks the rendered file.
# ---------------------------------------------------------------------------
QMD = ROOT / 'manuscript' / 'manuscript.qmd'


def _front_matter() -> dict:
    """Minimal YAML reader for the four author fields; avoids a PyYAML dependency."""
    text = QMD.read_text(encoding='utf-8')
    block = text.split('---', 2)[1]
    out = {}
    for key in ('author-affiliation',):
        for line in block.splitlines():
            s = line.strip()
            if s.startswith(key + ':'):
                out[key] = s.split(':', 1)[1].strip().strip('"\'')
    for line in block.splitlines():
        s = line.strip()
        if s.startswith('name:') and 'AUTHOR_NAME' not in out:
            out['name'] = s.split(':', 1)[1].strip().strip('"\'')
        if s.startswith('email:') and 'email' not in out:
            out['email'] = s.split(':', 1)[1].strip().strip('"\'')
    return out


_FM = _front_matter()
AUTHOR_NAME = _FM.get('name', 'Jerry Zachary Bannister')
AUTHOR_LINES = [
    _FM.get('author-affiliation', ''),
    f"E-mail: {_FM.get('email', '')}",
]


def inject_affiliation(path: pathlib.Path) -> int:
    """Append the affiliation and e-mail after the author name in document.xml."""
    with zipfile.ZipFile(path) as z:
        files = {n: z.read(n) for n in z.namelist()}
    doc = files['word/document.xml'].decode('utf-8')

    if _FM.get('email') and _FM['email'] in doc:
        return 0  # already present; do not duplicate on a second run

    # Find the run containing the author name and the paragraph that closes after it,
    # then append new paragraphs immediately following.
    idx = doc.find(AUTHOR_NAME)
    if idx == -1:
        return -1
    close = doc.find('</w:p>', idx)
    if close == -1:
        return -1
    close += len('</w:p>')

    def para(text: str) -> str:
        return ('<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
                f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                f'<w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">{text}</w:t></w:r></w:p>')

    extra = ''.join(para(t) for t in AUTHOR_LINES)
    doc = doc[:close] + extra + doc[close:]
    files['word/document.xml'] = doc.encode('utf-8')

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return 1


def main() -> int:
    if not DOCX.exists():
        print('no docx at', DOCX)
        return 1

    with zipfile.ZipFile(DOCX) as z:
        files = {n: z.read(n) for n in z.namelist()}

    # ---------------- styles ----------------
    styles = files['word/styles.xml'].decode('utf-8')
    styles = patch_rfonts(styles)

    # docDefaults: spacing and size
    styles = re.sub(r'<w:spacing w:after="\d+" ?/>',
                    f'<w:spacing w:after="0" w:line="{LINE_12}" w:lineRule="auto" />',
                    styles)
    styles = re.sub(r'<w:spacing w:line="\d+" w:lineRule="auto" ?/>',
                    f'<w:spacing w:after="0" w:line="{LINE_12}" w:lineRule="auto" />',
                    styles)
    # any 24 half-points (12pt) stays; force sizes to 24 unless already smaller
    styles = re.sub(r'<w:sz w:val="(\d+)" ?/>',
                    lambda m: '<w:sz w:val="24" />' if int(m.group(1)) > 24 else m.group(0),
                    styles)

    # Normal style: justify
    def justify_normal(m):
        block = m.group(0)
        if '<w:jc' in block:
            return re.sub(r'<w:jc w:val="[^"]*" ?/>', '<w:jc w:val="both" />', block)
        return block.replace('<w:qFormat />', '<w:qFormat /><w:pPr><w:jc w:val="both" /></w:pPr>', 1)
    styles = re.sub(r'<w:style [^>]*w:styleId="Normal".*?</w:style>',
                    justify_normal, styles, flags=re.S)

    files['word/styles.xml'] = styles.encode('utf-8')

    # ---------------- document: margins ----------------
    doc = files['word/document.xml'].decode('utf-8')
    doc = patch_rfonts(doc)
    m = dict(MARGINS)
    margin_xml = (f'<w:pgMar w:top="{m["top"]}" w:right="{m["right"]}" '
                  f'w:bottom="{m["bottom"]}" w:left="{m["left"]}" '
                  f'w:header="708" w:footer="708" w:gutter="0" />')
    if '<w:pgMar' in doc:
        doc = re.sub(r'<w:pgMar[^>]*/>', margin_xml, doc)
    else:
        doc = re.sub(r'(<w:sectPr[^>]*>)', r'\1' + margin_xml, doc)
    files['word/document.xml'] = doc.encode('utf-8')

    with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)

    # ---------------- report ----------------
    with zipfile.ZipFile(DOCX) as z:
        st = z.read('word/styles.xml').decode('utf-8')
        dx = z.read('word/document.xml').decode('utf-8')
    print(f'patched {DOCX.name}')
    print(f'  font refs to {FONT:9s}: {st.count(FONT) + dx.count(FONT)}')
    print(f'  line spacing {LINE_12}      : {st.count(f"w:line=\"{LINE_12}\"")}')
    print(f'  margins               : top {m["top"]}, bottom {m["bottom"]}, '
          f'left {m["left"]}, right {m["right"]} twips')
    print(f'  justified paragraphs  : {st.count("w:jc w:val=\"both\"") + dx.count("w:jc w:val=\"both\"")}')
    n = inject_affiliation(DOCX)
    print()
    if n == 1:
        print('  author affiliation + e-mail injected into the Word file')
        print('  (pandoc drops those YAML fields in docx output)')
    elif n == 0:
        print('  author affiliation already present, not duplicated')
    else:
        print('  WARNING: could not locate the author paragraph to inject into')

    print()
    print('REMINDER: the journal requires an ANONYMISED file for submission.')
    print('          This is the named version. Strip names/affiliations before uploading.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
