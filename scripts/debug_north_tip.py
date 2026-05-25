"""Why does the stitched Amelia polygon stop at lat 30.7058 when the
actual Fort Clinch peninsula extends to ~30.72?

Find coastline ways with points in the missing area (lat 30.706 to 30.74).
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "data" / "osm_modern.geojson").read_text())

# Coastline ways with at least one point in the missing area
missing_band = (30.706, -81.50, 30.740, -81.40)  # s, w, n, e

def in_box(p, b):
    s, w, n, e = b
    return s <= p[1] <= n and w <= p[0] <= e

print("Coastline LineStrings with >=1 point in [lat 30.706-30.740, lon -81.50 to -81.40]:")
for f in fc["features"]:
    if f["properties"].get("natural") != "coastline":
        continue
    g = f["geometry"]
    if g["type"] != "LineString":
        continue
    coords = g["coordinates"]
    n_in = sum(1 for c in coords if in_box(c, missing_band))
    if n_in > 0:
        first = coords[0]
        last = coords[-1]
        # also show min/max lat of points in this way
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        print(f"  id={f.get('id')} n={len(coords)} n_in_band={n_in} "
              f"lat[{min(lats):.4f},{max(lats):.4f}] lon[{min(lons):.4f},{max(lons):.4f}] "
              f"first=({first[0]:.4f},{first[1]:.4f}) last=({last[0]:.4f},{last[1]:.4f})")

# Also list closed Polygon coastlines (small islands) in this region
print("\nCoastline Polygons (closed islands) in the missing band:")
for f in fc["features"]:
    if f["properties"].get("natural") != "coastline":
        continue
    g = f["geometry"]
    if g["type"] != "Polygon":
        continue
    ring = g["coordinates"][0]
    n_in = sum(1 for c in ring if in_box(c, missing_band))
    if n_in > 0:
        lats = [c[1] for c in ring]
        lons = [c[0] for c in ring]
        print(f"  id={f.get('id')} n={len(ring)} n_in={n_in} "
              f"lat[{min(lats):.4f},{max(lats):.4f}] lon[{min(lons):.4f},{max(lons):.4f}]")
