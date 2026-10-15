# Portable render entry points.
# An earlier version hardcoded an absolute project path, so it failed for anyone who
# cloned the repo. This resolves its own directory instead.
#
# The target is the African Journal on Land Policy and Geospatial Sciences, so the
# typography step is fix_docx_ajlpgs.py (Cambria 12pt / 1.2 / AJLP&GS margins).
# scripts/fix_docx_format.py enforces the abandoned conference spec and is NOT called here.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Project root: $root"

Write-Host "`n[1/4] Rendering the manuscript -> manuscript/manuscript.docx + .pdf + .html"
quarto render manuscript/manuscript.qmd --to docx
if ($LASTEXITCODE -ne 0) { Write-Error "manuscript docx render failed ($LASTEXITCODE)" }
quarto render manuscript/manuscript.qmd --to pdf
if ($LASTEXITCODE -ne 0) { Write-Error "manuscript pdf render failed ($LASTEXITCODE)" }

Write-Host "`n[2/4] Enforcing AJLP&GS typography and injecting the author block"
python scripts/fix_docx_ajlpgs.py
if ($LASTEXITCODE -ne 0) { Write-Warning "AJLP&GS patch returned $LASTEXITCODE" }

Write-Host "`n[3/4] Rendering the methodology companion -> docs/methodology.pdf"
quarto render docs/methodology.qmd --to typst
if ($LASTEXITCODE -ne 0) { Write-Error "methodology render failed ($LASTEXITCODE)" }

Write-Host "`n[4/4] Checking the author block survived rendering"
python scripts/verify_author_block.py
if ($LASTEXITCODE -ne 0) { Write-Error "author block missing from a rendered file" }

Write-Host "`nDone. Check the page count against the journal's 20-page limit (File > Info in Word),"
Write-Host "and remember the journal requires an ANONYMISED copy for review."
