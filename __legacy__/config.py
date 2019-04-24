DELAY = 0.2
FILE_HLASY = "data/hlasy.h5"
FILE_KLUBY = "data/kluby.h5"
FILE_HLASY_METADATA = "data/hlasy_metadata.h5"
FILE_DEMAGOG = "data/demagog.h5"
FILE_ROZPRAVY = "data/rozpravy.pkl"
FILE_ZAKONY = "data/zakony.pkl"
HDF_KEY = "data"

HLASY_STATS_MEANING = {"[Z]": "Za", "[P]": "Proti", "[N]": "Nehlasoval/a",
                       "[0]": "Neprítomný/á", "[?]": "Zdržal/a sa"}
HLASY_STATS_ORDER = ["[Z]", "[P]", "[?]", "[0]", "[N]"]
HLASY_STATS_VYSLEDOK = ["prešiel", "neprešiel"]
FILE_STATS_HLASY_PIE = "data/hlasy_pie.h5"

DEMAGOG_LABELS = ["Pravda", "Nepravda", "Zavádzanie", "Neoveriteľné"]
FILE_DEMAGOG_PIE = "data/demagog_pie.h5"

ROZPRAVY_COLUMNS = ["name", "type", "start_time", "end_time", "text"]
FILE_ROZPRAVY_APP = "data/rozpravy_app.h5"
ROZPRAVY_APP_LABELS = ["trvanie (hod.)", "počet slov"]
FILE_ROZPRAVY_DURATION = "data/rozpravy_duration.pkl"

NEO4J_HLASY_NODES = "data/neo4j_hlasy_nodes.csv"
NEO4J_HLASY_ZAKONY_EDGES = "data/neo4j_hlasy_zakony_edges.csv"
NEO4J_ZMENY_NODES = "data/neo4j_zmeny_nodes.csv"
NEO4J_ZAKONY_NODES = "data/neo4j_zakony_nodes.csv"
NEO4J_POSLANCI_KLUBY_EDGES = "data/neo4j_poslanci_kluby_edges.csv"
NEO4J_ZMENY_PODPIS_EDGES = "data/neo4j_zmeny_podpis_edges.csv"
NEO4J_ZMENY_HLASOVANIA_EDGES = "data/neo4j_zmeny_hlasovania_edges.csv"
NEO4J_ZMENY_PREDKLADATEL_EDGES = "data/neo4j_zmeny_predkladatel_edges.csv"
NEO4J_ZAKON_POSLEDNE_EDGES = "data/neo4j_zakon_posledne_edges.csv"
NEO4J_ZAKON_NAVRHOVATEL_EDGES = "data/neo4j_zakon_navrhovatel_edges.csv"
NEO4J_POSLANEC_HLASOVANIE_EDGES = "data/neo4j_poslanec_hlasovanie_edges.csv"
NEO4J_ZAKONY_ZMENY_EDGES = "data/neo4j_zakony_zmeny_edges.csv"
NEO4J_KLUBY_SPEKTRUM_EDGES = "data/neo4j_kluby_spektrum_edges.csv"
NEO4J_ROZPRAVY_NODES_EDGES = "data/neo4j_rozpravy_nodes_edges.csv"
