## Title

[OC] Every building and structure in Wikidata built before AD 1100 (6,837 of them), seen through an arch: 65% were built for worship, and the survivors are either still in use or abandoned far from any city

## Body (optional)

I took every item Wikidata classes as an architectural structure with a construction date before 1100 and coordinates, cleaned out statues, streets and the like, and classified each by what it was built for and what it is today. 65% were built for worship and 88% of those are still places of worship, while 30% of castles and 72% of houses and palaces are ruins. Ruins sit a median 43 km from a city of 100,000 people, against 20 km for buildings still in use.

Caveat: Wikidata coverage is uneven (Japan, Italy and the UK hold 46% of records), and many dates are founding dates: in a hand check, 10 of 32 "old" buildings were mostly later walls on an older foundation.

Interactive version: https://tristan-hotham.github.io/oldest-buildings/

## Source comment

Source: Wikidata (CC0), items that are instances of a subclass of architectural structure (Q811979) with an inception before 1100 and coordinates, plus a comparison set for 1100 to 1599, pulled from the QLever Wikidata endpoint on 27 October 2026; Natural Earth country boundaries (public domain); GeoNames cities1000 (CC BY 4.0) for distances to cities; English Wikipedia (CC BY-SA 4.0) for the hand check and the UK comparison list.

Tools: Python (pandas, NumPy, SciPy, Shapely for the geography, matplotlib for the chart).

Interactive: https://tristan-hotham.github.io/oldest-buildings/
Blog post: https://blog.tristanhotham.com/2026/10/27/oldest-buildings/
Paper: https://doi.org/10.5281/zenodo.23687612
