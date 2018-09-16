import scrape
import process
import storage
import constants as const
import yaml

def main_routine():
    with open("config.yaml", "r") as f:
        conf = yaml.load(f)
    db = storage.MongoDatabase(conf=conf[const.CONF_MONGO])
    hl_scraper = scrape.Hlasovanie(db, conf)
    hl_scraper.store_all()
    hl_process = process.Hlasovanie(db, conf)
    hl_process.process_all()


if __name__ == "__main__":
    main_routine()