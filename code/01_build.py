"""Step 1: build the cleaned catalogue.

Inputs (Wikidata via the QLever endpoint, pulled 27 October 2026, CC0), read in place:
  _data5/wd_struct.json  architectural structures with inception before 1100 and coordinates (one row per join)
  _data5/wd_arch.json    archaeological sites with inception before 1100
  _data5/wd_later.json   architectural structures with inception 1100 to 1599 (comparison set)
Other inputs: Natural Earth 10 m countries (public domain), GeoNames cities1000 (CC BY 4.0),
ONS county boundaries for Great Britain (OGL v3, from the How Roman Is Your Road project).

Outputs:
  data/buildings.csv, data/buildings.geojson   one row per item before 1100, with classification and geography
  data/excluded.csv                            items removed (objects, places, routes) and why
  data/later_1100_1599.csv                     comparison set, classified with the same class-only rules
  data/archaeological_sites_only.csv           archaeological sites before 1100 not in the structures set (separate layer)
"""
import os, sys, json, re, csv, math
import numpy as np
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from rules import *

D5 = "/home/claude/hist/_data5"
NE = "/home/claude/hist/_data3/ne/geojson/ne_10m_admin_0_countries.geojson"
GN = "/home/claude/hist/_data2/geonames/cities1000.txt"
CTY = "/home/claude/hist/how-roman-is-your-road/data/counties.geojson"
OUT = os.path.join(ROOT, "data"); os.makedirs(OUT, exist_ok=True)


def pt(c):
    m = re.match(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)", c)
    return float(m.group(2)), float(m.group(1))


def year_of(inc):
    m = re.match(r"(-?)(\d+)-", inc)
    return -int(m.group(2)) if m.group(1) else int(m.group(2))


def aggregate(rows):
    items = {}
    for r in rows:
        it = items.setdefault(r["i"], {"i": r["i"], "label": r.get("label", ""), "incs": set(), "c": set(), "t": {}, "country": set(),
                                       "mat": set(), "cons": set(), "use": set(), "her": set(), "style": set(), "sl": 0, "enwiki": r.get("enwiki", "")})
        if r.get("inc"): it["incs"].add((year_of(r["inc"]), int(r.get("prec") or 9)))
        if r.get("c", "").startswith("POINT("): it["c"].add(r["c"])
        if r.get("t"): it["t"][r["t"]] = (r.get("tl") or r["t"]).strip()
        if r.get("cl"): it["country"].add(r["cl"])
        if r.get("ml"): it["mat"].add(r["ml"])
        if r.get("consl"): it["cons"].add(r["consl"])
        if r.get("usel"): it["use"].add(r["usel"])
        if r.get("her"): it["her"].add(r["her"])
        if r.get("stylel"): it["style"].add(r["stylel"])
        it["sl"] = max(it["sl"], int(r.get("sl") or 0))
        if r.get("label") and not it["label"]: it["label"] = r["label"]
    return items


# ---------- geography helpers ----------
ne = json.load(open(NE))["features"]
geoms = [shape(f["geometry"]) for f in ne]
tree = STRtree(geoms)
NAME_FIX = {"United States of America": "United States", "Republic of Serbia": "Serbia", "United Republic of Tanzania": "Tanzania",
            "Czechia": "Czech Republic", "Macedonia": "North Macedonia", "eSwatini": "Eswatini"}


def country_of(lat, lon):
    p = Point(lon, lat)
    for j in tree.query(p):
        if geoms[j].contains(p):
            f = ne[j]["properties"]; return NAME_FIX.get(f["ADMIN"], f["ADMIN"]), f["SUBREGION"], "polygon"
    j = tree.nearest(p)
    if geoms[j].distance(p) < 0.25:
        f = ne[j]["properties"]; return NAME_FIX.get(f["ADMIN"], f["ADMIN"]), f["SUBREGION"], "nearest (coast)"
    return "", "", "none"


cty = json.load(open(CTY))["features"]; cgeoms = [shape(f["geometry"]) for f in cty]; ctree = STRtree(cgeoms)


def county_of(lat, lon):
    p = Point(lon, lat)
    for j in ctree.query(p):
        if cgeoms[j].contains(p):
            return cty[j]["properties"]["county"], cty[j]["properties"]["nation"]
    return "", ""


def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


cities = []
for line in open(GN, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    pop = int(f[14] or 0)
    if pop >= 100000: cities.append((float(f[4]), float(f[5]), pop, f[1]))
C = np.array([(a, b) for a, b, _, _ in cities]); ctree100 = cKDTree(xyz(C[:, 0], C[:, 1]))
big = np.array([(a, b) for a, b, p, _ in cities if p >= 1000000]); ctree1m = cKDTree(xyz(big[:, 0], big[:, 1]))


def km_to(treeobj, lat, lon):
    d, _ = treeobj.query(xyz(np.asarray(lat), np.asarray(lon)))
    return 2 * 6371 * np.arcsin(np.minimum(1, d / 2))


# ---------- classify one item ----------
def classify(it, arch_ids, use_labels=True, yrep=0):
    labs = {v.lower() for v in it["t"].values()}
    real = {l for l in labs if not GENERIC.match(l)}
    cons = {c.lower() for c in it["cons"]}
    excl = [l for l in real if EXCLUDE.search(l)]
    built = [l for l in real if not EXCLUDE.search(l)]
    if excl and not built:
        return None, "object, place or route: " + "; ".join(sorted(excl))
    use = use_of(set(built))
    # form
    if any(EARTHWORK.search(l) for l in built) and not any(re.search(r"church|temple|shrine|keep|tower|^castle$|stone castle|castle ruin|palace|wall|fortress|cathedral|mosque|limes", l) for l in built):
        form = "earthwork"
    elif built and (all(STRUCTURE.search(l) or GENERIC.match(l) or RUIN_C.search(l) or LOST_C.match(l) for l in built) or
                    (any(STRUCTURE_STRONG.search(l) for l in built) and not any(re.search(r"church|temple|mosque|castle|palace|house|cathedral|monaster|abbey|shrine", l) for l in built))):
        form = "structure"
    else:
        form = "building"
    # state, with the basis for it
    label = it["label"] or ""
    if cons & CONS_LOST or any(LOST_C.match(l) for l in labs):
        state, basis = "lost", "recorded" if cons & CONS_LOST else "class"
    elif cons & CONS_SITE or any(SITE_C.search(l) for l in labs):
        state, basis = "site", "recorded" if cons & CONS_SITE else "class"
    elif form == "earthwork":
        state, basis = "earthwork", "class"
    elif cons & CONS_RUIN or any(RUIN_C.search(l) for l in labs):
        state, basis = "ruin", "recorded" if cons & CONS_RUIN else "class"
    elif use_labels and LABEL_RUIN.search(label):
        state, basis = "ruin", "label"
    elif use_labels and LABEL_SITE.search(label):
        state, basis = "site", "label"
    elif re.match(r"Q1395[89]\d{4}$", it["i"]) and yrep < 500:
        # a run of consecutive items for excavated Iron Age and Roman shrines in Britain; P366 there records the original use
        state, basis = "site", "excavated shrine series"
    elif use_labels and yrep < 500 and re.search(r"\bRoman\b", label) and not cons & CONS_OK:
        state, basis = "ruin", "label (Roman, before 500)"
    elif cons & CONS_OK:
        state, basis = "standing", "recorded"
    elif it["i"] in arch_ids and not it["use"] and use not in ("religious",) and form == "building" and yrep < 500:
        state, basis = "ruin", "archaeological site"
    elif built and all(ANCIENT_RUIN.match(l) or GENERIC.match(l) for l in built) and not it["use"]:
        state, basis = "ruin", "ancient type"
    elif form == "building" and yrep < 0 and not it["use"] and not any(re.search(r"shrine|jingū|taisha|shikina|-ji$|hachiman|gū\b|buddhist", l) for l in labs):
        state, basis = "ruin", "BC building, no use recorded"
    else:
        state, basis = "standing", "no ruin recorded"
    # use today
    p366 = {use_of_p366(u) for u in it["use"]}
    museum = any(MUSEUM_C.search(l) for l in labs) or "museum" in p366
    former = any(FORMER_C.match(l) for l in labs) or any(CHANGED_C.match(l) for l in labs)
    resid = any(RESIDENCE_C.search(l) for l in labs)
    if basis == "excavated shrine series": p366 = set()
    if state == "lost": today, tb = "lost", basis
    elif state == "earthwork": today, tb = "earthwork", "class"
    elif state in ("ruin", "site"): today, tb = "ruin", basis
    elif former: today, tb = "changed", "class"
    elif p366 - {"museum", "unknown"} and use not in p366 and use != "unknown": today, tb = "changed", "P366"
    elif use in p366: today, tb = "original", "P366"
    elif resid and use == "domestic": today, tb = "original", "class"
    elif museum: today, tb = "museum", "class" if any(MUSEUM_C.search(l) for l in labs) else "P366"
    elif use == "religious": today, tb = "original", "inferred (religious, no change recorded)"
    else: today, tb = "unknown", ""
    mats = material_of(it["mat"])
    if any(IMPLIED_TIMBER.search(l) for l in labs): mats.add("timber")
    if any(IMPLIED_STONE.search(l) for l in labs): mats.add("stone")
    christian = any(re.search(r"church|cathedral|basilica|chapel|abbey", l) for l in labs)
    islamic = any(re.search(r"mosque|masjid", l) for l in labs) or any(re.search(r"mosque", u.lower()) for u in it["use"])
    return {"use": use, "form": form, "state": state, "state_basis": basis, "today": today, "today_basis": tb,
            "materials": "|".join(sorted(mats)), "museum": int(museum), "church_and_mosque": int(christian and islamic)}, ""


def main():
    S = json.load(open(os.path.join(D5, "wd_struct.json")))
    A = json.load(open(os.path.join(D5, "wd_arch.json")))
    L = json.load(open(os.path.join(D5, "wd_later.json")))
    items = aggregate(S); arch = aggregate(A); later = aggregate(L)
    arch_ids = set(arch)
    rows, excl = [], []
    for it in items.values():
        if not it["c"] or not it["incs"]:
            excl.append({"qid": it["i"], "label": it["label"], "reason": "no coordinates or date"}); continue
        y, prec = min(it["incs"], key=lambda t: rep_year(*t))
        lat, lon = pt(sorted(it["c"])[0])
        if rep_year(y, prec) < -10000:
            excl.append({"qid": it["i"], "label": it["label"], "reason": f"date implausible for a built structure ({date_text(y, prec)})"}); continue
        cl, why = classify(it, arch_ids, yrep=rep_year(y, prec))
        if cl is None:
            excl.append({"qid": it["i"], "label": it["label"], "reason": why}); continue
        rows.append({"qid": it["i"], "label": it["label"] or "", "lat": round(lat, 5), "lon": round(lon, 5), "year": y, "prec": prec,
                     "year_rep": rep_year(y, prec), "date_text": date_text(y, prec), "fuzzy": int(prec <= 7),
                     "n_dates": len(it["incs"]), "classes": "|".join(sorted(it["t"].values())), "wd_country": "|".join(sorted(it["country"])),
                     **cl, "material_raw": "|".join(sorted(it["mat"])), "conservation": "|".join(sorted(it["cons"])),
                     "current_use_p366": "|".join(sorted(it["use"])), "styles": "|".join(sorted(it["style"])),
                     "heritage": int(bool(it["her"])), "sitelinks": it["sl"], "enwiki": it["enwiki"].replace("https://en.wikipedia.org/wiki/", ""),
                     "in_arch_set": int(it["i"] in arch_ids), "n_coords": len(it["c"])})
    # geography
    lat = np.array([r["lat"] for r in rows]); lon = np.array([r["lon"] for r in rows])
    k100 = km_to(ctree100, lat, lon); k1m = km_to(ctree1m, lat, lon)
    for r, a, b in zip(rows, k100, k1m):
        r["country"], r["subregion"], r["country_basis"] = country_of(r["lat"], r["lon"])
        if not r["country"]: r["country"] = r["wd_country"].split("|")[0]; r["country_basis"] = "wikidata"
        r["km_city100k"] = round(float(a), 1); r["km_city1m"] = round(float(b), 1)
        r["county"], r["nation"] = county_of(r["lat"], r["lon"]) if r["country"] == "United Kingdom" else ("", "")
    rows.sort(key=lambda r: (r["year_rep"], r["qid"]))
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, "buildings.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    gj = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
          "properties": {k: r[k] for k in keys if k not in ("lat", "lon")}} for r in rows]}
    json.dump(gj, open(os.path.join(OUT, "buildings.geojson"), "w"), ensure_ascii=False)
    with open(os.path.join(OUT, "excluded.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "label", "reason"]); w.writeheader(); w.writerows(sorted(excl, key=lambda r: r["reason"]))
    # comparison set 1100 to 1599, same rules without labels (the set has no labels), minus items also in the main set
    lrows = []
    for it in later.values():
        if it["i"] in items or not it["c"] or not it["incs"]: continue
        y, prec = min(it["incs"], key=lambda t: rep_year(*t))
        if rep_year(y, prec) < 1100: continue
        cl, why = classify(it, set(), use_labels=False)
        if cl is None: continue
        la, lo = pt(sorted(it["c"])[0])
        lrows.append({"qid": it["i"], "lat": round(la, 4), "lon": round(lo, 4), "year": y, "prec": prec, "year_rep": rep_year(y, prec),
                      "classes": "|".join(sorted(it["t"].values())), "use": cl["use"], "form": cl["form"], "state": cl["state"],
                      "state_basis": cl["state_basis"], "materials": cl["materials"]})
    la = np.array([r["lat"] for r in lrows]); lo = np.array([r["lon"] for r in lrows]); kk = km_to(ctree100, la, lo)
    for r, a in zip(lrows, kk):
        r["km_city100k"] = round(float(a), 1)
    # countries for the later set (polygon test is slow for 40k; use it anyway, it is a one-off)
    for r in lrows:
        r["country"], r["subregion"], _ = country_of(r["lat"], r["lon"])
    with open(os.path.join(OUT, "later_1100_1599.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lrows[0].keys())); w.writeheader(); w.writerows(lrows)
    # archaeological sites not in the structures set
    arows = []
    for it in arch.values():
        if it["i"] in items or not it["c"] or not it["incs"]: continue
        y, prec = min(it["incs"], key=lambda t: rep_year(*t)); la, lo = pt(sorted(it["c"])[0])
        arows.append({"qid": it["i"], "label": it["label"], "lat": round(la, 4), "lon": round(lo, 4), "year": y, "prec": prec,
                      "date_text": date_text(y, prec), "classes": "|".join(sorted(it["t"].values())), "country": country_of(la, lo)[0]})
    with open(os.path.join(OUT, "archaeological_sites_only.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(arows[0].keys())); w.writeheader(); w.writerows(arows)
    print("items", len(items), "kept", len(rows), "excluded", len(excl), "later", len(lrows), "arch only", len(arows))


if __name__ == "__main__":
    main()
