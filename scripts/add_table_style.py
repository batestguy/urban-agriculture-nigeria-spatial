"""Add the table style pandoc's docx writer points every table at.

Pandoc 3.8 emits `<w:tblStyle w:val="Table"/>` for every table, but neither Quarto's
`reference.docx` nor pandoc's built-in reference defines a style with that id — only the
built-in `TableNormal` and `TableGrid`. A table referencing an undefined style id may draw
nothing, or may break the table entirely, depending on the renderer, which is why the damage
appeared in some conversions and not others.

This adds a `Table` style to a reference doc, based on TableNormal, correct for the journal:
Times New Roman 10 pt, single-spaced cells, ½ pt rules top and bottom plus one under the
header row. Word's built-in table styles then keep working, because this does not shadow them.

Idempotent: running it twice with the same name adds nothing the second time unless --force.

    python scripts/add_table_style.py                      # -> manuscript/reference.docx
    python scripts/add_table_style.py --force              # rewrite the style even if present
"""

import argparse
import io
import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "manuscript" / "reference.docx"

STYLE_ID = "Table"
STYLE_XML = f"""
<w:style {nsdecls("w")} w:type="table" w:styleId="{STYLE_ID}">
  <w:name w:val="Table"/>
  <w:basedOn w:val="TableNormal"/>
  <w:uiPriority w:val="59"/>
  <w:qFormat/>
  <w:pPr>
    <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
    <w:jc w:val="left"/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
    <w:sz w:val="20"/>
    <w:szCs w:val="20"/>
  </w:rPr>
  <w:tblPr>
    <w:tblBorders>
      <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      <w:left w:val="nil"/>
      <w:right w:val="nil"/>
      <w:insideH w:val="nil"/>
      <w:insideV w:val="nil"/>
    </w:tblBorders>
  </w:tblPr>
  <w:tblStylePr w:type="firstRow">
    <w:rPr>
      <w:b/>
      <w:bCs/>
    </w:rPr>
    <w:tcPr>
      <w:tcBorders>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      </w:tcBorders>
    </w:tcPr>
  </w:tblStylePr>
</w:style>
"""


def has_style(blob: bytes, style_id: str) -> bool:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        styles = z.read("word/styles.xml").decode("utf-8")
    return f'w:styleId="{style_id}"' in styles


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", type=Path, default=REFERENCE)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.path.exists():
        print(f"FAIL: {args.path} does not exist")
        return 1

    blob = args.path.read_bytes()
    if has_style(blob, STYLE_ID) and not args.force:
        print(f"{args.path.name}: Table style already present, nothing to do")
        return 0

    backup = args.path.with_suffix(".docx.bak")
    if not backup.exists():
        shutil.copy2(args.path, backup)

    doc = Document(io.BytesIO(blob))
    if has_style(blob, STYLE_ID) and args.force:
        # Remove the old definition from its real parent. (doc.styles.element.remove(...) is
        # lxml's remove and discards children — an earlier version of this line silently
        # deleted every table style in the document.)
        old = doc.styles[STYLE_ID].element
        parent = old.getparent()
        if parent is not None:
            parent.remove(old)
    # add_style creates a paragraph style stub; replace its XML with the table definition.
    stub = doc.styles.add_style("Table", WD_STYLE_TYPE.TABLE)
    new = parse_xml(STYLE_XML)
    stub.element.getparent().replace(stub.element, new)

    buf = io.BytesIO()
    doc.save(buf)
    args.path.write_bytes(buf.getvalue())
    print(f"{args.path.name}: added the Table style ({len(buf.getvalue())} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
