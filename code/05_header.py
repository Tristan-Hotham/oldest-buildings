"""Step 5: render ../header.png (1200x630 social card) with Playwright Chromium.
Fonts: FONT_DIR with Fraunces, Source Serif 4 and IBM Plex Mono TTFs (github.com/google/fonts); else system serif.
"""
import os, json, math
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
S = json.load(open(os.path.join(ROOT, "work", "site.json"))); R = S["R"]
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
COL = ["#B4532A", "#4A5A70", "#C0892B", "#7E4A78", "#5E7A3A", "#2F7A80", "#B5677D", "#9A9384"]
# equirectangular map, lon -12..145, lat -10..62
x0, x1, y0, y1 = -12, 145, -10, 62
W, H = 640, 640 * (y1 - y0) / (x1 - x0) * 1.25
pts = sorted([(r[1], r[0], r[3], r[7]) for r in S["r"] if x0 < r[1] < x1 and y0 < r[0] < y1], key=lambda p: -p[3])
dots = "".join(f'<circle cx="{(lo - x0) / (x1 - x0) * W:.1f}" cy="{(y1 - la) / (y1 - y0) * H:.1f}" r="2.1" fill="{COL[u]}" opacity=".85"/>' for lo, la, u, _ in pts)
ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
    ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
    ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")]) if os.path.isdir(FD) else ""
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:#F4EEE3;color:#2A2622;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:64px;top:66px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#6B6358;display:flex;gap:12px;align-items:center}}
.k b{{background:#7A3A1E;color:#F4EEE3;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:104px;margin:0;font:900 118px/.86 Fraunces,Georgia,serif;letter-spacing:-.02em;font-variation-settings:"SOFT" 50}}
h1 em{{font-style:normal;color:#B4532A}}
p{{position:absolute;left:64px;top:345px;width:470px;margin:0;font-size:25px;line-height:1.36;color:#3A342E}}
.f{{position:absolute;left:64px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#7C7468}}
svg.m{{position:absolute;right:16px;top:128px}}
.lg{{position:absolute;right:40px;bottom:36px;font:400 13px/1.5 'IBM Plex Mono',monospace;color:#6B6358;text-align:right}}
.lg i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 5px 0 14px}}
</style></head><body>
<div class="k"><b>Data study</b><span>The oldest buildings</span></div>
<h1>Still<br><em>standing</em></h1>
<p>{R['n']:,} buildings and structures from before AD 1100 on one map. {R['uses']['religious']['share'] * 100:.0f}% were built for worship. Why did they survive?</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg class="m" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">{dots}</svg>
<div class="lg"><i style="background:#B4532A"></i>religious<i style="background:#4A5A70"></i>defensive<i style="background:#5E7A3A"></i>tombs<i style="background:#C0892B"></i>houses<i style="background:#9A9384"></i>not clear</div>
</body></html>"""
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
print("header.png written")
