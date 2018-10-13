# Mongo
MONGO_ID = "id"
MONGO_TIMESTAMP = "insertTime"
MONGO_URL = "url"
MONGO_HTML = "html"
MONGO_UNIQUE_ID = "_id"

# Base URLs
URL_HLASOVANIA = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/hlasklub&ID={}"
URL_ZAKONY = "https://www.nrsr.sk/web/Default.aspx?sid=zakony/zakon&ZakZborID=13&CisObdobia=7&CPT={}"
URL_POSLANCI = "https://www.nrsr.sk/web/Default.aspx?sid=poslanci/poslanec&PoslanecID={}&CisObdobia=7"
URL_NRSR = "https://www.nrsr.sk/web/"
URL_NRSR_SCHODZE = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/schodze"
URL_ZOZNAM_ZAKONOV = "https://www.nrsr.sk/web/Default.aspx?sid=zakony%2fprehlad%2fpredlozene"
URL_ZOZNAM_PREDLOZENYCH = "https://www.nrsr.sk/web/Default.aspx?sid=zakony/sslp&PredkladatelID=0&PredkladatelPoslanecId={}&CisObdobia=7"
URL_HLASOVANIA_CPT = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/vyhladavanie_vysledok&CPT={}" 
URL_ZMENA = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/nrepdn_detail&id={}"

# Config
CONF_SCRAPE = "scrape"
CONF_SCRAPE_DELAY = "delay"
CONF_MONGO = "mongo"
CONF_MONGO_CLIENT = "client"
CONF_MONGO_DATABASE = "database"
CONF_MONGO_DATABASE_NAME = "name"
CONF_MONGO_COLLECTION = "collections"
CONF_MONGO_HLASOVANIE = "hlasovanie"
CONF_MONGO_POSLANEC = "poslanec"
CONF_MONGO_ZAKON = "zakon"
CONF_MONGO_LEGISLATIVNAINICIATIVA = "legislativnainiciativa"
CONF_MONGO_HLASOVANIETLAC = "hlasovanietlace"
CONF_MONGO_RAW = "raw"
CONF_MONGO_NODES = "nodes"
CONF_MONGO_EDGES = "edges"
CONF_MONGO_PARSED = "parsed"
CONF_NEO4J = "neo4j"
CONF_NEO4J_CLIENT = "client"
CONF_NEO4J_AUTH = "auth"
CONF_NEO4J_URI = "uri"
CONF_NEO4J_TEMP_CSV = "temp_csv"
CONF_NEO4J_PERIODIC_COMMIT = "periodic_commit"
CONF_LOGGING = "logging"
CONF_LOGGING_FILENAME = "filename"

# Scrape
SCRAPE_MAX_ID_POSLANEC = 1000

# Process
PARSE_ERROR_NOT_FOUND = "We are sorry, but an unexpected error occured on the website."

# neo4j
NEO4J_INTEGER = "ToInteger({})"
NEO4J_STRING = "{}"
NEO4J_DATETIME = "datetime({})"
NEO4J_BOOLEAN = "(CASE {} WHEN \"True\" THEN true ELSE false END)"

NEO4J_NULLVALUE = "nullValue"

NEO4J_OBJECT_TYPE = "object_type"
NEO4J_NODE_NAME = "node_name"
NEO4J_BEGINNING_ID = "beginning_id"
NEO4J_ENDING_ID = "ending_id"
NEO4J_BEGINNING_NAME = "beginning_name"
NEO4J_ENDING_NAME = "ending_name"
NEO4J_EDGE_NAME = "edge_name"
NEO4J_OBJECT_NODE = "node"
NEO4J_OBJECT_EDGE = "edge"

# Node names

NODE_NAME_KLUB = "Klub"
NODE_NAME_POSLANEC = "Poslanec"
NODE_NAME_HLASOVANIE = "Hlasovanie"
NODE_NAME_VYBOR = "Výbor"
NODE_NAME_DELEGACIA = "Delegácia"
NODE_NAME_ZAKON = "Zákon"
NODE_NAME_SPEKTRUM = "Spektrum"

# edge names

EDGE_NAME_CLEN = "Člen"
EDGE_NAME_HLASOVAL = "Hlasoval"
EDGE_NAME_NAVHRNUTY = "Navrhnutý"
EDGE_NAME_GESTORSKY = "Gestorský"
EDGE_NAME_NAVRHOL = "Navrhol"
EDGE_NAME_BOL_CLEN = "BolČlenom"
EDGE_NAME_HLASOVALO_O = "HlasovaloO"

##########
# FIELDS #
##########

HLASOVANIE_CAS = "časHlasovania"
HLASOVANIE_CISLO = "čísloHlasovania"
HLASOVANIE_OBDOBIE = "čísloObdobia"
HLASOVANIE_IDZAKZBOR = "idZakZbor"
HLASOVANIE_SCHODZA = "čísloSchôdze"
HLASOVANIE_NAZOV = "názovHlasovania"
HLASOVANIE_VYSLEDOK = "výsledokHlasovania"
HLASOVANIE_INDIVIDUALNE = "individuálne"
HLASOVANIE_KLUB = "klub"
HLASOVANIE_HLAS = "hlas"
HLASOVANIE_CELE_MENO = "celéMeno"
HLASOVANIE_SURHN_PRITOMNI = "súhrnPrítomní"
HLASOVANIE_SURHN_HLASUJUCICH = "súhrnHlasujúcich"
HLASOVANIE_SURHN_ZA = "súhrnZa"
HLASOVANIE_SURHN_PROTI = "súhrnProti"
HLASOVANIE_SURHN_ZDRZALO = "súhrnZdržalo"
HLASOVANIE_SURHN_NEHLASOVALO = "súhrnNehlasovalo"
HLASOVANIE_SUHRN_NEPRITOMNI = "súhrnNeprítomní"
HLASOVANIE_SUHRN_DICT = {
    "Prítomní": HLASOVANIE_SURHN_PRITOMNI,
    "Hlasujúcich": HLASOVANIE_SURHN_HLASUJUCICH,
    "[Z] Za hlasovalo": HLASOVANIE_SURHN_ZA,
    "[P] Proti hlasovalo": HLASOVANIE_SURHN_PROTI,
    "[?] Zdržalo sa hlasovania": HLASOVANIE_SURHN_ZDRZALO,
    "[N] Nehlasovalo": HLASOVANIE_SURHN_NEHLASOVALO,
    "[0] Neprítomní": HLASOVANIE_SUHRN_NEPRITOMNI
}
HLASOVANIE_POSLANEC_DICT = {
    "PoslanecID": MONGO_ID,
    "CisObdobia": HLASOVANIE_OBDOBIE
}
HLASOVANIE_URL_DICT = {
    "CisObdobia": HLASOVANIE_OBDOBIE,
    "CisSchodze": HLASOVANIE_SCHODZA,
    "ZakZborID": HLASOVANIE_IDZAKZBOR
}

POSLANEC_PRIEZVISKO = "priezvisko"
POSLANEC_MENO = "meno"
POSLANEC_CLENSTVO = "členstvo"
POSLANEC_FOTO = "fotografia"
POSLANEC_NARODENY = "narodený"
POSLANEC_KANDIDOVAL = "kandidovalZa"
POSLANEC_TITUL = "titul"
POSLANEC_NARODNOST = "národnosť"
POSLANEC_BYDLISKO = "bydlisko"
POSLANEC_KRAJ = "kraj"
POSLANEC_EMAIL = "email"
POSLANEC_WEB = "web"
POSLANEC_AKTIVNY = "aktívny"
POSLANEC_INFO_DICT = {
    "meno": POSLANEC_MENO,
    "titul": POSLANEC_TITUL,
    "priezvisko": POSLANEC_PRIEZVISKO,
    "kandidoval(a) za": POSLANEC_KANDIDOVAL,
    "narodený(á)": POSLANEC_NARODENY,
    "národnosť": POSLANEC_NARODNOST,
    "bydlisko": POSLANEC_BYDLISKO,
    "kraj": POSLANEC_KRAJ,
    "e-mail": POSLANEC_EMAIL,
    "www": POSLANEC_WEB,
    "fotografia": POSLANEC_FOTO
}

KLUB_NAZOV = "názov"
KLUB_POCET = "početPoslancov"
KLUB_LSNS = "ĽSNS"
KLUB_SAS = "SaS"
KLUB_SMER = "Smer-SD"
KLUB_SME_RODINA = "SME RODINA"
KLUB_SNS = "SNS"
KLUB_OLANO = "OĽANO"
KLUB_MOST = "MOST-HÍD"
KLUB_NEZARADENI = "Nezaradení"
KLUB_DICT = {
    "Klub Kotleba - Ľudová strana Naše Slovensko": KLUB_LSNS,
    "Klub ĽS Naše Slovensko": KLUB_LSNS,
    "Klub MOST - HÍD": KLUB_MOST,
    "Klub OBYČAJNÍ ĽUDIA a nezávislé osobnosti": KLUB_OLANO,
    "Klub OĽANO": KLUB_OLANO,
    "Klub SME RODINA - Boris Kollár": KLUB_SME_RODINA,
    "Klub SME RODINA": KLUB_SME_RODINA,
    "Klub SMER - sociálna demokracia": KLUB_SMER,
    "Klub SMER - SD": KLUB_SMER,
    "Klub Sloboda a Solidarita": KLUB_SAS,
    "Klub SaS": KLUB_SAS,
    "Klub Slovenská národná strana": KLUB_SNS,
    "Klub SNS": KLUB_SNS
}

ZAKON_DRUH = "druh"
ZAKON_POPIS = "popis"
ZAKON_STAV = "stav"
ZAKON_VYSLEDOK = "výsledok"
ZAKON_DATUM_DORUCENIA = "dátumDoručenia"
ZAKON_NAVRHOVATEL = "navrhovateľ"
ZAKON_NAZOV = "názov"
ZAKON_POSLEDNE_CPT = "poslednéČPT"
ZAKON_ROZHODNUTIE_VYBORY = "rozhodnutieVýbory"
ZAKON_ROZHODNUTIE_GESTORSKY = "rozhodnutieGestorskýVýbor"
ZAKON_ROZHODNUTIE_VYSLEDOK = "rozhodnutieVýsledok"
ZAKON_CITANIE1_SCHODZA = "čítanie1ČísloSchôdze"
ZAKON_CITANIE1_UZNESENIE = "čítanie1Uznesenie"
ZAKON_CITANIE1_VYBORY = "čítanie1Výbory"
ZAKON_CITANIE1_GESTORSKY = "čítanie1GestorskýVýbor"
ZAKON_CITANIE1_SLKLABEL = "čítanie1SlkLabel"
ZAKON_CITANIE1_VYSLEDOK = "čítanie1Výsledok"
ZAKON_ROKOVANIE_VYBORY = "rokovanieVýbory"
ZAKON_PREROKOVANIE_GESTORSKY = "rokovanieDátumGestorskýVýbor"
ZAKON_GESTORSKY = "gestorskýVýbor"
ZAKON_CITANIE2_PREROKOVANY = "čítanie2Info"
ZAKON_CITANIE2_STANOVISKO = "čítanie2Stanovisko"
ZAKON_CITANIE2_VYSLEDOK = "čítanie2Výsledok"
ZAKON_CITANIE3_PREROKOVANY = "čítanie3Info"
ZAKON_CITANIE3_VYSLEDOK = "čítanie3Výsledok"
ZAKON_REDAKCIA_ODOSLANY = "redakciaOdoslaný"
ZAKON_REDAKCIA_VYSLEDOK = "redakciaVýsledok"
ZAKON_REDAKCIA_CISLO = "redakciaČísloZákona"
ZAKON_ID_DICT = {
    "_sectionLayoutContainer_ctl01__ProcessStateLabel": ZAKON_STAV,
    "_sectionLayoutContainer_ctl01__CurrentResultLabel": ZAKON_VYSLEDOK,
    "_sectionLayoutContainer_ctl01__SslpNameLabel": ZAKON_NAZOV,
    "_sectionLayoutContainer_ctl01_ctl00__CategoryNameLabel": ZAKON_DRUH,
    "_sectionLayoutContainer_ctl01_ctl00__LastCptLabel": ZAKON_POSLEDNE_CPT,
    "_sectionLayoutContainer_ctl01_ctl00__DatumDoruceniaLabel": ZAKON_DATUM_DORUCENIA,
    "_sectionLayoutContainer_ctl01_ctl00__NavrhovatelLabel": ZAKON_NAVRHOVATEL,
    "_sectionLayoutContainer_ctl01_ctl00__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl01__VyboryLabel": ZAKON_ROZHODNUTIE_VYBORY,
    "_sectionLayoutContainer_ctl01_ctl01__GestorskyVyborLabel": ZAKON_ROZHODNUTIE_GESTORSKY,
    "_sectionLayoutContainer_ctl01_ctl01__ResultLabel": ZAKON_ROZHODNUTIE_VYSLEDOK,
    "_sectionLayoutContainer_ctl01_ctl01__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl02__CisSchodzeLabel": ZAKON_CITANIE1_SCHODZA,
    "_sectionLayoutContainer_ctl01_ctl02__UznesenieLabel": ZAKON_CITANIE1_UZNESENIE,
    "_sectionLayoutContainer_ctl01_ctl02__VyboryLabel": ZAKON_CITANIE1_VYBORY,
    "_sectionLayoutContainer_ctl01_ctl02__GestorskyVyborLabel": ZAKON_CITANIE1_GESTORSKY,
    "_sectionLayoutContainer_ctl01_ctl02__SlkLabel": ZAKON_CITANIE1_SLKLABEL,
    "_sectionLayoutContainer_ctl01_ctl02__ResultLabel": ZAKON_CITANIE1_VYSLEDOK,
    "_sectionLayoutContainer_ctl01_ctl02__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl03__VyboryLabel": ZAKON_ROKOVANIE_VYBORY,
    "_sectionLayoutContainer_ctl01_ctl03__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl04__DatumPrerokovaniaLabel": ZAKON_PREROKOVANIE_GESTORSKY,
    "_sectionLayoutContainer_ctl01_ctl04__GVNameLabel": ZAKON_GESTORSKY,
    "_sectionLayoutContainer_ctl01_ctl04__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl05__PrerokovanyLabel": ZAKON_CITANIE2_PREROKOVANY,
    "_sectionLayoutContainer_ctl01_ctl05__ZaslaneStanoviskoLabel": ZAKON_CITANIE2_STANOVISKO,
    "_sectionLayoutContainer_ctl01_ctl05__PdnList__PdnLabel": None,
    "_sectionLayoutContainer_ctl01_ctl05__ResultLabel": ZAKON_CITANIE2_VYSLEDOK,
    "_sectionLayoutContainer_ctl01_ctl06__PrerokovanyLabel": ZAKON_CITANIE3_PREROKOVANY,
    "_sectionLayoutContainer_ctl01_ctl06__ResultLabel": ZAKON_CITANIE3_VYSLEDOK,
    "_sectionLayoutContainer_ctl01_ctl06__documentsList__captionLabel": None,
    "_sectionLayoutContainer_ctl01_ctl07__OdoslanyLabel": ZAKON_REDAKCIA_ODOSLANY,
    "_sectionLayoutContainer_ctl01_ctl07__ResultLabel": ZAKON_REDAKCIA_VYSLEDOK,
    "_sectionLayoutContainer_ctl01_ctl07__CiastkaLabel": ZAKON_REDAKCIA_CISLO
}
ZAKON_ZMENY = "návrhyZmien"
ZAKON_ZMENY_CAS = "časNávrhu"
ZAKON_ZMENY_PREDKLADATEL = "predkladateľ"
ZAKON_ZMENY_URL = "urlZmena"
ZAKON_ZMENY_DOKUMENT = "urlDokument"
ZAKON_ZMENY_HLASOVANIE_URL = "urlHlasovanie"
ZAKON_ZMENY_HLASOVANIE_ID = "idHlasovanie"
ZAKON_ZMENY_HLASOVANIE_VYSLEDOK = "výsledokHlasovanie"

SPEKTRUM_KOALICIA = "Koalícia"
SPEKTRUM_OPOZICIA = "Opozícia"
SPEKTRUM_CLEN = {
    KLUB_LSNS: SPEKTRUM_OPOZICIA,
    KLUB_SAS: SPEKTRUM_OPOZICIA,
    KLUB_SME_RODINA: SPEKTRUM_OPOZICIA,
    KLUB_OLANO: SPEKTRUM_OPOZICIA,
    KLUB_NEZARADENI: SPEKTRUM_OPOZICIA,
    KLUB_SMER: SPEKTRUM_KOALICIA,
    KLUB_SNS: SPEKTRUM_KOALICIA,
    KLUB_MOST: SPEKTRUM_KOALICIA
}

PREDLOZILZAKON_LIST = "zoznamZákonov"

HLASOVANIETLAC_LIST = "zoznamHlasovaní"

ZMENA_NAZOV = "názov"
ZMENA_PREDKLADATEL = "navrhovateľ"
ZMENA_SCHODZA = "čísloSchôdze"
ZMENA_OBDOBIE = "čísloObdobia"
ZMENA_DATUM = "dátumPodania"
ZMENA_DALSI = "ďalšíNavrhovatelia"
ZMENA_PODPISANI = "podpísaníPoslanci"
ZMENA_HLASOVANIE = "idHlasovania"
ZMENA_DOKUMENT = "dokument"
ZMENA_DICT = {
    "Názov": ZMENA_NAZOV,
    "Predkladateľ": ZMENA_PREDKLADATEL,
    "Číslo schôdze": ZMENA_SCHODZA,
    "Volebné obdobie": ZMENA_OBDOBIE,
    "Dátum podania": ZMENA_DATUM,
    "Podpísaní poslanci": ZMENA_PODPISANI,
    "Ďalší predkladatelia": ZMENA_DALSI,
    "Hlasovanie o návrhu": ZMENA_HLASOVANIE
}


CLEN_NAPOSLEDY = "časNaposledy"
CLEN_TYP = "typČlenstva"
CLEN_CLEN = "Člen"
CLEN_NAHRADNIK = "Náhradník"
CLEN_PODPREDSEDA = "Podpredseda"
CLEN_OVEROVATEL = "Overovateľ"
CLEN_PREDSEDA = "Predseda"
CLEN_VEDUCI = "Vedúci"
CLEN_TYP_DICT = {
    "Člen": CLEN_CLEN,
    "Členka": CLEN_CLEN,
    "Podpredseda": CLEN_PODPREDSEDA,
    "Podpredsedníčka": CLEN_PODPREDSEDA,
    "Podpredeseda": CLEN_PODPREDSEDA,
    "Predseda": CLEN_PREDSEDA,
    "Predsedníčka": CLEN_PREDSEDA,
    "Overovateľ": CLEN_OVEROVATEL,
    "Overovateľka": CLEN_OVEROVATEL,
    "Náhradný člen": CLEN_NAHRADNIK,
    "Náhradná členka": CLEN_NAHRADNIK,
    "Náhradník": CLEN_NAHRADNIK,
    "Náhradníčka": CLEN_NAHRADNIK,
    "Vedúci": CLEN_VEDUCI,
    "Vedúca": CLEN_VEDUCI
}

HLASOVAL_HLAS = "hlas"
HLASOVAL_KLUB = "klub"
HLASOVAL_ZA = "Za"
HLASOVAL_PROTI = "Proti"
HLASOVAL_ZDRZAL = "Zdržal sa"
HLASOVAL_NEPRITOMNY = "Neprítomný"
HLASOVAL_NEHLASOVAL = "Nehlasoval"
HLASOVAL_NEPLATNY = "Neplatný"
HLASOVAL_HLAS_DICT = {
    "[Z]": HLASOVAL_ZA,
    "[P]": HLASOVAL_PROTI,
    "[?]": HLASOVAL_ZDRZAL,
    "[N]": HLASOVAL_NEHLASOVAL,
    "[0]": HLASOVAL_NEPRITOMNY,
    "[-]": HLASOVAL_NEPLATNY
}

NAVRHNUTY_LEHOTA = "lehota"
NAVRHNUTY_TYP = "typ"
NAVRHNUTY_GESTORSKY = "Gestorský"
NAVRHNUTY_DOPLNUJUCI = "Doplňujúci"

NAVRHOL_NAVRHOVATEL = "navrhovateľ"
NAVRHOL_VLADA = "Vláda"
NAVRHOL_POSLANCI = "Poslanci"