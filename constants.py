#############
# Base URLs #
#############

URL_HLASOVANIA = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/hlasklub&ID={}"
URL_ZAKONY = "https://www.nrsr.sk/web/Default.aspx?sid=zakony/zakon&ZakZborID=13&CisObdobia=7&CPT={}"
URL_POSLANCI = "https://www.nrsr.sk/web/Default.aspx?sid=poslanci/poslanec&PoslanecID={}&CisObdobia=7"
URL_NRSR = "https://www.nrsr.sk/web/"
URL_NRSR_SCHODZE = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/schodze"
URL_ZOZNAM_ZAKONOV = "https://www.nrsr.sk/web/Default.aspx?sid=zakony%2fprehlad%2fpredlozene"
URL_ZOZNAM_PREDLOZENYCH = "https://www.nrsr.sk/web/Default.aspx?sid=zakony/sslp&PredkladatelID=0&PredkladatelPoslanecId={}&CisObdobia=7"
URL_HLASOVANIA_CPT = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/hlasovanie/vyhladavanie_vysledok&CPT={}"
URL_ZMENA = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/nrepdn_detail&id={}"
URL_ROZPRAVA = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/rozprava/vyhladavanie&CisObdobia=7&PoslanecID={}"

##########
# Config #
##########

# Scrape
CONF_SCRAPE = "scrape"
CONF_SCRAPE_DELAY = "delay"

# Mongo
CONF_MONGO = "mongo"
CONF_MONGO_CLIENT = "client"
CONF_MONGO_DATABASE = "database"
CONF_MONGO_DATABASE_NAME = "name"
CONF_MONGO_COLLECTION = "collections"

# Mongo collections

## Names
CONF_MONGO_HLASOVANIE = "hlasovanie"
CONF_MONGO_POSLANEC = "poslanec"
CONF_MONGO_ZAKON = "zakon"
CONF_MONGO_LEGISLATIVNAINICIATIVA = "legislativnainiciativa"
CONF_MONGO_HLASOVANIETLAC = "hlasovanietlace"
CONF_MONGO_ZMENA = "zmena"
CONF_MONGO_ROZPRAVA = "rozprava"

## Prefixes
CONF_MONGO_RAW = "raw"
CONF_MONGO_NODES = "nodes"
CONF_MONGO_EDGES = "edges"
CONF_MONGO_PARSED = "parsed"

# Neo4j
CONF_NEO4J = "neo4j"
CONF_NEO4J_CLIENT = "client"
CONF_NEO4J_AUTH = "auth"
CONF_NEO4J_URI = "uri"
CONF_NEO4J_TEMP_CSV = "temp_csv"
CONF_NEO4J_IMPORT_PATH = "import_path"
CONF_NEO4J_PERIODIC_COMMIT = "periodic_commit"

# Logging
CONF_LOGGING = "logging"
CONF_LOGGING_FILENAME = "filename"

##########
# Scrape #
##########
SCRAPE_MAX_ID_POSLANEC = 1000
SCRAPE_ROZPRAVA_EVENT_ARGUMENT = '<input name="__EVENTARGUMENT" value="{}" />'
SCRAPE_ROZPRAVA_EVENT_TARGET = '<input name="__EVENTTARGET" value="{}" />'
SCRAPE_ROZPRAVA_SEARCH_BUTTON = "_sectionLayoutContainer$ctl01$_searchButton"
SCRAPE_ROZPRAVA_FORM = "_sectionLayoutContainer$ctl01$_resultGrid"
SCRAPE_ROZPRAVA_TABLE = "#_sectionLayoutContainer_ctl01__resultGrid"

###########
# Process #
###########
PARSE_ERROR_NOT_FOUND = "We are sorry, but an unexpected error occured on the website."

#########
# Neo4j #
#########

NEO4J_BATCH_INSERT = 10000

# Query formatting
NEO4J_INTEGER = "ToInteger({})"
NEO4J_STRING = "{}"
NEO4J_DATETIME = "datetime({})"
NEO4J_BOOLEAN = "(CASE {} WHEN \"True\" THEN true ELSE false END)"
NEO4J_NULLVALUE = "nullValue"

# CSV fields
NEO4J_OBJECT_TYPE = "object_type"
NEO4J_NODE_NAME = "node_name"
NEO4J_BEGINNING_ID = "beginning_id"
NEO4J_ENDING_ID = "ending_id"
NEO4J_BEGINNING_NAME = "beginning_name"
NEO4J_ENDING_NAME = "ending_name"
NEO4J_EDGE_NAME = "edge_name"
NEO4J_OBJECT_NODE = "node"
NEO4J_OBJECT_EDGE = "edge"

#########
# Mongo #
#########

MONGO_ID = "id"
MONGO_TIMESTAMP = "insertTime"
MONGO_URL = "url"
MONGO_HTML = "html"
MONGO_UNIQUE_ID = "_id"
MONGO_BATCH_INSERT = 10000
MONGO_PAGE = "page"

#########
# Nodes #
#########

# Names
NODE_NAME_KLUB = "Klub"
NODE_NAME_POSLANEC = "Poslanec"
NODE_NAME_HLASOVANIE = "Hlasovanie"
NODE_NAME_VYBOR = "Vybor"
NODE_NAME_DELEGACIA = "Delegacia"
NODE_NAME_ZAKON = "Zakon"
NODE_NAME_SPEKTRUM = "Spektrum"
NODE_NAME_ZMENA = "Zmena"
NODE_NAME_ROZPRAVA = "Rozprava"

# Fields

## Hlasovanie
HLASOVANIE_CAS = "casHlasovania"
HLASOVANIE_CISLO = "cisloHlasovania"
HLASOVANIE_OBDOBIE = "cisloObdobia"
HLASOVANIE_IDZAKZBOR = "idZakZbor"
HLASOVANIE_SCHODZA = "cisloSchodze"
HLASOVANIE_NAZOV = "nazovHlasovania"
HLASOVANIE_VYSLEDOK = "vysledokHlasovania"
HLASOVANIE_INDIVIDUALNE = "individualne"
HLASOVANIE_KLUB = "klub"
HLASOVANIE_HLAS = "hlas"
HLASOVANIE_CELE_MENO = "celeMeno"
HLASOVANIE_SURHN_PRITOMNI = "suhrnPritomni"
HLASOVANIE_SURHN_HLASUJUCICH = "suhrnHlasujucich"
HLASOVANIE_SURHN_ZA = "suhrnZa"
HLASOVANIE_SURHN_PROTI = "suhrnProti"
HLASOVANIE_SURHN_ZDRZALO = "suhrnZdrzalo"
HLASOVANIE_SURHN_NEHLASOVALO = "suhrnNehlasovalo"
HLASOVANIE_SUHRN_NEPRITOMNI = "suhrnNepritomni"
HLASOVANIE_SUHRN_NEPLATNY = "suhrnNeplatny"
HLASOVANIE_SUHRN_DICT = {
    "Prítomní": HLASOVANIE_SURHN_PRITOMNI,
    "Hlasujúcich": HLASOVANIE_SURHN_HLASUJUCICH,
    "[Z] Za hlasovalo": HLASOVANIE_SURHN_ZA,
    "[P] Proti hlasovalo": HLASOVANIE_SURHN_PROTI,
    "[?] Zdržalo sa hlasovania": HLASOVANIE_SURHN_ZDRZALO,
    "[N] Nehlasovalo": HLASOVANIE_SURHN_NEHLASOVALO,
    "[0] Neprítomní": HLASOVANIE_SUHRN_NEPRITOMNI,
    "[X] Neplatných hlasov": HLASOVANIE_SUHRN_NEPLATNY
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

## Poslanec
POSLANEC_PRIEZVISKO = "priezvisko"
POSLANEC_MENO = "meno"
POSLANEC_CLENSTVO = "clenstvo"
POSLANEC_FOTO = "fotografia"
POSLANEC_NARODENY = "narodeny"
POSLANEC_KANDIDOVAL = "kandidovalZa"
POSLANEC_TITUL = "titul"
POSLANEC_NARODNOST = "narodnost"
POSLANEC_BYDLISKO = "bydlisko"
POSLANEC_KRAJ = "kraj"
POSLANEC_EMAIL = "email"
POSLANEC_WEB = "web"
POSLANEC_AKTIVNY = "aktivny"
POSLANEC_DELEGACIA = "delegácia"
POSLANEC_VYBOR = "výbor"
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

## Klub
KLUB_NAZOV = "nazov"
KLUB_POCET = "pocetPoslancov"
KLUB_LSNS = "LSNS"
KLUB_SAS = "SaS"
KLUB_SMER = "Smer-SD"
KLUB_SME_RODINA = "SME RODINA"
KLUB_SNS = "SNS"
KLUB_OLANO = "OLANO"
KLUB_MOST = "MOST-HID"
KLUB_NEZARADENI = "Nezaradeni"
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

## Zakon
ZAKON_DRUH = "druh"
ZAKON_POPIS = "popis"
ZAKON_STAV = "stav"
ZAKON_VYSLEDOK = "vysledok"
ZAKON_DATUM_DORUCENIA = "datumDorucenia"
ZAKON_NAVRHOVATEL = "navrhovatel"
ZAKON_NAZOV = "nazov"
ZAKON_POSLEDNE_CPT = "posledneCPT"
ZAKON_ROZHODNUTIE_VYBORY = "rozhodnutieVybory"
ZAKON_ROZHODNUTIE_GESTORSKY = "rozhodnutieGestorskýVybor"
ZAKON_ROZHODNUTIE_VYSLEDOK = "rozhodnutieVysledok"
ZAKON_CITANIE1_SCHODZA = "citanie1CisloSchodze"
ZAKON_CITANIE1_UZNESENIE = "citanie1Uznesenie"
ZAKON_CITANIE1_VYBORY = "citanie1Vybory"
ZAKON_CITANIE1_GESTORSKY = "citanie1GestorskyVybor"
ZAKON_CITANIE1_SLKLABEL = "citanie1SlkLabel"
ZAKON_CITANIE1_VYSLEDOK = "citanie1Vysledok"
ZAKON_ROKOVANIE_VYBORY = "rokovanieVybory"
ZAKON_PREROKOVANIE_GESTORSKY = "rokovanieDatumGestorskyVybor"
ZAKON_GESTORSKY = "gestorskyVybor"
ZAKON_CITANIE2_PREROKOVANY = "citanie2Info"
ZAKON_CITANIE2_STANOVISKO = "citanie2Stanovisko"
ZAKON_CITANIE2_VYSLEDOK = "citanie2Vysledok"
ZAKON_CITANIE3_PREROKOVANY = "citanie3Info"
ZAKON_CITANIE3_VYSLEDOK = "citanie3Vysledok"
ZAKON_REDAKCIA_ODOSLANY = "redakciaOdoslany"
ZAKON_REDAKCIA_VYSLEDOK = "redakciaVysledok"
ZAKON_REDAKCIA_CISLO = "redakciaCisloZakona"
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
ZAKON_ZMENY = "navrhyZmien"
ZAKON_ZMENY_CAS = "casNavrhu"
ZAKON_ZMENY_PREDKLADATEL = "predkladatel"
ZAKON_ZMENY_URL = "urlZmena"
ZAKON_ZMENY_DOKUMENT = "urlDokument"
ZAKON_ZMENY_HLASOVANIE_URL = "urlHlasovanie"
ZAKON_ZMENY_HLASOVANIE_ID = "idHlasovanie"
ZAKON_ZMENY_HLASOVANIE_VYSLEDOK = "vysledokHlasovanie"

## Spektrum
SPEKTRUM_KOALICIA = "Koalicia"
SPEKTRUM_OPOZICIA = "Opozicia"
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

## PredlozilZakon
PREDLOZILZAKON_LIST = "zoznamZakonov"

## HlasovanieTlac
HLASOVANIETLAC_LIST = "zoznamHlasovani"

## Zmena
ZMENA_NAZOV = "nazov"
ZMENA_PREDKLADATEL = "navrhovatel"
ZMENA_SCHODZA = "cisloSchodze"
ZMENA_OBDOBIE = "cisloObdobia"
ZMENA_DATUM = "datumPodania"
ZMENA_DALSI = "dalsiNavrhovatelia"
ZMENA_PODPISANI = "podpisaniPoslanci"
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

# Rozprava
ROZPRAVA_CAS_ZACIATOK = "casZaciatok"
ROZPRAVA_CAS_KONIEC = "casKoniec"
ROZPRAVA_SCHODZA = "cisloSchodze"
ROZPRAVA_SCHODZA_DEN = "denSchodze"
ROZPRAVA_SCHODZA_CAST_DNA = "castDnaSchodze"
ROZPRAVA_TLAC = "tlac"
ROZPRAVA_ZAZNAM_VYSTUPENIA = "zaznamVystupenia"
ROZPRAVA_ZAZNAM_ROKOVANIA = "zaznamRokovania"
ROZPRAVA_TYP_VYSTUPENIA = "typVystupenia"
ROZPRAVA_POSLANEC_ID = "poslanecId"
ROZPRAVA_POSLANEC_MENO = "meno"
ROZPRAVA_POSLANEC_PRIEZVISKO = "priezvisko"
ROZPRAVA_POSLANEC_KLUB = "klub"
ROZPRAVA_POSLANEC_TYP = "typPoslanca"
ROZPRAVA_TEXT = "text"
ROZPRAVA_VYSTUPENIA = "vystupenia"
ROZPRAVA_DLZKA = "dlzkaVystupenia"

#########
# Edges #
#########

# Names
EDGE_NAME_CLEN = "Clen"
EDGE_NAME_HLASOVAL = "Hlasoval"
EDGE_NAME_NAVRHNUTY = "Navrhnuty"
EDGE_NAME_GESTORSKY = "Gestorsky"
EDGE_NAME_NAVRHOL = "Navrhol"
EDGE_NAME_BOL_CLEN = "BolClenom"
EDGE_NAME_HLASOVALO_O = "HlasovaloO"
EDGE_NAME_PODPISAL = "Podpisal"
EDGE_NAME_NAVRHNUTA = "Navrhnuta"
EDGE_NAME_VYSTUPIL = "Vystupil"
EDGE_NAME_TYKALA_SA = "TykalaSa"

# Fields

## Clen
CLEN_NAPOSLEDY = "casNaposledy"
CLEN_TYP = "typClenstva"
CLEN_CLEN = "Clen"
CLEN_NAHRADNIK = "Nahradnik"
CLEN_PODPREDSEDA = "Podpredseda"
CLEN_OVEROVATEL = "Overovatel"
CLEN_PREDSEDA = "Predseda"
CLEN_VEDUCI = "Veduci"
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

## Hlasoval
HLASOVAL_HLAS = "hlas"
HLASOVAL_KLUB = "klub"
HLASOVAL_ZA = "Za"
HLASOVAL_PROTI = "Proti"
HLASOVAL_ZDRZAL = "Zdrzal sa"
HLASOVAL_NEPRITOMNY = "Nepritomny"
HLASOVAL_NEHLASOVAL = "Nehlasoval"
HLASOVAL_NEPLATNY = "Neplatny"
HLASOVAL_NEPLATNY2 = "Neplatny2"
HLASOVAL_HLAS_DICT = {
    "[Z]": HLASOVAL_ZA,
    "[P]": HLASOVAL_PROTI,
    "[?]": HLASOVAL_ZDRZAL,
    "[N]": HLASOVAL_NEHLASOVAL,
    "[0]": HLASOVAL_NEPRITOMNY,
    "[-]": HLASOVAL_NEPLATNY,
    "[X]": HLASOVAL_NEPLATNY2
}

## Navrhnuty
NAVRHNUTY_LEHOTA = "lehota"
NAVRHNUTY_TYP = "typ"
NAVRHNUTY_GESTORSKY = "Gestorsky"
NAVRHNUTY_DOPLNUJUCI = "Doplnujuci"

## Navrhol
NAVRHOL_NAVRHOVATEL = "navrhovatel"
NAVRHOL_VLADA = "Vlada"
NAVRHOL_POSLANCI = "Poslanci"
NAVRHOL_HLAVNY = "Hlavny"
NAVRHOL_DALSI = "Dalsi"
