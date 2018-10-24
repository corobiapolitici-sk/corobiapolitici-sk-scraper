import yaml
import logging

import scrape
import html_parser
import storage
import processing
import constants as const
from utils import set_up_logging
from time import time

def main_routine():
    t = time()
    with open("config.yaml", "r") as f:
        conf = yaml.load(f)
    set_up_logging(conf[const.CONF_LOGGING])
    logger = logging.getLogger("Main")

    db = storage.MongoDatabase(conf=conf[const.CONF_MONGO])

    scrape.Hlasovanie(db, conf).store_all()
    html_parser.Hlasovanie(db, conf).parse_all()
    scrape.Poslanec(db, conf).store_all()
    html_parser.Poslanec(db, conf).parse_all()
    scrape.Zakon(db, conf).store_all()
    html_parser.Zakon(db, conf).parse_all()
    scrape.LegislativnaIniciativa(db, conf).store_all()
    html_parser.LegislativnaIniciativa(db, conf).parse_all()
    scrape.HlasovanieTlace(db, conf).store_all()
    html_parser.HlasovanieTlace(db, conf).parse_all()
    scrape.Zmena(db, conf).store_all()
    html_parser.Zmena(db, conf).parse_all()

    logger.info("Total elapsed time after scrape + parse: %f", time() - t)

    processing.NodesHlasovanie(db, conf).process_and_store_all()
    processing.NodesPoslanec(db, conf).process_and_store_all()
    processing.NodesKlub(db, conf).process_and_store_all()
    processing.NodesVybor(db, conf).process_and_store_all()
    processing.NodesDelegacia(db, conf).process_and_store_all()
    processing.NodesZakon(db, conf).process_and_store_all()
    processing.NodesSpektrum(db, conf).process_and_store_all()
    processing.NodesZmena(db, conf).process_and_store_all()

    logger.info("Total elapsed time after nodes insert: %f", time() - t)

    processing.EdgesPoslanecKlubClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecKlubBolClenom(db, conf).process_and_store_all()
    processing.EdgesPoslanecVyborClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecDelegaciaClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecHlasovanieHlasoval(db, conf).process_and_store_all()
    processing.EdgesVyborZakonNavrhnuty(db, conf).process_and_store_all()
    processing.EdgesVyborZakonGestorsky(db, conf).process_and_store_all()
    processing.EdgesPoslanecZakonNavrhol(db, conf).process_and_store_all()
    processing.EdgesKlubSpektrumClen(db, conf).process_and_store_all()
    processing.EdgesSpektrumZakonNavrhol(db, conf).process_and_store_all()
    processing.EdgesHlasovanieZakonHlasovaloO(db, conf).process_and_store_all()
    processing.EdgesPoslanecZmenaNavrhol(db, conf).process_and_store_all()
    processing.EdgesPoslanecZmenaPodpisal(db, conf).process_and_store_all()
    processing.EdgesZmenaZakonNavrhnuta(db, conf).process_and_store_all()
    processing.EdgesHlasovanieZmenaHlasovaloO(db, conf).process_and_store_all()

    logger.info("Total elapsed time after edges insert: %f", time() - t)

if __name__ == "__main__":
    main_routine()