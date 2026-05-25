"""Quick inspection of fetched OSM data — what we got, sizes, bbox."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "data" / "osm_modern.geojson").read_text())

# Find Amelia Island specifically
islands = [f for f in fc["features"] if f["properties"].get("place") == "island"]
print(f"\n=== {len(islands)} island feature(s) ===")
for i, f in enumerate(islands):
    p = f["properties"]
    print(f"  [{i}] {p.get('name','?')} | osm_id={f.get('id')} | type={f['geometry']['type']}")

# Marshes / wetlands
wets = [f for f in fc["features"] if f["properties"].get("natural") == "wetland"]
print(f"\n=== {len(wets)} wetland feature(s) ===")
named = [f for f in wets if f["properties"].get("name")]
print(f"  {len(named)} named")
for f in named[:15]:
    p = f["properties"]
    print(f"    {p.get('name','?')} | wetland={p.get('wetland','?')}")

# Egans Creek specifically
egan = [f for f in fc["features"] if "egan" in (f["properties"].get("name", "").lower())]
print(f"\n=== {len(egan)} Egan-named feature(s) ===")
for f in egan:
    p = f["properties"]
    print(f"  {p.get('name')} | type={f['geometry']['type']} | tags={list(p.keys())[:8]}")

# Rivers and main water
rivers = [f for f in fc["features"]
          if f["properties"].get("waterway") in ("river",)
          or "river" in (f["properties"].get("name", "").lower())]
print(f"\n=== {len(rivers)} river feature(s) (named or waterway=river) ===")
seen = set()
for f in rivers:
    n = f["properties"].get("name", "")
    if n and n not in seen:
        seen.add(n)
        print(f"  {n}")

# Coastline
coast = [f for f in fc["features"] if f["properties"].get("natural") == "coastline"]
print(f"\n=== {len(coast)} coastline segment(s) ===")
total_pts = sum(len(g["coordinates"]) if g["type"] == "LineString" else 0
                for f in coast for g in [f["geometry"]])
print(f"  total points: {total_pts}")
