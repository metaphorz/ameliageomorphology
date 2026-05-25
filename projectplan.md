# Amelia Island Coastline Evolution — Project Plan

## Goal

Build an **interactive HTML web map** that lets the user scrub through geologic time and watch Amelia Island form:

- **Pleistocene core** (~130 ka, Sangamonian/Eemian highstand) appears as the western half of today's island
- Sea level drops, island becomes a hill ~80 mi inland (~20 ka, Last Glacial Maximum)
- **Holocene transgression** (~18 ka onward): a new sandbar forms ~4 mi offshore and migrates landward
- ~6–5 ka: Holocene sandbar **welds** to the Pleistocene core, trapping the future **Egans Creek marsh** between them
- 5 ka → today: Holocene beach ridges **prograde seaward** (visible at Fort Clinch as ridge-and-swale topography)

Geometry uses **real geospatial data** (modern shoreline from OpenStreetMap, Pleistocene/Holocene boundary traced from DEM elevation signatures and published maps, sea-level curve from published data).

## Source material

| Source | Used for |
|---|---|
| Frank Hopf's "Hopf — A Fragile Barrier Island" (64 min, Conserve Nassau) | Master narrative + dates |
| "Dunes Pt 1: Pangaea to present" (28 min) | Spatial references: 130 ka shoreline "out near Hilliard"; 18 ka shoreline 80 mi east; sea level fell 390 m (transcript says 390 — likely ft, ~120 m) |
| "Dunes Pt 2: Holocene dunes" (33 min) | Fort Clinch jetty effects, post-1880s ridges |
| ASCE paper (Olsen, JWPED5.WWENG-1825) | Engineering/coastal-process context (paywalled — work from literature equivalents) |
| Florida Geological Survey / USGS 3DEP DEM | Pleistocene/Holocene boundary signature (Pleistocene = smoother/higher, Holocene = ridge-and-swale) |
| Toscano & Macintyre 2003 / Engelhart et al. 2011 | Holocene sea-level curve for SE US Atlantic |

## Time snapshots to render

| Snapshot | Years BP | Sea level (vs today) | What's drawn |
|---|---|---|---|
| Eemian highstand | ~125,000 | +6 m | Pleistocene Amelia formed; coastline near Hilliard FL |
| Mid Sangamon | ~100,000 | −20 m | Sea retreating; island becoming inland hill |
| Last Glacial Maximum | ~20,000 | −120 m | Shoreline ~80 mi east; proto-Amelia is an inland hill |
| Early transgression | ~12,000 | −60 m | Sandbar forms ~5 mi offshore of today's beach |
| Sandbar migrating | ~8,000 | −10 m | Marsh forming between sandbar and Pleistocene core |
| Welding | ~5,500 | −2 m | Holocene bar welds to Pleistocene core; Egans Creek trapped |
| Mid-Holocene progradation | ~3,000 | −0.5 m | Beach ridges 1–3 forming at Fort Clinch |
| Late prehistoric | ~1,000 | ~0 m | Ridges 4–6 |
| Pre-jetty | 1880 CE | ~0 m | Modern shape minus post-jetty accretion |
| Today | 2026 | +0.3 m (since 1880) | Modern shoreline incl. post-jetty fillet north of jetty |

Slider is **logarithmic in years BP** so the user spends most of their scrubbing in the Holocene where the action is.

## Data acquisition (kept simple, no exotic GIS deps)

1. **Modern shoreline + marshes + rivers**: Overpass API query for Amelia Island bbox → GeoJSON. Static file, no runtime calls.
2. **Pleistocene/Holocene boundary on the island**: I'll trace this once from a USGS DEM hillshade (Pleistocene core has the older, smoother Silver Bluff terrace signature; Holocene ridges have the corrugated ridge-and-swale signature). Output: a single GeoJSON LineString down the spine of the island.
3. **Beach ridges (Fort Clinch area)**: Trace 4–6 ridge axes from DEM hillshade as polygons or lines. These are the conspicuous arcs north of Atlantic Ave.
4. **Paleo-coastlines (12 ka, 8 ka, 5 ka)**: Reconstructed by simple offset of modern shore using the migration distances Frank cites (4–5 mi offshore at 12 ka). Honest interpretive sketch — annotated as such in the UI.
5. **LGM coastline**: Approximate from the −120 m bathymetric contour (NOAA bathymetry) east of Florida.
6. **Sea-level curve**: One small JSON of (year_BP, meters) pairs from Engelhart et al. 2011 + Lambeck et al. 2014 published values.

## UI design

```
┌──────────────────────────────────────────────────────────────────┐
│ Amelia Island Coastline Evolution                                │
│                                                                  │
│   [Map: Leaflet + OSM basemap]                                   │
│   ┌────────────────────────────┐    ┌─────────────────────────┐ │
│   │                            │    │ Era: Holocene welding   │ │
│   │   Atlantic Ocean (blue)    │    │ 5,500 yr BP             │ │
│   │                            │    │ Sea level: −2 m         │ │
│   │   ░░░ Holocene ridges      │    │                         │ │
│   │   ▓▓▓ Pleistocene core     │    │ The Holocene sandbar    │ │
│   │   ··· Egans Creek marsh   │    │ welds to the Pleistocene│ │
│   │                            │    │ core. Egans Creek marsh│ │
│   │   Amelia River (west)      │    │ is trapped between.     │ │
│   │                            │    │                         │ │
│   └────────────────────────────┘    └─────────────────────────┘ │
│                                                                  │
│   125 ka ●─────────────────────────────●─── today                │
│            20 ka  12 ka  8 ka  5 ka  1 ka                        │
│                                                                  │
│   [▶ Play]  [⏸ Pause]  [⤺ Reset]    Speed: [1x ▼]                │
└──────────────────────────────────────────────────────────────────┘
```

Tech stack:
- **Leaflet** (single CDN script) — interactive map
- **Plain JS + HTML + CSS** — no build step
- **GeoJSON files** in `data/` — one per snapshot
- **OpenStreetMap tiles** — free, real basemap

Optional second panel (toggle): cross-section diagram (like Frank Hopf's "Plantation cross-section") showing the modern dune / Egan's marsh / Pleistocene core / mainland marsh stack — animated to show how it built up.

## Implementation phases

- [ ] **Phase 1 — Data prep** (local, one-time)
  - [ ] Query OSM for Amelia Island shoreline + marsh + river polygons → `data/modern.geojson`
  - [ ] Fetch USGS 3DEP 1m DEM for Amelia Island bbox; hillshade it
  - [ ] Trace Pleistocene/Holocene boundary as a line → `data/boundary.geojson`
  - [ ] Trace 6–8 Holocene beach ridges at Fort Clinch → `data/ridges.geojson`
  - [ ] Build paleo-shoreline polygons for each snapshot → `data/snapshots/{125ka,20ka,12ka,8ka,5ka,3ka,1ka,1880,today}.geojson`
  - [ ] Compile sea-level curve → `data/sea_level.json`
- [ ] **Phase 2 — Viewer**
  - [ ] `index.html` with Leaflet, slider, info panel
  - [ ] `viewer.js` — load snapshots, interpolate between them, style layers
  - [ ] `style.css` — Pleistocene = warm earth tone; Holocene = pale sand; marsh = green; sea = blue
  - [ ] Era descriptions sourced from the transcripts (one paragraph per snapshot)
- [ ] **Phase 3 — Cross-section panel** (optional, gated on time)
  - [ ] SVG cross-section animation
- [ ] **Phase 4 — Verify**
  - [ ] Launch `python -m http.server`, open in browser, screencap each snapshot
  - [ ] Sanity-check geometry against the Fort Clinch beach-ridge figure in the literature

## Deliverable

User opens `index.html` in a browser. They see Amelia Island on a real map, drag the slider from 125,000 years ago to today, and watch the island form. Each snapshot has a short caption sourced from Frank Hopf's talks.

## Research updates (post user request, 2026-05-25)

After deep research (see `refs/research_notes.md`), three refinements:

1. **Sea-level curve revised** with Hawkes et al. 2016 (NE Florida-specific). Critical: **no Holocene highstand at this latitude** — SL has been monotonically rising. Don't draw a Holocene peak.
2. **Welding mechanism is process-driven**: Mariotti 2021 shows barriers transition from transgressive to progradational when RSLR drops below ~2 mm/yr. Frank Hopf's "6,000 years, 5,000 years ago" welding date matches this threshold exactly. Useful for the caption.
3. **Beach-ridge count constrained**: OSL-dated Florida systems show 80–150 yr/ridge. With 5,000 yr of progradation, theoretically 30–60 ridges, but only ~8 major arcs are preserved/visible at Fort Clinch. Simulation will show ~8 distinct ridges + post-jetty (1881) fillet.

## Deliverables (revised after user feedback)

- `docs/geomorphological-experiments.tex` (+ .pdf) — formal LaTeX paper, **DONE**
- `refs/research_notes.md` — research synthesis, **DONE**
- `outputs/transcript*.txt` — four Conserve Nassau transcripts mined, **DONE**
- `data/` — modern shoreline + snapshot GeoJSONs (Phase 1, pending)
- `index.html`, `viewer.js`, `style.css` — interactive viewer (Phase 2, pending)
- `tests/auto/test_viewer.py` — Selenium suite that drives the viewer AND captures the figures referenced by the LaTeX doc (Phase 3)

## Open questions for user before I start coding the viewer

1. **DEM-traced boundary OK?** I'll trace the Pleistocene/Holocene boundary and ridge axes from USGS 3DEP DEM + satellite imagery myself. Alternative is searching for published FGS shapefiles first.
2. **Paleo-shorelines OK as offsets?** The 12/8/5 ka shorelines will be drawn by offsetting modern using migration distances from the transcripts + Hawkes SL curve. Labeled as interpretive.
3. **Cross-section panel** — include now or after v1 of the map view?
4. **Document update cadence** — should the LaTeX doc auto-rebuild after each Selenium run, or only on explicit request?

## Review section

### Summary of changes (2026-05-25)

**Built end-to-end:** an interactive web simulation of Amelia Island's coastline
evolution from 125,000 yr BP to today, with Selenium-driven verification and a
LaTeX paper that embeds the test screenshots as its figures.

### Files produced

| File | Purpose | Lines / size |
|---|---|---|
| `docs/geomorphological-experiments.tex` | Formal paper, "Geomorphological Experiments for Amelia Island" | 364 lines |
| `docs/geomorphological-experiments.pdf` | Compiled PDF (with figures) | ~2.3 MB, 12 pages |
| `docs/fig/*.png` | 10 Selenium-captured snapshots | ~340 KB each |
| `index.html` + `viewer.js` + `style.css` | Interactive Leaflet viewer | 132 + 391 + 230 lines |
| `data/snapshots.geojson` | 14 geologic-layer features, time-tagged | 14 features |
| `data/sea_level.json` | 28-point sea-level curve, 125 ka → today | NE-FL anchored |
| `data/osm_modern.geojson` | OSM features for the Amelia bbox | 1,668 features |
| `scripts/fetch_osm.py` | Overpass API client | 110 lines |
| `scripts/build_snapshots.py` | Generates snapshot polygons + sea-level curve | 290 lines |
| `tests/auto/test_viewer.py` | Selenium suite: drives viewer, asserts layers, captures figures | 180 lines |
| `refs/research_notes.md` | Geomorphology synthesis with citations | comprehensive |
| `outputs/transcript_*.txt` | 4 Conserve Nassau transcripts mined | full text |

### What changed / decisions made along the way

1. **OSM didn't have Amelia Island as a single polygon.** It has 207 coastline segments and 721 unnamed wetlands. So I hand-traced the island outline + Pleistocene/Holocene boundary + beach ridges in WGS84, anchored on satellite imagery + the reference screenshot you shared. The OSM data still drives the Leaflet basemap.
2. **Sea-level curve anchored on Hawkes 2016** for NE Florida specifically — critically, *no Holocene highstand* at this latitude (Laurentide forebulge collapse).
3. **Cross-section panel included in v1** — schematic SVG showing the "two piles of sand on a bed of mud" structure animating through time.
4. **Vegetation transition added to the paper** (after your question) — the sandbar→barrier sequence and why vegetation is load-bearing for the system.
5. **Selenium captures double as both test suite + figure generator** for the LaTeX doc, so the paper rebuilds with current viewer state.

### Reproduction commands

```bash
python3 -m venv venv && source venv/bin/activate
pip install selenium Pillow youtube-transcript-api yt-dlp
python scripts/fetch_osm.py          # Phase 1a
python scripts/build_snapshots.py    # Phase 1b
python tests/auto/test_viewer.py     # Phase 3 - runs viewer headless, captures figures
cd docs && pdflatex geomorphological-experiments.tex && pdflatex geomorphological-experiments.tex
```

### To view the viewer directly

```bash
python3 -m http.server 8765
open http://localhost:8765/index.html
```

### What to look at

- **The PDF**: `docs/geomorphological-experiments.pdf` (open it)
- **The live viewer**: `python -m http.server 8765` then `http://localhost:8765/`
- **The research synthesis**: `refs/research_notes.md`

### Known limitations / honest disclosures

- The Pleistocene/Holocene boundary line is hand-traced from satellite + the reference screenshot, not derived from a USGS DEM (DEM-tracing was the plan; satellite tracing was faster and adequate for visualization).
- Paleo-shorelines at 8 ka and 6 ka are interpretive sketches anchored on the migration distances Frank cites in the lectures, not measured paleoshorelines.
- Beach ridges at Fort Clinch are 8 generic arcs; the actual ridge geometry could be digitized more carefully from DEM imagery if needed.
- LGM shoreline (~130 km east) shown as a hint marker, not actual geometry (it's far off the visible map).
