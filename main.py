# Load external modules.
import logging
import pymongo
import time
import yaml

# Load internal modules.
import constants as const
import html_parser
import processing
import scrape
import storage

if __name__ != '__main__':
    exit(-1)

# Store the time at the beginning of the routine.
begin_time = time.time()

# Load the configuration.
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Set up the logging.
logging_config = config['logging']
logging.basicConfig(handlers=[logging.FileHandler(logging_config['filename'], 'w', 'utf-8')], level=logging_config['level'])
logger = logging.getLogger('Main')

# Set up the mongo database client connection.
mongo_config = config['mongo']
mongo_client = pymongo.MongoClient(**mongo_config['client'])
mongo_database = mongo_client[mongo_config['database']['name']]
logging.getLogger('Mongo').info(f'MongoDatabase initialized with database "{mongo_config["database"]["name"]}".')

scrape.Hlasovanie(mongo_database, config).store_all()
html_parser.Hlasovanie(mongo_database, config).parse_all()
logger.info(f'"Hlasovanie" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.Poslanec(mongo_database, config).store_all()
html_parser.Poslanec(mongo_database, config).parse_all()
logger.info(f'"Poslanec" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.Zakon(mongo_database, config).store_all()
html_parser.Zakon(mongo_database, config).parse_all()
logger.info(f'"Zakon" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.LegislativnaIniciativa(mongo_database, config).store_all()
html_parser.LegislativnaIniciativa(mongo_database, config).parse_all()
logger.info(f'"Legislativna Iniciativa" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.HlasovanieTlace(mongo_database, config).store_all()
html_parser.HlasovanieTlace(mongo_database, config).parse_all()
logger.info(f'"Hlasovanie Tlace" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.Zmena(mongo_database, config).store_all()
html_parser.Zmena(mongo_database, config).parse_all()
logger.info(f'"Zmena" elapsed time after scrape + parse: {time.time() - begin_time}')

scrape.Rozprava(mongo_database, config).store_all()
html_parser.Rozprava(mongo_database, config).parse_all()
logger.info(f'"Rozprava" elapsed time after scrape + parse: {time.time() - begin_time}')

processing.NodesHlasovanie(mongo_database, config).process_and_store_all()
processing.NodesPoslanec(mongo_database, config).process_and_store_all()
processing.NodesKlub(mongo_database, config).process_and_store_all()
processing.NodesVybor(mongo_database, config).process_and_store_all()
processing.NodesDelegacia(mongo_database, config).process_and_store_all()
processing.NodesZakon(mongo_database, config).process_and_store_all()
processing.NodesSpektrum(mongo_database, config).process_and_store_all()
processing.NodesZmena(mongo_database, config).process_and_store_all()
processing.NodesRozprava(mongo_database, config).process_and_store_all()

logger.info(f'Total elapsed time after nodes insert: {time.time() - begin_time}')

processing.EdgesPoslanecKlubClen(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecKlubBolClenom(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecVyborClen(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecDelegaciaClen(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecHlasovanieHlasoval(mongo_database, config).process_and_store_all()
processing.EdgesVyborZakonNavrhnuty(mongo_database, config).process_and_store_all()
processing.EdgesVyborZakonGestorsky(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecZakonNavrhol(mongo_database, config).process_and_store_all()
processing.EdgesKlubSpektrumClen(mongo_database, config).process_and_store_all()
processing.EdgesSpektrumZakonNavrhol(mongo_database, config).process_and_store_all()
processing.EdgesHlasovanieZakonHlasovaloO(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecZmenaNavrhol(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecZmenaPodpisal(mongo_database, config).process_and_store_all()
processing.EdgesZmenaZakonNavrhnuta(mongo_database, config).process_and_store_all()
processing.EdgesHlasovanieZmenaHlasovaloO(mongo_database, config).process_and_store_all()
processing.EdgesPoslanecRozpravaVystupil(mongo_database, config).process_and_store_all()
processing.EdgesRozpravaZakonTykalaSa(mongo_database, config).process_and_store_all()

logger.info(f'Total elapsed time after edges insert: {time.time() - begin_time}')

mongo_client.close()
