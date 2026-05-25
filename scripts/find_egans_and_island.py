"""
Examine the OSM data to locate (a) the real Amelia Island coastline and
(b) Egans Creek so we can use them instead of hand-traced approximations.

Strategy:
- Egans Creek runs N-S through northern Amelia Island. We search OSM water
  features whose centroid falls inside a bbox tight on the creek's known
  position (between Atlantic Ave and Fort Clinch, longitude band ~-81.46
  to -81.44, lat ~30.66 to 30.72).
- For Amelia Island coastline, we look for coastline ways whose first and
  last points fall in the bbox surrounding Amelia (excluding Cumberland to
  the north and the mainland to the west).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "data" / "osm_modern.geojson").read_text())

# Egans Creek search bbox - tight on the known creek corridor
EGANS_BBOX = (30.660, -81.470, 30.730, -81.430)  # s, w, n, e

def centroid(coords):
    """Roughly: mean of coordinates."""
    flat = []
    def walk(c):
        if isinstance(c, list) and c and isinstance(c[0], (int, float)) and len(c) == 2:
            flat.append(c)
        elif isinstance(c, list):
            for x in c: walk(x)
    walk(coords)
    if not flat: return None
    return (sum(p[0] for p in flat)/len(flat), sum(p[1] for p in flat)/len(flat))

def in_bbox(pt, bbox):
    if not pt: return False
    lon, lat = pt
    s, w, n, e = bbox
    return s <= lat <= n and w <= lon <= e


print(f"\n=== Water/wetland/waterway in Egans Creek bbox ===")
print(f"bbox = {EGANS_BBOX}")
candidates = []
for f in fc["features"]:
    p = f["properties"]
    if p.get("natural") in ("water", "wetland") or p.get("waterway") or p.get("water"):
        c = centroid(f["geometry"]["coordinates"])
        if c and in_bbox(c, EGANS_BBOX):
            candidates.append((f, c))

print(f"Found {len(candidates)} water/wetland features")
candidates.sort(key=lambda x: -sum(1 for _ in str(x[0]["geometry"])))  # roughly bigger first
for f, c in candidates[:15]:
    p = f["properties"]
    t = f["geometry"]["type"]
    n_pts = (len(f["geometry"]["coordinates"][0]) if t in ("Polygon",)
             else len(f["geometry"]["coordinates"]) if t == "LineString"
             else "?")
    kind = p.get("natural") or p.get("waterway") or p.get("water") or "?"
    name = p.get("name", "")
    print(f"  {kind:10s} {t:12s} pts~{str(n_pts):>5s}  centroid=({c[0]:.4f},{c[1]:.4f})  name='{name}'  id={f.get('id')}")

# Amelia Island coastline assembly: collect coastline segments
print(f"\n=== Amelia Island coastline segments ===")
# Amelia Island bbox - excluding Cumberland (north of 30.74) and far west marsh.
AMELIA_BBOX = (30.49, -81.50, 30.73, -81.40)
coast_segs = []
for f in fc["features"]:
    if f["properties"].get("natural") != "coastline":
        continue
    coords = f["geometry"]["coordinates"]
    if not coords: continue
    # Check if both ends are in Amelia bbox
    first_in = in_bbox(coords[0], AMELIA_BBOX)
    last_in = in_bbox(coords[-1], AMELIA_BBOX)
    if first_in and last_in:
        coast_segs.append((f, len(coords)))

print(f"Found {len(coast_segs)} coastline segments fully in Amelia bbox")
total_pts = sum(n for _, n in coast_segs)
print(f"Total points: {total_pts}")
# Show a few
for f, n in coast_segs[:5]:
    c0 = f["geometry"]["coordinates"][0]
    c1 = f["geometry"]["coordinates"][-1]
    print(f"  segment {f.get('id')}: {n} pts, ({c0[0]:.4f},{c0[1]:.4f}) -> ({c1[0]:.4f},{c1[1]:.4f})")
