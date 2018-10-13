import yaml
import logging

import scrape
import html_parser
import storage
import processing
import constants as const
from utils import set_up_logging

def main_routine():
    with open("config.yaml", "r") as f:
        conf = yaml.load(f)
    set_up_logging(conf[const.CONF_LOGGING])

    db = storage.MongoDatabase(conf=conf[const.CONF_MONGO])
    scrape.Hlasovanie(db, conf).store_all()
    html_parser.Hlasovanie(db, conf).parse_all()
    scrape.Poslanec(db, conf).store_all()
    html_parser.Poslanec(db, conf).parse_all()
    scrape.Zakon(db, conf).store_all()
    html_parser.Zakon(db, conf).parse_all()
    processing.NodesHlasovanie(db, conf).process_and_store_all()
    processing.NodesPoslanec(db, conf).process_and_store_all()
    processing.NodesKlub(db, conf).process_and_store_all()
    processing.NodesVybor(db, conf).process_and_store_all()
    processing.NodesDelegacia(db, conf).process_and_store_all()
    processing.NodesZakon(db, conf).process_and_store_all()
    processing.EdgesPoslanecKlubClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecVyborClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecDelegaciaClen(db, conf).process_and_store_all()
    processing.EdgesPoslanecHlasovanieHlasoval(db, conf).process_and_store_all()
    processing.EdgesVyborZakonNavrhnuty(db, conf).process_and_store_all()
    processing.EdgesVyborZakonGestorsky(db, conf).process_and_store_all()


if __name__ == "__main__":
    main_routine()