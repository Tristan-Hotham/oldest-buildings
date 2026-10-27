# Still Standing

Every building and structure in Wikidata dated before AD 1100, 6,837 of them in 94 countries, on one map: what they were built for, what they are now, and what seems to have kept them standing.

**Interactive version:** https://tristan-hotham.github.io/oldest-buildings/

This repository holds the interactive page, the cleaned catalogue and the analysis code for the data study *Still Standing: why buildings from before AD 1100 survive, in Wikidata* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Blog: https://blog.tristanhotham.com/

## Headline results

- After cleaning, 6,837 buildings and structures dated before 1100 in 94 countries. Japan (1,380), Italy (947) and the United Kingdom (785) hold 46% of them, so the findings are about shares within Wikidata, not a census.
- 65% were built for worship, 14% for defence, 7% as tombs and only 4% as houses or palaces.
- 58% still seem to do their original job (3,938), 99% of them religious; 88% of religious buildings are still in religious use against almost no castles or houses. 30% of castles and forts and 72% of houses and palaces are ruins or sites.
- Against 40,200 structures built 1100 to 1599, the oldest survivors are more often sacred (religious, funerary or commemorative: 73% against 59%) and less often houses (4% against 12%). Where a material is recorded, 75% are stone against 62%.
- Ruins sit far from today's cities (median 43 km to a city of 100,000 against 20 km for buildings in use) and cluster in the dry belt: west of 65° E, 67% of survivors between 25° and 35° N are ruins, against 14% between 45° and 55° N.
- Old names, younger walls: in a hand check of 32 random items, 14 keep substantial fabric from before 1100 and 10 are mostly later buildings on an older foundation. Of 1,255 survivors with a dated style in Wikidata, 20% list only styles that began after 1100.

## Files

- `index.html`: the interactive page (Leaflet map with filters for use, era, condition, material, form and country; charts; country table; UK section).
- `header.png`: social card.
- `data/buildings.csv` and `data/buildings.geojson`: the catalogue, one row per Wikidata item: QID, label, coordinates, date (year, Wikidata precision, representative year, text, broad-date flag), classes, original use, form, condition (`state`) and the rule that set it (`state_basis`), use today (`today`, `today_basis`), materials, raw material, conservation state and current use, styles, heritage flag, sitelinks, English Wikipedia title, country (Natural Earth), subregion, distance to the nearest city of 100,000 and of 1,000,000 people, and for the UK the county and nation.
- `data/later_1100_1599.csv`: the comparison set built 1100 to 1599, classified with the same rules (no labels).
- `data/archaeological_sites_only.csv`: early archaeological sites that are not in the building set (grey layer on the map).
- `data/excluded.csv`: items removed and why.
- `data/oldest_by_country.csv`: the five oldest surviving entries in each country.
- `data/uk_oldest.csv`: UK entries by category (churches, castles, houses, towers, bridges).
- `data/uk_reference_list.csv`: entries dated before 1100 in Wikipedia's list of the oldest buildings in the UK, with matches to the catalogue (CC BY-SA 4.0).
- `data/audit_sample.csv`: the hand check of a random sample against English Wikipedia, with the sentence behind each judgement (CC BY-SA 4.0). `data/nw_checks.csv`: a local check in Lancashire.
- `data/results.json`: every number quoted on the page, in the README, paper, blog and collage.
- `code/`: run in order `01_build.py`, `03_reference.py`, `02_analyse.py`, `04_build_site.py`, `05_header.py` (`rules.py` holds the classification rules). Release outputs come from `06_release_figs.py`, `07_paper.py` (needs xelatex) and `08_release.py`; the collage from `reddit/collage.py`.

The raw Wikidata pulls (about 13 MB) are not included; they are the results of the queries described below.

## Method in brief

Wikidata items that are instances of a subclass of architectural structure (Q811979) with an inception (P571) before 1100 and coordinates, pulled from the QLever Wikidata endpoint on 27 October 2026, with classes, material (P186), conservation state (P5816), current use (P366), heritage designation (P1435), style (P149) and sitelinks. 221 items that are objects, places or routes, or have impossible dates, were removed. Original use, form and condition come from rules on the English class labels (see `code/rules.py`), plus conservation state, current use and label words. Two rules of thumb fill gaps: classical public buildings and buildings dated before Christ count as ruins unless a use is recorded, and religious buildings with no sign of change count as still in use. A comparison set of structures from 1100 to 1599 was pulled and classified the same way. Countries come from Natural Earth; distances to cities from GeoNames.

Caveats: Wikidata coverage is very uneven between countries; 45% of dates are only to the century or millennium; many dates are foundation dates rather than the date of the standing fabric; condition and use today are inferred and sometimes wrong (the hand check confirms 15 of 20 sampled "still in original use" items); the study sees only survivors, so the reasons for survival are inferred by comparison, not proven.

## Sources and licences

- Wikidata: CC0 (https://www.wikidata.org), via the QLever endpoint (https://qlever.cs.uni-freiburg.de/wikidata), pulled 27 October 2026.
- GeoNames cities1000: CC BY 4.0 (https://www.geonames.org).
- Natural Earth 10 m countries: public domain (https://www.naturalearthdata.com).
- County boundaries for Great Britain: Office for National Statistics, Open Government Licence v3; contains OS data © Crown copyright and database right.
- English Wikipedia (CC BY-SA 4.0): List of oldest buildings in the United Kingdom (https://en.wikipedia.org/wiki/List_of_oldest_buildings_in_the_United_Kingdom) and the articles named in `data/audit_sample.csv` and `data/nw_checks.csv`, read on 27 October 2026.
- Base map tiles on the page: © Esri. Map library: Leaflet.

**Licence.** Text, figures and derived data are released under CC BY 4.0 (Wikidata is CC0). The two files that reproduce Wikipedia material, `data/uk_reference_list.csv` and `data/audit_sample.csv`, are CC BY-SA 4.0. Code is MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) *Still Standing: why buildings from before AD 1100 survive, in Wikidata.* Zenodo. https://doi.org/10.5281/zenodo.23687612

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
