@echo off
REM Portable render entry point.
REM The previous version hardcoded "cd /d D:\YohannaPaper", so it failed for anyone
REM who cloned the repo. %~dp0 resolves to this script's own directory instead.
setlocal
cd /d "%~dp0"
echo Project root: %CD%

echo.
echo [1/3] Rendering conference paper -^> manuscript\manuscript.docx
call quarto render manuscript/manuscript.qmd --to docx
if errorlevel 1 ( echo ERROR: manuscript render failed & exit /b 1 )

echo.
echo [2/3] Enforcing Times New Roman 12pt / 1.5 / 1in margins
python scripts\fix_docx_format.py
if errorlevel 1 echo WARNING: format patch returned %ERRORLEVEL%

echo.
echo [3/3] Rendering methodology companion -^> docs\methodology.pdf
call quarto render docs/methodology.qmd --to typst
if errorlevel 1 ( echo ERROR: methodology render failed & exit /b 1 )

echo.
echo Done. Verify page counts and styling in Word before submitting ^(File ^> Info^).
exit /b 0
