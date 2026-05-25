"""
Fetch Amelia Island geographic features from OpenStreetMap via the Overpass API.

Outputs: data/osm_modern.geojson with the modern shoreline polygon,
         Egans Creek, Amelia River, surrounding marsh tags.

This is real public-data geometry — it is the spatial anchor for every snapshot.
"""
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "osm_modern.geojson"

# Bounding box covering Amelia Island and the Nassau / Cumberland Sound mouths.
# south, west, north, east
BBOX = (30.490, -81.570, 30.755, -81.395)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Pull: natural=coastline, natural=wetland (marsh), waterway, place=island
# We use OSM's "out geom" to get coordinates inline.
QUERY = f"""
[out:json][timeout:60];
(
  way["natural"="coastline"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["natural"="wetland"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  relation["natural"="wetland"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["water"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  relation["water"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["waterway"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["place"="island"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  relation["place"="island"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
out geom;
"""


def fetch():
    body = ("data=" + QUERY).encode("utf-8")
    req = Request(OVERPASS_URL, data=body, method="POST")
    req.add_header("User-Agent", "amelia-geomorph/1.0 (paul; educational)")
    print(f"[osm] POST {OVERPASS_URL} bbox={BBOX}", flush=True)
    t0 = time.time()
    with urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    print(f"[osm] received {len(data.get('elements', []))} elements in {time.time()-t0:.1f}s", flush=True)
    return data


def to_geojson(data):
    feats = []
    for el in data.get("elements", []):
        t = el.get("type")
        tags = el.get("tags", {}) or {}
        if t == "way" and "geometry" in el:
            coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
            if len(coords) < 2:
                continue
            # closed way => polygon if it looks like an area tag
            is_area = any(k in tags for k in ("natural", "water", "place")) and coords[0] == coords[-1]
            geom = (
                {"type": "Polygon", "coordinates": [coords]}
                if is_area
                else {"type": "LineString", "coordinates": coords}
            )
            feats.append({
                "type": "Feature",
                "id": f"way/{el['id']}",
                "properties": {**tags, "_osm_type": "way"},
                "geometry": geom,
            })
        elif t == "relation" and "members" in el:
            outers, inners = [], []
            for m in el["members"]:
                if "geometry" not in m or m.get("type") != "way":
                    continue
                coords = [[p["lon"], p["lat"]] for p in m["geometry"]]
                if len(coords) < 2:
                    continue
                (outers if m.get("role") == "outer" else inners).append(coords)
            if not outers:
                continue
            # naive: treat as MultiPolygon with first ring per outer
            polys = []
            for ring in outers:
                if ring[0] != ring[-1]:
                    ring = ring + [ring[0]]
                polys.append([ring])
            feats.append({
                "type": "Feature",
                "id": f"rel/{el['id']}",
                "properties": {**tags, "_osm_type": "relation"},
                "geometry": {"type": "MultiPolygon", "coordinates": polys},
            })
    fc = {"type": "FeatureCollection", "features": feats}
    return fc


def main():
    try:
        data = fetch()
    except (URLError, HTTPError) as e:
        print(f"[osm] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    fc = to_geojson(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc))
    # quick categorical summary
    cats = {}
    for f in fc["features"]:
        p = f["properties"]
        k = p.get("natural") or p.get("water") or p.get("waterway") or p.get("place") or "?"
        cats[k] = cats.get(k, 0) + 1
    print(f"[osm] wrote {OUT} with {len(fc['features'])} features")
    print(f"[osm] categories: {cats}")


if __name__ == "__main__":
    main()
