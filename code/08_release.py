"""Step 8: blog post (release/blog/post.html, meta.json) and Zenodo files (release/zenodo/).
Numbers come from ../data/results.json via {{path|fmt}} placeholders; {{IMG|file|alt|caption}} lines are left for upload.
"""
import os, re, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
NAME = "Hotham_Still_Standing"; SLUG = "oldest-buildings"


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}%"
    if f == "km": return f"{v:.0f}"
    return str(v)


fill = lambda t: re.sub(r"\{\{(?!IMG)([^{}|]+)(?:\|([a-z0-9]+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(2) or "raw"), t)
B = os.path.join(ROOT, "release", "blog")
post = fill(open(os.path.join(HERE, "blog_template.html")).read())
open(os.path.join(B, "post.html"), "w").write(post)
meta = {"title": "Still Standing: why do old buildings survive?", "slug": SLUG,
        "excerpt": f"I mapped all {R['n']:,} buildings and structures in Wikidata from before AD 1100. {R['uses']['religious']['share'] * 100:.0f}% were built for worship, most still are, and the survivors are either indispensable or forgotten.",
        "seo_description": f"{R['n']:,} buildings from before AD 1100 on one map: what they were built for, what they are now, and why they survived.",
        "tags": ["oldest buildings", "architecture", "history", "heritage", "Wikidata", "maps", "data visualisation", "churches"],
        "header_alt": f"Title card reading Still standing: {R['n']:,} buildings and structures from before AD 1100 on one map, {R['uses']['religious']['share'] * 100:.0f}% built for worship. Beside it, a map from Europe to Japan dotted in terracotta, slate and green on a pale limestone background."}
json.dump(meta, open(os.path.join(B, "meta.json"), "w"), indent=2, ensure_ascii=False)
# ---- zenodo ----
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
shutil.copy(os.path.join(ROOT, "release", NAME + ".pdf"), Z)
for f in ("buildings.csv", "later_1100_1599.csv", "oldest_by_country.csv", "uk_oldest.csv", "uk_reference_list.csv", "audit_sample.csv", "results.json"):
    shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, f"{SLUG}_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isfile(p) and not fn.endswith(".pyc"):
                z.write(p, f"{SLUG}/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
tex = open(os.path.join(ROOT, "release", "paper", NAME + ".tex")).read()
ab = re.search(r"\\begin\{quote\}\\small\n(.*?)\n\n\\medskip", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("~", " ").replace("\\emph{", "").replace("}", "")
zm = {"title": "Still Standing: Why Buildings from Before AD 1100 Survive, in Wikidata",
      "description_html": f"<p>{ab}</p><p>Interactive version: https://tristan-hotham.github.io/{SLUG}/. Data and code: https://github.com/Tristan-Hotham/{SLUG}. Blog post: to follow.</p>",
      "keywords": ["oldest buildings", "architectural survival", "historic buildings", "Wikidata", "religious buildings", "ruins", "building materials", "heritage", "early medieval architecture", "open data"],
      "licence": "cc-by-4.0",
      "licence_note": "Paper, figures and derived data CC BY 4.0 (Wikidata is CC0). uk_reference_list.csv and audit_sample.csv reproduce Wikipedia material and are CC BY-SA 4.0. Code MIT.",
      "related": [
          {"identifier": f"https://github.com/Tristan-Hotham/{SLUG}", "relation": "issupplementedby", "resource_type": "software"},
          {"identifier": f"https://tristan-hotham.github.io/{SLUG}/", "relation": "issupplementedby", "resource_type": "other"},
          {"identifier": "https://www.wikidata.org", "relation": "isderivedfrom", "resource_type": "dataset"},
          {"identifier": "https://www.geonames.org", "relation": "isderivedfrom", "resource_type": "dataset"},
          {"identifier": "https://www.naturalearthdata.com", "relation": "isderivedfrom", "resource_type": "dataset"},
          {"identifier": "https://geoportal.statistics.gov.uk", "relation": "isderivedfrom", "resource_type": "dataset"},
          {"identifier": "https://en.wikipedia.org/wiki/List_of_oldest_buildings_in_the_United_Kingdom", "relation": "isderivedfrom", "resource_type": "other"}]}
json.dump(zm, open(os.path.join(Z, "meta.json"), "w"), indent=2, ensure_ascii=False)
print("blog words", len(re.sub(r"<[^>]+>", " ", post).split()), "; zenodo files", sorted(os.listdir(Z)))
