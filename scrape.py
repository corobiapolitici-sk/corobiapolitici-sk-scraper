# Load external modules.
import bs4
import requests
import robobrowser
import robobrowser.forms.fields as rbfields
from time import sleep
import yaml

# Load internal modules.
import constants as const
import storage
import utils

# Define url constants.
base_url = 'https://www.nrsr.sk/web/'
urls = {
    'hlasovania': base_url + 'Default.aspx?sid=schodze/hlasovanie/hlasklub&ID={}',
    'hlasovanie_vyhladavanie': base_url + 'Default.aspx?sid=schodze/hlasovanie/vyhladavanie_vysledok',
    'hlasovania_schodze': base_url + 'Default.aspx?sid=schodze/hlasovanie/schodze',
    'zakony': base_url + 'Default.aspx?sid=zakony/zakon&ZakZborID=13&CisObdobia=7&CPT={}',
    'poslanci': base_url + 'Default.aspx?sid=poslanci/poslanec&CisObdobia=7&PoslanecID={}',
    'zoznam_zakonov': base_url + 'Default.aspx?sid=zakony/prehlad/predlozene',
    'zoznam_predlozenych': base_url + 'Default.aspx?sid=zakony/sslp&PredkladatelID=0&CisObdobia=7&PredkladatelPoslanecId={}',
    'hlasovania_cpt': base_url + 'Default.aspx?sid=schodze/hlasovanie/vyhladavanie_vysledok&CPT={}',
    'zmena': base_url + 'Default.aspx?sid=schodze/nrepdn_detail&id={}',
    'rozprava': base_url + 'Default.aspx?sid=schodze/rozprava/vyhladavanie&CisObdobia=7&PoslanecID={}',
}

class Scraper(utils.Logged):
    def __init__(self, db, conf, base_url):
        super().__init__()
        name = str(self.__class__).split("'")[1].split('.')[-1].lower()
        self.db = db
        self.conf = conf
        self.collection = storage.MongoCollection(db, 'raw_' + name)
        self.base_url = base_url

    def get_html(self, url):
        try:
            html = requests.get(url).text
            self.log.debug(f'Content of url {url} received.')
        except requests.exceptions.RequestException as e:
            self.log.error(e)
        sleep(self.conf['scrape']['delay'])
        return html

    def get_soup(self, url):
        return bs4.BeautifulSoup(self.get_html(url), features='lxml')

    def store_raw_html(self, id_instance):
        url = self.base_url.format(id_instance)
        if self.collection.exists({ 'url': url }):
            self.log.debug(f'url {url} already in the database -- not replacing')
            return

        self.collection.update({
            'url': url,
            'html': self.get_html(url),
            'id': id_instance
        }, ['url'])

    def store_all(self):
        id_generator = self.create_id_generator()
        id_generator_length = len(id_generator)
        self.log.info(f'Starting to scrape {id_generator_length} ids!')

        id_count = 0
        for id_instance in id_generator:
            self.store_raw_html(id_instance)
            id_count += 1
            self.log.debug(f'Scraping total progress: {id_count} / {id_generator_length}')

        self.log.info('Scraping finished!')

    def get_start_end_id(self):
        return 0, 0

    def create_id_generator(self):
        start_id, end_id = self.get_start_end_id()

        self.log.debug(f'start_id set to default value: {start_id}')
        self.log.debug(f'end_id set to default value: {end_id}')

        return range(start_id, end_id + 1)

class Hlasovanie(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['hlasovania'])

    def get_start_end_id(self):
        soup = self.get_soup(urls['hlasovania_schodze'])
        url = base_url + soup.find('div', id='_sectionLayoutContainer__panelContent').find('ul')('a')[-1].attrs['href']

        soup = self.get_soup(url)
        first = int(soup.find('table', attrs={'class': 'tab_zoznam'}).find('a')['href'].split('=')[-1])

        soup = self.get_soup(urls['hlasovanie_vyhladavanie'])
        for element in soup('a', attrs={'title': 'Zobraziť detail hlasovania podľa klubov'}):
            if 'Hlasovanie' in element.text:
                break
        last = int(element['href'].split('=')[-1])

        return first, last

class Poslanec(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['poslanci'])

    def get_start_end_id(self):
        return 1, 1000

class Zakon(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['zakony'])

    def get_start_end_id(self):
        soup = self.get_soup(urls['zoznam_zakonov'])
        return 1, int(soup.find('tr', attrs={'class': 'tab_zoznam_nonalt'})('td')[1].text.strip())

class LegislativnaIniciativa(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['zoznam_predlozenych'])

    def create_id_generator(self):
        collection = storage.MongoCollection(self.db, 'parsed_poslanec')
        return collection.get_all_attribute('id')

class HlasovanieTlace(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['hlasovania_cpt'])

    def create_id_generator(self):
        collection = storage.MongoCollection(self.db, 'parsed_zakon')
        return collection.get_all_attribute('id')

class Zmena(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['zmena'])

    def create_id_generator(self):
        collection = storage.MongoCollection(self.db, 'parsed_zakon')
        return [
            int(zmena_id)
                for zmeny in collection.get_all_attribute(const.ZAKON_ZMENY)
                    for zmena_id in zmeny
        ]

class Rozprava(Scraper):
    def __init__(self, db, conf):
        super().__init__(db, conf, urls['rozprava'])

    def create_id_generator(self):
        collection = storage.MongoCollection(self.db, 'parsed_poslanec')
        return collection.get_all_attribute('id')

    def store_raw_html(self, entry_id):
        ids_collection = storage.MongoCollection(self.db, 'edges_poslanec_rozprava_vystupil')
        stored_ids = [
            entry[const.NEO4J_ENDING_ID]
                for entry in ids_collection.get_all({const.NEO4J_BEGINNING_ID: entry_id}, projections={const.NEO4J_ENDING_ID})
        ]

        entry_pages = [
            entry['page']
                for entry in self.collection.get_all({'id': entry_id}, projections={'page'})
        ]
        if entry_pages:
            min_page = min(entry_pages)

        url = self.base_url.format(entry_id)
        br = robobrowser.RoboBrowser(parser='html.parser', history=False)
        br.open(url)

        last_page = False
        page = 1
        while True:
            if not br.parsed.select('#_sectionLayoutContainer_ctl01__resultGrid'):
                break
            rozpravy_ids = [
                int(span.find('a')['href'].split('=')[-1])
                    for span in br.parsed('span', attrs={'class': 'daily_info_speech_header_right'})
                        if span.find('a')
            ]
            if rozpravy_ids[0] in stored_ids:
               break
            if rozpravy_ids[-1] in stored_ids:
                last_page = True
            if entry_pages:
                store_page = min_page - page
            else:
                store_page = page
            data = {
                'url': url,
                'html': str(br.parsed),
                'page': store_page,
                'id': entry_id
            }
            self.collection.update(data, ['url', 'page'])
            sleep(self.conf['scrape']['delay'])
            if last_page:
                break
            page += 1
            form = br.get_form(id='_f')
            form.add_field(rbfields.Input(f'<input name="__EVENTARGUMENT" value="Page${page}" />'))
            form.add_field(rbfields.Input('<input name="__EVENTTARGET" value="_sectionLayoutContainer$ctl01$_resultGrid" />'))
            form.fields.pop('_sectionLayoutContainer$ctl01$_searchButton')
            br.submit_form(form)
