"""Read statistics from the already-open manuscript in Word, without disturbing it.

Read-only: never saves, never closes the user's document.
"""
import sys
import win32com.client as win32

# Attach to the RUNNING Word instance rather than starting a new one, so we do not
# get a second copy of the file and risk the user editing a different object.
try:
    word = win32.GetActiveObject("Word.Application")
except Exception as e:
    print("Could not attach to the running Word instance:", e)
    sys.exit(1)

target = None
for d in word.Documents:
    if "manuscript" in d.Name.lower():
        target = d
        break

if target is None:
    print("manuscript.docx is not among the open documents:")
    for d in word.Documents:
        print("   -", d.Name)
    sys.exit(1)

print(f"Attached to: {target.Name}")
print(f"Full path  : {target.FullName}")
print()

# wdStatisticPage = 2, wdStatisticWords = 0, wdStatisticCharacters = 3
PAGES = 2
WORDS = 0
CHARS = 3

pages = target.ComputeStatistics(PAGES)
words = target.ComputeStatistics(WORDS)
chars = target.ComputeStatistics(CHARS)

print("=== The number that matters for the submission ===")
print(f"  Pages        : {pages}")
print(f"  Words        : {words}")
print(f"  Characters   : {chars}")
print()

limit = 12
if pages <= limit:
    print(f"  WITHIN the 12-page limit (headroom of {limit - pages} page(s)).")
else:
    print(f"  OVER the 12-page limit by {pages - limit} page(s).")

print()
print("=== Formatting sample (Normal style, first paragraphs) ===")
normal = target.Styles("Normal")
f = normal.Font
pf = normal.ParagraphFormat
print(f"  Normal font      : {f.Name}")
print(f"  Normal size      : {f.Size} pt")
mode = pf.LineSpacingRule
names = {0: "single", 1: "1.5 lines", 2: "double", 3: "at least",
         4: "exactly", 5: "multiple"}
print(f"  Line spacing     : {names.get(mode, mode)}"
      + (f" (value {pf.LineSpacing})" if mode == 5 else ""))
ps = target.PageSetup
print(f"  Margins (pt)     : top {ps.TopMargin:.0f}  bottom {ps.BottomMargin:.0f}"
      f"  left {ps.LeftMargin:.0f}  right {ps.RightMargin:.0f}"
      f"   (1 in = 72 pt)")

print()
print("=== Structure ===")
print(f"  Paragraphs   : {target.Paragraphs.Count}")
print(f"  Tables       : {target.Tables.Count}")
print(f"  Inline shapes: {target.InlineShapes.Count}")

print()
print("=== Section headings ===")
for p in target.Paragraphs:
    try:
        st = p.Style.NameLocal
    except Exception:
        continue
    if st.startswith("Heading 1") or st.startswith("Heading 2"):
        txt = p.Range.Text.strip()
        if txt:
            indent = "  " if st.startswith("Heading 2") else ""
            print(f"  {indent}{txt[:78]}")

print()
print("(Nothing was saved or closed.)")
