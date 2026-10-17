"""verify_trp_format.py - check that the rendered Word file meets Town and Regional Planning's
house style, and that the anonymised review copy contains no author identity.

Reads the rendered .docx files themselves rather than trusting scripts/fix_docx_trp.py's own
report. That matters: an earlier version of that script claimed to have applied a font change
and printed "0" for the count, which was accurate and useless — pandoc keeps typography in
word/styles.xml, not in word/document.xml.

Checks, from docs/trp-author-guidelines.md:
    Times New Roman throughout; body 12 pt; single spacing; paragraphs not indented;
    tables present and editable; author block in the named file, absent from the review copy.

Usage:
    python scripts/verify_trp_format.py
    python scripts/verify_trp_format.py --docx path/to/file.docx
"""
import argparse
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

FONT = "Times New Roman"


def check(label: str, cond: bool, detail: str = "") -> bool:
    print(f"  [{'OK' if cond else 'FAIL'}] {label:52s} {detail}")
    return cond


def verify(docx: pathlib.Path, anon: pathlib.Path | None) -> bool:
    ok = True
    z = zipfile.ZipFile(docx)
    styles = z.read("word/styles.xml").decode("utf-8")
    doc = z.read("word/document.xml").decode("utf-8")

    print(f"=== {docx.name} :: styles.xml ===")
    m = re.search(r'<w:style [^>]*w:styleId="Normal".*?</w:style>', styles, re.S)
    normal = m.group(0) if m else ""
    ok &= check("Normal font is Times New Roman", f'w:ascii="{FONT}"' in normal)
    ok &= check("Normal body size is 12 pt (sz 24)", '<w:sz w:val="24"' in normal)
    sp = re.search(r'<w:spacing[^>]*w:line="(\d+)"', normal)
    ok &= check("Normal line spacing is single (240)", bool(sp) and sp.group(1) == "240",
                f"line={sp.group(1) if sp else 'absent'}")
    ok &= check("Normal has no first-line indent", "firstLine" not in normal)

    dd = re.search(r"<w:docDefaults>.*?</w:docDefaults>", styles, re.S)
    dd = dd.group(0) if dd else ""
    ddsp = re.search(r'<w:spacing[^>]*w:line="(\d+)"', dd)
    ok &= check("docDefaults line spacing is single", bool(ddsp) and ddsp.group(1) == "240",
                f"line={ddsp.group(1) if ddsp else 'absent'}")

    missing = []
    for m2 in re.finditer(r'<w:style [^>]*?w:styleId="([^"]+)".*?</w:style>', styles, re.S):
        sid, blk = m2.group(1), m2.group(0)
        if sid in {"Normal", "BodyText", "Abstract", "Bibliography", "ListParagraph", "Caption"}:
            if f'w:ascii="{FONT}"' not in blk:
                missing.append(sid)
    ok &= check("all checked body styles use the journal font", not missing, f"missing: {missing}")
    ok &= check("no duplicated lineRule attributes",
                'w:lineRule="auto" w:lineRule' not in styles)

    print()
    print(f"=== {docx.name} :: document.xml ===")
    text = re.sub(r"<[^>]+>", "", doc)
    ok &= check("author name present", "Jerry Zachary Bannister" in text)
    ok &= check("affiliation present", "Abubakar Tafawa Balewa University" in text)
    ok &= check("e-mail present", "jzbannister@atbu.edu.ng" in text)
    n_tables = len(re.findall(r"<w:tbl>", doc))
    ok &= check("tables present", n_tables > 0, f"{n_tables} tables")

    if anon and anon.exists():
        print()
        print(f"=== {anon.name} :: double-blind copy ===")
        atext = re.sub(r"<[^>]+>", "",
                       zipfile.ZipFile(anon).read("word/document.xml").decode("utf-8"))
        ok &= check("author name ABSENT", "Jerry Zachary Bannister" not in atext)
        ok &= check("affiliation ABSENT", "Abubakar Tafawa Balewa University" not in atext)
        ok &= check("e-mail ABSENT", "jzbannister@atbu.edu.ng" not in atext)
        ok &= check("title still present", "Where urban agriculture concentrates" in atext)
        ok &= check("body still present", "Moran" in atext)

    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", type=pathlib.Path,
                    default=ROOT / "manuscript" / "manuscript.docx")
    ap.add_argument("--anonymised", type=pathlib.Path,
                    default=ROOT / "manuscript" / "manuscript-anonymised.docx")
    args = ap.parse_args()

    if not args.docx.exists():
        print(f"FAIL: {args.docx} not found - render it first")
        return 1

    ok = verify(args.docx, args.anonymised)
    print()
    print("TRP FORMAT:", "all checks passed" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
