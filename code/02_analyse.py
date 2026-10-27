"""Step 2: analysis. Reads data/buildings.csv, data/later_1100_1599.csv, data/archaeological_sites_only.csv
and data/audit_sample.csv; writes data/results.json (every number used anywhere), data/oldest_by_country.csv,
data/uk_oldest.csv and work/site.json (compact page data).
"""
import os, sys, json, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from rules import USES, USE_LABEL

D = pd.read_csv(os.path.join(ROOT, "data", "buildings.csv"), keep_default_na=False)
L = pd.read_csv(os.path.join(ROOT, "data", "later_1100_1599.csv"), keep_default_na=False)
A = pd.read_csv(os.path.join(ROOT, "data", "archaeological_sites_only.csv"), keep_default_na=False)
AU = pd.read_csv(os.path.join(ROOT, "data", "audit_sample.csv"), keep_default_na=False)
EX = pd.read_csv(os.path.join(ROOT, "data", "excluded.csv"), keep_default_na=False)
R = {}
sh = lambda a, b: float(a) / float(b) if b else 0.0

TODAY = ["original", "changed", "museum", "unknown", "ruin", "earthwork", "lost"]
TODAY_LABEL = {"original": "Still in original use", "changed": "Changed use", "museum": "Museum or visitor site",
               "unknown": "Standing, use not recorded", "ruin": "Ruin or site", "earthwork": "Earthwork", "lost": "Lost"}
STATES = ["standing", "ruin", "site", "earthwork", "lost"]
STATE_LABEL = {"standing": "Standing (no ruin recorded)", "ruin": "Standing ruin", "site": "Foundations or site", "earthwork": "Earthwork", "lost": "Lost"}
FORMS = ["building", "structure", "earthwork"]
MATS = ["stone", "brick", "timber", "earth"]


def region(country, sub):
    if country in ("United Kingdom", "Ireland"): return "Britain and Ireland"
    if country == "Iran": return "Middle East and Caucasus"
    return {"Northern Europe": "Northern and western Europe", "Western Europe": "Northern and western Europe",
            "Southern Europe": "Southern Europe", "Eastern Europe": "Eastern Europe", "Western Asia": "Middle East and Caucasus",
            "Northern Africa": "North Africa", "Southern Asia": "South and central Asia", "Central Asia": "South and central Asia",
            "Eastern Asia": "East Asia", "South-Eastern Asia": "South-east Asia"}.get(sub, "Rest of the world")


REGIONS = ["Britain and Ireland", "Northern and western Europe", "Southern Europe", "Eastern Europe", "Middle East and Caucasus",
           "North Africa", "South and central Asia", "East Asia", "South-east Asia", "Rest of the world"]
D["region"] = [region(c, s) for c, s in zip(D.country, D.subregion)]
L["region"] = [region(c, s) for c, s in zip(L.country, L.subregion)]


def era(y):
    if y < -1000: return "Before 1000 BC"
    if y < 0: return "1000 BC to 1 BC"
    if y < 500: return "AD 1 to 499"
    if y < 800: return "500 to 799"
    if y < 1000: return "800 to 999"
    if y < 1100: return "1000 to 1099"
    if y < 1300: return "1100 to 1299"
    if y < 1500: return "1300 to 1499"
    return "1500 to 1599"


ERAS = ["Before 1000 BC", "1000 BC to 1 BC", "AD 1 to 499", "500 to 799", "800 to 999", "1000 to 1099"]
LERAS = ["1100 to 1299", "1300 to 1499", "1500 to 1599"]
D["era"] = D.year_rep.map(era); L["era"] = L.year_rep.map(era)
for df in (D, L):
    for m in MATS: df["m_" + m] = df.materials.str.contains(m)
    df["has_mat"] = df[["m_" + m for m in MATS]].any(axis=1)
    df["ruin_c"] = df.state.isin(["ruin", "site"]) & df.state_basis.isin(["recorded", "class"])
    df["lost_c"] = (df.state == "lost") & df.state_basis.isin(["recorded", "class"])
    df["latband"] = pd.cut(df.lat.abs(), [0, 25, 35, 45, 55, 90], labels=["0 to 25", "25 to 35", "35 to 45", "45 to 55", "55 and over"], include_lowest=True).astype(str)
N = len(D)

# ---------------- totals ----------------
R["meta"] = {"pull": "27 October 2026", "endpoint": "QLever Wikidata", "doi": "10.5281/zenodo.23687612",
             "rows_struct": 12794, "rows_arch": 3781, "rows_later": 54315}
R["n"] = N
R["n_items_raw"] = int(N + len(EX))
R["n_excluded"] = int(len(EX))
R["excluded_reasons"] = {"objects_places_routes": int(EX.reason.str.startswith("object").sum()),
                         "implausible_date": int(EX.reason.str.startswith("date implausible").sum()),
                         "no_coords_or_date": int(EX.reason.str.startswith("no coord").sum())}
R["n_countries"] = int(D.country.nunique())
R["n_later"] = int(len(L)); R["n_arch_only"] = int(len(A))
R["fuzzy_share"] = sh(D.fuzzy.sum(), N); R["fuzzy_n"] = int(D.fuzzy.sum())
R["precise_year_n"] = int((D.prec >= 9).sum())
R["heritage_share"] = sh(D.heritage.sum(), N)
R["enwiki_n"] = int((D.enwiki != "").sum())
R["unnamed_n"] = int((D.label == "").sum())
R["uses"] = {u: {"label": USE_LABEL[u], "n": int((D.use == u).sum()), "share": sh((D.use == u).sum(), N)} for u in USES}
R["today"] = {t: {"label": TODAY_LABEL[t], "n": int((D.today == t).sum()), "share": sh((D.today == t).sum(), N)} for t in TODAY}
R["states"] = {s: {"label": STATE_LABEL[s], "n": int((D.state == s).sum()), "share": sh((D.state == s).sum(), N)} for s in STATES}
R["forms"] = {f: int((D.form == f).sum()) for f in FORMS}
R["state_basis"] = D.state_basis.value_counts().to_dict()
R["today_basis"] = {k if k else "none": int(v) for k, v in D.today_basis.value_counts().items()}
R["original_inferred_n"] = int((D.today_basis == "inferred (religious, no change recorded)").sum())
R["original_recorded_n"] = int(((D.today == "original") & (D.today_basis != "inferred (religious, no change recorded)")).sum())
R["church_and_mosque_n"] = int(D.church_and_mosque.sum())
stand = D[D.state == "standing"]
R["standing_n"] = int(len(stand)); R["standing_share"] = sh(len(stand), N)
R["standing_or_ruin_n"] = int(D.state.isin(["standing", "ruin"]).sum())
R["original_share_of_standing"] = sh((stand.today == "original").sum(), len(stand))
R["religious_share_of_original"] = sh(((D.today == "original") & (D.use == "religious")).sum(), (D.today == "original").sum())
R["religious_share_of_standing"] = sh((stand.use == "religious").sum(), len(stand))

# use then -> now flows
R["flows"] = [{"use": u, "today": t, "n": int(((D.use == u) & (D.today == t)).sum())} for u in USES for t in TODAY]
R["by_use"] = {}
for u in USES:
    q = D[D.use == u]
    R["by_use"][u] = {"n": int(len(q)), "label": USE_LABEL[u],
                      "today": {t: sh((q.today == t).sum(), len(q)) for t in TODAY},
                      "state": {s: sh((q.state == s).sum(), len(q)) for s in STATES},
                      "ruin_c": sh(q.ruin_c.sum(), len(q)), "lost_c": sh(q.lost_c.sum(), len(q)),
                      "ruin_any": sh(q.state.isin(["ruin", "site"]).sum(), len(q)), "lost_any": sh((q.state == "lost").sum(), len(q)),
                      "original": sh((q.today == "original").sum(), len(q)),
                      "km_city_median": float(q.km_city100k.median())}

# ---------------- eras ----------------
R["eras"] = []
for e in ERAS:
    q = D[D.era == e]
    R["eras"].append({"era": e, "n": int(len(q)), "fuzzy": sh(q.fuzzy.sum(), len(q)),
                      "use": {u: sh((q.use == u).sum(), len(q)) for u in USES},
                      "today": {t: sh((q.today == t).sum(), len(q)) for t in TODAY},
                      "ruin_any": sh(q.state.isin(["ruin", "site"]).sum(), len(q)),
                      "n_mat": int(q.has_mat.sum()), "mat": {m: sh(q["m_" + m].sum(), q.has_mat.sum()) for m in MATS}})
R["later_eras"] = []
for e in LERAS:
    q = L[L.era == e]
    R["later_eras"].append({"era": e, "n": int(len(q)), "use": {u: sh((q.use == u).sum(), len(q)) for u in USES},
                            "n_mat": int(q.has_mat.sum()), "mat": {m: sh(q["m_" + m].sum(), q.has_mat.sum()) for m in MATS}})
# survivors per century AD 1 to 1599 (both pulls use the same criteria apart from the date window)
cent = []
for c in range(1, 17):
    a, b = (c - 1) * 100, c * 100
    src = D if c <= 11 else L
    n = int(((src.year_rep >= max(a, 1)) & (src.year_rep < b)).sum())
    cent.append({"century": c, "n": n, "set": "before 1100" if c <= 11 else "1100 to 1599"})
R["centuries"] = cent
bc = []
for c in range(10, 0, -1):
    n = int(((D.year_rep >= -c * 100) & (D.year_rep < -(c - 1) * 100)).sum())
    bc.append({"century_bc": c, "n": n})
R["centuries_bc"] = bc
R["before_1000bc_n"] = int((D.year_rep < -1000).sum())
c11 = D[(D.year_rep >= 1000) & (D.year_rep < 1100)]
R["c11_n"] = int(len(c11)); R["c11_share"] = sh(len(c11), N)
R["c11_uk_share"] = sh((c11.country == "United Kingdom").sum(), len(c11))
R["c11_fuzzy_share"] = sh(c11.fuzzy.sum(), len(c11))
R["c11_uk_n"] = int((c11.country == "United Kingdom").sum())
R["c10_n"] = cent[9]["n"]; R["c12_n"] = cent[11]["n"]; R["c16_n"] = cent[15]["n"]; R["c1_n"] = cent[0]["n"]

# ---------------- comparison with 1100 to 1599 ----------------
def mix(df):
    return {u: sh((df.use == u).sum(), len(df)) for u in USES}
cmp_ = {"before": {"n": N, "use": mix(D), "ruin_c": sh(D.ruin_c.sum(), N), "lost_c": sh(D.lost_c.sum(), N),
                   "n_mat": int(D.has_mat.sum()), "mat_share_recorded": sh(D.has_mat.sum(), N),
                   "mat": {m: sh(D["m_" + m].sum(), D.has_mat.sum()) for m in MATS},
                   "km_city_median": float(D.km_city100k.median()), "within10km": sh((D.km_city100k <= 10).sum(), N),
                   "sacred": sh(D.use.isin(["religious", "funerary", "commemorative"]).sum(), N)},
        "after": {"n": int(len(L)), "use": mix(L), "ruin_c": sh(L.ruin_c.sum(), len(L)), "lost_c": sh(L.lost_c.sum(), len(L)),
                  "n_mat": int(L.has_mat.sum()), "mat_share_recorded": sh(L.has_mat.sum(), len(L)),
                  "mat": {m: sh(L["m_" + m].sum(), L.has_mat.sum()) for m in MATS},
                  "km_city_median": float(L.km_city100k.median()), "within10km": sh((L.km_city100k <= 10).sum(), len(L)),
                  "sacred": sh(L.use.isin(["religious", "funerary", "commemorative"]).sum(), len(L))}}
# same regions only (Europe), to take some of the coverage difference out
EU = ["Britain and Ireland", "Northern and western Europe", "Southern Europe", "Eastern Europe"]
de, le = D[D.region.isin(EU)], L[L.region.isin(EU)]
cmp_["europe_before"] = {"n": int(len(de)), "use": mix(de), "ruin_c": sh(de.ruin_c.sum(), len(de)), "n_mat": int(de.has_mat.sum()),
                         "mat": {m: sh(de["m_" + m].sum(), de.has_mat.sum()) for m in MATS}}
cmp_["europe_after"] = {"n": int(len(le)), "use": mix(le), "ruin_c": sh(le.ruin_c.sum(), len(le)), "n_mat": int(le.has_mat.sum()),
                        "mat": {m: sh(le["m_" + m].sum(), le.has_mat.sum()) for m in MATS}}
cmp_["by_use_ruin_c"] = {u: {"before": sh(D[D.use == u].ruin_c.sum(), (D.use == u).sum()), "after": sh(L[L.use == u].ruin_c.sum(), (L.use == u).sum()),
                             "n_before": int((D.use == u).sum()), "n_after": int((L.use == u).sum())} for u in USES}
R["compare"] = cmp_
R["later_top_countries"] = L.country.value_counts().head(8).to_dict()

# ---------------- regions ----------------
R["regions"] = []
for g in REGIONS:
    q = D[D.region == g]
    if not len(q): continue
    R["regions"].append({"region": g, "n": int(len(q)), "use": {u: sh((q.use == u).sum(), len(q)) for u in USES},
                         "today": {t: sh((q.today == t).sum(), len(q)) for t in TODAY},
                         "ruin_any": sh(q.state.isin(["ruin", "site"]).sum(), len(q)),
                         "n_mat": int(q.has_mat.sum()), "mat": {m: sh(q["m_" + m].sum(), q.has_mat.sum()) for m in MATS},
                         "n_later": int((L.region == g).sum())})

# ---------------- latitude ----------------
R["latbands"] = []
for b in ["0 to 25", "25 to 35", "35 to 45", "45 to 55", "55 and over"]:
    q = D[D.latband == b]; ql = L[L.latband == b]
    R["latbands"].append({"band": b, "n": int(len(q)), "ruin_any": sh(q.state.isin(["ruin", "site"]).sum(), len(q)),
                          "ruin_c": sh(q.ruin_c.sum(), len(q)), "original": sh((q.today == "original").sum(), len(q)),
                          "religious": sh((q.use == "religious").sum(), len(q)), "n_later": int(len(ql)),
                          "ruin_c_later": sh(ql.ruin_c.sum(), len(ql))})

W65 = D[D.lon < 65]
dry = W65[(W65.lat >= 25) & (W65.lat < 35)]; temp = W65[(W65.lat >= 45) & (W65.lat < 55)]
R["dry"] = {"n_dry": int(len(dry)), "ruin_dry": sh(dry.state.isin(["ruin", "site"]).sum(), len(dry)),
            "n_temperate": int(len(temp)), "ruin_temperate": sh(temp.state.isin(["ruin", "site"]).sum(), len(temp)),
            "ruin_c_dry": sh(dry.ruin_c.sum(), len(dry)),
            "n_dry_ex_dura": int((~(dry.lat.between(34.70, 34.80) & dry.lon.between(40.68, 40.78))).sum()),
            "ruin_dry_ex_dura": sh(dry[~(dry.lat.between(34.70, 34.80) & dry.lon.between(40.68, 40.78))].state.isin(["ruin", "site"]).sum(),
                                   (~(dry.lat.between(34.70, 34.80) & dry.lon.between(40.68, 40.78))).sum()), "ruin_c_temperate": sh(temp.ruin_c.sum(), len(temp))}

# ---------------- remoteness ----------------
R["remote"] = {}
for t in TODAY:
    q = D[D.today == t]
    R["remote"][t] = {"n": int(len(q)), "km_median": float(q.km_city100k.median()) if len(q) else None,
                      "within10km": sh((q.km_city100k <= 10).sum(), len(q)), "beyond50km": sh((q.km_city100k > 50).sum(), len(q))}
inuse = D[D.today == "original"]; ruins = D[D.state.isin(["ruin", "site"])]
R["remote_summary"] = {"inuse_km": float(inuse.km_city100k.median()), "ruin_km": float(ruins.km_city100k.median()),
                       "inuse_within10": sh((inuse.km_city100k <= 10).sum(), len(inuse)), "ruin_within10": sh((ruins.km_city100k <= 10).sum(), len(ruins)),
                       "ruin_beyond50": sh((ruins.km_city100k > 50).sum(), len(ruins)), "inuse_beyond50": sh((inuse.km_city100k > 50).sum(), len(inuse))}

# ---------------- materials ----------------
M = D[D.has_mat]
R["materials"] = {"n_recorded": int(len(M)), "share_recorded": sh(len(M), N), **{m: sh(M["m_" + m].sum(), len(M)) for m in MATS},
                  "counts": {m: int(M["m_" + m].sum()) for m in MATS},
                  "ruin_by_mat": {m: sh(M[M["m_" + m]].state.isin(["ruin", "site"]).sum(), M["m_" + m].sum()) for m in MATS},
                  "lost_by_mat": {m: sh((M[M["m_" + m]].state == "lost").sum(), M["m_" + m].sum()) for m in MATS}}

# ---------------- styles: is the standing fabric later than the founding date? ----------------
LATE = re.compile(r"gothic|baroque|renaissance|neoclassic|classicism|revival|historicis|rococo|mannerism|art nouveau|eclectic|mud[eé]jar|tudor|"
                  r"georgian|victorian|perpendicular|plateresque|manueline|herrerian|modern", re.I)
EARLY = re.compile(r"romanesque|pre-romanesque|byzantine|carolingian|anglo-saxon|norman|early christian|ancient roman|ancient greek|"
                   r"visigothic|asturian|ottonian|mozarabic|merovingian|doric|ionic|corinthian|hellenistic|umayyad|abbasid|fatimid|sasanian|"
                   r"lombard|first romanesque|insular|achaemenid|pharaonic|ancient egyptian", re.I)
st = D[D.styles != ""]
late_only = st[st.styles.map(lambda s: bool(LATE.search(s)) and not EARLY.search(s))]
early_any = st[st.styles.map(lambda s: bool(EARLY.search(s)))]
dated = st[st.styles.map(lambda s: bool(LATE.search(s)) or bool(EARLY.search(s)))]
R["styles"] = {"n_with_style": int(len(st)), "n_dated_style": int(len(dated)), "late_only": int(len(late_only)),
               "early_any": int(len(early_any)), "late_only_share": sh(len(late_only), len(dated)),
               "both": int(len(dated) - len(late_only) - (len(early_any) - len(early_any[early_any.styles.map(lambda s: bool(LATE.search(s)))]))),
               "early_and_late": int(len(early_any[early_any.styles.map(lambda s: bool(LATE.search(s)))])),
               "early_only": int(len(early_any[early_any.styles.map(lambda s: not LATE.search(s))]))}

# ---------------- audit ----------------
au = AU[~AU.checked_status.str.startswith("not checked")]
R["audit"] = {"n": int(len(au)), "status": au.checked_status.value_counts().to_dict(), "fabric": au.checked_fabric.value_counts().to_dict()}
orig = au[au.catalogue_today == "original"]
R["audit"]["catalogue_original_n"] = int(len(orig))
R["audit"]["catalogue_original_confirmed"] = int((orig.checked_status == "in original use").sum())
R["audit"]["catalogue_original_status"] = orig.checked_status.value_counts().to_dict()
inu = au[au.checked_status == "in original use"]
R["audit"]["inuse_n"] = int(len(inu)); R["audit"]["inuse_fabric"] = inu.checked_fabric.value_counts().to_dict()
rn = au[au.checked_status.isin(["ruin or remains", "earthwork", "changed use or monument"])]
R["audit"]["notinuse_n"] = int(len(rn)); R["audit"]["notinuse_fabric"] = rn.checked_fabric.value_counts().to_dict()
R["audit"]["sample_drawn"] = 60; R["audit"]["sample_checked_first"] = 33

# ---------------- countries ----------------
cc = D.country.value_counts()
R["countries"] = []
rows_obc = []
for c, n in cc.items():
    q = D[D.country == c]
    alive = q[q.state != "lost"].sort_values(["year_rep", "sitelinks"], ascending=[True, False])
    top = alive.head(5)
    R["countries"].append({"country": c, "n": int(n), "religious": sh((q.use == "religious").sum(), n),
                           "ruin_any": sh(q.state.isin(["ruin", "site"]).sum(), n), "original": sh((q.today == "original").sum(), n),
                           "fuzzy": sh(q.fuzzy.sum(), n), "n_later": int((L.country == c).sum()),
                           "oldest": [{"qid": r.qid, "label": r.label or "Unnamed", "date": r.date_text, "use": r.use, "today": r.today, "state": r.state}
                                      for r in top.head(3).itertuples()]})
    for k, r in enumerate(top.itertuples()):
        rows_obc.append({"country": c, "rank": k + 1, "qid": r.qid, "label": r.label, "date_text": r.date_text, "year_rep": r.year_rep,
                         "fuzzy": r.fuzzy, "use": r.use, "state": r.state, "today": r.today, "classes": r.classes, "enwiki": r.enwiki})
pd.DataFrame(rows_obc).to_csv(os.path.join(ROOT, "data", "oldest_by_country.csv"), index=False)
R["top_countries"] = [{"country": c, "n": int(n), "share": sh(n, N)} for c, n in cc.head(12).items()]
R["top3_share"] = sh(cc.head(3).sum(), N)
R["n_countries_10plus"] = int((cc >= 10).sum())
R["japan"] = {"n": int(cc.get("Japan", 0)), "religious": sh(((D.country == "Japan") & (D.use == "religious")).sum(), cc.get("Japan", 1)),
              "kofun": int(((D.country == "Japan") & D.classes.str.contains("kofun", case=False)).sum()),
              "shrine": int(((D.country == "Japan") & D.classes.str.contains("shrine|Shikina|jingū|taisha", case=False)).sum()),
              "temple": int(((D.country == "Japan") & D.classes.str.contains("temple|-ji", case=False)).sum())}
R["dura"] = int(D.label.str.contains("Dura-Europos").sum() + ((D.country == "Syria") & (D.lat.between(34.70, 34.80)) & (D.lon.between(40.68, 40.78))).sum())
R["dura_box"] = int(((D.lat.between(34.70, 34.80)) & (D.lon.between(40.68, 40.78))).sum())

# ---------------- UK depth ----------------
U = D[D.country == "United Kingdom"].copy()
R["uk"] = {"n": int(len(U)), "share": sh(len(U), N), "nations": U.nation.replace("", "Unassigned (coast or Northern Ireland)").value_counts().to_dict(),
           "use": {u: int((U.use == u).sum()) for u in USES}, "today": {t: int((U.today == t).sum()) for t in TODAY},
           "c11": int(((U.year_rep >= 1000) & (U.year_rep < 1100)).sum()), "c11_share": sh(((U.year_rep >= 1000) & (U.year_rep < 1100)).sum(), len(U)),
           "fuzzy": sh(U.fuzzy.sum(), len(U)), "before_1000": int((U.year_rep < 1000).sum()), "roman": int(((U.year_rep >= 43) & (U.year_rep < 410)).sum()),
           "prehistoric": int((U.year_rep < 43).sum()), "anglo_saxon": int(((U.year_rep >= 410) & (U.year_rep < 1066)).sum()),
           "post_1066": int((U.year_rep >= 1066).sum()), "counties_top": U.county.value_counts().head(8).to_dict()}
cats = {"churches": lambda r: r.use == "religious" and re.search(r"church|chapel|cathedral|minster|abbey|priory", r.classes + " " + r.label, re.I),
        "castles": lambda r: re.search(r"castle|motte", r.classes, re.I),
        "houses": lambda r: r.use == "domestic" or re.search(r"\bhouse\b|manor|\bhall\b", r.classes, re.I),
        "towers": lambda r: re.search(r"tower", r.classes + " " + r.label, re.I),
        "bridges": lambda r: re.search(r"bridge", r.classes, re.I)}
R["uk"]["lists"] = {}
uk_rows = []
Ua = U[U.state != "lost"].sort_values(["year_rep", "sitelinks"], ascending=[True, False])
for k, f in cats.items():
    q = [r for r in Ua.itertuples() if f(r) and (k == "castles" or (r.state in ("standing", "ruin") and r.form != "earthwork"))]
    R["uk"]["lists"][k] = {"n": len(q), "top": [{"qid": r.qid, "label": r.label, "date": r.date_text, "year": int(r.year_rep), "county": r.county or "", "nation": r.nation,
                                                  "state": r.state, "today": r.today, "enwiki": r.enwiki, "fuzzy": int(r.fuzzy)} for r in q[:8]]}
    for r in q: uk_rows.append({"category": k, "qid": r.qid, "label": r.label, "date_text": r.date_text, "year_rep": r.year_rep, "fuzzy": r.fuzzy,
                                "county": r.county, "nation": r.nation, "use": r.use, "state": r.state, "today": r.today, "classes": r.classes, "enwiki": r.enwiki})
pd.DataFrame(uk_rows).to_csv(os.path.join(ROOT, "data", "uk_oldest.csv"), index=False)
REF = pd.read_csv(os.path.join(ROOT, "data", "uk_reference_list.csv"), keep_default_na=False)
R["uk"]["ref"] = {"n": int(len(REF)), "matched": int((REF.qid != "").sum()), "by_table": REF.table.value_counts().to_dict(),
                  "by_category": REF.category.value_counts().to_dict(),
                  "first": {c: [{"building": r.building, "location": r.location, "date": r.date_as_written, "qid": r.qid, "cat_date": r.catalogue_date}
                                for r in REF[REF.category == c].sort_values("year_approx").head(6).itertuples()] for c in REF.category.unique()},
                  "unmatched_prehistoric": int(((REF.table == "Prehistoric") & (REF.qid == "")).sum()),
                  "n_prehistoric": int((REF.table == "Prehistoric").sum())}
NWC = ["Lancashire", "Cumbria", "Merseyside", "Greater Manchester", "Cheshire"]
NW = U[U.county.isin(NWC)].sort_values("year_rep")
R["uk"]["nw"] = {"n": int(len(NW)), "counties": {c: int((NW.county == c).sum()) for c in NWC},
                 "items": [{"qid": r.qid, "label": r.label, "date": r.date_text, "county": r.county, "state": r.state, "today": r.today, "use": r.use, "enwiki": r.enwiki}
                           for r in NW.itertuples()], "lancs": int((NW.county == "Lancashire").sum())}

# ---------------- headline ----------------
oldest_standing = D[(D.state == "standing") & (D.form != "earthwork")].sort_values("year_rep")
R["headline"] = {"religious_share": R["uses"]["religious"]["share"], "original_share": R["today"]["original"]["share"],
                 "ruin_share": sh(D.state.isin(["ruin", "site"]).sum(), N), "lost_share": R["today"]["lost"]["share"],
                 "stone_share": R["materials"]["stone"], "sacred_before": cmp_["before"]["sacred"], "sacred_after": cmp_["after"]["sacred"],
                 "relig_before": cmp_["before"]["use"]["religious"], "relig_after": cmp_["after"]["use"]["religious"],
                 "def_before": cmp_["before"]["use"]["defensive"], "def_after": cmp_["after"]["use"]["defensive"],
                 "dom_before": cmp_["before"]["use"]["domestic"], "dom_after": cmp_["after"]["use"]["domestic"],
                 "uk_n": R["uk"]["n"], "japan_n": R["japan"]["n"], "italy_n": int(cc.get("Italy", 0)),
                 "oldest_standing_examples": [{"label": r.label, "date": r.date_text, "country": r.country} for r in oldest_standing.head(5).itertuples()]}

# ---------------- story cards (famous survivors, chosen by hand, data from the catalogue) ----------------
STORY = [("Q37200", "A tomb built as a mountain of limestone. Nothing to reuse, nothing to repair: sheer mass is its survival plan."),
         ("Q10288", "A temple, then a church, then a mosque, then a powder store that blew up in 1687. It survives as a ruin, not a building."),
         ("Q99309", "A Roman temple that became a church in the 7th century. Continuous use kept its concrete dome roofed."),
         ("Q12506", "Church, mosque, museum and mosque again. It changed faith but never lost its job, or its roof."),
         ("Q10285", "An arena turned quarry, fortress and housing. What was not robbed for stone stands as a ruin."),
         ("Q43473", "A Hindu, then Buddhist temple in Cambodia, never fully abandoned."),
         ("Q5933", "Founded before 1100, but the abbey church you see is largely Gothic, rebuilt from the 13th century."),
         ("Q62378", "A Norman keep that stayed useful: royal palace, prison, armoury, treasury, museum."),
         ("Q43244", "One of the most famous lost buildings: brought down by earthquakes. Wikidata records it as destroyed."),
         ("Q221716", "Founded in 778; the timber halls standing today were rebuilt in the 1630s, as Japanese temples often are."),
         ("Q57357", "A frontier wall of stone and turf. Long stretches were robbed for farm buildings and a road."),
         ("Q187702", "Founded in the 4th century, burned, wrecked and rebuilt, but always a place of worship.")]
SR = D.set_index("qid")
R["stories"] = []
for q, txt in STORY:
    if q not in SR.index: continue
    r = SR.loc[q]
    R["stories"].append({"qid": q, "label": r.label, "date": r.date_text, "year": int(r.year_rep), "country": r.country, "use": r.use,
                         "today": r.today, "state": r.state, "materials": r.materials, "sitelinks": int(r.sitelinks), "enwiki": r.enwiki, "text": txt})

EW = D[D.today == "earthwork"]
R["earthwork_japan"] = {"n": int((EW.country == "Japan").sum()), "km_japan": float(EW[EW.country == "Japan"].km_city100k.median()),
                        "km_other": float(EW[EW.country != "Japan"].km_city100k.median())}
R["shrine_series_n"] = int((D.state_basis == "excavated shrine series").sum())
R["outside_map_window"] = int(((D.lon < -20) | (D.lon > 150) | (D.lat < -12) | (D.lat > 66)).sum())
json.dump(R, open(os.path.join(ROOT, "data", "results.json"), "w"), indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))

# ---------------- compact page data ----------------
CL = sorted(D.country.unique())
def short_classes(s):
    return ", ".join(s.split("|")[:3])
recs = []
for r in D.itertuples():
    mb = sum(1 << i for i, m in enumerate(MATS) if getattr(r, "m_" + m))
    recs.append([round(r.lat, 4), round(r.lon, 4), r.label, USES.index(r.use), TODAY.index(r.today), STATES.index(r.state), FORMS.index(r.form),
                 int(r.year_rep), r.date_text, CL.index(r.country), mb, int(r.fuzzy), r.qid, r.enwiki, int(r.sitelinks), short_classes(r.classes)])
site = {"r": recs, "c": CL, "uses": USES, "useLab": [USE_LABEL[u] for u in USES], "today": TODAY, "todayLab": [TODAY_LABEL[t] for t in TODAY],
        "states": STATES, "stateLab": [STATE_LABEL[s] for s in STATES], "forms": FORMS, "mats": MATS,
        "arch": [[round(r.lat, 3), round(r.lon, 3), r.label, r.date_text] for r in A.itertuples()], "R": R,
        "eras": ERAS, "lateras": LERAS,
        "audit": [[r.label, r.checked_status, r.checked_fabric, r.evidence] for r in au.itertuples()]}
os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
json.dump(site, open(os.path.join(ROOT, "work", "site.json"), "w"), ensure_ascii=False, separators=(",", ":"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("N", N, "site.json KB", os.path.getsize(os.path.join(ROOT, "work", "site.json")) // 1024)
