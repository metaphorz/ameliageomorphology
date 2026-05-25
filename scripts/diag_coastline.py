"""Diagnose coastline structure in our OSM fetch."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "data" / "osm_modern.geojson").read_text())

coasts = [f for f in fc["features"] if f["properties"].get("natural") == "coastline"]
print(f"Total coastline features: {len(coasts)}")
type_counts = {}
for f in coasts:
    t = f["geometry"]["type"]
    type_counts[t] = type_counts.get(t, 0) + 1
print(f"Geometry types: {type_counts}")

# Look at LineString endpoints
linestrings = [f for f in coasts if f["geometry"]["type"] == "LineString"]
polys = [f for f in coasts if f["geometry"]["type"] == "Polygon"]
print(f"\n{len(linestrings)} linestrings, {len(polys)} polygons")

# Print bbox of all linestring coastlines combined
all_lon, all_lat = [], []
for f in linestrings:
    for lon, lat in f["geometry"]["coordinates"]:
        all_lon.append(lon)
        all_lat.append(lat)
print(f"\nLineString bbox: lon [{min(all_lon):.4f}, {max(all_lon):.4f}] "
      f"lat [{min(all_lat):.4f}, {max(all_lat):.4f}]")

# Find linestrings near the Amelia reference point (30.67, -81.46)
import math
def dist(p, q):
    return math.hypot(p[0]-q[0], p[1]-q[1])
nearby = []
for f in linestrings:
    coords = f["geometry"]["coordinates"]
    if len(coords) < 2: continue
    # Check first/last point distance from a known Amelia ocean-shore point
    pole = (-81.43, 30.67)  # Amelia Atlantic shore center
    p0 = coords[0]
    p1 = coords[-1]
    minD = min(dist(p0, pole), dist(p1, pole))
    nearby.append((minD, id(f), f, len(coords)))
nearby.sort(key=lambda x: x[0])
print(f"\nClosest 10 linestrings to Amelia Atlantic shore:")
for d, _, f, n in nearby[:10]:
    c0 = f["geometry"]["coordinates"][0]
    c1 = f["geometry"]["coordinates"][-1]
    print(f"  d={d:.4f} id={f.get('id')} n={n}  "
          f"({c0[0]:.4f},{c0[1]:.4f}) -> ({c1[0]:.4f},{c1[1]:.4f})")

# Also: closed polygons in coastline
print(f"\nClosed coastline polygons (first 10):")
for f in polys[:10]:
    g = f["geometry"]
    n = len(g["coordinates"][0])
    bbox_x = [c[0] for c in g["coordinates"][0]]
    bbox_y = [c[1] for c in g["coordinates"][0]]
    print(f"  id={f.get('id')} n={n} bbox=lon[{min(bbox_x):.4f},{max(bbox_x):.4f}] "
          f"lat[{min(bbox_y):.4f},{max(bbox_y):.4f}]")
