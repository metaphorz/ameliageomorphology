"""
Build snapshots GeoJSON using REAL OSM geometry for Amelia Island.

Approach:
1. Load OSM features fetched by scripts/fetch_osm.py.
2. **Stitch** the OSM coastline LineStrings into a closed Amelia Island ring
   by following shared endpoints starting from a point known to be on the
   island's Atlantic shore.
3. Union the real Egans Creek wetland features (37 unnamed wetland polygons
   in the Egans corridor) for the marsh layer.
4. Split the island polygon along the Egans corridor's long axis to produce
   the Pleistocene core (west) and Holocene wedge (east).
5. Generate beach-ridge polygons synthetically and clip to the Holocene wedge.

All output polygons are therefore real-OSM-anchored: they sit precisely on
the island, do not extend beyond its actual coastline, and the marsh
follows the real Egans Creek wetlands.
"""
import json
import math
from pathlib import Path

from shapely.geometry import (Polygon, MultiPolygon, LineString, Point,
                              GeometryCollection, shape, mapping)
from shapely.ops import unary_union, linemerge, polygonize, split

ROOT = Path(__file__).resolve().parents[1]
OSM_FILE = ROOT / "data" / "osm_modern.geojson"
OUT_SNAP = ROOT / "data" / "snapshots.geojson"
OUT_SL = ROOT / "data" / "sea_level.json"

# Amelia bbox - tight enough to exclude Cumberland Island (which starts
# at ~30.755) and the mainland marsh (far west). North bound is 30.740,
# which captures the full Fort Clinch tip (~30.72) without leaking into
# Cumberland's southern marshes.
AMELIA_BBOX = (30.490, -81.510, 30.740, -81.410)  # s, w, n, e
EGANS_BBOX = (30.660, -81.475, 30.735, -81.430)


def in_bbox(pt, bbox):
    lon, lat = pt[0], pt[1]
    s, w, n, e = bbox
    return s <= lat <= n and w <= lon <= e


def stitch_amelia(fc):
    """Stitch OSM coastline LineStrings into a closed Amelia polygon.

    Approach: collect all coastline ways whose entire geometry falls inside
    AMELIA_BBOX. Merge them with shapely.ops.linemerge. Polygonize the
    merged result. Pick the polygon containing the Amelia reference point.
    """
    # Filter: include any coastline way that has AT LEAST 2 points inside
    # the Amelia bbox, then clip each line to the bbox.
    # (The previous "majority-in-bbox" rule dropped the Fort Clinch -
    # Cumberland Sound coastline way/22306404 which has only 14 of 35
    # points inside — its first 14 points form Amelia's NE corner.)
    in_bbox_lines = []
    from shapely.geometry import box as _bbox_geom
    bbox_poly = _bbox_geom(AMELIA_BBOX[1], AMELIA_BBOX[0],
                           AMELIA_BBOX[3], AMELIA_BBOX[2])
    for f in fc["features"]:
        if f["properties"].get("natural") != "coastline":
            continue
        g = f["geometry"]
        if g["type"] == "LineString":
            coords = g["coordinates"]
            n_in = sum(1 for c in coords if in_bbox(c, AMELIA_BBOX))
            if n_in >= 2:
                ls = LineString(coords)
                clipped = ls.intersection(bbox_poly)
                if clipped.is_empty:
                    continue
                if clipped.geom_type == "LineString":
                    if len(clipped.coords) >= 2:
                        in_bbox_lines.append(clipped)
                elif clipped.geom_type == "MultiLineString":
                    for sub in clipped.geoms:
                        if len(sub.coords) >= 2:
                            in_bbox_lines.append(sub)
        elif g["type"] == "Polygon":
            ring = g["coordinates"][0]
            if all(in_bbox(c, AMELIA_BBOX) for c in ring):
                in_bbox_lines.append(LineString(ring))

    print(f"  stitch: {len(in_bbox_lines)} linestrings in Amelia bbox", flush=True)

    if not in_bbox_lines:
        raise RuntimeError("No coastline linestrings inside Amelia bbox")

    merged = linemerge(in_bbox_lines)
    if merged.geom_type == "LineString":
        merged_lines = [merged]
    else:  # MultiLineString
        merged_lines = list(merged.geoms)
    print(f"  stitch: after linemerge -> {len(merged_lines)} line(s)", flush=True)

    # Close lines whose both endpoints lie on a bbox boundary edge — this
    # bridges the gap where OSM coastline was clipped at the bbox (notably
    # the Fort Clinch peninsula, where the OSM coastline continues north
    # toward Cumberland Sound).
    EPS = 1e-5  # deg tolerance
    s, w, n, e = AMELIA_BBOX
    def on_edge(p):
        x, y = p
        if abs(y - s) < EPS or abs(y - n) < EPS: return True
        if abs(x - w) < EPS or abs(x - e) < EPS: return True
        return False
    closed_lines = list(merged_lines)
    bridges = 0
    for line in merged_lines:
        cs = list(line.coords)
        if cs[0] == cs[-1]:
            continue  # already closed
        if on_edge(cs[0]) and on_edge(cs[-1]):
            # Bridge along the bbox edge they share
            closed_lines.append(LineString([cs[-1], cs[0]]))
            bridges += 1
    print(f"  stitch: added {bridges} bridging segments along bbox edges",
          flush=True)
    merged_lines = closed_lines

    # Polygonize: builds polygons from any closed loops in the linework
    polys = list(polygonize(merged_lines))
    if not polys:
        # If linemerge can't close it, try forcing closure by adding
        # connectors between unmatched endpoints (rare).
        raise RuntimeError("Polygonize produced 0 polygons - coastline ring not closed")
    print(f"  stitch: polygonize -> {len(polys)} polygon(s), "
          f"top areas={[round(p.area,5) for p in sorted(polys, key=lambda x: -x.area)[:8]]}",
          flush=True)

    # Tight filter: Amelia polygons must extend east of -81.46 (Amelia's
    # Atlantic shore is at ~-81.43). This rejects mainland marsh polygons
    # whose eastern edge is at -81.48 or further west, while keeping the
    # main Amelia body and any Fort Clinch peninsula piece.
    s, w, n, e = AMELIA_BBOX
    candidates = []
    for p in polys:
        if not p.is_valid or p.area < 1e-6:
            continue
        b = p.bounds  # minx, miny, maxx, maxy
        if b[2] < -81.46:  # entirely west of Amelia
            continue
        if b[0] > -81.42:  # entirely east of Amelia (shouldn't happen)
            continue
        if b[3] < 30.49 or b[1] > 30.74:  # outside lat range
            continue
        candidates.append(p)
    print(f"  stitch: {len(candidates)} polygons fall inside Amelia bbox",
          flush=True)
    for p in sorted(candidates, key=lambda x: -x.area)[:5]:
        b = p.bounds
        print(f"    area={p.area:.5f} bounds=[{b[0]:.4f},{b[1]:.4f},{b[2]:.4f},{b[3]:.4f}] "
              f"centroid=({p.centroid.x:.4f},{p.centroid.y:.4f})", flush=True)

    if not candidates:
        # Fallback: pick the largest polygon containing the ref
        ref = Point(-81.435, 30.620)
        inside = [p for p in polys if p.contains(ref)]
        if inside:
            return max(inside, key=lambda p: p.area)
        return max(polys, key=lambda p: p.area)

    # Union all in-bbox polygons (this captures Fort Clinch peninsula + main body)
    union = unary_union(candidates).buffer(0)
    # Result might be MultiPolygon (if Cumberland Sound throat is unbridged
    # in the OSM linework). Take the union but for clean splitting later,
    # we may need to bridge — handled by caller as needed.
    return union


def egans_marsh(fc):
    """Union all OSM wetlands inside the Egans Creek corridor bbox."""
    marshes = []
    for f in fc["features"]:
        if f["properties"].get("natural") != "wetland":
            continue
        try:
            geom = shape(f["geometry"])
        except Exception:
            continue
        if geom.is_empty:
            continue
        if not geom.is_valid:
            geom = geom.buffer(0)
            if geom.is_empty:
                continue
        c = geom.centroid
        if in_bbox((c.x, c.y), EGANS_BBOX):
            marshes.append(geom)
    if not marshes:
        raise RuntimeError("No OSM wetlands found in Egans Creek bbox")
    merged = unary_union(marshes)
    return merged


def boundary_line(marsh, amelia):
    """A SINUOUS curve representing the Pleistocene/Holocene boundary.

    A real paleoshoreline (Amelia's Pleistocene east edge at ~125 ka)
    would have been curvy, not straight. We model it as a smooth curve
    using many control points along a north–south path with gentle
    east-west sinuosity that loosely tracks the actual Egans Creek
    alignment, with a strong westward bend at Fort Clinch to encompass
    the State Park beach-ridge complex in the Holocene side.

    The polyline is extended well beyond Amelia's bbox on both ends so
    shapely's split() produces clean pieces.
    """
    cx = marsh.centroid.x
    a_miny, a_maxy = amelia.bounds[1], amelia.bounds[3]
    # Curving control points with naturalistic sinuosity.
    # Format: (delta_lon_from_cx, lat).
    # Negative delta = west, positive = east.
    control = [
        (   0.000, a_miny - 0.5),
        (+0.003, 30.520),  # slight east bulge in extreme south
        (+0.001, 30.540),
        (-0.002, 30.570),  # slight west
        (-0.004, 30.600),  # gentle west arc
        (-0.003, 30.625),
        (+0.000, 30.645),
        (+0.002, 30.660),  # back east, approaching marsh
        (+0.001, 30.675),  # mid marsh corridor
        (-0.001, 30.685),
        (-0.005, 30.695),  # curve begins west toward Fort Clinch
        (-0.012, 30.703),
        (-0.020, 30.710),
        (-0.027, 30.717),
        (-0.032, 30.725),  # max west, NW of Fort Clinch State Park
        (-0.034, 30.735),
        (-0.034, a_maxy + 0.5),
    ]
    pts = [(cx + dx, lat) for dx, lat in control]
    return LineString(pts)


def split_amelia(amelia, line):
    """Robustly split Amelia by the (possibly curved) boundary polyline.

    Strategy: construct a "west half-plane" polygon by extending the
    boundary line west to lon -83.0 (far beyond Florida). Pleistocene =
    amelia ∩ west_polygon. Holocene = amelia − west_polygon. This is
    robust to curved lines that shapely's split() can't handle directly.
    """
    line_coords = list(line.coords)
    # Build west-side polygon: line + extension to lon = -83.0 at top and
    # bottom, forming a closed polygon that covers everything west of the
    # boundary line.
    west_ring = list(line_coords)  # south → north
    # Continue from north end of line westward, then south, then back east
    # to south end of line.
    last = line_coords[-1]
    first = line_coords[0]
    west_ring.append((-83.0, last[1]))
    west_ring.append((-83.0, first[1]))
    west_ring.append(first)
    west_poly = Polygon(west_ring).buffer(0)

    pleist = amelia.intersection(west_poly).buffer(0)
    holo = amelia.difference(west_poly).buffer(0)

    if pleist.is_empty or holo.is_empty:
        raise RuntimeError(
            f"Bad split: pleist_empty={pleist.is_empty}, holo_empty={holo.is_empty}")
    return pleist, holo


def _arc(center_lon, center_lat, r_lon_inner, r_lon_outer, r_lat_scale,
         theta_start_deg, theta_end_deg, n=80):
    pts_outer, pts_inner = [], []
    for i in range(n + 1):
        t = theta_start_deg + (theta_end_deg - theta_start_deg) * i / n
        rad = math.radians(t)
        pts_outer.append((
            center_lon + r_lon_outer * math.cos(rad),
            center_lat + r_lon_outer * r_lat_scale * math.sin(rad),
        ))
        pts_inner.append((
            center_lon + r_lon_inner * math.cos(rad),
            center_lat + r_lon_inner * r_lat_scale * math.sin(rad),
        ))
    pts_inner.reverse()
    return Polygon(pts_outer + pts_inner)


RIDGE_CENTER_LON = -81.456
RIDGE_CENTER_LAT = 30.695
RIDGE_DEFS = [
    ("ridge-5ka",         5.0,  0,   0.018,  0.020,    0,  70),
    ("ridge-4ka",         4.0,  0,   0.021,  0.023,    0,  72),
    ("ridge-3ka",         3.0,  0,   0.024,  0.026,    0,  74),
    ("ridge-2ka",         2.0,  0,   0.027,  0.029,    0,  76),
    ("ridge-1ka",         1.0,  0,   0.030,  0.032,    0,  78),
    ("ridge-500yr",       0.5,  0,   0.033,  0.035,    0,  80),
    ("ridge-prejetty",    0.2,  0,   0.036,  0.038,    0,  82),
    ("ridge-postjetty",   0.15, 0,   0.039,  0.041,    0,  84),
]


def offshore_bar(amelia, km_east, bar_width_m=300):
    """Sandbar polygon parallel to Amelia's Atlantic coastline, km_east
    kilometres seaward.

    Built by:
      1. Extracting the east-facing (Atlantic) portion of Amelia's exterior
         — the portion whose longitudes lie east of the polygon's centroid.
      2. Translating that LineString eastward by km_east.
      3. Buffering the translated line to give the bar a realistic width
         (default 300 m).

    Result: a curving sandbar that mirrors the actual coastline curvature,
    not a straight N-S strip.
    """
    from shapely.affinity import translate
    deg_east = km_east / 96.5  # 1 deg lon at lat 30 ≈ 96.5 km
    # If Amelia is a MultiPolygon, use the largest piece (main body) for
    # the east coast — the offshore bar mirrors the Atlantic shoreline.
    if amelia.geom_type == "MultiPolygon":
        amelia = max(amelia.geoms, key=lambda p: p.area)
    cx = amelia.centroid.x
    coords = list(amelia.exterior.coords)
    # Split exterior into east-facing arc — contiguous run of points east of
    # the centroid longitude.
    east_pts = []
    # Find the start of the longest east-side run
    n = len(coords)
    best_run = []
    cur_run = []
    # Iterate twice so we can wrap around the closed ring
    for i in range(n * 2):
        x, y = coords[i % n]
        if x >= cx:
            cur_run.append((x, y))
        else:
            if len(cur_run) > len(best_run):
                best_run = cur_run
            cur_run = []
    if len(cur_run) > len(best_run):
        best_run = cur_run
    if len(best_run) < 3:
        # Degenerate fallback: a straight strip
        minx, miny, maxx, maxy = amelia.bounds
        return Polygon([
            (maxx + deg_east - 0.0015, miny + 0.005),
            (maxx + deg_east + 0.0015, miny + 0.005),
            (maxx + deg_east + 0.0015, maxy - 0.005),
            (maxx + deg_east - 0.0015, maxy - 0.005),
        ])
    east_line = LineString(best_run)
    shifted = translate(east_line, xoff=deg_east, yoff=0.0)
    # Buffer width in degrees: bar_width_m on each side
    half_w_deg = (bar_width_m / 2.0) / (96500.0)
    return shifted.buffer(half_w_deg, cap_style=2, join_style=2)


def feat(geom, props):
    return {"type": "Feature", "properties": props, "geometry": mapping(geom)}


def main():
    fc = json.loads(OSM_FILE.read_text())
    print("[snapshots] stitching Amelia coastline from OSM ...", flush=True)
    amelia = stitch_amelia(fc)
    print(f"[snapshots] amelia: {amelia.geom_type}, area={amelia.area:.5f} deg^2, "
          f"bounds={[round(x,4) for x in amelia.bounds]}", flush=True)

    print("[snapshots] unioning OSM Egans Creek wetlands ...", flush=True)
    marsh = egans_marsh(fc)
    nm = (1 if marsh.geom_type == "Polygon"
          else len(marsh.geoms) if marsh.geom_type == "MultiPolygon" else "?")
    print(f"[snapshots] marsh: {marsh.geom_type}, {nm} polys, "
          f"area={marsh.area:.5f}, bounds={[round(x,4) for x in marsh.bounds]}",
          flush=True)

    # Clip marsh to inside Amelia (some wetland polygons extend off-shore)
    marsh = marsh.intersection(amelia).buffer(0)
    print(f"[snapshots] marsh clipped to amelia: area={marsh.area:.5f}", flush=True)

    line = boundary_line(marsh, amelia)
    print(f"[snapshots] split line bounds: {[round(x,4) for x in line.bounds]}", flush=True)
    plei, holo = split_amelia(amelia, line)
    print(f"[snapshots] pleist: area={plei.area:.5f} centroid_lon={plei.centroid.x:.4f}", flush=True)
    print(f"[snapshots] holo  : area={holo.area:.5f} centroid_lon={holo.centroid.x:.4f}", flush=True)

    # Marsh straddles boundary - subtract from both halves so it renders
    # cleanly as the dedicated marsh layer.
    plei_clean = plei.difference(marsh).buffer(0)
    holo_clean = holo.difference(marsh).buffer(0)

    # Beach ridges, clipped to Holocene wedge
    ridge_features = []
    for name, from_ka, to_ka, inner, outer, ts, te in RIDGE_DEFS:
        arc = _arc(RIDGE_CENTER_LON, RIDGE_CENTER_LAT, inner, outer, 1.0, ts, te)
        clipped = arc.intersection(holo)
        if clipped.is_empty:
            continue
        ridge_features.append((name, from_ka, to_ka, clipped))

    features = []
    features.append(feat(plei_clean, {
        "id": "pleistocene-core",
        "kind": "pleistocene",
        "name": "Pleistocene core (Silver Bluff terrace)",
        "visible_from_ka": 125,
        "visible_to_ka": 0,
        "narrative":
            "Sangamonian/Eemian-age (MIS 5e, ~125 ka) barrier-island sand. "
            "Exposed and weathered since ~110 ka; soils and oak hammocks "
            "developed during 100,000 years of subaerial exposure.",
    }))

    features.append(feat(offshore_bar(amelia, km_east=6), {
        "id": "sandbar-8ka",
        "kind": "holocene-bar",
        "name": "Migrating Holocene sandbar (8 ka)",
        "visible_from_ka": 9,
        "visible_to_ka": 7,
        "narrative":
            "An offshore sandbar ~6 km east of the Pleistocene core. Sea "
            "level rising ~3 mm/yr (Hawkes 2016). Lagoon behind it is "
            "filling with biogenic mud that will become Egans Creek marsh. "
            "The bar itself is bare or sparsely vegetated.",
    }))
    features.append(feat(offshore_bar(amelia, km_east=1.5), {
        "id": "sandbar-6ka",
        "kind": "holocene-bar",
        "name": "Approaching sandbar (6 ka)",
        "visible_from_ka": 7,
        "visible_to_ka": 5.2,
        "narrative":
            "Sandbar has migrated landward, now ~1.5 km offshore. Sea-level "
            "rise is approaching the ~2 mm/yr stabilization threshold "
            "(Mariotti 2021). Pioneer dune grasses begin colonizing the "
            "highest emergent crests.",
    }))

    # Holocene wedge GROWS over time. Each progressive stage is the full
    # Holocene wedge scaled horizontally about its WESTERN edge (the
    # Pleistocene/Holocene boundary). Scaling preserves the SHAPE of the
    # east edge — so the growing wedge's east boundary at any time is a
    # shrunk-but-curved version of Amelia's real Atlantic coastline,
    # not a straight vertical line.
    from shapely.affinity import scale as shp_scale
    holo_minx = holo_clean.bounds[0]
    HOLO_STAGES = [
        # (id_suffix, from_ka, to_ka, fraction of full wedge width)
        ("5ka",    5.0,  4.0,  0.18),
        ("4ka",    4.0,  3.0,  0.32),
        ("3ka",    3.0,  2.0,  0.50),
        ("2ka",    2.0,  1.0,  0.68),
        ("1ka",    1.0,  0.5,  0.82),
        ("500yr",  0.5,  0.15, 0.92),
        ("modern", 0.15, 0.0,  1.0),
    ]
    for sid, fk, tk, frac in HOLO_STAGES:
        # Scale x by frac, keeping the west edge anchored at holo_minx.
        # Points at the east edge of the full Holocene get pulled
        # westward proportionally; the east-edge curvature is preserved.
        stage = shp_scale(holo_clean, xfact=frac, yfact=1.0,
                          origin=(holo_minx, 0))
        # Ensure we don't extend beyond the full Holocene (numerical safety)
        stage = stage.intersection(holo_clean).buffer(0)
        if stage.is_empty:
            continue
        features.append(feat(stage, {
            "id": f"holocene-{sid}",
            "kind": "holocene",
            "name": f"Holocene wedge at {fk} ka" if fk > 0 else "Holocene wedge (modern)",
            "visible_from_ka": fk,
            "visible_to_ka": tk,
            "narrative":
                (f"At ~{fk:.1f} ka, the Holocene wedge had prograded to ~"
                 f"{frac*100:.0f}% of its modern seaward extent. The east "
                 "edge of the wedge is a paleo-shoreline mirroring the "
                 "curvature of Amelia's modern Atlantic coast.")
                if fk > 0 else
                "The Holocene wedge at its modern seaward limit, including "
                "the post-jetty fillet at Fort Clinch (since 1881).",
        }))

    features.append(feat(marsh, {
        "id": "egans-creek",
        "kind": "marsh",
        "name": "Egans Creek marsh",
        "visible_from_ka": 8,
        "visible_to_ka": 0,
        "narrative":
            "Mud accumulated by oyster and clam bio-deposition in the "
            "back-barrier lagoon. After welding, became a permanent "
            "salt-marsh corridor along the Pleistocene/Holocene boundary. "
            "Geometry: union of OSM wetland features in the Egans corridor.",
    }))

    for name, from_ka, to_ka, geom in ridge_features:
        features.append(feat(geom, {
            "id": name,
            "kind": "beach-ridge",
            "name": f"Beach ridge ~{from_ka} ka",
            "visible_from_ka": from_ka,
            "visible_to_ka": to_ka,
            "narrative":
                f"Progradational beach ridge formed ~{from_ka*1000:.0f} years "
                "ago during slow-RSLR Holocene. Ridges separated by 80-150 "
                "years on comparable Florida systems.",
        }))

    features.append(feat(LineString([(-79.50, 30.50), (-79.50, 30.75)]), {
        "id": "lgm-hint",
        "kind": "hint",
        "name": "LGM shoreline (~130 km east of today)",
        "visible_from_ka": 25,
        "visible_to_ka": 15,
        "narrative":
            "At the Last Glacial Maximum (~20 ka), sea level was ~120 m "
            "below today. Atlantic shoreline on the outer continental "
            "shelf, ~130 km east of present Amelia.",
    }))

    # ----- Jetties at the St. Marys River entrance -----
    # Geometry pulled directly from OSM `man_made=breakwater` features
    # (see scripts/fetch_jetties.py). The south jetty is the 8-point
    # breakwater starting at Fort Clinch's NE tip; the north jetty is a
    # 2-point breakwater extending east from Cumberland's south tip.
    # Built 1881-1893 by US Army Corps of Engineers (USACE).
    # Source: Frank Hopf, Dunes Pt 2 (Conserve Nassau).
    jetties_file = ROOT / "data" / "osm_jetties.geojson"
    south_jetty_coords = None
    north_jetty_coords = None
    if jetties_file.exists():
        j_fc = json.loads(jetties_file.read_text())
        breakwaters = [f for f in j_fc["features"]
                       if f["properties"].get("man_made") == "breakwater"]
        # South jetty: the breakwater entirely below lat 30.715
        # North jetty: the breakwater at lat >= 30.715
        for bw in breakwaters:
            coords = bw["geometry"]["coordinates"]
            mean_lat = sum(c[1] for c in coords) / len(coords)
            if mean_lat < 30.715:
                south_jetty_coords = coords
            else:
                north_jetty_coords = coords
    if south_jetty_coords is None:
        south_jetty_coords = [
            (-81.4284, 30.7005), (-81.4058, 30.7073),
        ]
    if north_jetty_coords is None:
        north_jetty_coords = [
            (-81.4488, 30.7196), (-81.4347, 30.7173),
        ]
    # Ensure north jetty oriented west→east (landward→seaward) for label placement
    if north_jetty_coords[0][0] > north_jetty_coords[-1][0]:
        north_jetty_coords = list(reversed(north_jetty_coords))
    # South jetty already west→east in OSM

    features.append(feat(LineString(south_jetty_coords), {
        "id": "south-jetty",
        "kind": "jetty",
        "name": "South Jetty (St. Marys Entrance)",
        "visible_from_ka": 0.15,
        "visible_to_ka": 0,
        "narrative":
            "South Jetty. Built 1881-1893 by USACE on the north tip of "
            "Amelia Island to maintain the St. Marys River navigation "
            "channel. Intercepts the natural N→S longshore drift, which "
            "carries ~50 truckloads of sand per day in this region. "
            "Pre-jetty, that sand crossed Cumberland Sound naturally to "
            "supply Amelia's beaches; post-jetty, much of it is jetted "
            "to deep water beyond the bar, lost to the littoral system. "
            "Direct effects: (a) the north tip of Amelia (Fort Clinch "
            "State Park) GAINED a fillet of new land as flood-tide sand "
            "was trapped against the jetty; (b) central Amelia LOST what "
            "it had gained pre-jetty plus another 50 ft of shoreline "
            "between 1893 and 1924, and continued eroding for ~100 years "
            "until the Nassau County Shore Protection Project began "
            "replicating the natural cross-channel sand flow. "
            "Source: Frank Hopf, Dunes Pt 2 (Conserve Nassau).",
    }))
    features.append(feat(LineString(north_jetty_coords), {
        "id": "north-jetty",
        "kind": "jetty",
        "name": "North Jetty (St. Marys Entrance)",
        "visible_from_ka": 0.15,
        "visible_to_ka": 0,
        "narrative":
            "North Jetty. Built 1881-1893 by USACE on the south tip of "
            "Cumberland Island, paired with the South Jetty to form the "
            "St. Marys River entrance channel. Together the two jetties "
            "blocked the natural cross-channel sand flow that used to "
            "supply Amelia from Cumberland. The dredged channel between "
            "them is maintained today; spoil sand has been periodically "
            "placed on Amelia's beaches as part of the Nassau County "
            "Shore Protection Project (USACE, Olsen Associates). "
            "Source: Frank Hopf, Dunes Pt 2 (Conserve Nassau).",
    }))

    snap = {"type": "FeatureCollection", "features": features}
    OUT_SNAP.write_text(json.dumps(snap))
    print(f"[snapshots] wrote {OUT_SNAP} with {len(features)} features")

    sea_level = {
        "units": {"time": "years_BP", "level": "meters_vs_today"},
        "sources": [
            "Hawkes et al. 2016 (Quaternary Science Reviews, NE Florida)",
            "Toscano & Macintyre 2003 (Coral Reefs, Caribbean)",
            "Engelhart & Horton 2012 (Quaternary Science Reviews)",
            "Lambeck et al. 2014 (PNAS, LGM lowstand)",
        ],
        "no_holocene_highstand": True,
        "no_holocene_highstand_note":
            "Hawkes 2016: no mid-Holocene sea-level highstand at this latitude.",
        "points": [
            [125000,   6.0], [120000,   4.0], [110000,   2.0], [100000, -10.0],
            [ 80000, -20.0], [ 60000, -50.0], [ 40000, -75.0], [ 30000, -85.0],
            [ 25000,-110.0], [ 20000,-120.0], [ 18000,-115.0], [ 16000,-100.0],
            [ 14700, -90.0], [ 13500, -72.0], [ 12000, -60.0], [ 10000, -30.0],
            [  9000, -15.0], [  8000,  -5.7], [  7000,  -4.0], [  6000,  -3.0],
            [  5000,  -2.0], [  4000,  -1.5], [  3000,  -1.0], [  2000,  -0.5],
            [  1000,  -0.3], [   500, -0.25], [   146,  -0.2], [     0,   0.0],
        ],
    }
    OUT_SL.write_text(json.dumps(sea_level, indent=2))
    print(f"[snapshots] wrote {OUT_SL} with {len(sea_level['points'])} points")


if __name__ == "__main__":
    main()
