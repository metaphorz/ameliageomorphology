"""Probe: what does the 0.00584-area Amelia polygon look like at its northern edge?"""
import json
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, polygonize
from shapely.geometry import box as _box
ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "data" / "osm_modern.geojson").read_text())

def inb(c, b):
    s,w,n,e = b
    return s<=c[1]<=n and w<=c[0]<=e

AMELIA_BBOX = (30.490, -81.510, 30.740, -81.410)
bp = _box(AMELIA_BBOX[1], AMELIA_BBOX[0], AMELIA_BBOX[3], AMELIA_BBOX[2])

lines = []
for f in fc["features"]:
    if f["properties"].get("natural") != "coastline":
        continue
    g = f["geometry"]
    if g["type"] == "LineString":
        coords = g["coordinates"]
        n_in = sum(1 for c in coords if inb(c, AMELIA_BBOX))
        if n_in >= 2:
            clipped = LineString(coords).intersection(bp)
            if clipped.is_empty: continue
            if clipped.geom_type == "LineString":
                if len(clipped.coords) >= 2:
                    lines.append(clipped)
            elif clipped.geom_type == "MultiLineString":
                for sub in clipped.geoms:
                    if len(sub.coords) >= 2:
                        lines.append(sub)

merged = linemerge(lines)
ml = [merged] if merged.geom_type == "LineString" else list(merged.geoms)
print(f"linemerge: {len(ml)} resulting line(s)")
for i, l in enumerate(sorted(ml, key=lambda x: -x.length)[:5]):
    cs = list(l.coords)
    print(f"  line {i}: {len(cs)} pts, length={l.length:.4f}")
    print(f"    first: {cs[0]}")
    print(f"    last:  {cs[-1]}")
    lats = [c[1] for c in cs]
    print(f"    lat range: [{min(lats):.4f}, {max(lats):.4f}]")

polys = list(polygonize(ml))
print(f"\npolygonize: {len(polys)} polygons")
for i, p in enumerate(sorted(polys, key=lambda x: -x.area)[:3]):
    print(f"  polygon {i}: area={p.area:.5f}, bounds={[round(x,4) for x in p.bounds]}")
    # Print the highest-latitude exterior points
    coords = list(p.exterior.coords)
    coords_sorted = sorted(coords, key=lambda c: -c[1])
    print(f"    top 5 highest-lat exterior points:")
    for c in coords_sorted[:5]:
        print(f"      ({c[0]:.4f}, {c[1]:.4f})")
