#!/usr/bin/env python
r"""
fetch_osm_urban_ag.py — One-time Overpass API harvest for urban agriculture footprints.
Source: OpenStreetMap via Overpass API (attribution: OSM contributors, ODbL).
Frozen to data/raw/osm_<city>.csv + data/raw/provenance.json
Usage:
  conda activate C:\Users\TOSHIBA\ds-general
  python scripts/fetch_osm_urban_ag.py --city Abuja --city Lagos --out data/raw/osm_urban_ag.csv
"""
import argparse, json, csv, time, pathlib, sys
from datetime import datetime, timezone
try:
    import requests
except ImportError:
    requests = None

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]
OVERPASS_URL = OVERPASS_URLS[0]
CITIES = {
    "Abuja": (8.90, 7.15, 9.25, 7.65),       # approx bbox: (south, west, north, east)
    "Lagos": (6.35, 2.90, 6.75, 4.10),
    "Kano": (11.85, 8.35, 12.20, 8.70),
    "Port Harcourt": (4.70, 6.90, 4.95, 7.15),
    "Gombe": (10.20, 11.05, 10.40, 11.30),
}

# Per-tag templates — smaller queries reduce timeout risk vs 4-in-1 union
QUERY_TEMPLATES = [
    '[out:json][timeout:30];nwr["landuse"="allotments"]({bbox});out center tags;',
    '[out:json][timeout:30];nwr["landuse"="farmland"]({bbox});out center tags;',
    '[out:json][timeout:30];nwr["landuse"="farmyard"]({bbox});out center tags;',
    '[out:json][timeout:30];nwr["leisure"="garden"]({bbox});out center tags;',
]

def fetch_city(city, bbox):
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    headers = {"User-Agent": "urban-agriculture-nigeria-spatial/1.0 (batestguy/urban-agriculture-nigeria-spatial)"}
    if requests is None:
        raise RuntimeError("requests not installed — conda install requests")
    all_elements = []
    for q_tmpl in QUERY_TEMPLATES:
        q = q_tmpl.format(bbox=bbox_str)
        data = {"data": q}
        last_err = None
        for url in OVERPASS_URLS:
            try:
                r = requests.post(url, data=data, headers=headers, timeout=60)
                r.raise_for_status()
                # Overpass may return XML on error — ensure JSON
                j = r.json()
                all_elements.extend(j.get("elements", []))
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err is not None:
            print(f"  tag failed {q_tmpl[:30]}...: {last_err}", file=sys.stderr)
        time.sleep(1)
    # Dedupe by (type,id)
    seen = set()
    uniq = []
    for e in all_elements:
        key = (e.get("type"), e.get("id"))
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    return uniq

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--city", action="append", dest="cities", default=[], help="City name (repeatable)")
    p.add_argument("--out", default="data/raw/osm_urban_ag.csv")
    args = p.parse_args()
    cities = args.cities or list(CITIES.keys())
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for city in cities:
        bbox = CITIES.get(city)
        if not bbox:
            print(f"Unknown city {city}, skipping", file=sys.stderr)
            continue
        print(f"Fetching {city} {bbox} ...")
        try:
            els = fetch_city(city, bbox)
        except Exception as e:
            print(f"Failed {city}: {e}", file=sys.stderr)
            els = []
        for e in els:
            lat = e.get("lat") or e.get("center", {}).get("lat")
            lon = e.get("lon") or e.get("center", {}).get("lon")
            rows.append({"city": city, "osm_id": e.get("id"), "type": e.get("type"),
                         "lat": lat, "lon": lon,
                         "landuse": e.get("tags", {}).get("landuse"),
                         "leisure": e.get("tags", {}).get("leisure"),
                         "name": e.get("tags", {}).get("name","")})
        time.sleep(2)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["city","osm_id","type","lat","lon","landuse","leisure","name"])
        w.writeheader(); w.writerows(rows)
    prov = pathlib.Path("data/raw/provenance.json")
    prov.parent.mkdir(parents=True, exist_ok=True)
    entry = {"source": "OpenStreetMap Overpass API", "url": OVERPASS_URL,
             "cities": cities, "out": str(out), "n_rows": len(rows),
             "timestamp_utc": datetime.now(timezone.utc).isoformat(),
             "license": "ODbL — © OpenStreetMap contributors"}
    if prov.exists():
        try:
            prev = json.loads(prov.read_text(encoding="utf-8"))
            if isinstance(prev, list): prev.append(entry)
            else: prev = [prev, entry]
        except: prev = [entry]
    else: prev = [entry]
    prov.write_text(json.dumps(prev, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {out} and provenance to {prov}")

if __name__ == "__main__": main()
