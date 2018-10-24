from requests import get
from requests.exceptions import RequestException
import logging
from time import sleep
from bs4 import BeautifulSoup

import storage
import constants as const
import yaml
import utils

class Scraper:
    def __init__(self, db, conf, collection=None):
        self.db = db
        self.conf = conf
        if collection is None:
            collection = utils.get_collection(self, self.conf, const.CONF_MONGO_RAW, self.db)
        self.collection = collection
        self.log = logging.getLogger(str(self.__class__).split("'")[1])
        self.base_url = None
    
    def get(self, url):
        try:
            html = get(url).text
            self.log.debug("Content of url %r received.", url)
        except RequestException as e:
            self.log.error(e)
        sleep(self.conf[const.CONF_SCRAPE][const.CONF_SCRAPE_DELAY])
        return html

    def get_soup(self, url):
        html = self.get(url)
        return BeautifulSoup(html, features="lxml")

    def store_raw_html(self, url=None, entry_id=None, replace=False):
        if url is None and entry_id is None:
            self.log.error("Specify either url or entry_id for store_raw_html!")
            return
        if url is None:
            url = self.base_url.format(entry_id)
        if not replace:
            if self.collection.exists({const.MONGO_URL: url}):
                self.log.debug("url %r already in the database -- not replacing", url)
                return
        html = self.get(url)
        data = {const.MONGO_URL: url, const.MONGO_HTML: html}
        if entry_id is not None:
            data[const.MONGO_ID] = entry_id
        self.collection.update(data, const.MONGO_URL)

    def store_all(self, replace=False, **kwargs):
        gen = self.create_id_generator(**kwargs)
        n_entries = len(gen)
        self.log.info("Starting to scrape %d ids!", n_entries)
        count = 0
        for i in gen:
            self.store_raw_html(entry_id=i, replace=replace)
            count += 1
            self.log.debug("Scraping total progress: %d / %d",
                count, n_entries)
        self.log.info("Scraping finished!")

    def get_start_end_id(self):
        return 0, 0

    def create_id_generator(self, start_id=None, end_id=None):
        if start_id is None or end_id is None:
            default_start_id, default_end_id = self.get_start_end_id()
            if start_id is None:
                start_id = default_start_id
                self.log.debug("start_id set to default value: %d", start_id)
            if end_id is None:
                end_id = default_end_id
                self.log.debug("end_id set to default value: %d", end_id)
        return range(start_id, end_id + 1)



class Hlasovanie(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_HLASOVANIA

    def get_start_end_id(self):
        soup = self.get_soup(const.URL_NRSR_SCHODZE)
        url = soup.find(
            "div", id="_sectionLayoutContainer__panelContent"
            ).find("ul")("a")[-1].attrs["href"]
        url = const.URL_NRSR + url
        soup = self.get_soup(url)
        first = int(soup.find(
            "table", attrs={"class": "tab_zoznam"}
            ).find("a")["href"].split("=")[-1])
        soup = self.get_soup(const.URL_NRSR + "default.aspx?SectionId=108")
        hrefs = soup("a", attrs={
            "title": "Zobraziť detail hlasovania podľa klubov"})
        for s in hrefs:
            if "Hlasovanie" in s.text:
                break
        last = int(s["href"].split("=")[-1])
        return [first, last]


class Zakon(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_ZAKONY
    
    def get_start_end_id(self):
            first = 1
            soup = self.get_soup(const.URL_ZOZNAM_ZAKONOV)
            last = int(soup.find(
                "tr", attrs={"class": "tab_zoznam_nonalt"})("td")[1].text.strip())
            return [first, last]


class Poslanec(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_POSLANCI

    def get_start_end_id(self):
            return [1, const.SCRAPE_MAX_ID_POSLANEC]

class LegislativnaIniciativa(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_ZOZNAM_PREDLOZENYCH

    def create_id_generator(self):
        collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        poslanci_id = collection.get_all_attribute(const.MONGO_ID)
        return poslanci_id

class HlasovanieTlace(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_HLASOVANIA_CPT

    def create_id_generator(self):
        collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        zakony_id = collection.get_all_attribute(const.MONGO_ID)
        return zakony_id

class Zmena(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_ZMENA
    
    def create_id_generator(self):
        collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        return [
            int(zmena_id) 
            for zmeny in collection.get_all_attribute(const.ZAKON_ZMENY) 
            for zmena_id in zmeny
        ]