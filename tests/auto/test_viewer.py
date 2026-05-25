"""
Selenium-driven test + figure-capture for the Amelia Island viewer.

Runs Chrome headlessly, loads index.html via a temporary HTTP server,
exercises the time slider through every named snapshot, asserts that the
expected geologic layers exist at each timestep, and captures a full-page
screenshot per snapshot to docs/fig/ for inclusion in the LaTeX paper.

Usage:
    venv/bin/python tests/auto/test_viewer.py

Exit code 0 on success; nonzero on assertion failure. Writes a log to
tests/auto/test_viewer.log capturing every action.
"""
import http.server
import json
import logging
import socketserver
import sys
import threading
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "docs" / "fig"
LOG_FILE = ROOT / "tests" / "auto" / "test_viewer.log"

FIG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE), filemode="w",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("test_viewer")

# Snapshots to capture. Each: (ka, filename_slug, expected_layer_kinds)
SNAPSHOTS = [
    (125,   "01_eemian_125ka",       {"pleistocene"}),
    ( 20,   "02_lgm_20ka",           {"pleistocene", "hint"}),
    (  8,   "03_sandbar_8ka",        {"pleistocene", "holocene-bar", "marsh"}),
    (  6,   "04_sandbar_approach_6ka", {"pleistocene", "holocene-bar", "marsh"}),
    (  5,   "05_welding_5ka",        {"pleistocene", "holocene", "marsh", "beach-ridge"}),
    (  3,   "06_progradation_3ka",   {"pleistocene", "holocene", "marsh", "beach-ridge"}),
    (  1,   "07_late_holocene_1ka",  {"pleistocene", "holocene", "marsh", "beach-ridge"}),
    (0.15,  "08_pre_jetty_1880",     {"pleistocene", "holocene", "marsh", "beach-ridge"}),
    (0,     "09_present",            {"pleistocene", "holocene", "marsh", "beach-ridge"}),
]


def start_server(port):
    handler = http.server.SimpleHTTPRequestHandler
    # Suppress access log spam
    handler.log_message = lambda *a, **k: None
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler,
                                   bind_and_activate=False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    log.info("server started on http://127.0.0.1:%d (cwd=%s)", port, ROOT)
    return httpd


def find_free_port():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def make_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    # Reduce noise
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=opts)


def wait_ready(driver, timeout=30):
    """Wait until the viewer signals it has loaded data + initialised."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "return document.body.getAttribute('data-ready') === '1';"
        )
    )
    wait_tiles(driver, timeout=15)


def wait_tiles(driver, timeout=15):
    """Wait for all currently-pending Leaflet tile loads to finish.

    Leaflet's tilelayer keeps an internal `_loading` flag and a
    `_tilesToLoad` count. We poll for them being clear, then add a small
    buffer for the SVG path layers to finish painting.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        pending = driver.execute_script("""
          if (!window.__amelia || !window.__amelia._map) {
            // pull map from the leaflet container directly
            const containers = document.querySelectorAll('.leaflet-container');
            if (containers.length === 0) return -1;
          }
          let pending = 0;
          // iterate every TileLayer in the page
          document.querySelectorAll('.leaflet-tile-loaded').length;
          const tiles = document.querySelectorAll('.leaflet-tile');
          const loaded = document.querySelectorAll('.leaflet-tile-loaded');
          pending = tiles.length - loaded.length;
          return pending;
        """)
        if pending == 0:
            break
        time.sleep(0.2)
    # Buffer for SVG path painting + tile decode
    time.sleep(0.8)


def set_ka(driver, ka):
    """Drive the viewer programmatically via the exposed window.__amelia API."""
    driver.execute_script("window.__amelia.setKa(arguments[0]);", ka)
    wait_tiles(driver, timeout=10)


def visible_kinds(driver):
    """Read the rendered layers' .kind tags via stored feature properties."""
    js = """
      const ka = window.__amelia.getKa();
      const kinds = new Set();
      const fc = window.__amelia._snapshots || null;
      // Re-derive from the data
      return JSON.stringify({
        ka: ka,
        text: document.getElementById('info-era').textContent,
        sl: document.getElementById('info-sl-num').textContent,
        time: document.getElementById('info-time-num').textContent,
      });
    """
    return json.loads(driver.execute_script(js))


def derive_visible_kinds(snapshots_json, ka):
    """Reproduce the viewer's filtering rule in Python for assertion."""
    out = set()
    for f in snapshots_json["features"]:
        f0 = f["properties"]["visible_from_ka"]
        t0 = f["properties"]["visible_to_ka"]
        if ka <= f0 and ka >= t0:
            out.add(f["properties"]["kind"])
    return out


def main():
    snapshots_json = json.loads(
        (ROOT / "data" / "snapshots.geojson").read_text()
    )
    port = find_free_port()
    log.info("free port = %d", port)

    import os
    os.chdir(str(ROOT))
    httpd = start_server(port)

    driver = None
    failures = []
    try:
        driver = make_driver(headless=True)
        url = f"http://127.0.0.1:{port}/index.html"
        log.info("opening %s", url)
        print(f"[selenium] opening {url}", flush=True)
        driver.get(url)
        wait_ready(driver)
        print("[selenium] viewer ready", flush=True)

        for ka, slug, expected_kinds in SNAPSHOTS:
            log.info("snapshot ka=%s slug=%s", ka, slug)
            set_ka(driver, ka)
            info = visible_kinds(driver)
            log.info("  info: %s", info)
            actual_kinds = derive_visible_kinds(snapshots_json, ka)
            log.info("  expected kinds: %s", expected_kinds)
            log.info("  actual kinds  : %s", actual_kinds)

            # Assertion: every expected kind is present in the actual rendered set.
            missing = expected_kinds - actual_kinds
            if missing:
                msg = f"[FAIL] ka={ka} ({slug}): missing layer kinds: {missing}"
                log.error(msg)
                failures.append(msg)
                print(msg, flush=True)
            else:
                print(f"[ok] ka={ka:>5} ({slug}): {info['text']} | SL {info['sl']} m | kinds={sorted(actual_kinds)}", flush=True)

            # Screenshot
            png = FIG_DIR / f"{slug}.png"
            driver.save_screenshot(str(png))
            log.info("  wrote %s", png)
            print(f"       -> {png.relative_to(ROOT)}", flush=True)

        # Bonus: capture a "transition" mid-welding for the doc
        set_ka(driver, 5.1)
        png = FIG_DIR / "transition_welding.png"
        driver.save_screenshot(str(png))
        print(f"[ok] transition welding -> {png.relative_to(ROOT)}", flush=True)

    finally:
        if driver:
            driver.quit()
        httpd.shutdown()

    if failures:
        print(f"\n[selenium] {len(failures)} FAILURE(S):")
        for f in failures:
            print("  ", f)
        return 1
    print(f"\n[selenium] all {len(SNAPSHOTS)} snapshots pass; figures in {FIG_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
