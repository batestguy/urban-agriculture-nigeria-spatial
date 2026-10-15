# rename_folder.ps1 — move the project from D:\YohannaPaper to its new name and verify.
#
# Run from OUTSIDE the folder (cwd on D:\): Windows will not rename a directory that a
# process is using as its current directory. This script checks its own cwd first and
# refuses rather than half-moving anything.
#
# Deliberately NOT a git operation. `git mv` operates inside a repository; this changes
# where the repository root lives. Git needs no help -- .git travels with the folder --
# but the global safe.directory entry does need updating, which is the last step here.

$ErrorActionPreference = 'Stop'

$old = 'D:\YohannaPaper'
$new = 'D:\urban-agriculture-nigeria-spatial'

if (-not (Test-Path -LiteralPath $old)) { throw "source not found: $old" }
if (Test-Path -LiteralPath $new) { throw "destination already exists: $new" }

$here = (Get-Location).Path
if ($here -like "$old*") { throw "cwd is inside $old ($here); run me from D:\ instead" }

Write-Host "moving $old -> $new"
Move-Item -LiteralPath $old -Destination $new

if (-not (Test-Path -LiteralPath $new)) { throw "move reported success but $new is missing" }
if (Test-Path -LiteralPath $old) { throw "move reported success but $old still exists" }
Write-Host "  moved"

# The global safe.directory allow-list is keyed on the absolute path, so the old entry
# no longer covers this checkout and git would refuse to read it as a different owner.
$entries = git config --global --get-all safe.directory
if ($entries -notcontains $new.Replace('\', '/')) {
    git config --global --add safe.directory $new.Replace('\', '/')
    Write-Host "  added safe.directory $($new.Replace('\','/'))"
}

Push-Location $new
try {
    Write-Host "`n--- git status ---"
    git status --short --branch
    Write-Host "`n--- remote ---"
    git remote -v
    Write-Host "`n--- HEAD ---"
    git log --oneline -1
    Write-Host "`n--- tracked file count ---"
    (git ls-files | Measure-Object).Count
} finally {
    Pop-Location
}

Write-Host "`n--- the archive that must have travelled intact ---"
Get-ChildItem -LiteralPath "$new\abandoned" -Recurse -File | Measure-Object |
    ForEach-Object { Write-Host "  abandoned/: $($_.Count) files" }
Get-ChildItem -LiteralPath "$new\abandoned" -File | ForEach-Object { Write-Host "  $($_.Name)" }

Write-Host "`n--- the file that must NOT have been touched ---"
$thesis = Join-Path $new 'MR. YOHAN FINAL BINDING.docx'
if (Test-Path -LiteralPath $thesis) {
    $f = Get-Item -LiteralPath $thesis
    Write-Host ("  {0}  {1:N1} MB  last write {2}" -f $f.Name, ($f.Length / 1MB), $f.LastWriteTime)
} else {
    Write-Host "  not present at the repo root (it is git-ignored, but it is on disk)"
}

Write-Host "`n--- README + AGENTS.md agree on the new path ---"
(Select-String -Path "$new\README.md","$new\AGENTS.md" -Pattern 'urban-agriculture-nigeria-spatial' |
    Measure-Object).Count | ForEach-Object { Write-Host "  $_ mention(s)" }
