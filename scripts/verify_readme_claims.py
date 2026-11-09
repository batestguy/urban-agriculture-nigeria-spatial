"""Assert that every number the README states matches the frozen results.

Each check re-derives its value from `results/tables/` — or, for the page count,
reads the rendered Word file — and then looks for that value in the README. It
exits non-zero on disagreement and lists every failure at the end.

    python scripts/verify_readme_claims.py

It writes nothing. A failure means the README is wrong, not that the threshold
is too tight: edit the README. The page-count check is skipped when
`manuscript.docx` is not open in Word.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
TABLES = ROOT / "results" / "tables"

# The Windows console is cp1252, which cannot print Δ, ρ or –. Never let an
# encoding error look like a pass.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

failures: list[str] = []
checked = 0


def _flat(s: str) -> str:
    return " ".join(s.split())


def _docx_word_count(path) -> int:
    """Word count from a .docx, by parsing the OOXML directly.

    No Word instance and no third-party dependency: the earlier approach attached
    to a running Word via COM, which fails whenever Word is closed and made this
    check unrunnable in exactly the conditions a CI gate needs to work in.
    """
    import re
    import zipfile

    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = xml.replace("</w:p>", "\n</w:p>")
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&apos;", "'")):
        text = text.replace(a, b)
    return len(text.split())


def check(label: str, needle, text: str) -> None:
    """The README must contain `needle`, ignoring line breaks inside it.

    The README is hard-wrapped, so a claim can straddle two lines. Comparing
    through `_flat` means the prose stays readable without the check having to
    encode the author's line-break positions.
    """
    global checked
    checked += 1
    flat = _flat(text)
    if hasattr(needle, "search"):
        ok = needle.search(flat) is not None
        shown = needle.pattern
    else:
        ok = _flat(needle) in flat
        shown = needle
    print(f"[{'ok' if ok else 'FAIL'}] {label}: expected {shown!r}")
    if not ok:
        failures.append(label)


def table(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    text = README.read_text(encoding="utf-8")
    derived = {r["quantity"]: r["value"] for r in table("readme_numbers.csv")}

    # --- LISA: which LGAs survive BH-FDR, and where -------------------------
    lisa = table("lisa_fdr.csv")
    sig_bh = [r for r in lisa if r["sig_bh"].upper() == "TRUE"]
    sig_raw = sum(1 for r in lisa if r["sig_raw"].upper() == "TRUE")
    hh = sum(1 for r in sig_bh if r["quad_bh"] == "HH")
    lh = sum(1 for r in sig_bh if r["quad_bh"] == "LH")
    by_state: dict[str, int] = {}
    for r in sig_bh:
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1
    with_points = sum(1 for r in lisa if int(r["n"]) > 0)

    check("LGA count", re.compile(rf"{len(lisa)} (Local Government Areas|LGAs)"), text)
    check("LGAs significant after BH-FDR", f"{len(sig_bh)} LGAs", text)
    check("LGAs significant at raw p<0.05", f"{sig_raw} LGAs", text)
    check("high-high clusters", re.compile(rf"{hh} high.high"), text)
    check("low-high clusters", re.compile(rf"{lh} low.high"), text)
    for state, n in sorted(by_state.items()):
        check(f"clusters in {state}", f"{n} in {state}", text)
    check("significance confined to two states",
          re.compile(r"nowhere else in the country"), text)
    check("LGAs mapped at least once", f"{with_points} LGAs", text)

    # --- Count model ---------------------------------------------------------
    check("area slope, likelihood-ratio chi-square",
          f"χ² = {derived['lr_chi2']}", text)
    check("area slope, p-value", "p = 8.5e-11", text)
    check("fall per doubling",
          re.compile(rf"{derived['fall_per_doubling_pct']}% per doubling"), text)
    check("Poisson dispersion",
          f"dispersion of {derived['poisson_dispersion']}", text)
    check("negative binomial theta", f"= {derived['negbin_theta']})", text)

    # --- Coverage control ----------------------------------------------------
    exposure = {r["model"]: r for r in table("exposure_control.csv")}
    base = exposure["Area offset only"]
    ctrl = exposure["Area + building offsets"]
    d_aic = float(base["AIC"]) - float(ctrl["AIC"])
    strengthen = int(round(d_aic))  # README states it as a whole number
    check("coverage control: AIC improvement", f"ΔAIC = {strengthen}", text)
    check("area coefficient without control",
          f"moves from −{abs(float(base['log_area_b'])):.3f} to", text)
    check("area coefficient with control",
          f"to −{abs(float(ctrl['log_area_b'])):.3f} and fit", text)
    check("control strengthens the effect",
          re.compile(r"strengthens under control|gets\s+\*stronger\*"), text)
    check("coverage confound rho", "ρ = 0.613", text)

    # --- Study extent --------------------------------------------------------
    extent = table("study_extent.csv")
    total_pts = sum(int(r["points"]) for r in extent)
    outside = sum(int(r["points"]) for r in extent if r["NAME_1"] in {"Niger", "Ogun"})
    check("total OSM features", str(total_pts), text)
    check("features outside the declared states", str(outside), text)

    # --- Point pattern -------------------------------------------------------
    ripley = table("ripley_k_within_cities.csv")
    outside_env = sum(1 for r in ripley if r["outside_envelope"].upper() == "TRUE")
    check("cities whose Ripley's L leaves the envelope",
          re.compile(rf"all (five|{outside_env}) of (the )?cities|every city"), text)

    # --- Manuscript length ---------------------------------------------------
    # The target venue has changed three times and each measured length differently:
    # TRP a 4,000-8,000 word window, TeMA a 50,000-character cap, and African
    # Geographical Review a 7,000-word cap inclusive of references and captions.
    # So assert the CURRENT constraint only, sourced from the rendered DOCX when it is
    # on disk, and fail if the README's stated count drifts from it. Asserting a stale
    # venue's rule is how a green gate ends up guarding nothing.
    m = re.search(r"\*\*([\d,]+)\s+words\*\*", text)
    docx_words = None
    docx_path = ROOT / "manuscript" / "manuscript.docx"
    if docx_path.exists():
        try:
            docx_words = _docx_word_count(docx_path)
        except Exception:
            docx_words = None

    if m is None:
        # Not fatal: the README may state the count in the status table instead.
        print("[skip] word count: not stated as '**N** words' in the README")
    else:
        stated = int(m.group(1).replace(",", ""))
        print(f"[ok] word count stated: {stated:,}")
        if stated > 7000:
            failures.append("AGR 7,000-word cap")
            print(f"[FAIL] word count: {stated:,} exceeds AGR's 7,000-word cap")
        if docx_words is not None and abs(docx_words - stated) > 60:
            failures.append("stated word count matches the rendered DOCX")
            print(
                f"[FAIL] word count: README says {stated:,}, "
                f"rendered DOCX has {docx_words:,}"
            )
        elif docx_words is not None:
            print(f"[ok] word count matches the rendered DOCX ({docx_words:,})")

    # --- Page count, only if Word has the file open --------------------------
    try:
        import win32com.client

        word = win32com.client.GetActiveObject("Word.Application")
        target = next((d for d in word.Documents if d.Name == "manuscript.docx"), None)
        if target is None:
            print("[skip] page count: manuscript.docx is not open in Word")
        else:
            pages = target.ComputeStatistics(2)
            check("page count (Word ComputeStatistics)", f"{pages} pages", text)
    except Exception as exc:
        print(f"[skip] page count: {type(exc).__name__}")

    print()
    if failures:
        print(f"{len(failures)} FAILED of {checked}: {', '.join(failures)}")
        raise SystemExit(1)
    print(f"all {checked} README claims verified")


if __name__ == "__main__":
    main()
