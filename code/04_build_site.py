"""Step 4: build ../index.html and ../README.md from page_template.html and README_template.md.

Every number in the text is a placeholder like {{uses.religious.share|pct0}} filled from ../data/results.json,
and the compact page data (../work/site.json) is embedded as `const D = ...`.
Formats: int, pct0, pct1, f1, km (one decimal), yr (negative = BC), raw.
"""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
site = open(os.path.join(ROOT, "work", "site.json")).read().replace("–", "-").replace("—", "-")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "km": return f"{v:.0f}"
    if f == "yr": return f"{-int(v)} BC" if v < 0 else f"AD {int(v)}"
    return str(v)


def fill(t):
    return re.sub(r"\{\{(.+?)\}\}", lambda m: fmt(get(m.group(1).partition("|")[0].strip()), m.group(1).partition("|")[2].strip() or "raw"), t)


if __name__ == "__main__":
    t = fill(open(os.path.join(HERE, "page_template.html")).read()).replace("/*DATA*/", "const D = " + site + ";")
    open(os.path.join(ROOT, "index.html"), "w").write(t)
    md = fill(open(os.path.join(HERE, "README_template.md")).read())
    open(os.path.join(ROOT, "README.md"), "w").write(md)
    print("index.html", len(t.encode()) // 1024, "KB; README.md written")
