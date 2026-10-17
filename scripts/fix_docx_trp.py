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

Run:
    python scripts/fix_docx_trp.py                 # named docx: style + author block
    python scripts/fix_docx_trp.py --anonymise     # also write the review copy
"""
from __future__ import annotations

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
    counts = {"body styled": 0, "headings re-fonted": 0, "docDefaults": 0}

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

    def substitute(m: re.Match) -> str:
        sid, block = m.group(1), m.group(0)
        if sid in BODY_STYLES:
            block = _ensure_rfonts(block, FONT)
            block = _set_size(block, TABLE_HALF_PT if False else BODY_HALF_PT)
            block = _set_single_line(block)
            block = _unindent(block)
            counts["body styled"] += 1
        elif sid in HEADING_STYLES or sid.endswith("Char"):
            block = _ensure_rfonts(block, FONT)
            counts["headings re-fonted"] += 1
        return block

    styles_xml = re.sub(r"<w:style [^>]*?w:styleId=\"([^\"]+)\".*?</w:style>",
                        substitute, styles_xml, flags=re.S)
    return styles_xml, counts


# ---------------------------------------------------------------------------
# document.xml: author block injection and anonymisation
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

    xml = re.sub(r"<w:p[ >].*?</w:p>", repl, xml, flags=re.S)
    return xml, done


def anonymise(xml: str) -> tuple[str, int]:
    """Strip byline, affiliation and e-mail for double-blind review."""
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

    xml = re.sub(r"<w:p[ >].*?</w:p>", strip_text, xml, flags=re.S)
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
    document, injected = inject_author_block(document)

    write_docx(DOCX, DOCX, {"word/styles.xml": styles, "word/document.xml": document})

    print(f"patched {DOCX.relative_to(ROOT)}")
    print(f"  body styles -> {FONT} {BODY_HALF_PT // 2}pt single-spaced : {counts['body styled']}")
    print(f"  headings re-fonted                        : {counts['headings re-fonted']}")
    print(f"  docDefaults single-spaced                 : {counts['docDefaults']}")
    print(f"  author block injected                     : {'yes' if injected else 'already present'}")
    print()

    if args.anonymise:
        axml, removed = anonymise(document)
        write_docx(DOCX, ANON, {"word/styles.xml": styles, "word/document.xml": axml})
        print(f"wrote {ANON.relative_to(ROOT)}")
        print(f"  identifying paragraphs removed: {removed}")
        if removed == 0:
            print("  WARNING: nothing matched - check the front matter before relying on this")
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
