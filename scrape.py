from requests import get
from requests.exceptions import RequestException
import logging
from time import sleep
from bs4 import BeautifulSoup
import robobrowser
import robobrowser.forms.fields as rbfields

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

class Rozprava(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_ROZPRAVA
    
    def create_id_generator(self):
        collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        poslanci_id = collection.get_all_attribute(const.MONGO_ID)
        return poslanci_id

    def store_raw_html(self, entry_id, replace=False):
        if replace:
            self.collection.collection.delete_many({const.MONGO_ID: entry_id})
            stored_ids = []
            entry_pages = []
        else:
            ids_collection = storage.MongoCollection(self.db, "edges_poslanec_rozprava_vystupil")
            stored_ids = [
                entry[const.NEO4J_ENDING_ID] for entry in ids_collection.get_all(
                    {const.NEO4J_BEGINNING_ID: entry_id}, projections={const.NEO4J_ENDING_ID})
            ]

            entry_pages = [entry[const.MONGO_PAGE] for entry in self.collection.get_all(
                {const.MONGO_ID: entry_id}, projections={const.MONGO_PAGE}
            )]
            if entry_pages:
                min_page = min(entry_pages)

        url = self.base_url.format(entry_id)
        br = robobrowser.RoboBrowser(parser='html.parser', history=False)
        br.open(url)

        last_page = False
        page = 1
        while True:
            if not br.parsed.select(const.SCRAPE_ROZPRAVA_TABLE):
                break
            rozpravy_ids = self.get_page_rozpravy_ids(br.parsed)
            if rozpravy_ids[0] in stored_ids:
               break
            if rozpravy_ids[-1] in stored_ids:
                last_page = True
            if entry_pages:
                store_page = min_page - page
            else:
                store_page = page
            data = {
                const.MONGO_URL: url,
                const.MONGO_HTML: str(br.parsed),
                const.MONGO_PAGE: store_page,
                const.MONGO_ID: entry_id}
            self.collection.update(data, [const.MONGO_URL, const.MONGO_PAGE])
            sleep(self.conf[const.CONF_SCRAPE][const.CONF_SCRAPE_DELAY])
            if last_page:
                break
            page += 1
            form = br.get_form(id="_f")
            self.js_prepare_form(
                form, 
                const.SCRAPE_ROZPRAVA_FORM, 
                f"Page${page}")
            br.submit_form(form)

    @staticmethod
    def js_prepare_form(form, event_target, event_argument):
        """Emulate js __doPostBack function used by nrsr.sk"""
        new_field = rbfields.Input(
            const.SCRAPE_ROZPRAVA_EVENT_ARGUMENT.format(event_argument))
        form.add_field(new_field)
        new_field = rbfields.Input(
            const.SCRAPE_ROZPRAVA_EVENT_TARGET.format(event_target))
        form.add_field(new_field)
        form.fields.pop(const.SCRAPE_ROZPRAVA_SEARCH_BUTTON)

    @staticmethod
    def get_page_rozpravy_ids(soup):
        return [
            int(span.find("a")["href"].split("=")[-1]) 
            for span in soup("span", attrs={"class": "daily_info_speech_header_right"})
            if span.find("a")]
