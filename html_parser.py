# Load external modules.
import bs4
from datetime import datetime, timedelta
import logging

# Load internal modules.
import constants as const
import storage
import utils

class HTMLParser(utils.Logged):
    def __init__(self, db, conf):
        super().__init__()
        name = str(self.__class__).split("'")[1].split('.')[-1].lower()
        self.source_collection = storage.MongoCollection(db, 'raw_' + name)
        self.target_collection = storage.MongoCollection(db, 'parsed_' + name)
        self.unique_ids = ['id']

    def extract_structure(self, entry):
        return entry

    def parse(self, query):
        entry = self.source_collection.get(query)
        if entry is None:
            self.log.debug(f'No object satisfying query {str(query)} in collection {self.target_collection.collection.name}')
            return
        if const.PARSE_ERROR_NOT_FOUND in entry['html']:
            self.log.debug(f'Object id {str(query)} corresponds to an empty page')
            return

        parsed_entry = self.extract_structure(entry)
        if parsed_entry is None:
            self.log.debug(f'Entry {str(query)} has invalid structure.')
            return

        self.target_collection.update(parsed_entry, self.unique_ids)

        self.log.debug(f'Entry {str(query)} parsed!')

    def parse_all(self):
        self.log.info('Parsing started.')

        # For each item in the source collection.
        for index, entry in enumerate(self.source_collection.iterate_all()):
            # Find an entry in the target collection corresponding to the current entry using the type's unique ids.
            query = {unique_id: entry[unique_id] for unique_id in self.unique_ids}
            target_entry = self.target_collection.get(query, projection=['insertTime'])

            # If a target entry is found, verify that the source entry's insert time is lesser than that of the target entry.
            if target_entry is not None:
                source_entry = self.source_collection.get(query, projection=['insertTime'])
                if source_entry['insertTime'] < target_entry['insertTime']:
                    self.log.debug(f'Entry {str(query)} already parsed.')
                    continue

            # Parse the entry.
            self.parse(query)

            self.log.debug(f'Overall progress: {index + 1} items parsed!')

        self.log.info('Parsing finished!')

    def strip(self, s):
        if s is None:
            return ''
        else:
            return s.text.strip()

class Hlasovanie(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        try:
            first_box, second_box = soup('div', attrs={'class': 'voting_stats_summary_full'})
        except:
            return

        for item in first_box('div')[0].find('a')['href'].split('&')[1:-1]:
            tokens = item.split('=')
            entry[const.HLASOVANIE_URL_DICT[tokens[0]]] = int(tokens[1])

        time = first_box('div')[1].find('span').text.strip()
        entry[const.HLASOVANIE_CAS] = datetime.strptime(time, '%d. %m. %Y %H:%M')
        entry[const.HLASOVANIE_CISLO] = int(first_box('div')[2].find('span').text.strip())
        entry[const.HLASOVANIE_NAZOV] = first_box('div')[3].find('span').text.strip().replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
        entry[const.HLASOVANIE_VYSLEDOK] = first_box('div')[4].find('span').text.strip()

        for result in second_box('div')[:-1]:
            key = result.find('strong').text.strip()
            item = int(result.find('span').text.strip())
            entry[const.HLASOVANIE_SUHRN_DICT[key]] = item

        entry[const.HLASOVANIE_INDIVIDUALNE] = {}
        table = soup.find('table', attrs={'class': 'hpo_result_table'})
        for tr in table('tr'):
            for td in tr('td'):
                if ('class' in td.attrs and td['class'][0] == 'hpo_result_block_title'):
                    club = td.text.strip()
                elif td.text != '':
                    poslanec = {}
                    poslanec[const.HLASOVANIE_KLUB] = club
                    gen = td.children
                    poslanec[const.HLASOVANIE_HLAS] = next(gen).strip()
                    info = next(gen)
                    for item in info['href'].split('&')[1:]:
                        tokens = item.split('=')
                        poslanec[const.HLASOVANIE_POSLANEC_DICT[tokens[0]]] = int(tokens[1])
                    poslanec[const.HLASOVANIE_CELE_MENO] = info.text.strip()
                    poslanec_id = poslanec.pop('id')
                    entry[const.HLASOVANIE_INDIVIDUALNE][str(poslanec_id)] = poslanec

        return entry

class Poslanec(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        personal = soup.find('div', attrs={'class':'mp_personal_data'})
        for div in personal('div'):
            if div.find('strong') is not None:
                key = div.find('strong').text.strip().lower()
                entry[const.POSLANEC_INFO_DICT[key]] = div.find('span').text.strip()

        entry[const.POSLANEC_NARODENY] = datetime.strptime(entry[const.POSLANEC_NARODENY], '%d. %m. %Y')
        clenstvo = soup.find('span', attrs={'id': '_sectionLayoutContainer_ctl01_ctlClenstvoLabel'})
        entry[const.POSLANEC_CLENSTVO] = {}
        for li in clenstvo.parent.parent('li'):
            text = li.text
            tokens = text.split('(')
            if len(tokens) == 1:
                res = ''
            else:
                res = tokens[1].split(')')[0].strip().capitalize()
            entry[const.POSLANEC_CLENSTVO][tokens[0].strip()] = res
        entry[const.POSLANEC_FOTO] = soup.find('div', attrs={'class': 'mp_foto'}).find('img')['src']

        return entry

class Zakon(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        entry[const.ZAKON_POPIS] = self.strip(soup.find('h1'))
        main_soup = soup.find('div', attrs={'id': '_sectionLayoutContainer__panelContent'})
        missing_citanie1 = 'I. čítanie' not in [s.text.strip() for s in main_soup('h2')]
        for span in main_soup('span'):
            span_id = self.add_one_id(span['id'], missing_citanie1)
            if const.ZAKON_ID_DICT[span_id] is not None:
                entry[const.ZAKON_ID_DICT[span_id]] = self.strip(span)
        entry[const.ZAKON_VYSLEDOK] = entry[const.ZAKON_VYSLEDOK][1:-1]
        if const.ZAKON_CITANIE1_SCHODZA in entry:
            entry[const.ZAKON_CITANIE1_SCHODZA] = int(entry[const.ZAKON_CITANIE1_SCHODZA])
        for field in [const.ZAKON_DATUM_DORUCENIA, const.ZAKON_PREROKOVANIE_GESTORSKY]:
            if field in entry:
                entry[field] = datetime.strptime(entry[field].split(',')[0].strip(), '%d. %m. %Y')
        self.add_zmeny(soup, entry, missing_citanie1)
        return entry

    def add_one_id(self, span_id, add_one):
        if add_one:
            tokens = span_id.split('_ctl0')
            if len(tokens) == 3:
                num = int(tokens[2][0])
                if num >= 2:
                    num += 1
                    tokens[2] = str(num) + tokens[2][1:]
                span_id = '_ctl0'.join(tokens)
        return span_id

    def add_zmeny(self, soup, entry, add_one):
        if add_one:
            div_id = '_sectionLayoutContainer_ctl01_ctl04__PdnList__pdnListPanel'
        else:
            div_id = '_sectionLayoutContainer_ctl01_ctl05__PdnList__pdnListPanel'
        table = soup.find('div', attrs={'id': div_id})
        if table is not None:
            entry[const.ZAKON_ZMENY] = {}
            for tr in table.find('table')('tr'):
                zmena = {}
                tds = tr('td')
                zmena[const.ZAKON_ZMENY_CAS] = tds[0].text.strip()
                zmena[const.ZAKON_ZMENY_PREDKLADATEL] = tds[1].text.strip()
                zmena[const.ZAKON_ZMENY_URL] = tds[2].find('a')['href']
                zmena_id = zmena[const.ZAKON_ZMENY_URL].split('=')[-1]
                zmena[const.ZAKON_ZMENY_DOKUMENT] = tds[3].find('a')['href']
                if len(tds) == 5 and tds[4].text.strip() != '':
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_URL] = tds[4].find('a')['href']
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_ID] = int(zmena[const.ZAKON_ZMENY_HLASOVANIE_URL].split('=')[-1])
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_VYSLEDOK] = tds[4].text.strip()
                entry[const.ZAKON_ZMENY][zmena_id] = zmena

class LegislativnaIniciativa(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        entry[const.PREDLOZILZAKON_LIST] = {}
        table = soup.find('table', attrs={'class': 'tab_zoznam paginated sortable'})
        if table is None:
            return entry
        for row in table('tr')[1:]:
            zakon = {}
            cols = row('td')
            zakon[const.ZAKON_NAZOV] = cols[0].text.strip()
            zakon[const.ZAKON_STAV] = cols[2].text.strip()
            zakon[const.ZAKON_DATUM_DORUCENIA] = datetime.strptime(cols[3].text.strip(), '%d. %m. %Y')
            zakon[const.ZAKON_NAVRHOVATEL] = cols[4].text.strip()
            zakon[const.ZAKON_DRUH] = cols[5].text.strip()
            zakon_id = cols[1].text.strip()
            entry[const.PREDLOZILZAKON_LIST][zakon_id] = zakon
        return entry

class HlasovanieTlace(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        entry[const.HLASOVANIETLAC_LIST] = {}
        table = soup.find('table', attrs={'class': 'tab_zoznam'})
        if table is None:
            return entry
        for row in table('tr')[1:]:
            hlasovanie = {}
            cols = row('td')
            hlasovanie[const.HLASOVANIE_SCHODZA] = int(cols[0].text.strip())
            hlasovanie[const.HLASOVANIE_CAS] = self.parse_date(cols[1].text.strip())
            hlasovanie[const.HLASOVANIE_CISLO] = int(cols[2].text.strip())
            hlasovanie[const.HLASOVANIE_NAZOV] = cols[4].text.strip()
            hlasovanie_id = cols[5].find('a')['href'].split('=')[-1]
            if hlasovanie_id != '':
                entry[const.HLASOVANIETLAC_LIST][hlasovanie_id] = hlasovanie
        return entry

    def parse_date(self, date):
        tokens = date.split(' ')
        formatted = ' '.join(tokens[i].strip() for i in [0, -1])
        return datetime.strptime(formatted, '%d.%m.%Y %H:%M:%S')

class Zmena(HTMLParser):
    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        divs = [div for div in soup.find('div', attrs={'class': 'change_request_details'})('div') if div['class'] != ['clear']]
        for div in divs:
            title = const.ZMENA_DICT[div.find('strong').text.strip()]
            if title in [const.ZMENA_NAZOV, const.ZMENA_PREDKLADATEL]:
                entry[title] = div.find('span').text.strip()
            if title in [const.ZMENA_SCHODZA, const.ZMENA_OBDOBIE]:
                entry[title] = int(div.find('span').text.strip())
            if title == const.ZMENA_DATUM:
                text = div.find('span').text.strip()
                try:
                    entry[title] = datetime.strptime(text, '%d. %m. %Y')
                except:
                    entry[title] = datetime.strptime(text, '%d. %m. %Y %H:%M')
            if title in [const.ZMENA_DALSI, const.ZMENA_PODPISANI]:
                entry[title] = [name.text.strip() for name in div('li')]
            if title == const.ZMENA_HLASOVANIE:
                a = div.find('a')
                if a is not None:
                    entry[title] = int(a['href'].split('=')[-1])
            dokument = soup.find('a', attrs={'target': '_blank'})
            if dokument is not None:
                entry[const.ZMENA_DOKUMENT] = dokument['href']
        return entry

class Rozprava(HTMLParser):
    def __init__(self, db, conf):
        super().__init__(db, conf)
        self.unique_ids = ['id', 'page']

    def extract_structure(self, entry):
        soup = bs4.BeautifulSoup(entry.pop('html'), features='lxml')
        table = soup.find('table', attrs={'class': 'tab_zoznam'})
        if table is None:
            return
        entry[const.ROZPRAVA_VYSTUPENIA] = []
        for row in table('tr', attrs={'class': 'tab_zoznam_nalt'}):
            info = {}
            date = row.find('span', attrs={'class': 'daily_info_speech_header_left'}).text.strip()
            start_time, end_time = self.parse_date(date)
            info[const.ROZPRAVA_CAS_ZACIATOK] = start_time
            info[const.ROZPRAVA_CAS_KONIEC] = end_time

            schodza, tlac = row('span', attrs={'class': 'daily_info_speech_header_middle'})
            tokens = schodza.text.strip().split('-')
            info[const.ROZPRAVA_SCHODZA] = int(tokens[0].replace('.',' ').strip().split(' ')[0])
            info[const.ROZPRAVA_SCHODZA_DEN] = int(tokens[1].strip().split('.')[0])
            info[const.ROZPRAVA_SCHODZA_CAST_DNA] = tokens[2].strip()
            tlac = tlac.find('a')
            if tlac is not None:
                info[const.ROZPRAVA_TLAC] = int(tlac.text.strip())

            links, vystupenie = row('span', attrs={'class': 'daily_info_speech_header_right'})
            links = links('a')
            info[const.ROZPRAVA_ZAZNAM_VYSTUPENIA] = links[0]['href']
            info[const.ROZPRAVA_ZAZNAM_ROKOVANIA] = links[1]['href']
            info[const.ROZPRAVA_TYP_VYSTUPENIA] = vystupenie.find('em').text.strip()

            info[const.MONGO_ID] = int(info[const.ROZPRAVA_ZAZNAM_VYSTUPENIA].split('=')[-1])

            tokens = row('span', attrs={'class': ''})
            priezvisko, meno = tokens[0].text.split(',')
            info[const.ROZPRAVA_POSLANEC_PRIEZVISKO] = priezvisko.strip()
            info[const.ROZPRAVA_POSLANEC_MENO] = meno.strip()
            info[const.ROZPRAVA_POSLANEC_KLUB] = tokens[1].text.strip()[1:-1]
            info[const.ROZPRAVA_POSLANEC_TYP] = tokens[2].text.split('-')[-1].strip()
            info[const.ROZPRAVA_TEXT] = tokens[3].text.strip().replace('\r', ' ').replace('\n', ' ')
            entry[const.ROZPRAVA_VYSTUPENIA].append(info)
        return entry

    def parse_date(self, date):
        tokens = date.split('-')
        start_time = datetime.strptime(tokens[0].strip(), '%d. %m. %Y %H:%M:%S')
        end_time = datetime.combine(
            start_time.date(),
            datetime.strptime(tokens[1].strip(), '%H:%M:%S').time())
        if end_time < start_time:
            self.log.debug('start_time: %s, end_time: %s', str(start_time), str(end_time))
            if end_time - start_time > timedelta(hours=12): # midnight between start and end
                end_time += timedelta(days=1)
            else: # a mistake in the input
                end_time = start_time
        return start_time, end_time
