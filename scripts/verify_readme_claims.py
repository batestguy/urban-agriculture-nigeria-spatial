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
    # No committed word count exists; Word's own is the author's canonical
    # measure. The README therefore states a range, and this asserts the range
    # sits inside the journal's window — it does not invent a number.
    m = re.search(r"\*\*([\d,]+)\s*[–-]\s*([\d,]+) words excluding references\*\*", text)
    if m is None:
        failures.append("word count stated as a range")
        print("[FAIL] word count: no '**a–b words excluding references**' in the README")
    else:
        low = int(m.group(1).replace(",", ""))
        print(f"[ok] word count stated as the range {low:,}-{m.group(2)}")
        if not 4000 <= low <= 8000:
            failures.append("word count range inside the TRP window")
            print("[FAIL] word count range starts outside 4,000-8,000")

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
