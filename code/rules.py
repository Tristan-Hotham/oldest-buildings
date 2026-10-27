"""Classification rules shared by the build and analysis scripts.

Every Wikidata item carries one or more 'instance of' classes (labels in English). From these,
plus its conservation state (P5816), current use (P366), material (P186) and its own label,
I assign:
  use   : original use (religious, defensive, domestic, civic, funerary, infrastructure, commemorative, unknown)
  form  : building, structure, earthwork
  state : standing (no ruin recorded), ruin, foundations or site, earthwork, lost
  today : original use, changed use, museum or visitor site, ruin or site, earthwork, lost, not recorded
Rules are regular expressions on lower-case class labels, applied in a fixed order.
"""
import re

USES = ["religious", "defensive", "domestic", "civic", "funerary", "infrastructure", "commemorative", "unknown"]
USE_LABEL = {"religious": "Religious", "defensive": "Defensive", "domestic": "Houses and palaces", "civic": "Civic and public",
             "funerary": "Tombs and funerary", "infrastructure": "Bridges, water and roads", "commemorative": "Monuments",
             "unknown": "Not clear"}

# classes that say nothing about use
GENERIC = re.compile(r"^(building|built structure|architectural landmark|historic site|historic building|monument|ancient monument|"
                     r"architectural heritage monument|kulturdenkmal|bodendenkmal|real property|architectural structure|structure|"
                     r"nonbuilding structure|tourist attraction|heritage site|none|unfinished building|underground structure|"
                     r"submerged structure|octagonal building|portal|façade|doorway|dome|iwan|mon|isar|kanji|decipoint|"
                     r"architectural reconstruction)$")
# things that are not buildings or structures: places, routes, objects and artworks
EXCLUDE = re.compile(r"(^street$|^square$|garden|urban park|^avenue$|land parcel|city block|historic village|grand place|mosaic|"
                     r"stained-glass|^bucket$|^lintel$|^minbar$|^road$|roman road|historic road|ancient trackway|stele|statue|"
                     r"relief|runestone|pictish stone|menhir|khachkar|cross$|^moai$|^sphinx$|^atlas$|grave marker|tombstone|"
                     r"boundary marker|^horos$|sundial|milestone|milliarium|^vishap$|^stechak$|monumental sculpture|daibutsu|"
                     r"^pillar$|cave with prehistoric art|^grotto$|^kōgoishi$|^pile$|triangulation station|^manor park$|"
                     r"^celtiberian town$|^decipoint$|^tell$|^ancient city$|^city$|^settlement$|^fortified town$|^historic village$|^cemetery$|^former cemetery$|^altar$|^arula \(altar\)$)")
# condition classes
LOST_C = re.compile(r"^(destroyed .*|former monument|former cemetery)$")
RUIN_C = re.compile(r"(\bruins?$|^ruins$|castle ruin|church ruin|monastery ruins|religious building ruin|synagogue ruin|mosque ruin|roman ruins)")
SITE_C = re.compile(r"(deserted castle site|^tell$|^stilt house$|archaeological park|archaeological site|castle site|^ancient city$)")
FORMER_C = re.compile(r"^(former |secularized |secularised |defunct )")
MUSEUM_C = re.compile(r"(museum)")
CHANGED_C = re.compile(r"^(hotel|parador|paradores de turismo|youth hostel|resort|ryokan|onsen ryokan|irish pub|boarding school)$")
RESIDENCE_C = re.compile(r"(residence of the british royal family|official residence|state guest house)")

RULES = [
    ("religious", r"church|chapel|cathedral|(?<!civil )basilica|abbey|priory|monaster|convent|nunnery|friary|hermitage|oratory|"
                  r"baptister|(?<!temple )temple(?! tank)|shrine|-ji$|jingū|taisha|shikina|shikige|sessha|massha|mosque|masjid|musalla|"
                  r"synagogue|pagoda|stupa|vihāra|gompa|^wat$|candi|mithraeum|hieron|heraion|serapeum|asclepeion|delphinion|"
                  r"sanctuary|ziggurat|gopuram|skete|martyrium|sangharama|mahavihara|^dō$|amida-dō|hokke-dō|dharma hall|main hall|"
                  r"pilgrim|reijō|chokugan|monzeki|shukubō|tatchū|bettō-ji|jōgaku-ji|kokushi genzaisha|chinjusha|keidai-sha|"
                  r"setsumatsusha|keigai-sessha|kanpei-sha|chokusaisha|moto-ise|holy well|ordination platform|zarih|pieve|collegiate|"
                  r"simultaneum|royal peculiar|clergy house|episcopal palace|gū\b|gū |hachiman|kapische|crypt|provost|archabbey|"
                  r"domus ecclesiae|propylaea|ancestral shrine|confucius|sun temple|speos|hydrangea temple|cave monastery|"
                  r"shōsō|commandry|grand shrine|kokubu|minaret|madrasa|temple complex"),
    ("funerary", r"kofun|fun$|-fun|burial|tomb|mausoleum|pyramid(?!.*mesoamerican)|necropolis|grave|tumulus|^mound$|cairn|dolmen|"
                 r"barrow|catacomb|mastaba|columbarium|hypogeum|sepulch|polyandrion|naveta|gonbad|türbe|kurgan|reference site|"
                 r"kofungun|chariot burial|imperial mausoleum|funerary"),
    ("defensive", r"castle|(?<!pur)fort(?!une)|fortress|fortif|citadel|rocca|castrum|castellum|burgus|^keep$|donjon|motte|hillfort|"
                  r"oppidum|broch|rampart|city wall|defensive wall|capital city wall|roman walls|^wall$|city gate|fortified gateway|"
                  r"^gate$|watchtower|defensive tower|gate tower|kremlin|limes|alcazaba|kasbah|ribat|qal'a|hiṣn|sconce|blockhouse|"
                  r"garrison|barracks|military|defen[cs]e line|cordon|bōrui|eupseong|^gord$|ringfort|ring fortress|castelliere|"
                  r"^warte$|vigilarium|defensive dyke|naval arsenal|principia|praetorium|château|alqasaba|acropolis|compound"),
    ("domestic", r"(?<!bath)(?<!guest )(?<!boat)(?<!play)(?<!ware)(?<!light)house|villa|domus|insula|palace|manor|mansion|residen|estate|masia|farm|^barn$|outbuilding|cortijo|pazo|cascina|"
                 r"alqueria|kominka|stilt|thatched|gosho|throne room|hôtel de|auszugshaus|palazzo|dovecote|granary"),
    ("civic", r"theatre|amphitheat|odeon|circus|hippodrome|stadium|sports venue|gymnasium|^gym$|palaestra|thermae|bath|balneum|"
              r"hammam|^spa$|forum|stoa|agora|civil basilica|bouleuterion|curia|macellum|market|caravanserai|funduk|mansio|guest house|"
              r"hostel|inn$|pub$|tavern|gasthaus|buschenschank|hospital|hôtel-dieu|hospice|school|university|library|prison|mint|"
              r"treasury|town hall|rathaus|city hall|parliament|administrative|public building|commercial building|warehouse|"
              r"workshop|brewery|winery|kiln|observatory|headquarters|bullring|playhouse|association football|colonnade|exedra|"
              r"hôtel de la région|national pavillon|saunas"),
    ("infrastructure", r"bridge|aqueduct|well|cistern|reservoir|water tank|ab anbar|aljibe|dam$|weir|canal|acequia|mill race|"
                       r"sewer|tunnel|lighthouse|pharos|port$|pier$|harbour|nilometer|fountain|nymphaeum|mill|irrigation|"
                       r"low-water crossing|temple tank|boathouse|retaining wall|covered passageway|mountain hut"),
    ("commemorative", r"obelisk|triumphal arch|^arch$|column|memorial|cenotaph|tropaion|choragic|tetrapylon|pedestal|"
                      r"monumental|victory|honorific"),
]
RULES = [(k, re.compile(v)) for k, v in RULES]

EARTHWORK = re.compile(r"(kofun|fun$|-fun|burial mound|tumulus|^mound$|hillfort|oppidum|motte|barrow|henge|rampart|dyke|ringfort|"
                       r"contour fort|promontory fort|ring fortress|^gord$|earthworks|reference site|"
                       r"kofungun|^cairn$|grave cairn|chambered cairn|mausoleum or tomb|imperial mausoleum/tomb|^tell$|kurgan)")
STRUCTURE_STRONG = re.compile(r"(pyramid|obelisk|ziggurat|stupa|bridge|aqueduct|wall|limes|cordon|defen[cs]e line|lighthouse|^arch$|triumphal arch|column|dam$|tower)")
STRUCTURE = re.compile(r"(cordon|defen[cs]e line|bridge|aqueduct|wall|gate$|gateway|arch$|obelisk|column|tower|well$|stepwell|cistern|dam$|weir|canal|"
                       r"lighthouse|pharos|fountain|pier$|tunnel|reservoir|water tank|ab anbar|aljibe|acequia|mill race|sewer|"
                       r"limes|tetrapylon|tropaion|pedestal|nilometer|pyramid|ziggurat|stupa|cenotaph|memorial|rampart|"
                       r"irrigation|low-water|temple tank|retaining|colonnade|exedra|propylaea|stoa|pagoda|minaret|dovecote|"
                       r"choragic|monumental)")
# classical and other ancient types that survive almost only as excavated or standing ruins
ANCIENT_RUIN = re.compile(r"^(insula|domus|thermae|roman temple|ancient greek temple|roman theatre|roman amphitheatre|greek theatre|odeon|"
                          r"forum|stoa|palaestra|gymnasium|bouleuterion|circus|hippodrome|macellum|nymphaeum|mithraeum|"
                          r"romano-celtic temple|hieron|heraion|delphinion|asclepeion|serapeum|treasury \(ancient greece\)|tholos|"
                          r"castrum|castellum|burgus|principia|praetorium|mansio|villa rustica|roman villa|ancient roman structure|"
                          r"egyptian temple|greek baths|balneum|ancient stadium|ancient greek stadium|roman limes|propylaea|"
                          r"ancient roman imperial palace|civil basilica|ancient roman cistern|roman mint|exedra|palaestra|ancient port|"
                          r"umayyad desert castles|acropolis|ancient city)$")

CONS_RUIN = {"ruinous", "partially destroyed", "damaged", "abandoned"}
CONS_LOST = {"demolished or destroyed", "unlocated, probably destroyed", "unknown location", "backfilled (conservation status)", "flooded"}
CONS_SITE = {"ruin, foundations only"}
CONS_OK = {"preserved", "restored", "renewed", "in situ", "architectural reconstruction", "structure under restoration", "ex situ"}

LABEL_RUIN = re.compile(r"(\bruins?\b|\bruine\b|\brovine\b|\bruinas?\b|\bruïne\b|\bruiny\b|ruined)", re.I)
LABEL_SITE = re.compile(r"(\bsite of\b|\bremains of\b|burgstall|\bburgstelle\b)", re.I)

MAT = [("stone", re.compile(r"stone|limestone|sandstone|marble|granite|basalt|tuff|tufa|travertine|ashlar|rubble|flint|slate|andesite|"
                            r"^rock$|bluestone|gneiss|schist|porphyry|chalk|dolerite|quartzite|diorite|breccia|ironstone|greensand|"
                            r"conglomerate|calcarenite|dolomite|syenite|^lava|trachyte|serpentin|alabaster|gypsum|masonry")),
       ("brick", re.compile(r"brick|^tile$|terracotta")),
       ("earth", re.compile(r"mudbrick|adobe|^mud$|rammed earth|^earth$|^soil$|cob$|^clay$|wattle|daub|turf|loam")),
       ("timber", re.compile(r"wood|timber|oak|pine|cedar|cypress|hinoki|larch|log$|^beam$|thatch|bamboo"))]
IMPLIED_TIMBER = re.compile(r"(stave church|wooden church|wooden bridge|thatched building|stilt house)")
IMPLIED_STONE = re.compile(r"(stone bridge|roman bridge)")


def use_of(labels):
    """Original use from a set of class labels (lower case)."""
    real = [l for l in labels if not GENERIC.match(l)]
    for k, rx in RULES:
        for l in real:
            if MUSEUM_C.search(l) or CHANGED_C.match(l):
                continue
            if rx.search(l):
                return k
    return "unknown"


def use_of_p366(lbl):
    l = lbl.lower()
    if l in ("place of worship", "structure of worship", "religion", "salah", "hindu pilgrimage site", "108 divya desams"):
        return "religious"
    if MUSEUM_C.search(l) or l in ("tourist attraction", "monument", "public space"):
        return "museum"
    return use_of({l})


def material_of(mats):
    out = set()
    for m in mats:
        m = m.lower()
        for k, rx in MAT:
            if rx.search(m):
                out.add(k); break
    return out


def century_of(year, prec):
    """(century number, BC flag) for a year in Wikidata's historical numbering (negative = BC)."""
    c = (abs(year) + 99) // 100
    return c, year < 0


def rep_year(year, prec):
    """A representative calendar year (negative = BC) used for sorting and grouping."""
    if prec >= 8:
        return year
    if prec == 7:
        c = (abs(year) + 99) // 100
        return -(c * 100 - 50) if year < 0 else c * 100 - 50
    m = (abs(year) + 999) // 1000
    return -(m * 1000 - 500) if year < 0 else m * 1000 - 500


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def date_text(year, prec):
    if prec >= 9:
        return f"{-year} BC" if year < 0 else f"AD {year}"
    if prec == 8:
        d = abs(year) // 10 * 10
        return f"{d}s BC" if year < 0 else f"{d}s"
    if prec == 7:
        c = (abs(year) + 99) // 100
        return f"{ordinal(c)} century" + (" BC" if year < 0 else "")
    m = (abs(year) + 999) // 1000
    return f"{ordinal(m)} millennium" + (" BC" if year < 0 else "")
