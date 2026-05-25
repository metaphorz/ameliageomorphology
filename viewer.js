/* Amelia Island Coastline Evolution — viewer */
/* eslint-env browser */
'use strict';

const SVG_NS = 'http://www.w3.org/2000/svg';

const STATE = {
  snapshots: null,
  seaLevel: null,
  layerGroup: null,
  map: null,
  ka: 125,           // current time in thousands of years BP
  playing: false,
  playSpeed: 5,
  lastFrameTs: 0,
};

const ERAS = [
  { kaStart: 125, kaEnd: 110, name: "Eemian highstand (MIS 5e)",
    src: "Hawkes 2016; Toscano 2003",
    narrative:
      "Sea level stands ~6 m above today. The Pleistocene Amelia barrier " +
      "island forms on the Silver Bluff terrace. Behind it: a lagoon and " +
      "salt marsh, the same system that built neighboring Cumberland Island." },
  { kaStart: 110, kaEnd: 25, name: "Wisconsinan lowstand",
    src: "Lambeck 2014",
    narrative:
      "Sea level falls progressively to about –120 m as ice sheets grow. " +
      "The Pleistocene Amelia is exposed and slowly weathers — soils deepen, " +
      "slopes round, oak hammocks colonize. For 100,000 years it sits as " +
      "a hill on the dry continental shelf." },
  { kaStart: 25, kaEnd: 15, name: "Last Glacial Maximum",
    src: "Lambeck 2014; Clark 2009",
    narrative:
      "Sea level reaches its lowest at ~–120 m around 20 ka. The Atlantic " +
      "shoreline is ~130 km east of present Amelia, on the outer continental " +
      "shelf. The Pleistocene Amelia is an inland hill, far from any sea." },
  { kaStart: 15, kaEnd: 13, name: "Meltwater Pulse 1A",
    src: "Lin et al. 2021 (Nature Comm.)",
    narrative:
      "Deglaciation accelerates dramatically. Sea level rises ~18 m in 500 " +
      "years (~36 mm/yr). Any forming sandbars are repeatedly drowned and " +
      "reformed landward — the system is firmly transgressive (rollover)." },
  { kaStart: 13, kaEnd: 9, name: "Late transgression",
    src: "Engelhart 2012; Toscano 2003",
    narrative:
      "Sea-level rise slows somewhat. Ephemeral bars continue to migrate " +
      "landward across the shelf. No persistent island yet." },
  { kaStart: 9, kaEnd: 7, name: "Sandbar offshore",
    src: "Hawkes 2016",
    narrative:
      "By 8 ka, sea level is at –5.7 m (Hawkes 2016 anchor for NE Florida) " +
      "and a persistent Holocene sandbar has formed ~4 mi east of the " +
      "Pleistocene core. Behind it, a protected lagoon traps biogenic mud — " +
      "the future Egans Creek marsh begins to build." },
  { kaStart: 7, kaEnd: 5.2, name: "Sandbar approaches",
    src: "Mariotti 2021",
    narrative:
      "The sandbar has migrated landward, now about a mile offshore. Sea-" +
      "level rise is approaching the ~2 mm/yr threshold below which barriers " +
      "stabilize. Egans Creek marsh is well established between the two." },
  { kaStart: 5.2, kaEnd: 4.5, name: "Welding event",
    src: "Hoyt & Hails 1967; Mariotti 2021",
    narrative:
      "Around 5 ka, RSLR drops below the stabilization threshold. The " +
      "Holocene sandbar welds onto the Pleistocene core — first at the " +
      "south end, then propagating north. Egans Creek is permanently " +
      "trapped between the two. This is the moment Amelia becomes today's " +
      "double-island structure." },
  { kaStart: 4.5, kaEnd: 0.5, name: "Progradation",
    src: "Rink & Forrest 2005; Forrest 2008",
    narrative:
      "With slow RSLR and abundant longshore sand from the St. Marys River, " +
      "the Atlantic face begins to build seaward. Successive shorelines " +
      "preserved as beach ridges, ~80–150 years per ridge. Most visible " +
      "at Fort Clinch where the island's plan-form favors accretion." },
  { kaStart: 0.5, kaEnd: 0.15, name: "Late prehistoric",
    src: "Rink 2005",
    narrative:
      "Beach-ridge plain continues to build out. The island reaches roughly " +
      "its pre-modern geometry. Native Timucua peoples occupy the island." },
  { kaStart: 0.15, kaEnd: 0.05, name: "Pre-jetty (1880)",
    src: "USACE archival",
    narrative:
      "Just before 1881. Modern Amelia is essentially complete. The seaward " +
      "Atlantic face has not yet seen the human-induced fillet of accretion " +
      "that the St. Marys Entrance jetty will produce." },
  { kaStart: 0.05, kaEnd: 0, name: "Post-jetty / present",
    src: "USACE / Nassau County Shore Protection Project",
    narrative:
      "The St. Marys Entrance jetty (completed 1881, extended thereafter) " +
      "intercepts longshore drift. The north end of Amelia gains an extra " +
      "fillet — the post-jetty dune set — in just 150 years. Today the " +
      "USACE and the Nassau County Shore Protection Project manage " +
      "periodic beach nourishment on the developed central portion." },
];

function pickEra(ka) {
  for (const e of ERAS) {
    if (ka <= e.kaStart && ka >= e.kaEnd) return e;
  }
  return ERAS[0];
}

const SLIDER_STOPS = [
  [0, 125], [60, 80], [180, 25], [240, 15], [280, 13], [400, 9],
  [500, 7], [580, 5.2], [700, 4.5], [840, 0.5], [920, 0.15],
  [970, 0.05], [1000, 0],
];

function sliderToKa(v) {
  for (let i = 0; i < SLIDER_STOPS.length - 1; i++) {
    const [s0, k0] = SLIDER_STOPS[i];
    const [s1, k1] = SLIDER_STOPS[i + 1];
    if (v <= s1) {
      const f = (v - s0) / (s1 - s0);
      return k0 + (k1 - k0) * f;
    }
  }
  return 0;
}

function kaToSlider(ka) {
  for (let i = 0; i < SLIDER_STOPS.length - 1; i++) {
    const [s0, k0] = SLIDER_STOPS[i];
    const [s1, k1] = SLIDER_STOPS[i + 1];
    if (ka <= k0 && ka >= k1) {
      const f = (k0 - ka) / (k0 - k1);
      return s0 + (s1 - s0) * f;
    }
  }
  return 1000;
}

function sl(yrBP) {
  const pts = STATE.seaLevel.points;
  if (yrBP >= pts[0][0]) return pts[0][1];
  if (yrBP <= pts[pts.length - 1][0]) return pts[pts.length - 1][1];
  for (let i = 0; i < pts.length - 1; i++) {
    const [y0, v0] = pts[i];
    const [y1, v1] = pts[i + 1];
    if (yrBP <= y0 && yrBP >= y1) {
      const f = (y0 - yrBP) / (y0 - y1);
      return v0 + (v1 - v0) * f;
    }
  }
  return 0;
}

function styleFor(kind) {
  const m = {
    pleistocene: { fillColor: '#a47148', color: '#6e4e32', weight: 1, fillOpacity: 0.65 },
    'holocene-bar': { fillColor: '#f0deaf', color: '#b89a73', weight: 1, fillOpacity: 0.6, dashArray: '4 3' },
    holocene: { fillColor: '#e8d29a', color: '#b89a73', weight: 1, fillOpacity: 0.7 },
    marsh: { fillColor: '#6a8f4d', color: '#4f6e38', weight: 1, fillOpacity: 0.55 },
    'beach-ridge': { fillColor: '#d9b876', color: '#8e6a3c', weight: 0.8, fillOpacity: 0.85 },
    hint: { color: '#b94a3c', weight: 2, dashArray: '6 4' },
    jetty: { color: '#3a3a3a', weight: 4, opacity: 0.95 },
  };
  return m[kind] || { color: '#888', weight: 1 };
}

function visibleAt(feature, ka) {
  const f = feature.properties.visible_from_ka;
  const t = feature.properties.visible_to_ka;
  return ka <= f && ka >= t;
}

function renderLayers() {
  if (!STATE.snapshots || !STATE.map) return;
  STATE.layerGroup.clearLayers();
  const ka = STATE.ka;

  for (const ft of STATE.snapshots.features) {
    if (!visibleAt(ft, ka)) continue;
    const kind = ft.properties.kind;
    const style = styleFor(kind);
    let s = Object.assign({}, style);
    if (kind === 'pleistocene' && sl(ka * 1000) > 4) {
      s.fillOpacity = 0.25;
      s.dashArray = '3 3';
    }
    if (kind === 'jetty') {
      // Jetties get TWO Leaflet layers for the same geometry:
      //   - A wide TRANSPARENT line for easier mouse hit detection
      //     (Leaflet's hit testing only catches strokes within their
      //     own pixel width, so a 4px line is hard to hover.)
      //   - The visible thin black line drawn on top.
      // Both share a rich tooltip and click-popup.
      const tooltipEl = renderJettyPopup(ft.properties.name, ft.properties.narrative || '');
      const tooltipOpts = {
        sticky: true, direction: 'top', opacity: 0.97, className: 'jetty-tooltip',
      };
      // Hit area (thick, transparent) for easy mouse interaction
      const hit = L.geoJSON(ft, {
        style: { color: '#000', weight: 18, opacity: 0.001 },
      });
      hit.bindTooltip(tooltipEl, tooltipOpts);
      hit.bindPopup(tooltipEl.cloneNode(true), { maxWidth: 360, autoPan: true });
      hit.addTo(STATE.layerGroup);

      // Visible line
      const visible = L.geoJSON(ft, { style: s });
      visible.addTo(STATE.layerGroup);
    } else {
      const layer = L.geoJSON(ft, { style: s });
      layer.bindTooltip(ft.properties.name, { sticky: true });
      layer.addTo(STATE.layerGroup);
    }
  }
}

/**
 * Build an HTML element for the jetty rich tooltip/popup, using DOM
 * construction (no innerHTML) to avoid XSS pitfalls.
 */
function renderJettyPopup(name, narrative) {
  const root = document.createElement('div');
  root.className = 'jetty-popup';
  const h = document.createElement('div');
  h.className = 'jp-title';
  h.textContent = name;
  root.appendChild(h);
  const para = document.createElement('div');
  para.className = 'jp-body';
  para.textContent = narrative;
  root.appendChild(para);
  return root;
}

function updateInfo() {
  const ka = STATE.ka;
  const yrBP = ka * 1000;
  const era = pickEra(ka);
  const slm = sl(yrBP);

  document.getElementById('info-era').textContent = era.name;
  document.getElementById('info-narrative').textContent = era.narrative;
  document.getElementById('info-src').textContent = `Source: ${era.src}`;
  document.getElementById('info-sl-num').textContent = slm.toFixed(1);

  let timeLabel;
  if (ka >= 1) {
    timeLabel = `${(ka).toFixed(ka >= 10 ? 0 : 1)} ka`;
  } else if (ka >= 0.05) {
    const yearCE = 2026 - Math.round(yrBP);
    timeLabel = `${yearCE} CE`;
  } else if (yrBP > 5) {
    timeLabel = `${Math.round(yrBP)} years BP`;
  } else {
    timeLabel = `today`;
  }
  document.getElementById('info-time-num').textContent = timeLabel;
}

// ---------------------------------------------------------------------------
// Cross-section rendering — built via SVG DOM, no innerHTML.
// ---------------------------------------------------------------------------
function svgEl(tag, attrs) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) {
    if (attrs[k] !== undefined && attrs[k] !== null) el.setAttribute(k, attrs[k]);
  }
  return el;
}

function svgText(tag, attrs, text) {
  const el = svgEl(tag, attrs);
  el.textContent = text;
  return el;
}

function clearChildren(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function renderCrossSection() {
  const svg = document.getElementById('cross-svg');
  if (!svg) return;
  clearChildren(svg);

  const ka = STATE.ka;
  const slm = sl(ka * 1000);

  // Coordinate system: y = ELEV_Y0 - elevation_m * Y_PER_M
  // ELEV_Y0 = y-pixel for elevation 0 (today's sea level)
  // Lower y = higher elevation. Sea fills from seaY DOWN to y=160.
  // Today (slm=0): seaY = 100. Land tops are at y < 100 (above SL).
  const ELEV_Y0 = 100;
  const Y_PER_M = 0.5;
  const elevY = (m) => ELEV_Y0 - m * Y_PER_M;

  const seaY = elevY(slm);
  // Reference elevations (m above present SL)
  const PLIE_TOP_M = 6;
  const HOLO_TOP_M = 4;
  const MAIN_TOP_M = 8;
  const MARSH_TOP_M = 0;
  const BASE_M = -10;
  const SUBSTRATE_BOTTOM_M = -30;

  // Sea fill (from seaY down to the bottom of the svg)
  if (seaY < 160) {
    svg.appendChild(svgEl('rect', {
      x: 0, y: seaY, width: 600, height: 160 - seaY,
      fill: '#1f6fb5', opacity: 0.55,
    }));
  }
  // Mud / substrate (always)
  svg.appendChild(svgEl('rect', {
    x: 0, y: elevY(BASE_M), width: 600,
    height: elevY(SUBSTRATE_BOTTOM_M) - elevY(BASE_M),
    fill: '#7a6650', opacity: 0.7,
  }));
  // Mainland (with raised top)
  svg.appendChild(svgEl('path', {
    d: `M 0 ${elevY(BASE_M)} L 0 ${elevY(SUBSTRATE_BOTTOM_M)} ` +
       `L 110 ${elevY(SUBSTRATE_BOTTOM_M)} ` +
       `L 110 ${elevY(MAIN_TOP_M - 4)} ` +
       `L 60 ${elevY(MAIN_TOP_M)} Z`,
    fill: '#8a7e60', stroke: '#5d543f', 'stroke-width': 0.8,
  }));
  // Mainland marsh on the back side
  svg.appendChild(svgEl('rect', {
    x: 110, y: elevY(MARSH_TOP_M), width: 40,
    height: elevY(BASE_M) - elevY(MARSH_TOP_M),
    fill: '#6a8f4d', opacity: 0.85,
  }));

  // Pleistocene core (rounded dome)
  if (ka <= 125) {
    const plieY = elevY(PLIE_TOP_M);
    svg.appendChild(svgEl('path', {
      d: `M 150 ${elevY(BASE_M)} L 150 ${plieY + 4} ` +
         `Q 210 ${plieY - 4} 270 ${plieY + 4} ` +
         `L 270 ${elevY(BASE_M)} Z`,
      fill: '#a47148', stroke: '#6e4e32', 'stroke-width': 0.8,
      opacity: slm > PLIE_TOP_M - 1 ? 0.3 : 1,
    }));
    svg.appendChild(svgText('text', {
      x: 210, y: plieY - 6,
      'font-size': 9, 'text-anchor': 'middle', fill: '#5d4030',
    }, 'Pleistocene core'));
  }

  // Holocene wedge: grows in from 7 ka, full at <5 ka
  let holoFrac = 0;
  if (ka < 7 && ka >= 5.2) holoFrac = (7 - ka) / (7 - 5.2) * 0.4;
  else if (ka < 5.2) holoFrac = 0.4 + Math.min(1, (5.2 - ka) / 5) * 0.6;
  const holoY = elevY(HOLO_TOP_M * holoFrac);
  const holoX0 = 310, holoX1 = 470;

  // Egans Creek marsh
  let marshFrac = 0;
  if (ka <= 8 && ka >= 5) marshFrac = (8 - ka) / 3;
  else if (ka < 5) marshFrac = 1;
  if (marshFrac > 0) {
    const my = elevY(MARSH_TOP_M);
    svg.appendChild(svgEl('rect', {
      x: 270, y: my, width: 40,
      height: elevY(BASE_M) - my,
      fill: '#6a8f4d', opacity: 0.4 + 0.5 * marshFrac,
    }));
    if (marshFrac > 0.5) {
      svg.appendChild(svgText('text', {
        x: 290, y: my - 4, 'font-size': 8,
        'text-anchor': 'middle', fill: '#3a5028',
      }, "Egans"));
    }
  }

  if (holoFrac > 0) {
    svg.appendChild(svgEl('path', {
      d: `M ${holoX0} ${elevY(BASE_M)} L ${holoX0} ${holoY} ` +
         `L ${holoX1 - 4} ${holoY + 2} L ${holoX1} ${elevY(BASE_M)} Z`,
      fill: '#e8d29a', stroke: '#b89a73', 'stroke-width': 0.8,
    }));
    if (holoFrac > 0.4) {
      svg.appendChild(svgText('text', {
        x: 390, y: holoY - 6, 'font-size': 9,
        'text-anchor': 'middle', fill: '#7a5a20',
      }, 'Holocene wedge'));
    }
  }

  // Beach ridges along the east face of Holocene
  let ridgeCount = 0;
  if (ka <= 5) ridgeCount = Math.min(7, Math.round((5 - ka) * 1.6));
  if (ka <= 0.15) ridgeCount = 8;
  for (let i = 0; i < ridgeCount; i++) {
    svg.appendChild(svgEl('circle', {
      cx: holoX1 - 10 - i * 5, cy: holoY - 2, r: 3,
      fill: '#d9b876', stroke: '#8e6a3c', 'stroke-width': 0.5,
    }));
  }

  // Pre-weld sandbar - crests just above SL
  let barX = null;
  if (ka <= 9 && ka >= 7) barX = 545;
  else if (ka < 7 && ka >= 5.2) barX = 545 - ((7 - ka) / (7 - 5.2)) * 60;
  if (barX !== null) {
    const barTop = elevY(2);
    const barBase = elevY(MARSH_TOP_M);
    svg.appendChild(svgEl('path', {
      d: `M ${barX - 12} ${barBase} Q ${barX} ${barTop} ${barX + 12} ${barBase} ` +
         `L ${barX + 12} ${barBase + 4} L ${barX - 12} ${barBase + 4} Z`,
      fill: '#f0deaf', stroke: '#b89a73',
      'stroke-dasharray': '2 2', 'stroke-width': 0.8,
    }));
  }

  // Sea-level dashed line + label (label clamped to visible band)
  svg.appendChild(svgEl('line', {
    x1: 0, y1: seaY, x2: 600, y2: seaY,
    stroke: '#1f6fb5', 'stroke-dasharray': '3 3', 'stroke-width': 0.8,
  }));
  const labelY = Math.max(10, Math.min(155, seaY - 3));
  svg.appendChild(svgText('text', {
    x: 595, y: labelY, 'font-size': 9,
    'text-anchor': 'end', fill: '#134a7a',
  }, `SL ${slm.toFixed(1)} m`));

  // Compass markers
  svg.appendChild(svgText('text', {
    x: 6, y: 14, 'font-size': 9, fill: '#666',
  }, 'W (mainland) ←'));
  svg.appendChild(svgText('text', {
    x: 594, y: 14, 'font-size': 9, 'text-anchor': 'end', fill: '#666',
  }, '→ E (Atlantic)'));
}

function updateAll() {
  renderLayers();
  updateInfo();
  renderCrossSection();
}

function setKa(ka) {
  STATE.ka = ka;
  document.getElementById('time-slider').value = String(Math.round(kaToSlider(ka)));
  updateAll();
}

async function init() {
  const [snaps, seaLevel] = await Promise.all([
    fetch('data/snapshots.geojson').then(r => r.json()),
    fetch('data/sea_level.json').then(r => r.json()),
  ]);
  STATE.snapshots = snaps;
  STATE.seaLevel = seaLevel;

  // Center+zoom chosen so the view captures all of Amelia (south tip at
  // Nassau Sound ~30.50 to Fort Clinch tip ~30.72) plus the southern end
  // of Cumberland Island (down to ~30.74), with a little Atlantic margin
  // on the east for the offshore sandbar polygons at 8-6 ka.
  const map = L.map('map', { zoomControl: true }).setView([30.62, -81.45], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);
  STATE.map = map;
  STATE.layerGroup = L.layerGroup().addTo(map);

  const slider = document.getElementById('time-slider');
  slider.addEventListener('input', () => {
    const v = parseInt(slider.value, 10);
    STATE.ka = sliderToKa(v);
    updateAll();
  });

  document.querySelectorAll('.ticks span').forEach(s => {
    s.style.cursor = 'pointer';
    s.addEventListener('click', () => {
      const ka = parseFloat(s.dataset.ka);
      setKa(ka);
    });
  });

  document.getElementById('play-btn').addEventListener('click', togglePlay);
  document.getElementById('reset-btn').addEventListener('click', () => {
    STATE.playing = false;
    setPlayBtnLabel(false);
    setKa(125);
  });
  document.getElementById('speed-sel').addEventListener('change', (e) => {
    STATE.playSpeed = parseFloat(e.target.value);
  });

  setKa(125);
  document.body.setAttribute('data-ready', '1');
}

function setPlayBtnLabel(playing) {
  const btn = document.getElementById('play-btn');
  btn.textContent = playing ? '⏸ Pause' : '▶ Play';
}

function togglePlay() {
  STATE.playing = !STATE.playing;
  setPlayBtnLabel(STATE.playing);
  if (STATE.playing) {
    if (STATE.ka <= 0) setKa(125);
    STATE.lastFrameTs = performance.now();
    requestAnimationFrame(playStep);
  }
}

function playStep(ts) {
  if (!STATE.playing) return;
  const dt = (ts - STATE.lastFrameTs) / 1000;
  STATE.lastFrameTs = ts;
  const sliderDelta = dt * 6 * STATE.playSpeed;
  const cur = parseInt(document.getElementById('time-slider').value, 10);
  const next = cur + sliderDelta;
  if (next >= 1000) {
    setKa(0);
    STATE.playing = false;
    setPlayBtnLabel(false);
    return;
  }
  document.getElementById('time-slider').value = String(next);
  STATE.ka = sliderToKa(next);
  updateAll();
  requestAnimationFrame(playStep);
}

window.addEventListener('DOMContentLoaded', () => {
  init().catch(err => {
    console.error('init failed', err);
    document.getElementById('info-narrative').textContent =
      'Failed to load data: ' + (err && err.message ? err.message : String(err));
  });
});

// Expose for Selenium
window.__amelia = { setKa, getKa: () => STATE.ka, ERAS };
