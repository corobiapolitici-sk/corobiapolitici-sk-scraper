# Load external modules.
import logging
import time
import yaml

# Load internal modules.
import constants as const
import html_parser
import processing
import scrape
import storage

def main_routine():
    # Store the time at the beginning of the routine.
    begin_time = time.time()

    # Load the configuration.
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Set up the logging.
    logging_config = config['logging']
    logging.basicConfig(handlers=[logging.FileHandler(logging_config['filename'], 'w', 'utf-8')], level=logging_config['level'])
    logger = logging.getLogger('Main')

    db = storage.MongoDatabase(conf=config['mongo'])
    """
    scrape.Hlasovanie(db, config).store_all()
    html_parser.Hlasovanie(db, config).parse_all()
    logger.info(f'"Hlasovanie" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.Poslanec(db, config).store_all()
    html_parser.Poslanec(db, config).parse_all()
    logger.info(f'"Poslanec" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.Zakon(db, config).store_all()
    html_parser.Zakon(db, config).parse_all()
    logger.info(f'"Zakon" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.LegislativnaIniciativa(db, config).store_all()
    html_parser.LegislativnaIniciativa(db, config).parse_all()
    logger.info(f'"Legislativna Iniciativa" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.HlasovanieTlace(db, config).store_all()
    html_parser.HlasovanieTlace(db, config).parse_all()
    logger.info(f'"Hlasovanie Tlace" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.Zmena(db, config).store_all()
    html_parser.Zmena(db, config).parse_all()
    logger.info(f'"Zmena" elapsed time after scrape + parse: {time.time() - begin_time}')

    scrape.Rozprava(db, config).store_all()
    html_parser.Rozprava(db, config).parse_all()
    logger.info(f'"Rozprava" elapsed time after scrape + parse: {time.time() - begin_time}')
    """
    processing.NodesHlasovanie(db, config).process_and_store_all()
    processing.NodesPoslanec(db, config).process_and_store_all()
    processing.NodesKlub(db, config).process_and_store_all()
    processing.NodesVybor(db, config).process_and_store_all()
    processing.NodesDelegacia(db, config).process_and_store_all()
    processing.NodesZakon(db, config).process_and_store_all()
    processing.NodesSpektrum(db, config).process_and_store_all()
    processing.NodesZmena(db, config).process_and_store_all()
    """
    processing.NodesRozprava(db, config).process_and_store_all()
    """

    logger.info(f'Total elapsed time after nodes insert: {time.time() - begin_time}')

    processing.EdgesPoslanecKlubClen(db, config).process_and_store_all()
    processing.EdgesPoslanecKlubBolClenom(db, config).process_and_store_all()
    processing.EdgesPoslanecVyborClen(db, config).process_and_store_all()
    processing.EdgesPoslanecDelegaciaClen(db, config).process_and_store_all()
    processing.EdgesPoslanecHlasovanieHlasoval(db, config).process_and_store_all()
    processing.EdgesVyborZakonNavrhnuty(db, config).process_and_store_all()
    processing.EdgesVyborZakonGestorsky(db, config).process_and_store_all()
    processing.EdgesPoslanecZakonNavrhol(db, config).process_and_store_all()
    processing.EdgesKlubSpektrumClen(db, config).process_and_store_all()
    processing.EdgesSpektrumZakonNavrhol(db, config).process_and_store_all()
    processing.EdgesHlasovanieZakonHlasovaloO(db, config).process_and_store_all()
    processing.EdgesPoslanecZmenaNavrhol(db, config).process_and_store_all()
    processing.EdgesPoslanecZmenaPodpisal(db, config).process_and_store_all()
    processing.EdgesZmenaZakonNavrhnuta(db, config).process_and_store_all()
    processing.EdgesHlasovanieZmenaHlasovaloO(db, config).process_and_store_all()
    """
    processing.EdgesPoslanecRozpravaVystupil(db, config).process_and_store_all()
    processing.EdgesRozpravaZakonTykalaSa(db, config).process_and_store_all()
    """

    logger.info(f'Total elapsed time after edges insert: {time.time() - begin_time}')

if __name__ == '__main__':
    main_routine()
