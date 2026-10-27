"""r/dataisbeautiful collage for Still Standing (2400 x 3000 px).
Hero: every building and structure from before AD 1100 seen through a stone arch. The arch has twenty
voussoirs, each worth 5% of the survivors, coloured by what they were built for.
All numbers from ../data/results.json and ../data/buildings.csv. Run from this folder: python3 collage.py
"""
import os, json, math
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, PathPatch, Rectangle
from matplotlib.path import Path
from matplotlib.collections import PatchCollection

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
F = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=900); DISP7 = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=700)
SER = "Source Serif 4"; MONO = "IBM Plex Mono"
BG = "#F2EBDD"; FG = "#2A2622"; MUT = "#6B6358"; LAND = "#E4DACA"; EDGE = "#D2C6B1"; SLATE = "#4A5A70"; TERRA = "#B4532A"; MOSS = "#5E7A3A"
UCOL = ["#B4532A", "#4A5A70", "#C0892B", "#7E4A78", "#5E7A3A", "#2F7A80", "#B5677D", "#9A9384"]
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
D = pd.read_csv(os.path.join(ROOT, "data", "buildings.csv"), keep_default_na=False)
USES = list(R["uses"].keys())

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
fig.text(.045, .968, "Why do old buildings survive?", fontproperties=DISP, fontsize=46, color=FG, va="top")
fig.text(.047, .921, f"Every building and structure in Wikidata built before AD 1100: {R['n']:,} of them in {R['n_countries']} countries,\n"
         "seen through an arch. Each of its 20 stones is 5% of the survivors, coloured by what they were built for.",
         family=SER, fontsize=15.5, color=FG, va="top", linespacing=1.38)

# ---------- hero: map through an arch ----------
ax = fig.add_axes([.03, .405, .94, .465]); ax.set_aspect("equal"); ax.axis("off")
K = 1.15
x0, x1 = -25, 150; spring = 50 * K; a = (x1 - x0) / 2; b = 31; cx = (x0 + x1) / 2; ybot = -13 * K
th = np.linspace(0, np.pi, 200)
arch = np.r_[[[x1, ybot]], np.c_[cx + a * np.cos(th), spring + b * np.sin(th)], [[x0, ybot]]]
clip = PathPatch(Path(np.r_[arch, arch[:1]], closed=True), transform=ax.transData, facecolor="none", edgecolor="none")
ax.add_patch(clip)
ax.add_patch(PathPatch(Path(np.r_[arch, arch[:1]], closed=True), facecolor="#F8F3EA", edgecolor="none", zorder=0))
land = json.load(open("/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"))
polys = []
for f in land["features"]:
    g = f["geometry"]; cs = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for c in cs:
        q = np.array(c[0])
        if q[:, 0].max() < -40 or q[:, 0].min() > 170: continue
        polys.append(MPoly(np.c_[q[:, 0], q[:, 1] * K], closed=True))
pc = PatchCollection(polys, facecolor=LAND, edgecolor=EDGE, lw=.3, zorder=1); ax.add_collection(pc); pc.set_clip_path(clip)
for u in reversed(range(len(USES))):
    q = D[D.use == USES[u]]
    s = ax.scatter(q.lon, q.lat * K, s=3.2, c=UCOL[u], lw=0, alpha=.92, zorder=3 + (u == 0)); s.set_clip_path(clip)
# voussoirs: 20 stones, 5% each, largest remainder
shares = [R["uses"][u]["share"] * 20 for u in USES]; nst = [int(v) for v in shares]
for i in sorted(range(len(USES)), key=lambda i: -(shares[i] - nst[i]))[:20 - sum(nst)]: nst[i] += 1
cols = [UCOL[i] for i in range(len(USES)) for _ in range(nst[i])]
order = cols[:]  # place religious stones from the left springer over the crown, then the rest
T = 9.5; g = .012
for k in range(20):
    t0, t1 = np.pi - k / 20 * np.pi + g, np.pi - (k + 1) / 20 * np.pi - g
    tt = np.linspace(t0, t1, 12)
    inner = np.c_[cx + a * np.cos(tt), spring + b * np.sin(tt)]
    outer = np.c_[cx + (a + T) * np.cos(tt[::-1]), spring + (b + T * 1.15) * np.sin(tt[::-1])]
    ax.add_patch(MPoly(np.r_[inner, outer], closed=True, facecolor=order[k], edgecolor=BG, lw=1.2, zorder=6))
# pillars with masonry courses
for xa in (x0 - T, x1):
    ax.add_patch(Rectangle((xa, ybot), T, spring - ybot, facecolor=SLATE, edgecolor="none", zorder=6))
    for yy in np.arange(ybot + 8, spring, 8): ax.plot([xa, xa + T], [yy, yy], color=BG, lw=1, zorder=7)
ax.add_patch(Rectangle((x0 - T - 3, ybot - 4), (x1 - x0) + 2 * T + 6, 4, facecolor=FG, zorder=7))
# stone key
lx = x0 + 2; ly = ybot + 2
lab_pos = []
for i, u in enumerate(USES):
    if nst[i] == 0: continue
    lab_pos.append((i, u))
# callouts
def note(lon, lat, txt, dx, dy, ha="left"):
    ax.annotate(txt, xy=(lon, lat * K), xytext=(lon + dx, lat * K + dy), family=MONO, fontsize=10.5, color=FG, ha=ha, zorder=9,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.7))
cc = {c["country"]: c["n"] for c in R["countries"]}
note(138, 36, f"Japan {cc['Japan']:,}\nshrines, temples, kofun", -14, -30, "center")
note(12.5, 42.5, f"Italy {cc['Italy']:,}", -22, -24, "center")
note(-2, 53, f"UK {cc['United Kingdom']:,}", -4, 21, "center")
note(40.7, 34.75, f"Dura-Europos, Syria\n{R['dura_box']} excavated ruins", 14, -24)
note(31.1, 29.9, "Giza", 8, -26, "center")
ax.set_xlim(x0 - T - 5, x1 + T + 5); ax.set_ylim(ybot - 6, spring + b + T * 1.2 + 4)
# stone legend under the arch base
lgx = .06
for i, u in enumerate(USES):
    if nst[i] == 0: continue
    fig.patches.append(Rectangle((lgx, .392), .013, .011, transform=fig.transFigure, facecolor=UCOL[i], edgecolor="none"))
    t = fig.text(lgx + .018, .3975, f"{R['uses'][u]['label']} {nst[i]}", family=MONO, fontsize=10.5, color=FG, va="center")
    lgx += .026 + len(f"{R['uses'][u]['label']} {nst[i]}") * .0079

# ---------- big numbers ----------
bu = R["by_use"]
nums = [(f"{R['uses']['religious']['share'] * 100:.0f}%", TERRA, "were built for worship.\nHouses and palaces: " + f"{R['uses']['domestic']['share'] * 100:.0f}%.\nThe filter of time is holy."),
        (f"{bu['religious']['original'] * 100:.0f}%", MOSS, f"of religious buildings are still\nin religious use. Castles: {bu['defensive']['ruin_any'] * 100:.0f}%\nruined. Houses: {bu['domestic']['ruin_any'] * 100:.0f}% ruined."),
        (f"{R['remote_summary']['ruin_km']:.0f} km", SLATE, "median from a ruin to a city\nof 100,000 people. Buildings\nstill in use: " + f"{R['remote_summary']['inuse_km']:.0f} km."),
        (f"{R['audit']['fabric']['later']} of {R['audit']['n']}", FG, "hand-checked survivors are\nmostly younger walls on an\nolder foundation.")]
for i, (big, c, s) in enumerate(nums):
    x = .045 + i * .237
    fig.text(x, .36, big, fontproperties=DISP, fontsize=33, color=c, va="top")
    fig.text(x, .315, s, family=SER, fontsize=12.3, color=FG, va="top", linespacing=1.2)

# ---------- bottom left: built for -> today ----------
fig.text(.045, .232, "BUILT FOR  >  WHAT IT IS TODAY", family=MONO, fontsize=10.5, color=MUT)
segs = [("original", "in use", MOSS), ("changed", "", "#C0892B"), ("museum", "", "#2F7A80"), ("unknown", "standing", "#C9C0B0"), ("ruin", "ruin", TERRA), ("earthwork", "earthwork", "#7E4A78"), ("lost", "lost", FG)]
bx = fig.add_axes([.2, .07, .33, .15]); bx.axis("off")
us = ["religious", "defensive", "domestic", "funerary", "civic"]
for i, u in enumerate(us):
    x = 0
    for k, lab, c in segs:
        v = bu[u]["today"][k]; bx.barh(i, v, left=x, color=c, height=.62, lw=0)
        if lab and v > (len(lab) + 5) * .021: bx.text(x + .015, i, f"{lab} {v * 100:.0f}%", va="center", fontsize=9.6, family=MONO, color="white" if k != "unknown" else FG)
        x += v
    fig.text(.195, .07 + .15 * (1 - (i + .5) / len(us)) , R["by_use"][u]["label"].replace(" and ", " & "), family=MONO, fontsize=10.5, color=FG, ha="right", va="center")
bx.set_xlim(0, 1); bx.set_ylim(len(us) - .5, -.5)

# ---------- bottom right: survivors per century ----------
fig.text(.6, .232, "SURVIVORS PER CENTURY BUILT, AD 1 TO 1599", family=MONO, fontsize=10.5, color=MUT)
cxa = fig.add_axes([.6, .085, .36, .135]); C = R["centuries"]
cxa.bar([c["century"] for c in C], [c["n"] for c in C], color=[TERRA if c["century"] <= 11 else "#B7AC98" for c in C], width=.78)
cxa.set_yscale("log"); cxa.set_ylim(90, 16000); cxa.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
cxa.set_yticks([100, 1000, 10000]); cxa.set_yticklabels(["100", "1,000", "10,000"], family=MONO, fontsize=9.5, color=MUT)
cxa.set_xticks([1, 6, 11, 16]); cxa.set_xticklabels(["1st", "6th", "11th", "16th"], family=MONO, fontsize=9.5, color=MUT)
for s in ("top", "right", "left"): cxa.spines[s].set_visible(False)
cxa.spines["bottom"].set_color(EDGE); cxa.tick_params(length=0); cxa.set_facecolor(BG); cxa.grid(axis="y", color=EDGE, lw=.6); cxa.set_axisbelow(True)
cxa.text(1, 3000, f"{C[0]['n']} from the\n1st century", family=MONO, fontsize=9.5, color=TERRA)
cxa.text(9.1, 15000, f"{C[15]['n']:,} from the 16th", family=MONO, fontsize=9.5, color="#8A7F6C", va="top")

fig.text(.045, .012, f"Data: Wikidata (CC0) via QLever, pulled 27 Oct 2026: items classed as architectural structures with an inception before 1100 and coordinates;\n"
         f"comparison set 1100 to 1599. Countries: Natural Earth. Cities: GeoNames (CC BY 4.0). Hand check: English Wikipedia. Coverage is uneven (Japan,\n"
         f"Italy and the UK hold {R['top3_share'] * 100:.0f}% of records) and condition and use are partly inferred. Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         family=MONO, fontsize=9, color=MUT, linespacing=1.3, va="bottom")
fig.savefig(os.path.join(HERE, "still_standing.png"), facecolor=BG, dpi=200)
print("ok", nst)
