# Barrier Island Geomorphology — Research Notes

Synthesized for the Amelia Island simulation. Every claim cites a source. Frank Hopf's transcripts referenced as **C-N** (Conserve Nassau).

---

## 1. Formation theories (three classics + modern synthesis)

| Theory | Year | Mechanism | Status |
|---|---|---|---|
| **De Beaumont** | 1845 | Offshore bars built by wave shoaling, then emerge | Partial — flume tests can't grow bars above SL |
| **Gilbert (spit-accretion)** | 1885 | Longshore drift builds spit, storms breach it → island | Partial — works for some islands |
| **McGee (submergence)** | 1890 | Mainland coastal ridges drowned by rising sea, become islands | **Dominant theory** post-Hoyt |
| **Hoyt** | 1967 | Confirmed McGee via stratigraphy: no shoreface sediments below early barriers | Standard for Georgia Bight |

**Modern view (Mariotti 2021, others):** Self-organization — barriers emerge from feedback between sediment supply, accommodation space, and SL change. The three classical theories describe **endmembers**; real barriers like Amelia mix mechanisms over time.

[Wikipedia: Barrier Island](https://en.wikipedia.org/wiki/Barrier_island)
[Mariotti 2021, JGR Earth Surface](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020JF005867)

---

## 2. Two regimes a barrier can be in

| Regime | What's happening | Visible signature |
|---|---|---|
| **Transgressive (rolling over)** | SL rising fast OR sediment-starved; **overwash** moves sand landward; whole island migrates landward over its own back-barrier marsh | Washover fans on lagoon side; landward-migrating shoreline; no preserved ridges |
| **Regressive (progradational)** | Sediment supply > accommodation; new sand builds seaward of older shoreline | **Beach-ridge plains** (the arc pattern at Fort Clinch); seaward-younging |

Amelia today: **regressive on the Atlantic face** (ridges at Fort Clinch). Was transgressive 18–6 ka while the Holocene sandbar migrated landward toward the Pleistocene core.

**Critical threshold (Mariotti 2021):**
- SLR > ~5–10 mm/yr → transgressive, barriers ephemeral
- SLR < ~2 mm/yr → barriers stabilize, can prograde

[Self-Organization of Coastal Barrier Systems (Mariotti 2021)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020JF005867)
[Long-term washover fan accretion (Sci Reports 2020)](https://www.nature.com/articles/s41598-020-76521-4)

---

## 3. Bruun rule (and why it doesn't apply at Amelia today)

- Bruun 1962: shoreline retreat = (SLR × shoreface width) ÷ active shoreface depth
- Assumes equilibrium profile, all eroded sand goes offshore
- **Modified Bruun (Dean & Maurmeier 1983)** adds overwash + aeolian terms
- **Not applicable** to regressive/prograding coasts — Amelia's Atlantic face is gaining sand, not losing it

[Bruun Rule (Wikipedia)](https://en.wikipedia.org/wiki/Bruun_rule)
[Modified Bruun extended for landward transport](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1218&context=usarmyresearch)

---

## 4. Sea-level history — values used in the simulation

Built from: Toscano & Macintyre 2003 (Caribbean coral/mangrove), Engelhart & Horton 2012 (US Atlantic database), **Hawkes et al. 2016 (specifically NE Florida — most relevant)**, Lambeck et al. 2014 (global LGM).

| Time (yr BP) | RSL vs today | Source / phase |
|---|---|---|
| 125,000 | **+6 m** | Sangamonian/Eemian highstand (MIS 5e) — Pleistocene Amelia forms on Silver Bluff terrace |
| 110,000 | +2 m | MIS 5a/5c (minor highstands) |
| 80,000 | −20 m | MIS 5a→4 transition, glaciation accelerating |
| 30,000 | −80 m | Late Wisconsinan |
| **20,000** | **−120 to −130 m** | **LGM** — shore ~130 km east; proto-Amelia is an inland hill |
| 14,700–13,500 | −90 → −70 m | **Meltwater Pulse 1A**: ~18 m rise in 500 yr (~36 mm/yr) |
| 12,000 | −60 m | Younger Dryas slowdown |
| 11,500 | −55 m | Meltwater Pulse 1B (smaller) |
| 8,000 | **−5.7 m** | **Hawkes 2016 anchor** for NE FL |
| 6,000 | −3 m | SLR slowing; Holocene sandbar nears Pleistocene core |
| **5,000** | **−2 m** | **Welding event** — Holocene wedge fuses with Pleistocene core; Egans Creek marsh trapped |
| 4,000 | −1.5 m | Progradation begins at Fort Clinch |
| 2,000 | −0.5 m | Ridge generations 4–6 |
| 1880 CE | −0.2 m | Pre-jetty modern shape |
| 2026 CE | 0 m | Today |

**Critical finding for NE Florida (Hawkes 2016):** **NO Holocene highstand** in this region. SL has risen monotonically — different from regions farther north (Chesapeake) or south (Caribbean keys) that show a mid-Holocene highstand. Reflects collapse of the Laurentide forebulge.

[Hawkes 2016 NE Florida RSL (PDF)](https://www2.whoi.edu/site/coastalgroup/wp-content/uploads/sites/139/2021/07/Hawkes-2016-Relative-sea-level-change-in-northeastern-Florida-USA-during-the-last-8.0-KA.pdf)
[Engelhart & Horton 2012 US Atlantic database](https://www.sciencedirect.com/science/article/abs/pii/S0277379111002927)
[Toscano & Macintyre 2003 western Atlantic curve](https://www.semanticscholar.org/paper/Corrected-western-Atlantic-sea-level-curve-for-the-Toscano-Macintyre/7d84a00d3229cfdd7b2a1751ea2b5394c91d6c12)
[Meltwater Pulse 1A (Wikipedia / Lin 2021)](https://www.nature.com/articles/s41467-021-21990-y)

---

## 5. Florida marine terraces (the substrate Amelia's Pleistocene core sits on)

| Terrace | Elevation | Likely age |
|---|---|---|
| **Silver Bluff** | +2 to +10.5 m | Sangamonian (MIS 5e ~125 ka) — Amelia's Pleistocene core |
| Pamlico | +2 to +10.5 m | Sangamonian |
| Talbot | +12 to +13 m | MIS 7 or older |
| Penholoway | +21 to +24 m | Earlier interglacial |
| Wicomico | +27 to +32 m | Earliest preserved Pleistocene highstand |

Amelia's Pleistocene core = Silver Bluff terrace age. Today it sits ~5–8 m above MSL — Frank Hopf shows this in his cross-sections (Plantation, Little Nana, Big Nana).

[Geology of Florida (Wikipedia)](https://en.wikipedia.org/wiki/Geology_of_Florida)
[USGS Geolex: Silver Bluff](https://ngmdb.usgs.gov/Geolex/UnitRefs/SilverBluffRefs_3832.html)

---

## 6. Georgia Bight specifics (Amelia is at the southern end)

**Hoyt & Hails (Pleistocene Shoreline Sediments in Coastal Georgia, *Science* 1967):** identified **six major Pleistocene shoreline complexes** in Georgia, each a former barrier-lagoon system. Today's Holocene wedge welded onto these older cores → "double island" pattern.

**"Double island" islands in the Georgia Bight (north → south):**
Hilton Head SC, Tybee, Wassaw, Ossabaw, St. Catherines, Sapelo, Little St. Simons, St. Simons, Jekyll, Cumberland, **Amelia**.

**Key processes during welding (Hoyt 1967, Mariotti 2021):**
1. As SLR slowed past ~5–7 ka, an offshore sandbar 3–5 mi out stopped retreating
2. The sandbar grew vertically and laterally; back-barrier accommodation filled with mud → marsh
3. Eventually the bar **welded** to the older Pleistocene island at one or both ends
4. Once welded, with continued slow SLR + abundant sediment, the seaward face began **prograding** (building beach ridges)

[The Georgia Bight Barrier System (Springer)](https://link.springer.com/chapter/10.1007/978-3-642-78360-9_7)
[Pleistocene Shoreline Sediments in Coastal Georgia (Hoyt & Hails 1967, Science)](https://www.science.org/doi/10.1126/science.155.3769.1541)
[Barrier islands of the central Georgia coast (2021)](https://www.researchgate.net/publication/356743317_Barrier_islands_of_the_central_Georgia_coast_Formation_function_and_future)

---

## 7. Beach-ridge progradation rates (key for Amelia's eastern accretion)

OSL-dated ridges in similar Florida systems:

| Site | Ridge interval | Land accretion rate |
|---|---|---|
| St. Vincent Island, FL | 78–148 yr/ridge | — |
| Cape Canaveral | ~80 yr/ridge | 135 m/century |
| Merritt Island | similar | similar |

Implication for Amelia: ~5,000 yr of progradation → ~30–60 ridges if continuous, but at Fort Clinch only **~8–15 major arcs** are visible — consistent with episodic ridge formation (storm-deposited), not all preserved. Frank Hopf's reference screenshot shows ~8 major arcs in Fort Clinch State Park.

**Post-jetty (1881 CE → present):** the Fernandina/Fort Clinch jetty trapped longshore-drifted sand on its south side, accelerating accretion at the **north end of Amelia**. This is the youngest ridge set Frank Hopf calls "Post-Jetty Dunes" — formed in 150 yr, not the natural 80–150 yr/ridge pace.

[Cape Canaveral/Merritt Island OSL dating (Rink & Forrest)](https://www.researchgate.net/publication/240778984_Dating_Evidence_for_the_Accretion_History_of_Beach_Ridges_on_Cape_Canaveral_and_Merritt_Island_Florida_USA)
[St. Vincent Island OSL ages](https://complete.bioone.org/journals/journal-of-coastal-research/volume-24/issue-sp1/05-0473.1/New-Quartz-Optical-Stimulated-Luminescence-Ages-for-Beach-Ridges-on/10.2112/05-0473.1.short)

---

## 8. Synthesis — narrative arc for the simulation

**Phase 0 — Pleistocene buildup (≥125 ka):**
Sangamonian highstand (+6 m) deposits sand on the Silver Bluff terrace. A barrier island forms on what will become Amelia's western half. Behind it: lagoon, salt marsh. Same system as the Georgia Bight neighbors. ⟶ **Pleistocene core polygon.**

**Phase 1 — Sea-level drop (125–20 ka):**
SL falls ~125 m over ~100 ky (with oscillations). Pleistocene Amelia is exposed, becomes an inland hill. Shoreline retreats ~130 km east to the LGM lowstand position on the outer continental shelf. ⟶ **LGM shoreline polygon** at the −120 m contour east of FL.

**Phase 2 — Transgression begins (20–8 ka):**
Deglaciation begins. Sea level rises rapidly (especially during MWP-1A at 14.7–13.5 ka, ~36 mm/yr). Multiple ephemeral barriers form on the shelf, drown, reform landward — **transgressive rollover** regime. ⟶ **Migrating offshore bar** sequence.

**Phase 3 — Sandbar approaches (8–5 ka):**
SL is now within −6 m of present and rising more slowly (~2–3 mm/yr in NE FL per Hawkes 2016). A persistent offshore sandbar forms ~4 mi east of the Pleistocene core. Behind it: protected lagoon where mud + biogenic processes build salt marsh (future Egans Creek). ⟶ **Sandbar + lagoon + marsh polygons.**

**Phase 4 — Welding (~5 ka):**
SLR drops below ~2 mm/yr (Mariotti's threshold). The Holocene sandbar welds to the Pleistocene island, first at the south end (per Frank Hopf). Egans Creek marsh permanently trapped between. ⟶ **Welding event snapshot** — both islands joined.

**Phase 5 — Progradation (5 ka → 1880 CE):**
With slow SLR + plentiful longshore sand from the north (St. Marys River), the Atlantic face builds seaward. Successive shorelines preserved as **beach ridges**, ~80–150 yr each. Most visible at Fort Clinch where the island's curve allowed maximum accretion. ⟶ **8 nested ridge polygons.**

**Phase 6 — Human modification (1880 CE → present):**
1881 — St. Marys Entrance jetty completed. Traps longshore drift on its south face. Amelia's north end gains an extra ~150 yr of accelerated accretion. Today: USACE manages a Nassau County Shore Protection Project. ⟶ **Post-jetty ridge polygon.**

---

## 9. What this tells the simulation

1. **SL curve is monotonic at NE FL** — no Holocene highstand. Don't draw one.
2. **The welding event is the visual climax** — must be obvious in the time-slider.
3. **Beach ridges should be ~8 distinct arcs**, not 50 — episodic preservation matches what's visible at Fort Clinch.
4. **The Pleistocene core is the larger, smoother polygon** on the west; the Holocene wedge is the corrugated eastern half. The boundary roughly follows Egans Creek.
5. **LGM shoreline matters for orientation** — it's ~130 km east, off the visible map. Show as an indicator, not literal geometry, when slider is at 20 ka.
6. **Cross-section view** would re-create Frank Hopf's Plantation cross-section and clarify "two piles of sand on a bed of mud." Worth including in v1 as a small inset.
