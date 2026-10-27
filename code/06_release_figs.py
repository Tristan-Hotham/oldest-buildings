"""Step 6: static figures for the blog (release/blog/b_*.png, 1520 px wide) and the paper (release/paper/fig*.png).
Light background, house palette, no titles inside images. All values from ../data/results.json and the data files.
"""
import os, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib import font_manager as fm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MPoly

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf"]:
    if os.path.exists(FD + f): fm.fontManager.addfont(FD + f)
MONO = "IBM Plex Mono"
BG, FG, MUT, RULE, LAND = "#F4EEE3", "#2A2622", "#6B6358", "#DCD2C1", "#E6DECF"
UCOL = ["#B4532A", "#4A5A70", "#C0892B", "#7E4A78", "#5E7A3A", "#2F7A80", "#B5677D", "#9A9384"]
TCOL = {"original": "#5E7A3A", "changed": "#C0892B", "museum": "#2F7A80", "unknown": "#B9B1A2", "ruin": "#B4532A", "earthwork": "#7E4A78", "lost": "#2A2622"}
plt.rcParams.update({"font.family": MONO, "font.size": 15, "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUT, "ytick.color": FG,
                     "axes.edgecolor": RULE, "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG})
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
D = pd.read_csv(os.path.join(ROOT, "data", "buildings.csv"), keep_default_na=False)
AU = pd.read_csv(os.path.join(ROOT, "data", "audit_sample.csv"), keep_default_na=False)
USES = list(R["uses"].keys()); UL = [R["uses"][u]["label"] for u in USES]
B = os.path.join(ROOT, "release", "blog"); P = os.path.join(ROOT, "release", "paper")
os.makedirs(B, exist_ok=True); os.makedirs(P, exist_ok=True)


def save(fig, name, fig_no=None):
    fig.savefig(os.path.join(B, f"b_{name}.png"), dpi=200)
    if fig_no: fig.savefig(os.path.join(P, f"fig{fig_no}_{name}.png"), dpi=200)
    plt.close(fig)


def clean(ax, left=True):
    for s in ("top", "right") + (("left",) if left else ()): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)


# ---------- 1 map ----------
land = json.load(open("/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"))
fig = plt.figure(figsize=(7.6, 5.6)); ax = fig.add_axes([0, .2, 1, .8])
polys = []
for f in land["features"]:
    g = f["geometry"]; cs = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for c in cs:
        a = np.array(c[0])
        if a[:, 0].max() < -25 or a[:, 0].min() > 160 or a[:, 1].max() < -40: continue
        polys.append(MPoly(a, closed=True))
ax.add_collection(PatchCollection(polys, facecolor=LAND, edgecolor="#D3C9B7", lw=.3))
for u in reversed(range(len(USES))):
    q = D[D.use == USES[u]]
    ax.scatter(q.lon, q.lat, s=2.2, c=UCOL[u], lw=0, alpha=.9, zorder=3 + (u == 0), label=f"{UL[u]}  {len(q):,}")
ax.set_xlim(-20, 150); ax.set_ylim(-12, 66); ax.set_aspect(1.15); ax.axis("off")
h, l = ax.get_legend_handles_labels()
fig.legend(h[::-1], l[::-1], loc="lower center", ncol=2, frameon=False, markerscale=4.5, prop={"family": MONO, "size": 11.5}, bbox_to_anchor=(.5, .0), columnspacing=1.4)
save(fig, "map", 1)

# ---------- 2 eras ----------
rows = [(e["era"], e["n"], e["use"], False) for e in R["eras"]] + [(e["era"], e["n"], e["use"], True) for e in R["later_eras"]]
fig, ax = plt.subplots(figsize=(7.6, 5.0)); fig.subplots_adjust(left=.24, right=.88, top=.86, bottom=.04)
ys = [i + (1 if r[3] else 0) for i, r in enumerate(rows)]
for y, (lab, n, mix, later) in zip(ys, rows):
    x = 0
    for u, k in enumerate(USES):
        v = mix[k]; ax.barh(y, v, left=x, color=UCOL[u], height=.72, alpha=.5 if later else 1, lw=0)
        if v > .07: ax.text(x + .008, y, f"{v * 100:.0f}%", va="center", fontsize=10, color="white")
        x += v
    ax.text(1.015, y, f"{n:,}", va="center", fontsize=11, color=MUT)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=11.5); ax.invert_yaxis()
for t, r in zip(ax.get_yticklabels(), rows): t.set_color(MUT if r[3] else FG)
ax.text(0, 6.15, "Comparison: built 1100 to 1599", fontsize=10.5, color=MUT, va="center")
ax.set_xlim(0, 1); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
hs = [plt.Rectangle((0, 0), 1, 1, color=UCOL[u]) for u in range(len(USES))]
fig.legend(hs, UL, loc="upper center", ncol=4, frameon=False, fontsize=9.6, bbox_to_anchor=(.53, 1.0), handlelength=1, columnspacing=1)
save(fig, "eras", 2)

# ---------- 3 fare ----------
us = [u for u in USES if u != "unknown"]; segs = ["original", "changed", "museum", "unknown", "ruin", "earthwork", "lost"]
SEGL = {"original": "Still in original use", "changed": "Changed use", "museum": "Museum", "unknown": "Standing, use not recorded", "ruin": "Ruin or site", "earthwork": "Earthwork", "lost": "Lost"}
fig, ax = plt.subplots(figsize=(7.6, 4.6)); fig.subplots_adjust(left=.35, right=.97, top=.82, bottom=.05)
for i, u in enumerate(us):
    x = 0; b = R["by_use"][u]
    for s in segs:
        v = b["today"][s]; ax.barh(i, v, left=x, color=TCOL[s], height=.66, lw=0)
        if v > .08: ax.text(x + .01, i, f"{v * 100:.0f}%", va="center", fontsize=10.5, color="white" if s != "unknown" else FG)
        x += v
ax.set_yticks(range(len(us))); ax.set_yticklabels([f"{R['by_use'][u]['label']}\n{R['by_use'][u]['n']:,}" for u in us], fontsize=11); ax.invert_yaxis()
ax.set_xlim(0, 1); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
hs = [plt.Rectangle((0, 0), 1, 1, color=TCOL[s]) for s in segs]
fig.legend(hs, [SEGL[s] for s in segs], loc="upper center", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(.55, 1.0), handlelength=1, columnspacing=1)
save(fig, "fare", 3)

# ---------- 4 curve ----------
C = R["centuries"]
fig, ax = plt.subplots(figsize=(7.6, 4.0)); fig.subplots_adjust(left=.12, right=.98, top=.95, bottom=.15)
ax.bar([c["century"] for c in C], [c["n"] for c in C], color=["#B4532A" if c["century"] <= 11 else "#A79C88" for c in C], width=.8)
ax.set_yscale("log"); ax.set_ylim(80, 20000); ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator()); ax.tick_params(axis="y", length=0); ax.set_yticks([100, 1000, 10000]); ax.set_yticklabels(["100", "1,000", "10,000"], fontsize=11)
ax.set_xticks(range(1, 17)); ax.set_xticklabels([str(i) for i in range(1, 17)], fontsize=10.5); ax.set_xlabel("Century AD of construction", fontsize=11, color=MUT)
ax.grid(axis="y", color=RULE, lw=.6); ax.set_axisbelow(True); clean(ax, left=False)
ax.text(1, 9000, "before 1100", color="#B4532A", fontsize=11.5); ax.text(12, 16000, "1100 to 1599", color="#8A7F6C", fontsize=11.5)
save(fig, "curve", 4)

# ---------- 5 compare (use mix and material) ----------
fig, axs = plt.subplots(1, 2, figsize=(7.6, 4.8), gridspec_kw={"width_ratios": [1.5, 1]}); fig.subplots_adjust(left=.335, right=.97, top=.86, bottom=.06, wspace=.62)
cb, ca = R["compare"]["before"], R["compare"]["after"]
ax = axs[0]; y = np.arange(len(us))
ax.barh(y - .18, [cb["use"][u] for u in us], height=.36, color=[UCOL[USES.index(u)] for u in us])
ax.barh(y + .18, [ca["use"][u] for u in us], height=.36, color=[UCOL[USES.index(u)] for u in us], alpha=.4)
for i, u in enumerate(us):
    ax.text(cb["use"][u] + .01, i - .18, f"{cb['use'][u] * 100:.0f}%", va="center", fontsize=9.5)
    ax.text(ca["use"][u] + .01, i + .18, f"{ca['use'][u] * 100:.0f}%", va="center", fontsize=9.5, color=MUT)
ax.set_yticks(y); ax.set_yticklabels([R["by_use"][u]["label"] for u in us], fontsize=10.5); ax.invert_yaxis(); ax.set_xlim(0, .8); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
ax.set_title("Original use", loc="left", fontsize=11.5, color=FG)
ax = axs[1]; ms = ["stone", "brick", "timber"]; y = np.arange(3)
ax.barh(y - .18, [cb["mat"][m] for m in ms], height=.36, color="#4A5A70"); ax.barh(y + .18, [ca["mat"][m] for m in ms], height=.36, color="#4A5A70", alpha=.4)
for i, m in enumerate(ms):
    ax.text(cb["mat"][m] + .02, i - .18, f"{cb['mat'][m] * 100:.0f}%", va="center", fontsize=9.5)
    ax.text(ca["mat"][m] + .02, i + .18, f"{ca['mat'][m] * 100:.0f}%", va="center", fontsize=9.5, color=MUT)
ax.set_yticks(y); ax.set_yticklabels(ms, fontsize=10.5); ax.invert_yaxis(); ax.set_xlim(0, 1.05); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
ax.set_title("Material", loc="left", fontsize=11.5, color=FG)
fig.legend([plt.Rectangle((0, 0), 1, 1, color="#777"), plt.Rectangle((0, 0), 1, 1, color="#777", alpha=.4)],
           [f"before 1100 ({cb['n']:,}; material {cb['n_mat']:,})", f"1100 to 1599 ({ca['n']:,}; material {ca['n_mat']:,})"], loc="upper center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(.55, 1.0))
save(fig, "compare", 5)

# ---------- 6 audit ----------
rowsA = ["in original use", "changed use or monument", "ruin or remains", "earthwork", "destroyed", "unclear"]
FAB = [("pre-1100", "Pre-1100 fabric survives", "#5E7A3A"), ("later", "Mostly later", "#B4532A"), ("unclear", "Unclear", "#B9B1A2")]
au = AU[~AU.checked_status.str.startswith("not checked")]
fig, ax = plt.subplots(figsize=(7.6, 3.6)); fig.subplots_adjust(left=.33, right=.98, top=.84, bottom=.04)
for i, r in enumerate(rowsA):
    q = au[au.checked_status == r]; q = q.assign(o=q.checked_fabric.map({f[0]: k for k, f in enumerate(FAB)})).sort_values("o")
    for j, f in enumerate(q.checked_fabric):
        ax.add_patch(plt.Rectangle((j * 1.1, i - .38), 1, .76, color=dict((a, c) for a, _, c in FAB)[f]))
ax.set_xlim(-.2, 18); ax.set_ylim(len(rowsA) - .5, -.6); ax.set_yticks(range(len(rowsA))); ax.set_yticklabels([r.capitalize() for r in rowsA], fontsize=11)
ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in FAB], [l for _, l, _ in FAB], loc="upper center", ncol=3, frameon=False, fontsize=10.5, bbox_to_anchor=(.6, 1.0))
save(fig, "audit", 6)

# ---------- 7 latitude and distance (blog only) ----------
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.8)); fig.subplots_adjust(left=.15, right=.97, top=.86, bottom=.08, wspace=.75)
ax = axs[0]; L2 = R["latbands"]; y = np.arange(len(L2))
ax.barh(y, [b["ruin_any"] for b in L2], color="#5E7A3A", height=.6)
for i, b in enumerate(L2): ax.text(b["ruin_any"] + .01, i, f"{b['ruin_any'] * 100:.0f}%", va="center", fontsize=10)
ax.set_yticks(y); ax.set_yticklabels([b["band"] + "°" for b in L2], fontsize=10.5); ax.invert_yaxis(); ax.set_xlim(0, .35); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
ax.set_title("Ruins or sites, by latitude", loc="left", fontsize=11, color=FG)
ax = axs[1]; ks = ["original", "unknown", "ruin", "earthwork", "lost"]; y = np.arange(len(ks))
v = [R["remote"][k]["km_median"] for k in ks]
ax.hlines(y, 0, v, color=RULE, lw=2); ax.scatter(v, y, s=70, c=[TCOL[k] for k in ks], zorder=3)
for i, x in enumerate(v): ax.text(x + 2, i, f"{x:.0f} km", va="center", fontsize=10)
ax.set_yticks(y); ax.set_yticklabels(["In original use", "Standing, use\nnot recorded", "Ruin or site", "Earthwork", "Lost"], fontsize=10); ax.invert_yaxis(); ax.set_xlim(0, 60); ax.set_xticks([]); clean(ax); ax.spines["bottom"].set_visible(False)
ax.set_title("Median km to a big city", loc="left", fontsize=11, color=FG)
save(fig, "remote")
print("figures written")
