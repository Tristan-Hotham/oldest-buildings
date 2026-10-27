"""Checking screenshots of index.html (desktop and phone widths) into a folder given as argv[1]."""
import sys, os
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w in (("desk", 1280), ("phone", 390)):
        pg = b.new_page(viewport={"width": w, "height": 900})
        LD = os.environ.get("LEAFLET_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/leaflet/dist")
        pg.route("**/leaflet.min.js", lambda r: r.fulfill(path=os.path.join(LD, "leaflet.js")))
        pg.route("**/leaflet.min.css", lambda r: r.fulfill(path=os.path.join(LD, "leaflet.css")))
        errs = []; pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + os.path.abspath(os.path.join(ROOT, "index.html"))); pg.wait_for_timeout(2500)
        sw = pg.evaluate("document.documentElement.scrollWidth"); print(name, "scrollWidth", sw, "errors", [e for e in errs if "tile" not in e and "arcgis" not in e][:5])
        pg.screenshot(path=f"{out}/{name}.png", full_page=True)
    b.close()
