"""Step 7: fill paper_template.tex from ../data/results.json and compile with xelatex into
../release/paper/ (tex, figures, PDF); copy the PDF to ../release/.
Placeholders {{path|fmt}} (int, pct0, km, f1, raw) and {{X:TABLE1}}, {{X:TABLE2}}.
"""
import os, re, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
P = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Still_Standing"
R = json.load(open(os.path.join(ROOT, "data", "results.json")))


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


esc = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}\\%"
    if f == "km": return f"{v:.0f}"
    if f == "f1": return f"{v:.1f}"
    return esc(v)


p0 = lambda v: f"{v * 100:.0f}\\%"
rows = ""
for u, b in R["by_use"].items():
    rows += f"{esc(b['label'])} & {b['n']:,} & {p0(R['uses'][u]['share'])} & {p0(b['today']['original'])} & {p0(b['ruin_any'])} & {p0(b['today']['earthwork'])} & {p0(b['lost_any'])} & {b['km_city_median']:.0f} \\\\\n"
TABLE1 = ("\\begin{table}[H]\\centering\\small\\caption{Survivors by original use: count, share of the catalogue, and the share of each use that is still in original use, "
          "a ruin or site, an earthwork or lost, with the median distance in km to a city of 100,000 people.}\\label{tab:use}\n"
          "\\begin{tabular}{lrrrrrrr}\\toprule Original use & N & Share & In use & Ruin & Earthwork & Lost & km\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
cb, ca = R["compare"]["before"], R["compare"]["after"]
rows2 = [("Items", f"{cb['n']:,}", f"{ca['n']:,}")]
for u in ("religious", "defensive", "domestic", "civic", "funerary", "infrastructure"):
    rows2.append((R["uses"][u]["label"], p0(cb["use"][u]), p0(ca["use"][u])))
rows2 += [("Religious, funerary or commemorative", p0(cb["sacred"]), p0(ca["sacred"])),
          ("Ruin (recorded state or class only)", p0(cb["ruin_c"]), p0(ca["ruin_c"])),
          ("Lost (recorded state or class only)", p0(cb["lost_c"]), p0(ca["lost_c"])),
          ("Material recorded", f"{cb['n_mat']:,} ({p0(cb['mat_share_recorded'])})", f"{ca['n_mat']:,} ({p0(ca['mat_share_recorded'])})"),
          ("Stone, of recorded", p0(cb["mat"]["stone"]), p0(ca["mat"]["stone"])),
          ("Brick, of recorded", p0(cb["mat"]["brick"]), p0(ca["mat"]["brick"])),
          ("Timber, of recorded", p0(cb["mat"]["timber"]), p0(ca["mat"]["timber"])),
          ("Median km to a city of 100,000", f"{cb['km_city_median']:.0f}", f"{ca['km_city_median']:.0f}"),
          ("Within 10 km of such a city", p0(cb["within10km"]), p0(ca["within10km"]))]
TABLE2 = ("\\begin{table}[H]\\centering\\small\\caption{The early survivors against the comparison set built 1100 to 1599, classified with the same rules.}\\label{tab:cmp}\n"
          "\\begin{tabular}{lrr}\\toprule & Before 1100 & 1100 to 1599\\\\\\midrule\n" + "".join(f"{esc(a)} & {b} & {c}\\\\\n" for a, b, c in rows2) + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(HERE, "paper_template.tex")).read().replace("{{X:TABLE1}}", TABLE1).replace("{{X:TABLE2}}", TABLE2)
t = re.sub(r"\{\{(.+?)\}\}", lambda m: fmt(get(m.group(1).partition("|")[0]), m.group(1).partition("|")[2] or "raw"), t)
os.makedirs(P, exist_ok=True)
shutil.copy(os.path.join(HERE, "paper_template.tex"), os.path.join(P, "paper_template.tex"))
open(os.path.join(P, NAME + ".tex"), "w").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=P, capture_output=True, text=True)
for ext in (".aux", ".log", ".out"):
    if os.path.exists(os.path.join(P, NAME + ext)): os.remove(os.path.join(P, NAME + ext))
shutil.copy(os.path.join(P, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
print("paper built", r.returncode)
