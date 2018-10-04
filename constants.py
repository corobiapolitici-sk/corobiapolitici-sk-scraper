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

# Config
CONF_SCRAPE = "scrape"
CONF_SCRAPE_DELAY = "delay"
CONF_MONGO = "mongo"
CONF_MONGO_CLIENT = "client"
CONF_MONGO_DATABASE = "database"
CONF_MONGO_DATABASE_NAME = "name"
CONF_MONGO_COLLECTION = "collections"
CONF_MONGO_HLASOVANIE = "hlasovanie"
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

NEO4J_OBJECT_TYPE = "object_type"
NEO4J_NODE_NAME = "node_name"
NEO4J_BEGINNING_ID = "beginning_id"
NEO4J_ENDING_ID = "ending_id"
NEO4J_BEGINNING_NAME = "beginning_name"
NEO4J_ENDING_NAME = "ending_name"
NEO4J_EDGE_NAME = "edge_name"
NEO4J_OBJECT_NODE = "node"
NEO4J_OBJECT_EDGE = "edge"

# Node / edge names

NODE_NAME_KLUB = "Klub"
NODE_NAME_POSLANEC = "Poslanec"
NODE_NAME_HLASOVANIE = "Hlasovanie"

EDGE_NAME_CLEN = "Člen"
EDGE_NAME_HLASOVAL = "Hlasoval"

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
POSLANEC_NARODENY = "narodený(á)"

KLUB_NAZOV = "názov"
KLUB_POCET = "početPoslancov"

CLEN_NAPOSLEDY = "časNaposledy"

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