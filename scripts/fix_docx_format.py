#!/usr/bin/env python3
"""Fix docx to meet conference spec: TNR 12pt, 1.5 spacing, 1in margins, numbered headings already via quarto."""
import zipfile, pathlib, re

docx = pathlib.Path(r"D:\urban-agriculture-nigeria-spatial\manuscript\manuscript.docx")
out = docx  # in-place

with zipfile.ZipFile(docx, 'r') as zin:
    files = {n: zin.read(n) for n in zin.namelist()}

# 1) Patch styles.xml — docDefaults
styles = files['word/styles.xml'].decode()
# Replace docDefaults rFonts theme with explicit TNR
orig_rFonts = r'<w:rFonts w:asciiTheme="minorHAnsi" w:cstheme="minorBidi" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorHAnsi" />'
new_rFonts = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" />'
if orig_rFonts in styles:
    styles = styles.replace(orig_rFonts, new_rFonts)
else:
    # fallback regex
    styles = re.sub(r'<w:rFonts[^>]*?/>', new_rFonts, styles, count=1)

# Set docDefaults pPr spacing to 1.5 lines (360) and after 0
if '<w:spacing w:after="200" />' in styles:
    styles = styles.replace('<w:spacing w:after="200" />', '<w:spacing w:after="0" w:line="360" w:lineRule="auto" />')
# Ensure Normal style has TNR 12pt
# Add rPr inside Normal if missing
normal_pat = r'(<w:style w:default="1" w:styleId="Normal"[^>]*>.*?<w:name w:val="Normal" />.*?<w:qFormat />)'
def repl_normal(m):
    inner = m.group(1)
    rpr = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
    # also pPr line 1.5
    ppr = '<w:pPr><w:spacing w:after="0" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
    return inner + rpr + ppr

styles_new, n = re.subn(normal_pat, repl_normal, styles, count=1, flags=re.S)
if n==0:
    # fallback: insert after qFormat
    styles = styles.replace('<w:qFormat />', '<w:qFormat /><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr><w:pPr><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>', 1)
else:
    styles = styles_new

files['word/styles.xml'] = styles.encode()

# 1b) Patch table/caption/bibliography to single spacing (save pages) — keep Normal 1.5
styles2 = files['word/styles.xml'].decode()
for sid in ["Table", "Caption", "Bibliography", "TOC"]:
    pat = rf'(<w:style[^>]*w:styleId="[^"]*{sid}[^"]*"[^>]*>.*?</w:style>)'
    def repl_sid(m, sid=sid):
        txt = m.group(1)
        # force single spacing inside this style
        if 'w:line="360"' in txt:
            txt = txt.replace('w:line="360"', 'w:line="240"')
        elif 'w:spacing' not in txt:
            txt = txt.replace('</w:pPr>', '<w:spacing w:line="240" w:lineRule="auto"/></w:pPr>', 1)
        else:
            # add line where missing
            txt = txt.replace('<w:spacing', '<w:spacing w:line="240" w:lineRule="auto"', 1) if 'w:line=' not in txt else txt
        return txt
    styles2 = re.sub(pat, repl_sid, styles2, flags=re.S)
files['word/styles.xml'] = styles2.encode()

# 2) Patch document.xml sectPr for 1 inch margins (1440 twips) if absent
doc_xml = files['word/document.xml'].decode()
if 'w:pgMar' not in doc_xml:
    # inject before closing sectPr
    doc_xml = doc_xml.replace('</w:sectPr>', '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')
files['word/document.xml'] = doc_xml.encode()

# Write back
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for name, data in files.items():
        zout.writestr(name, data)

print(f"Patched {docx} — TNR 12pt 1.5, margins 1in, docDefaults")
# verify
with zipfile.ZipFile(docx, 'r') as z:
    s = z.read('word/styles.xml').decode()
    print("TNR in styles?", "Times New Roman" in s)
    print("line 360 in styles?", 'w:line="360"' in s)
