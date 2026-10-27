"""Step 3: the UK reference list and local checks, and how they match the catalogue.

uk_reference_list.csv: rows dated before 1100 in Wikipedia's "List of oldest buildings in the United Kingdom"
(https://en.wikipedia.org/wiki/List_of_oldest_buildings_in_the_United_Kingdom), read on 27 October 2026 through a
web reader that returns a summary: building, location and date as written there, with a short paraphrased note.
Each row is matched to the catalogue by name (normalised words) where possible.
nw_checks.csv: individual checks for north-west England items, with source URLs.
Run before 02_analyse.py.
"""
import os, re, csv, unicodedata
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SRC = "https://en.wikipedia.org/wiki/List_of_oldest_buildings_in_the_United_Kingdom"
ROWS = """Prehistoric|Knap of Howar|Papa Westray, Orkney|3800 BC|-3800|Neolithic farmstead|house
Prehistoric|West Kennet Long Barrow|Wiltshire|3650 BC|-3650|Passage grave|tomb
Prehistoric|Midhowe Chambered Cairn|Rousay, Orkney|3500 BC|-3500|Chambered cairn|tomb
Prehistoric|Trethevy Quoit|Tremar, Cornwall|3700 to 3500 BC|-3600|Neolithic dolmen|tomb
Prehistoric|Pentre Ifan|Nanhyfer, Pembrokeshire|3500 BC|-3500|Neolithic dolmen|tomb
Prehistoric|Tomb of the Eagles|South Ronaldsay, Orkney|3150 BC|-3150|Chambered tomb|tomb
Prehistoric|Skara Brae|Bay of Skaill, Mainland Orkney|3100 BC|-3100|Neolithic village|house
Prehistoric|Unstan Chambered Cairn|Stenness, Mainland Orkney|3400 to 2800 BC|-3100|Chambered cairn|tomb
Prehistoric|Belas Knap|Winchcombe, Gloucestershire|3000 BC|-3000|Neolithic long barrow|tomb
Prehistoric|Maeshowe|Stenness, Mainland Orkney|2700 BC|-2700|Chambered cairn and passage grave|tomb
Prehistoric|Barnhouse Settlement|Stenness, Mainland Orkney|2600 BC|-2600|Neolithic settlement|house
Prehistoric|Grimspound|Dartmoor, Devon|1300 BC|-1300|Bronze Age settlement|house
Iron Age and Roman|Jarlshof|Sumburgh, Shetland|200 BC|-200|Wheelhouse remains|house
Iron Age and Roman|Broch of Mousa|Mousa, Shetland|1st century BC|-50|Broch|tower
Iron Age and Roman|Bartlow Hills|Ashdon, Essex|1st to 2nd century|100|Roman burial mounds|tomb
Iron Age and Roman|Viroconium|Wroxeter, Shropshire|1st to 2nd century|100|Roman masonry, bathhouse|public
Iron Age and Roman|Temple of Claudius|Colchester, Essex|c. 60|60|Roman temple podium and vaults|church
Iron Age and Roman|Vinovia|Bishop Auckland, County Durham|mid 70s|75|Roman fort and settlement|castle
Iron Age and Roman|Caerleon Roman Amphitheatre|Caerleon, Newport|c. 80|80|Roman amphitheatre|public
Iron Age and Roman|Balkerne Gate|Colchester, Essex|c. 80|80|Roman city gateway|castle
Iron Age and Roman|Roman lighthouse at Dover Castle|Dover, Kent|1st century|50|Roman lighthouse|tower
Iron Age and Roman|Hardknott Roman Fort|Cumbria|c. 120 to 138|129|Roman fort|castle
Iron Age and Roman|Walls Castle|Ravenglass, Cumbria|c. 120|120|Roman bathhouse remains|public
Iron Age and Roman|Hadrian's Wall|Northern England|c. 122|122|Defensive wall|castle
Iron Age and Roman|Housesteads Roman Fort|Hexham, Northumberland|c. 124|124|Fort on Hadrian's Wall|castle
Iron Age and Roman|Jewry Wall|Leicester, Leicestershire|c. 125|125|Roman wall of a public building|public
Iron Age and Roman|Edin's Hall Broch|Duns, Berwickshire|c. 140|140|Broch|tower
Iron Age and Roman|London Wall|London|c. 200|200|Roman wall remains|castle
Iron Age and Roman|Painted House|Dover, Kent|c. 200|200|Roman house|house
Iron Age and Roman|Portchester Castle|Portchester, Hampshire|285 to 290|287|Walled Roman fort|castle
Iron Age and Roman|Pevensey Castle|Pevensey, East Sussex|280s|285|Roman fort curtain wall|castle
Iron Age and Roman|Cardiff Castle|Cardiff, Wales|c. 290|290|Sections of Roman fort wall|castle
Iron Age and Roman|Newport Arch|Lincoln|3rd century|250|Roman gate arch|castle
Iron Age and Roman|Multangular Tower|York|4th century|350|Roman fortifications|tower
Iron Age and Roman|Calleva Atrebatum walls|Silchester, Hampshire|4th century|350|Roman walls and amphitheatre|castle
Anglo-Saxon and early medieval|Beehive cells|Eileach an Naoimh, Argyll|6th century|550|Monastic cells|house
Anglo-Saxon and early medieval|St Martin's Church|Canterbury, Kent|597|597|Church|church
Anglo-Saxon and early medieval|Nendrum Monastery mill|Mahee Island, County Down|619|619|Tide mill|other
Anglo-Saxon and early medieval|St Peter-on-the-Wall|Bradwell-on-Sea, Essex|654|654|Chapel on Roman fort ruins|church
Anglo-Saxon and early medieval|Escomb Church|Escomb, County Durham|670|670|Church|church
Anglo-Saxon and early medieval|Ripon Cathedral|Ripon, North Yorkshire|672|672|Crypt|church
Anglo-Saxon and early medieval|Hexham Abbey|Hexham, Northumberland|674|674|Crypt|church
Anglo-Saxon and early medieval|St Peter's Church|Monkwearmouth, Sunderland|674|674|Monastery church|church
Anglo-Saxon and early medieval|St Mary Magdalene Church|Hart, County Durham|675|675|Church|church
Anglo-Saxon and early medieval|St Paul's Church|Jarrow, Tyne and Wear|680|680|Saxon chancel|church
Anglo-Saxon and early medieval|Anglian Tower|York|7th century|650|Fortification|tower
Anglo-Saxon and early medieval|St Laurence's Church|Bradford on Avon, Wiltshire|7th century|650|Church|church
Anglo-Saxon and early medieval|St Mary's Priory|Deerhurst, Gloucestershire|7th century|650|Church|church
Anglo-Saxon and early medieval|St Mary the Virgin Church|Prittlewell, Essex|pre-1066|1000|North wall and arch|church
Anglo-Saxon and early medieval|All Saints Church|Brixworth, Northamptonshire|650 to 870|760|Church|church
Anglo-Saxon and early medieval|Abbey Church of St Mary the Virgin|Sherborne, Dorset|705|705|Saxon cathedral and abbey|church
Anglo-Saxon and early medieval|Saint Helen's Chapel|Colchester, Essex|8th century|750|Chapel|church
Anglo-Saxon and early medieval|St Peter's Church|Conisbrough, South Yorkshire|8th century|750|Church|church
Anglo-Saxon and early medieval|Greensted Church|Greensted, Essex|845|845|Wooden church|church
Anglo-Saxon and early medieval|St Mary's Church|Barby, Northamptonshire|891|891|Church|church
Anglo-Saxon and early medieval|St Nicholas' Church|Leicester, Leicestershire|c. 900|900|Church|church
Anglo-Saxon and early medieval|St Peter's Church|Barton-upon-Humber, North Lincolnshire|9th and 10th centuries|900|Church, baptistery|church
Anglo-Saxon and early medieval|St Nicholas' Church|Worth, Crawley|c. 950 or 1050|950|Church|church
Anglo-Saxon and early medieval|St Mary's Church|Sompting, West Sussex|c. 960|960|Church|church
Anglo-Saxon and early medieval|All Saints' Church|Earls Barton, Northamptonshire|c. 970|970|Church tower|tower
Anglo-Saxon and early medieval|Stow Minster|Stow, Lincolnshire|975|975|Minster church|church
Anglo-Saxon and early medieval|Nendrum Monastery|Mahee Island, County Down|9th or 10th century|900|Monastic church|church
Anglo-Saxon and early medieval|St Mary's Church|Northchurch, Hertfordshire|late Anglo-Saxon|1000|Church walls|church
Norman to 1100|St Bene't's Church|Cambridge, Cambridgeshire|c. 1000|1000|Church tower|tower
Norman to 1100|Holy Trinity Church|Colchester, Essex|1020|1020|Anglo-Saxon tower|tower
Norman to 1100|Corhampton Church|Corhampton, Hampshire|c. 1020|1020|Saxon church|church
Norman to 1100|St Andrew's Church|Ashingdon, Essex|1020|1020|Parish church|church
Norman to 1100|St Martin's Church|Wareham, Dorset|1030|1030|Church|church
Norman to 1100|St Michael at the North Gate|Oxford|1040|1040|Church tower|tower
Norman to 1100|St George's Tower, Oxford Castle|Oxford|perhaps mid 11th century|1050|Tower|tower
Norman to 1100|Holy Trinity Church|Great Paxton, Cambridgeshire|1050|1050|Aisled church|church
Norman to 1100|St Chad's Church|Stafford, Staffordshire|1050|1050|Church|church
Norman to 1100|Berkhamsted Castle|Berkhamsted, Hertfordshire|1067|1067|Castle earthworks and ruins|castle
Norman to 1100|Chepstow Castle|Chepstow, Monmouthshire|1067|1067|Castle|castle
Norman to 1100|Norwich Castle|Norwich, Norfolk|1067|1067|Castle|castle
Norman to 1100|Lincoln Castle|Lincoln|1068|1068|Castle|castle
Norman to 1100|Canterbury Cathedral|Canterbury, Kent|1070|1070|Cathedral|church
Norman to 1100|St Michael's Church|Southampton, Hampshire|1070|1070|Church|church
Norman to 1100|Richmond Castle|Richmond, North Yorkshire|from 1071|1071|Castle|castle
Norman to 1100|Lincoln Cathedral|Lincoln|1072|1072|Cathedral, west end|church
Norman to 1100|Durham Castle|Durham|1072 (started)|1072|Castle|castle
Norman to 1100|Tower of London|London|1078|1078|Castle|castle
Norman to 1100|Hereford Cathedral|Hereford|1079|1079|Cathedral|church
Norman to 1100|Winchester Cathedral|Winchester, Hampshire|1079 (started)|1079|Cathedral|church
Norman to 1100|Rochester Cathedral|Rochester, Kent|1080|1080|Tower and nave piers|church
Norman to 1100|Ely Cathedral|Ely, Cambridgeshire|1083 (started)|1083|Cathedral|church
Norman to 1100|Shrewsbury Abbey|Shrewsbury, Shropshire|1083|1083|Abbey|church
Norman to 1100|St Mary's Church|Harrow on the Hill|1087 (started)|1087|Church|church
Norman to 1100|Icomb Place|Icomb, Gloucestershire|1085|1085|House|house
Norman to 1100|Hedingham Castle|Castle Hedingham, Essex|c. 1086|1086|Castle|castle
Norman to 1100|St Albans Cathedral|St Albans, Hertfordshire|1089|1089|Cathedral|church
Norman to 1100|St Nicholas Church|Iford, East Sussex|c. 1090|1090|Church|church
Norman to 1100|Durham Cathedral|Durham|1093 (started)|1093|Cathedral|church
Norman to 1100|Norwich Cathedral|Norwich, Norfolk|1096|1096|Cathedral|church
Norman to 1100|Westminster Hall|City of Westminster|1097|1097|Hall, part of the Palace of Westminster|house
Norman to 1100|Lancaster Castle|Lancaster, Lancashire|speculated 11th century|1050|Castle|castle
Norman to 1100|Borley Church|Borley, Essex|11th century|1050|Church|church
Norman to 1100|Conisbrough Castle|Conisbrough, South Yorkshire|11th century|1050|Castle|castle
Norman to 1100|St Botolph's Church|Botolphs, West Sussex|11th century|1050|Parish church|church"""

NW = [("Q7595057", "St Patrick's Chapel, Heysham", "ruin", "The ruin dates from the 8th or 9th century, and is built of sandstone rubble.",
       "https://en.wikipedia.org/wiki/St_Patrick%27s_Chapel,_Heysham")]


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(the|of|church|st|saint|s|and|at|on)\b", " ", re.sub(r"[^a-z ]", " ", s))
    return " ".join(s.split())


def main():
    D = pd.read_csv(os.path.join(ROOT, "data", "buildings.csv"), keep_default_na=False)
    U = D[D.country == "United Kingdom"]
    rows = []
    for line in ROWS.split("\n"):
        tab, name, place, date, yr, note, cat = line.split("|")
        key = norm(name); town = norm(place.split(",")[0])
        cand = [r for r in U.itertuples() if norm(r.label) == key or (key and key in norm(r.label) and (town in norm(r.label) or len(key.split()) >= 2 and key not in ("peter", "mary", "nicholas")))]
        exact = [r for r in cand if norm(r.label) == key]
        if len(exact) == 1: cand = exact
        if len(cand) > 1:  # prefer a candidate whose label names the place
            c2 = [r for r in cand if town and town.split()[0] in norm(r.label)]
            cand = c2 or cand
        m = cand[0] if len(cand) == 1 else None
        rows.append({"table": tab, "building": name, "location": place, "date_as_written": date, "year_approx": int(yr), "note": note,
                     "category": cat, "qid": m.qid if m else "", "catalogue_label": m.label if m else "", "catalogue_date": m.date_text if m else "",
                     "catalogue_state": m.state if m else "", "source_url": SRC, "read_on": "2026-10-27"})
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "data", "uk_reference_list.csv"), index=False)
    pd.DataFrame([{"qid": q, "label": l, "checked_state": s, "evidence": e, "source_url": u, "read_on": "2026-10-27"} for q, l, s, e, u in NW]).to_csv(
        os.path.join(ROOT, "data", "nw_checks.csv"), index=False)
    print("reference rows", len(rows), "matched", sum(1 for r in rows if r["qid"]))


if __name__ == "__main__":
    main()
