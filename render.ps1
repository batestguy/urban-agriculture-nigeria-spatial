# Portable render entry points.
# The previous versions hardcoded D:\YohannaPaper, so they failed for anyone who
# cloned the repo. These resolve their own directory instead.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Project root: $root"

Write-Host "`n[1/3] Rendering conference paper -> manuscript/manuscript.docx"
quarto render manuscript/manuscript.qmd --to docx
if ($LASTEXITCODE -ne 0) { Write-Error "manuscript render failed ($LASTEXITCODE)" }

Write-Host "`n[2/3] Enforcing Times New Roman 12pt / 1.5 / 1in margins"
python scripts/fix_docx_format.py
if ($LASTEXITCODE -ne 0) { Write-Warning "format patch returned $LASTEXITCODE" }

Write-Host "`n[3/3] Rendering methodology companion -> docs/methodology.pdf"
quarto render docs/methodology.qmd --to typst
if ($LASTEXITCODE -ne 0) { Write-Error "methodology render failed ($LASTEXITCODE)" }

Write-Host "`nDone. Verify page counts and styling in Word before submitting (File > Info)."
