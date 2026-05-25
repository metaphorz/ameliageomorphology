"""Pull the actual jetty geometry from OSM at the St. Marys Entrance."""
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "osm_jetties.geojson"

# Tight bbox around the St. Marys River entrance jetties
BBOX = (30.680, -81.460, 30.760, -81.360)

OVERPASS = "https://overpass-api.de/api/interpreter"
# Jetties are usually tagged man_made=breakwater, man_made=pier, or
# man_made=groyne. Also try barrier=jetty.
QUERY = f"""
[out:json][timeout:60];
(
  way["man_made"="breakwater"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["man_made"="pier"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["man_made"="groyne"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["man_made"="jetty"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["barrier"="jetty"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
out geom;
"""

body = ("data=" + QUERY).encode("utf-8")
req = Request(OVERPASS, data=body, method="POST")
req.add_header("User-Agent", "amelia-geomorph/1.0")
print(f"POST overpass bbox={BBOX}", flush=True)
t0 = time.time()
with urlopen(req, timeout=120) as r:
    data = json.loads(r.read().decode("utf-8"))
print(f"received {len(data.get('elements', []))} elements in {time.time()-t0:.1f}s")

feats = []
for el in data.get("elements", []):
    tags = el.get("tags", {})
    if el.get("type") == "way" and "geometry" in el:
        coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
        feats.append({
            "type": "Feature",
            "id": f"way/{el['id']}",
            "properties": tags,
            "geometry": {"type": "LineString", "coordinates": coords},
        })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, indent=2))
print(f"wrote {OUT} with {len(feats)} features")
for f in feats:
    p = f["properties"]
    c = f["geometry"]["coordinates"]
    if not c: continue
    print(f"  {p.get('man_made') or p.get('barrier') or '?'}: "
          f"name='{p.get('name','')}' {len(c)} pts "
          f"({c[0][0]:.4f},{c[0][1]:.4f}) -> ({c[-1][0]:.4f},{c[-1][1]:.4f})")
