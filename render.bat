@echo off
REM Portable render entry point.
REM An earlier version hardcoded an absolute project path, so it failed for anyone who
REM cloned the repo. %~dp0 resolves to this script's own directory instead.
REM
REM Target is the African Journal on Land Policy and Geospatial Sciences, so the
REM typography step is fix_docx_ajlpgs.py. scripts\fix_docx_format.py enforces the
REM abandoned conference spec and is deliberately NOT called here.
setlocal
cd /d "%~dp0"
echo Project root: %CD%

echo.
echo [1/4] Rendering the manuscript -^> manuscript\manuscript.docx + .pdf
call quarto render manuscript/manuscript.qmd --to docx
if errorlevel 1 ( echo ERROR: manuscript docx render failed & exit /b 1 )
call quarto render manuscript/manuscript.qmd --to pdf
if errorlevel 1 ( echo ERROR: manuscript pdf render failed & exit /b 1 )

echo.
echo [2/4] Enforcing AJLP^&GS typography and injecting the author block
python scripts\fix_docx_ajlpgs.py
if errorlevel 1 echo WARNING: AJLP^&GS patch returned %ERRORLEVEL%

echo.
echo [3/4] Rendering methodology companion -^> docs\methodology.pdf
call quarto render docs/methodology.qmd --to typst
if errorlevel 1 ( echo ERROR: methodology render failed & exit /b 1 )

echo.
echo [4/4] Checking the author block survived rendering
python scripts\verify_author_block.py
if errorlevel 1 ( echo ERROR: author block missing from a rendered file & exit /b 1 )

echo.
echo Done. Check the page count against the journal's 20-page limit ^(File ^> Info in Word^),
echo and remember the journal requires an ANONYMISED copy for review.
exit /b 0
