"""Remove throwaway probe scripts from the repository root.

Scratch files are named with a leading underscore (`_probe.py`, `_t9.docx`, `_dis.txt`).
They are how this repo is explored without leaving debris in `scripts/`. Nothing here is
ever part of the research record: a probe worth keeping gets promoted into `scripts/` first.

Never removes dotfiles or tracked files.

    python scripts/clean_scratch.py            # list what would go
    python scripts/clean_scratch.py --delete   # remove it
"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tracked() -> set[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=False).stdout
        return {line.strip() for line in out.splitlines() if line.strip()}
    except OSError:
        return set()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delete", action="store_true")
    args = ap.parse_args()

    keep = tracked()
    candidates = [
        f for f in sorted(ROOT.iterdir())
        if f.is_file() and f.name.startswith("_") and not f.name.startswith(".")
        and f.name not in keep
    ]
    if not candidates:
        print("nothing to clean")
        return 0
    for f in candidates:
        if args.delete:
            f.unlink()
        print(("removed  " if args.delete else "would remove  ") + f.name)
    if not args.delete:
        print(f"\n{len(candidates)} file(s); re-run with --delete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
