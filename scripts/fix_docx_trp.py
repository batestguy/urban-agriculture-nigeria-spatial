#!/usr/bin/env python3
"""fix_docx_trp.py - enforce the Town and Regional Planning house style on the manuscript,
and (optionally) emit the anonymised review copy.

Replaces the AJLP&GS-era scripts for the current target. Those are kept because they encode
working tools for dropped specs; this one matches the venue actually being submitted to.

Per docs/trp-author-guidelines.md, extracted from the journal's own site (/about/submissions):

    Font          Times New Roman, throughout
    Body          12 pt
    Line spacing  single
    Tables        Times New Roman 10 pt, single spacing, ½ pt borders
    Paragraphs    "should start on a new line, not indented"
    Figures       TIF or JPEG, 300 dpi  -> scripts/prepare_figures_trp.py
    Abstract      250 words, single spaced
    Headings      Arabic numerals to three levels - Quarto does this via number-sections

HOW PANDOC LAYS OUT A DOCX, because it determines what this script must edit:

    word/document.xml holds NO font or size. It carries only <w:pStyle> references, one per
    paragraph. All typography lives in word/styles.xml (styles + docDefaults) and the theme
    fonts in word/theme/theme1.xml.

    An earlier version of this script edited runs in document.xml and reported
    "font refs -> Times New Roman: 0", which was correct and useless: there was nothing there
    to change. Formatting has to be applied to the styles part and to any inline overrides
    that do exist.

NOTE ON THE REFERENCE DOC. manuscript/reference.docx (produced from an earlier AJLP&GS pass)
already sets Normal to Times New Roman 12 pt and justifies it, so the font and size largely
arrive without help. What it does NOT set is single spacing (Normal is 1.5, docDefaults 1.15).
This script makes the spacing correct and makes the font/size explicit for every style that
carries text, so the result does not depend on which reference doc was last used.

The journal's peer review is DOUBLE BLIND, so an anonymised copy is required. The named
version always goes to manuscript/manuscript.docx; the anonymised copy, when requested, goes
to manuscript/manuscript-anonymised.docx so the two can never be confused.

TABLES: why every table has to be given a style here.

    Pandoc emits every table as a bare <w:tbl> with no <w:tblPr><w:tblStyle>. A table with no
    style inherits NOTHING: no borders, and cell paragraphs at the document default 12 pt. On
    paper that is a list of words in columns with no rule under the header - the "tables with no
    bands" the author reported. The old version of this script styled the paragraph styles but
    never touched a table, because a table carries no pStyle to find.

    Each table therefore gets <w:tblStyle w:val="TRPTable"/> (a style this script defines),
    fixed column widths taken from its own grid, 10 pt cell text, zero cell padding, and
    "keep with next" on every row but the last so a table does not break across a page.

FRONT MATTER: pandoc puts the title, subtitle and byline in consecutive single-line paragraphs
with NO blank line between them, so the title block reads as a paragraph containing the whole
name rather than a centred block. Those paragraphs are regrouped into one byline paragraph and
spacing is set per element.

Run:
    python scripts/fix_docx_trp.py                 # named docx: style + author block
    python scripts/fix_docx_trp.py --anonymise     # also write the review copy
"""
from __future__ import annotations

# Pandoc and python-docx both leave whitespace between block elements, so a paragraph match
# must not assume the character before <w:p> is `<`.
PARA = r"<w:p(?: [^>]*)?>.*?</w:p>"

import argparse
import pathlib
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "manuscript" / "manuscript.docx"
ANON = ROOT / "manuscript" / "manuscript-anonymised.docx"

FONT = "Times New Roman"
BODY_HALF_PT = 24      # 12 pt
TABLE_HALF_PT = 20     # 10 pt
SINGLE = 240           # w:line for single spacing (240 twips = 1 line)
HALF_PT_BORDER = 4     # ½ pt in eighths of a point

# Styles whose text is body text and therefore 12 pt single-spaced.
BODY_STYLES = {
    "Normal", "BodyText", "BodyText2", "BodyText3", "ListParagraph",
    "List", "List2", "List3", "ListBullet", "ListBullet2", "ListBullet3",
    "ListNumber", "ListNumber2", "ListNumber3", "ListContinue",
    "ListContinue2", "ListContinue3", "Quote", "IntenseQuote", "Abstract",
    "Bibliography", "NoSpacing", "MacroText", "Caption",
}
# Headings keep their own sizes; they only need the font family.
HEADING_STYLES = {f"Heading{i}" for i in range(1, 10)} | {"Title", "Subtitle", "TOCHeading"}


def _flat(s: str) -> str:
    return " ".join(s.split())


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_part(path: pathlib.Path, name: str) -> str | None:
    with zipfile.ZipFile(path) as z:
        if name in z.namelist():
            return z.read(name).decode("utf-8")
    return None


def write_docx(src: pathlib.Path, dst: pathlib.Path, replacements: dict[str, str]) -> None:
    """Rewrite the docx, swapping whole parts. Safe when src == dst.

    Builds into a temporary file and only replaces the target once the archive verifies.
    Reading and writing one path simultaneously truncates the zip mid-copy: an earlier
    version did exactly that and left a 22-byte manuscript.docx behind.
    """
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    try:
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in replacements:
                    data = replacements[item.filename].encode("utf-8")
                zout.writestr(item, data)
        with zipfile.ZipFile(tmp) as check:
            if not check.namelist():
                raise zipfile.BadZipFile("archive is empty after rewrite")
        tmp.replace(dst)
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# styles.xml
# ---------------------------------------------------------------------------

def _style_blocks(styles_xml: str):
    for m in re.finditer(r"<w:style [^>]*?w:styleId=\"([^\"]+)\".*?</w:style>", styles_xml, re.S):
        yield m.group(1), m.group(0)


def _ensure_rfonts(block: str, font: str) -> str:
    repl = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}" />'
    if "<w:rFonts" in block:
        return re.sub(r"<w:rFonts[^>]*?/>", repl, block)
    # insert as the first child of rPr, creating rPr if needed
    if "<w:rPr>" in block:
        return block.replace("<w:rPr>", "<w:rPr>" + repl, 1)
    return block.replace("</w:style>", f"<w:rPr>{repl}</w:rPr></w:style>", 1)


def _set_single_line(block: str) -> str:
    """Set single line spacing in a style's paragraph properties, without duplicating attrs.

    The previous version appended `w:lineRule="auto"` on every pass and produced
    `w:lineRule="auto" w:lineRule="auto" w:lineRule="auto"` — malformed enough that Word
    may reject the file, and certainly wrong. This rebuilds the element cleanly instead.
    """
    def clean_spacing(m: re.Match) -> str:
        attrs = m.group(1)
        # keep w:after / w:before / w:beforeLines / w:afterLines; drop line + lineRule
        keep = re.findall(r'w:(?:after|before|afterLines|beforeLines|afterAutospacing|'
                          r'beforeAutospacing)="[^"]*"', attrs)
        rebuilt = "".join(" " + a for a in keep)
        return f'<w:spacing{rebuilt} w:line="{SINGLE}" w:lineRule="auto"/>'

    if re.search(r"<w:spacing[^>]*/>", block):
        return re.sub(r"<w:spacing([^>]*?)/>", clean_spacing, block, count=1)

    if "<w:pPr>" in block:
        return block.replace(
            "<w:pPr>", f'<w:pPr><w:spacing w:line="{SINGLE}" w:lineRule="auto"/>', 1)
    return block.replace(
        "</w:style>",
        f'<w:pPr><w:spacing w:line="{SINGLE}" w:lineRule="auto"/></w:pPr></w:style>',
        1,
    )


def _unindent(block: str) -> str:
    if "<w:ind" in block and ("firstLine" in block or "hanging" in block):
        return re.sub(r"<w:ind[^>]*?/>", '<w:ind w:firstLine="0" w:left="0" />', block)
    return block


def _set_size(block: str, half_pt: int) -> str:
    if "<w:sz " in block:
        block = re.sub(r'<w:sz w:val="\d+" />', f'<w:sz w:val="{half_pt}" />', block)
    if "<w:szCs " in block:
        block = re.sub(r'<w:szCs w:val="\d+" />', f'<w:szCs w:val="{half_pt}" />', block)
    if "<w:sz " not in block:
        add = f'<w:sz w:val="{half_pt}" /><w:szCs w:val="{half_pt}" />'
        if "<w:rPr>" in block:
            block = block.replace("<w:rPr>", "<w:rPr>" + add, 1)
        else:
            block = block.replace("</w:style>", f"<w:rPr>{add}</w:rPr></w:style>", 1)
    return block


def patch_styles(styles_xml: str, journal: bool) -> tuple[str, dict]:
    counts = {"body styled": 0, "headings re-fonted": 0, "docDefaults": 0,
              "title block": 0, "table style": 0}

    # docDefaults: the inherited default must also be single-spaced. This is what a paragraph
    # with no explicit w:spacing falls back to, so leaving it at 276 (1.15) would keep most
    # of the document slightly loose.
    def fix_defaults(m: re.Match) -> str:
        block = m.group(0)
        new, n = re.subn(r'w:line="\d+"', f'w:line="{SINGLE}"', block)
        if n:
            counts["docDefaults"] += 1
            return new
        # no line attribute: insert one into the existing spacing element, or add one
        if "<w:spacing" in block:
            counts["docDefaults"] += 1
            return re.sub(r"<w:spacing",
                          f'<w:spacing w:line="{SINGLE}" w:lineRule="auto" ', block, count=1)
        counts["docDefaults"] += 1
        return block.replace(
            "<w:pPrDefault>",
            f'<w:pPrDefault><w:pPr><w:spacing w:line="{SINGLE}" w:lineRule="auto"/></w:pPr>',
            1,
        )

    styles_xml = re.sub(r"<w:docDefaults>.*?</w:docDefaults>", fix_defaults, styles_xml, flags=re.S)

    # The Title/Subtitle styles are defined AND linked (w:link) to character styles here.
    # Dropping the link would leave w:titleChar / w:subtitleChar dangling.
    title_font = (f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}" '
                  f'w:eastAsia="{FONT}"/>')

    def substitute(m: re.Match) -> str:
        sid, block = m.group(1), m.group(0)
        if sid in BODY_STYLES:
            block = _ensure_rfonts(block, FONT)
            block = _set_size(block, BODY_HALF_PT)
            block = _set_single_line(block)
            block = _unindent(block)
            counts["body styled"] += 1
        elif sid in HEADING_STYLES or sid.endswith("Char"):
            block = _ensure_rfonts(block, FONT)
            counts["headings re-fonted"] += 1
        return block

    styles_xml = re.sub(r"<w:style [^>]*?w:styleId=\"([^\"]+)\".*?</w:style>",
                        substitute, styles_xml, flags=re.S)

    def fix_block(m: re.Match) -> str:
        sid = m.group(1)
        block = m.group(0)
        if sid == "Title":
            block = block.replace(
                "<w:jc w:val=\"center\"/>\n    </w:pPr>",
                "<w:jc w:val=\"center\"/>\n    </w:pPr>",
            )
            block = re.sub(r"</w:pPr>",
                           '<w:spacing w:before="0" w:after="120" w:line="240" '
                           'w:lineRule="auto"/></w:pPr>', block, count=1)
            block = re.sub(r"<w:rPr>.*?</w:rPr>",
                           f"<w:rPr>{title_font}<w:b/><w:sz w:val=\"28\"/><w:szCs w:val=\"28\"/>"
                           "</w:rPr>", block, count=1, flags=re.S)
            counts["title block"] += 1
        elif sid == "Subtitle":
            # pandoc's Subtitle style carries <w:numPr ilvl=1>, a numbering artefact that can
            # indent the subtitle as a list item. It is not a numbered element here.
            block = re.sub(r"<w:numPr>.*?</w:numPr>", "", block, flags=re.S)
            block = re.sub(r"</w:pPr>",
                           '<w:spacing w:before="0" w:after="120" w:line="240" '
                           'w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>', block, count=1)
            block = re.sub(r"<w:rPr>.*?</w:rPr>",
                           f"<w:rPr>{title_font}<w:i/><w:iCs/><w:sz w:val=\"24\"/>"
                           "<w:szCs w:val=\"24\"/></w:rPr>", block, count=1, flags=re.S)
            counts["title block"] += 1
        return block

    styles_xml = re.sub(r"<w:style [^>]*?w:styleId=\"(Title|Subtitle)\".*?</w:style>",
                        fix_block, styles_xml, flags=re.S)

    # One table style, defined here so document.xml has something to point at.
    # ½ pt (sz=4 in eighths) rules: top, bottom and under the header row only. Closed boxes
    # round every cell are harder to read than open ones and are not what the journal shows.
    # Also define pandoc's `Compact` and `Table`, which document.xml references but a reference
    # doc generated elsewhere may not contain. A paragraph or table pointing at an undefined
    # style collapses the table to one element per line — the "tables with bands" the author
    # saw, and it appears or not depending on how the reference doc was made.
    # Define the style this script points tables at. The test is on TRPTable, the style actually
    # added: testing for "Table" combined with "Table" being a substring of "TRPTable" meant the
    # branch was skipped exactly when the style was missing.
    if 'w:styleId="TRPTable"' not in styles_xml:
        styles_xml = styles_xml.replace("</w:styles>", _table_style_xml() + "</w:styles>", 1)
        counts["table style"] = 1
    if 'w:styleId="Compact"' not in styles_xml:
        styles_xml = styles_xml.replace("</w:styles>", _compact_style_xml() + "</w:styles>", 1)
    if 'w:styleId="TRPTable"' not in styles_xml or 'w:styleId="Compact"' not in styles_xml:
        raise RuntimeError("style injection failed: styles.xml has no </w:styles> to insert before")

    return styles_xml, counts


def _table_style_xml() -> str:
    return (
        '<w:style w:type="table" w:styleId="TRPTable">'
        '<w:name w:val="TRP Table"/><w:basedOn w:val="TableNormal"/>'
        f'<w:pPr><w:spacing w:before="0" w:after="0" w:line="{SINGLE}" w:lineRule="auto"/>'
        f'<w:jc w:val="left"/></w:pPr>'
        f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
        f'<w:sz w:val="{TABLE_HALF_PT}"/><w:szCs w:val="{TABLE_HALF_PT}"/></w:rPr>'
        '<w:tblPr>'
        '<w:tblBorders>'
        f'<w:top w:val="single" w:sz="{HALF_PT_BORDER}" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="{HALF_PT_BORDER}" w:space="0" w:color="000000"/>'
        '<w:left w:val="nil"/><w:right w:val="nil"/><w:insideH w:val="nil"/>'
        '<w:insideV w:val="nil"/>'
        '</w:tblBorders>'
        '<w:tblCellMar><w:top w:w="30" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
        '<w:bottom w:w="30" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar>'
        '</w:tblPr>'
        '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/></w:rPr>'
        '<w:tcPr><w:tcBorders>'
        f'<w:bottom w:val="single" w:sz="{HALF_PT_BORDER}" w:space="0" w:color="000000"/>'
        '</w:tcBorders></w:tcPr></w:tblStylePr>'
        '</w:style>'
    )


def _compact_style_xml() -> str:
    return (
        '<w:style w:type="paragraph" w:styleId="Compact">'
        '<w:name w:val="Compact"/><w:basedOn w:val="Normal"/>'
        f'<w:pPr><w:spacing w:before="0" w:after="0" w:line="{SINGLE}" w:lineRule="auto"/>'
        '<w:contextualSpacing/></w:pPr>'
        f'<w:rPr><w:sz w:val="{TABLE_HALF_PT}"/><w:szCs w:val="{TABLE_HALF_PT}"/></w:rPr>'
        '</w:style>'
    )


# ---------------------------------------------------------------------------
# document.xml: tables
# ---------------------------------------------------------------------------

# A4 page (11906 twips wide) less 1 in margins each side: the width a table may occupy.
TEXT_WIDTH_TWIPS = 11906 - 2 * 1440
TEXT_WIDTH_EMU = TEXT_WIDTH_TWIPS * 635
# A column narrower than this cannot hold a short heading such as "AIC" beside a value.
MIN_COL_TWIPS = 1080      # 1.9 cm


def _content_width(table, col: int) -> int:
    """Width in characters a column needs for its widest unbreakable token.

    Characters, not words: the question is whether the longest single word, heading or number
    fits on a line. Counting whole cells made narrow numeric columns look wide, and "AIC" next
    to "374.2" came out 1.1 cm apart and broke. The header cell is weighted extra because a
    heading that wraps over two lines is what collides with its neighbour.
    """
    need = 4
    for r_idx, row in enumerate(table.rows):
        try:
            text = row.cells[col].text
        except IndexError:
            continue
        longest = max((len(tok) for tok in text.split()), default=0)
        need = max(need, longest * (1.35 if r_idx == 0 else 1.0))
    return int(need)


def _distribute(want: list[int], total: int, min_twips: int) -> list[int]:
    """Split `total` twips in proportion to `want`, honouring a per-column minimum.

    Water-filling: any column below the minimum is pinned there and the remainder is
    redistributed among the others, so a narrow numeric column gets its minimum and the
    text column absorbs the loss instead of both ending up unreadably tight.
    """
    n = len(want)
    floor = min_twips if n * min_twips <= total else total // n
    fixed = [False] * n
    widths = [0] * n
    while True:
        pool = total - sum(widths[i] for i in range(n) if fixed[i])
        free = [i for i in range(n) if not fixed[i]]
        if not free:
            break
        base = sum(want[i] for i in free) or len(free)
        moved = False
        for i in free:
            candidate = int(pool * want[i] / base)
            if candidate < floor:
                widths[i] = floor
                fixed[i] = True
                moved = True
        if not moved:
            for i in free:
                widths[i] = int(pool * want[i] / base)
            break
    return widths


def _is_numeric_column(table, col: int) -> bool:
    """True if every cell below the header in this column is a number or an empty string."""
    values = []
    for row in table.rows[1:]:
        try:
            values.append(row.cells[col].text.strip())
        except IndexError:
            continue
    values = [v for v in values if v]
    if not values:
        return False

    def numeric(v: str) -> bool:
        v = v.replace(",", "").replace("%", "").replace("−", "-")
        return bool(re.fullmatch(r"[-+]?[\d.]+(?:[eE][-+]?\d+)?", v))

    return all(numeric(v) for v in values)


def style_tables(parts: dict[str, bytes]) -> tuple[dict[str, bytes], dict]:
    """Give every pandoc table a style, fixed widths, 10 pt cells and no page splits.

    Works on the whole package, not on document.xml alone: python-docx opens a zip, and a
    body fragment has no package around it to open. Uses python-docx for the table structure
    (it understands it), then the XML for the parts python-docx has no API for.
    """
    import io

    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt

    doc = Document(io.BytesIO(_pack(parts)))
    counts = {"tables styled": 0, "cells 10 pt": 0, "header rows repeated": 0,
              "figure blocks unwrapped": 0, "columns resized": 0}

    for table in doc.tables:
        # Figure captions are emitted by pandoc as a one-cell table with an inline image.
        # They are not tabular data and must not get table rules.
        if len(table.columns) == 1 and len(table.rows) == 1:
            tbl = table._tbl
            parent = tbl.getparent()
            if parent is not None:
                parent.remove(tbl)
                counts["figure blocks unwrapped"] += 1
            continue

        # By style NAME ("TRP Table"), not id: python-docx keys table styles on w:name.
        table.style = "TRP Table"
        # Word does not wrap inside a cell by default when autofit is off: an AIC of 374.2 in a
        # narrow column breaks at "374." / "2". Prefer a full-text-width layout with autofit on,
        # which lets Word size columns to content and is what a reader expects of a data table.
        table.autofit = True
        counts["tables styled"] += 1

        # (a) Column widths: give each column its share of the full text width, so that no
        #     column is left at pandoc's uniform minimum and every cell has room.
        #     Sets w:gridCol directly. Neither Column.width nor Cell.width works here: pandoc's
        #     w:tcW="0 auto" wins over the grid, python-docx refuses to overwrite a cell width it
        #     can read, and Column.width reads a cached layout so it reports the new width while
        #     writing the old one. The grid, written straight into the tree, is what LibreOffice
        #     and Word both honour.
        tbl_el = table._tbl
        columns = list(table.columns)
        want = [_content_width(table, i) for i in range(len(columns))]
        widths = _distribute(want, TEXT_WIDTH_TWIPS, MIN_COL_TWIPS)
        grid = tbl_el.find(qn("w:tblGrid"))
        for gcol, twips in zip(grid.findall(qn("w:gridCol")), widths):
            gcol.set(qn("w:w"), str(twips))
        # The "0 auto" cell widths would otherwise override the grid in Word.
        for tc in tbl_el.iter(qn("w:tc")):
            tcPr = tc.find(qn("w:tcPr"))
            if tcPr is None:
                continue
            for old in tcPr.findall(qn("w:tcW")):
                if old.get(qn("w:type")) == "auto":
                    tcPr.remove(old)
        counts["columns resized"] += 1

        # (b) Numeric columns flush right, without touching the preceding text cell.
        for i in range(len(columns)):
            if _is_numeric_column(table, i):
                for cell in table.columns[i].cells:
                    for p in cell.paragraphs:
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        for r_idx, row in enumerate(table.rows):
            if r_idx == 0:
                trPr = row._tr.get_or_add_trPr()
                if trPr.find(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblHeader"
                ) is None:
                    trPr.append(OxmlElement("w:tblHeader"))
                    counts["header rows repeated"] += 1
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(TABLE_HALF_PT / 2)
                        run.font.name = FONT
                        counts["cells 10 pt"] += 1

    parts["word/document.xml"] = doc.element.xml.encode("utf-8")
    return parts, counts


def _pack(parts: dict[str, bytes]) -> bytes:
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    return buf.getvalue()


def _unpack(blob: bytes) -> dict[str, bytes]:
    import io

    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return {i.filename: z.read(i.filename) for i in z.infolist()}


# --------------------------------------------------------------------------
# document.xml: front matter
# ---------------------------------------------------------------------------

def front_matter() -> dict:
    qmd = (ROOT / "manuscript" / "manuscript.qmd").read_text(encoding="utf-8")
    block = qmd.split("---", 2)[1]
    out: dict[str, str] = {}
    for line in block.splitlines():
        s = line.strip().lstrip("-").strip()
        for key in ("author-affiliation", "affiliation", "name", "email"):
            if s.startswith(key + ":") and key not in out:
                out[key] = s.split(":", 1)[1].strip().strip("\"'")
    return out


def inject_author_block(xml: str) -> tuple[str, bool]:
    fm = front_matter()
    name, affil, email = fm.get("name", ""), fm.get("author-affiliation", ""), fm.get("email", "")
    if not (name and affil and email):
        print("  WARNING: front matter is missing name/affiliation/e-mail; not injecting")
        return xml, False
    if affil in re.sub(r"<[^>]+>", "", xml):
        return xml, False          # already there from a previous run

    done = False

    def repl(m: re.Match) -> str:
        nonlocal done
        block = m.group(0)
        if done or name not in re.sub(r"<[^>]+>", "", block):
            return block
        add = (f'<w:r><w:br/></w:r>'
               f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/></w:rPr>'
               f'<w:t xml:space="preserve">{affil}</w:t></w:r>'
               f'<w:r><w:br/></w:r>'
               f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/></w:rPr>'
               f'<w:t xml:space="preserve">E-mail: {email}</w:t></w:r>')
        done = True
        return block.replace("</w:p>", add + "</w:p>", 1)

    xml = re.sub(PARA, repl, xml, flags=re.S)
    return xml, done


def regroup_front_matter(xml: str) -> tuple[str, bool]:
    """Merge the separate byline paragraphs pandoc emits into one block.

    Pandoc writes the author line, the affiliation and the e-mail as separate single-line
    paragraphs with no space between them, so page 1 reads as a paragraph whose lines are the
    three parts of the name. They become one paragraph: bold name, then affiliation and e-mail
    on their own lines at body size.
    """
    fm = front_matter()
    name, affil, email = fm.get("name", ""), fm.get("author-affiliation", ""), fm.get("email", "")
    if not (name and affil):
        return xml, False

    def text(w: str) -> str:
        return (f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{_esc(w)}</w:t></w:r>')

    lines = [
        text(name),
        '<w:r><w:br/></w:r>',
        f'<w:r><w:t xml:space="preserve">{_esc(affil)}</w:t></w:r>',
    ]
    if email:
        lines += ['<w:r><w:br/></w:r>',
                  f'<w:r><w:t xml:space="preserve">E-mail: {_esc(email)}</w:t></w:r>']
    byline = ('<w:p><w:pPr><w:spacing w:before="0" w:after="240" w:line="240" '
              'w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>' + "".join(lines) + '</w:p>')

    # Replace the paragraph holding the name with the merged block, then drop the separate
    # affiliation and e-mail paragraphs that followed it. Matching runs on text-extracted
    # paragraphs: pandoc splits the name across runs, so searching the raw XML for the name
    # finds nothing and the byline is silently dropped.
    done = False

    def paragraph(text_of) -> str:
        return re.sub(PARA, text_of, xml, flags=re.S)

    def replace_name(m: re.Match) -> str:
        nonlocal done
        block = m.group(0)
        flat = re.sub(r"<[^>]+>", " ", block)
        if not done and _flat(name) in _flat(flat):
            done = True
            return byline
        return block

    xml = paragraph(replace_name)
    if not done:
        return xml, False

    byline_probe = _flat(name + " " + affil)

    def drop_rest(m: re.Match) -> str:
        block = m.group(0)
        flat = _flat(re.sub(r"<[^>]+>", " ", block))
        # Never drop the block that was just inserted: it *is* the affiliation, by design.
        if not flat or byline_probe in flat:
            return block
        if _flat(affil) in flat or (email and _flat(email) in flat):
            return ""
        return block

    xml = paragraph(drop_rest)
    return xml, True


def anonymise(xml: str) -> tuple[str, int]:
    fm = front_matter()
    needles = [v for v in (fm.get("name", ""), fm.get("email", ""),
                           fm.get("author-affiliation", "")) if v]
    removed = 0

    def strip_text(m: re.Match) -> str:
        nonlocal removed
        text = re.sub(r"<[^>]+>", "", m.group(0))
        if any(n and n in text for n in needles):
            removed += 1
            return ""
        return m.group(0)

    xml = re.sub(PARA, strip_text, xml, flags=re.S)
    return xml, removed


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anonymise", action="store_true",
                    help="also write manuscript-anonymised.docx for double-blind review")
    args = ap.parse_args()

    if not DOCX.exists() or DOCX.stat().st_size < 1000:
        size = DOCX.stat().st_size if DOCX.exists() else 0
        print(f"FAIL: {DOCX.relative_to(ROOT)} missing or truncated ({size} bytes).")
        print("      cd manuscript && quarto render manuscript.qmd --to docx")
        return 1

    styles = read_part(DOCX, "word/styles.xml")
    document = read_part(DOCX, "word/document.xml")
    if styles is None or document is None:
        print("FAIL: the docx has no word/styles.xml or word/document.xml")
        return 1

    styles, counts = patch_styles(styles, True)
    # Tables first: python-docx re-serialises the whole body, so the paragraph edits below
    # must happen on its output, not before it. It needs the whole package, not the fragment.
    parts: dict[str, bytes] = {}
    with zipfile.ZipFile(DOCX) as z:
        for name in z.namelist():
            parts[name] = z.read(name)
    parts["word/styles.xml"] = styles.encode("utf-8")
    parts["word/document.xml"] = document.encode("utf-8")
    parts, table_result = style_tables(parts)
    document = parts["word/document.xml"].decode("utf-8")
    # --- Tables: keep each table with its caption and give it room ----------
    # pandoc emits the caption as the paragraph immediately before the table. Without this,
    # a table's bottom rule sits flush against the next paragraph and the caption can be
    # orphaned across a page break.
    def table_spacing(xml: str) -> tuple[str, int]:
        n = 0

        def before_table(m: re.Match) -> str:
            nonlocal n
            caption, table = m.group(1), m.group(2)
            n += 1
            ppr = ('<w:pPr><w:keepNext/><w:spacing w:before="200" w:after="60" '
                   'w:line="240" w:lineRule="auto"/></w:pPr>')
            if "<w:pPr>" in caption:
                caption = re.sub(r"(<w:pPr>)(?:(?!</w:pPr>).)*?</w:pPr>",
                                 lambda mm: mm.group(1) + ppr[len("<w:pPr>"):],
                                 caption, count=1, flags=re.S)
            else:
                caption = caption.replace("<w:p>", "<w:p>" + ppr, 1)
            return caption + table

        # Anchored on </w:p> so the stored group is the whole preceding paragraph. An
        # unanchored `<w:p[^>]*>.*?</w:p>` matches from the caption paragraph's OWN opening
        # tag and overwrites its <w:p> with <w:pPr>, producing a file no renderer will load.
        xml = re.sub(r"(<w:p(?: [^>]*)?>(?:(?!<w:p[ >]).)*?</w:p>)\s*(<w:tbl>)",
                     before_table, xml, flags=re.S)
        return xml, n

    document, captions = table_spacing(document)

    document, injected = inject_author_block(document)
    document, regrouped = regroup_front_matter(document)
    document_named = document

    write_docx(DOCX, DOCX, {"word/styles.xml": styles, "word/document.xml": document_named})

    print(f"patched {DOCX.relative_to(ROOT)}")
    print(f"  body styles -> {FONT} {BODY_HALF_PT // 2}pt single-spaced : {counts['body styled']}")
    print(f"  headings re-fonted                        : {counts['headings re-fonted']}")
    print(f"  docDefaults single-spaced                 : {counts['docDefaults']}")
    print(f"  title block styled                        : {counts['title block']}")
    print(f"  table style defined                       : {counts['table style']}")
    print(f"  tables styled + cells at {TABLE_HALF_PT // 2}pt            : {table_result['tables styled']} "
          f"({table_result['cells 10 pt']} cells)")
    print(f"  byline regrouped                          : {'yes' if regrouped else 'no change'}")
    print(f"  author block injected                     : {'yes' if injected else 'already present'}")
    print()

    # Anonymise from the version on disk, before either rewrite, never from `document`:
    # that variable is reassigned by the two calls above, and the review copy was silently
    # built from the NAMED output - identity and all - with "removed: 0" reported as a
    # warning rather than as the failure it was.
    if args.anonymise:
        if not (injected or regrouped):
            print("FAIL: refusing to build the review copy - neither the author block nor the")
            print("      byline was found, so anonymising cannot be shown to remove anything.")
            return 1
        axml, removed = anonymise(document_named)
        fm = front_matter()
        identity = [fm.get(k, "") for k in ("name", "email", "author-affiliation")]
        needle_hits = [n for n in identity if n and n in axml]
        if removed == 0 or needle_hits:
            print(f"FAIL: the anonymised copy still carries {len(needle_hits)} identifying")
            print("      string(s); refusing to write it. Do not submit this review copy.")
            return 1
        write_docx(DOCX, ANON, {"word/styles.xml": styles, "word/document.xml": axml})
        print(f"wrote {ANON.relative_to(ROOT)}")
        print(f"  identifying paragraphs removed: {removed}")
        print("  identity re-checked in the output: absent")
        print()

    print("TWO ARTEFACTS, not to be confused:")
    print("  manuscript.docx              NAMED (ORCID goes here)")
    print("  manuscript-anonymised.docx   REVIEW copy (no identity)")
    print()
    print("Verify: python scripts/verify_author_block.py   (checks the NAMED artefacts)")
    print("Rebuild note: any re-render overwrites both, so re-run this script after rendering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
