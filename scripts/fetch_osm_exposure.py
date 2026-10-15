#!/usr/bin/env python
"""fetch_osm_exposure.py - per-LGA OSM mapping-effort counts (exposure control).

Why this exists
---------------
`landuse=farmland` inside a rectangular city bounding box measures how much of a
place OpenStreetMap contributors have mapped at least as much as it measures urban
agriculture. Kano is the best-mapped state in Nigerian OSM, and Kano also has the
most "urban agriculture" points. Those two facts are not separable without an
independent measure of mapping effort.

The fix is an exposure offset: count *other* OSM features in the same polygon and
condition on it, so the agriculture signal is read per unit of mapped environment.

Method
------
For each LGA polygon exported by `analysis/spatial/05_export_lga_polys.R`, ask
Overpass for aggregate counts via `out count;` (returns one number, so responses are
tiny and the run is cheap and resumable):

  * `way["building"]` - built-environment mapped density (primary exposure proxy)
  * `way["highway"]`  - road-network mapped density (robustness proxy)

Polygon membership uses Overpass's `poly:` filter (point-in-polygon), which is more
faithful than a bounding box.

Env: C:\\Users\\TOSHIBA\\ds-general\\python.exe  (python 3.12, requests 2.34.2)
Run: python scripts/fetch_osm_exposure.py
Out: data/raw/osm_exposure_by_lga.csv  (+ provenance entry)
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "data" / "processed" / "lga_polys_for_overpass.csv"
OUT_CSV = ROOT / "data" / "raw" / "osm_exposure_by_lga.csv"
PROV = ROOT / "data" / "raw" / "provenance.json"

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
HEADERS = {"User-Agent": "YohannaPaper/1.1 (reproducibility audit; contact: repo owner)"}
SLEEP = 1.2

# tag -> output column
TAGS = {
    'way["building"]': "n_buildings",
    'way["highway"]': "n_highways",
}


def query(poly: str, selector: str, timeout: int = 90) -> int | None:
    """Return the aggregate element count for `selector` inside `poly`, or None on failure."""
    q = f'[out:json][timeout:{timeout}];{selector}(poly:"{poly}");out count;'
    body = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout + 30) as r:
                payload = json.loads(r.read())
            el = payload.get("elements", [])
            if el and "tags" in el[0]:
                return int(el[0]["tags"]["total"])
            return 0
        except Exception as exc:  # noqa: BLE001 - endpoint fallback is the point
            last = exc
            continue
    print(f"    all endpoints failed: {type(last).__name__}", file=sys.stderr)
    return None


def main() -> int:
    rows = list(csv.DictReader(IN_CSV.open(encoding="utf-8")))
    print(f"{len(rows)} LGAs to query x {len(TAGS)} selectors")

    done: dict[str, dict] = {}
    if OUT_CSV.exists():
        for r in csv.DictReader(OUT_CSV.open(encoding="utf-8")):
            done[r["gid2"]] = r
        print(f"resuming: {len(done)} already cached")

    fields = ["gid2", "state", "lga", "n", "kind", "n_vertices", *TAGS.values()]
    failed: list[str] = []

    for i, row in enumerate(rows, 1):
        gid = row["gid2"]
        prev = done.get(gid)
        if prev and all(prev.get(c, "") not in ("", None) for c in TAGS.values()):
            continue

        rec = {
            "gid2": gid,
            "state": row["state"],
            "lga": row["lga"],
            "n": row["n"],
            "kind": row["kind"],
            "n_vertices": row["n_vertices"],
        }
        for sel, col in TAGS.items():
            rec[col] = query(row["poly"], sel)
        done[gid] = {k: ("" if v is None else v) for k, v in rec.items()}

        if rec["n_buildings"] is None:
            failed.append(gid)

        # incremental write: the run is cheap to resume if interrupted
        with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in done.values():
                w.writerow({k: r.get(k, "") for k in fields})

        if i % 10 == 0 or i == len(rows):
            print(f"  {i}/{len(rows)}  last: {row['state']} / {row['lga']} "
                  f"-> buildings={rec['n_buildings']}")
        time.sleep(SLEEP)

    ok = sum(1 for r in done.values() if str(r.get("n_buildings", "")) not in ("", "None"))
    print(f"\nWrote {OUT_CSV.relative_to(ROOT)} : {ok}/{len(rows)} LGAs with counts")
    if failed:
        print(f"failed: {len(failed)} -> {failed[:12]}")

    prov = json.loads(PROV.read_text(encoding="utf-8")) if PROV.exists() else []
    prov.append({
        "source": "OpenStreetMap Overpass API (aggregate counts)",
        "url": ENDPOINTS[0],
        "query": 'way["building"] | way["highway"] inside LGA polygon, `out count;`',
        "out": str(OUT_CSV),
        "n_rows": ok,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "license": "ODbL - (c) OpenStreetMap contributors",
        "note": ("Per-LGA OSM mapping-effort control. Used as an exposure covariate so that "
                 "urban-agriculture density is not confused with OSM completeness. "
                 "Polygons simplified to 0.002 deg from GADM v4.1 via 05_export_lga_polys.R."),
    })
    PROV.write_text(json.dumps(prov, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"appended provenance entry ({len(prov)} total)")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
