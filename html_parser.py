from bs4 import BeautifulSoup
import logging
from datetime import datetime

import constants as const
import storage
import utils


class HTMLParser:
    def __init__(self, db, conf, source_collection=None, target_collection=None):
        self.db = db
        self.conf = conf
        if source_collection is None:
            source_collection = utils.get_collection(
                self, self.conf, const.CONF_MONGO_RAW, self.db)
        if target_collection is None:
            target_collection = utils.get_collection(
                self, self.conf, const.CONF_MONGO_PARSED, self.db)
        self.source_collection = source_collection
        self.target_collection = target_collection
        self.log = logging.getLogger(str(self.__class__).split("'")[1])
        self.unique_ids = [const.MONGO_ID]

    def get(self, query):
        entry = self.source_collection.get(query)
        if entry is None:
            self.log.info("No objectsatisfying query %s in collection %r", 
                str(query), self.target_collection.name)
            return
        if const.PARSE_ERROR_NOT_FOUND in entry[const.MONGO_HTML]:
            self.log.info("Object id %s corresponds to an empty page", str(query))
            return
        return entry
    
    def extract_structure(self, entry):
        return entry

    def store(self, data):
        self.target_collection.update(data, const.MONGO_ID)

    def parse(self, query):
        entry = self.get(query)
        if entry is None:
            return
        entry = self.extract_structure(entry)
        if entry is None:
            self.log.info("Entry %s has invalid structure.", str(query))
            return
        self.store(entry)
        self.log.info("Entry %d parsed!", str(query))

    def parse_all(self):
        for i, entry in enumerate(self.source_collection.iterate_all()):
            query = {unique_id: entry[unique_id] for unique_id in self.unique_ids}
            target = self.target_collection.get(query, 
                projection=[const.MONGO_TIMESTAMP])
            if target is not None:
                source_insert = self.source_collection.get(query,
                projection=[const.MONGO_TIMESTAMP])[const.MONGO_TIMESTAMP]
                if source_insert < target[const.MONGO_TIMESTAMP]:
                    self.log.info("Entry %s already parsed.", str(query))
                    continue
            self.parse(query)
            self.log.info("Overall progress: %d items parsed!", i+1)
        self.log.info("Parsing finished!")

    def strip(self, s):
        if s is None:
            return ""
        else:
            return s.text.strip()

class Hlasovanie(HTMLParser):
    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        try:
            first_box, second_box = soup("div", attrs={"class": "voting_stats_summary_full"})
        except:
            return
        
        for item in first_box("div")[0].find("a")["href"].split("&")[1:-1]:
            tokens = item.split("=")
            entry[const.HLASOVANIE_URL_DICT[tokens[0]]] = int(tokens[1])
        time = first_box("div")[1].find("span").text.strip()
        entry[const.HLASOVANIE_CAS] = datetime.strptime(time, "%d. %m. %Y %H:%M")
        entry[const.HLASOVANIE_CISLO] = int(first_box("div")[2].find("span").text.strip())
        entry[const.HLASOVANIE_NAZOV] = first_box("div")[3].find("span").text.strip().replace(
            "\n", " ").replace("\r", " ").replace("  ", " ")
        vysledok = first_box("div")[4].find("span")
        if vysledok is not None:
            entry[const.HLASOVANIE_VYSLEDOK] = vysledok.text.strip()

        try:
            for result in second_box("div")[:-1]:
                key = result.find("strong").text.strip()
                item = int(result.find("span").text.strip())
                entry[const.HLASOVANIE_SUHRN_DICT[key]] = item
        except:
            return entry

        entry[const.HLASOVANIE_INDIVIDUALNE] = {}
        table = soup.find("table", attrs={"class": "hpo_result_table"})
        for tr in table("tr"):
            for td in tr("td"):
                if ("class" in td.attrs and
                        td["class"][0] == "hpo_result_block_title"):
                    club = td.text.strip()
                elif td.text != "":
                    poslanec = {}
                    poslanec[const.HLASOVANIE_KLUB] = club
                    gen = td.children
                    poslanec[const.HLASOVANIE_HLAS] = next(gen).strip()
                    info = next(gen)
                    for item in info["href"].split("&")[1:]:
                        tokens = item.split("=")
                        poslanec[const.HLASOVANIE_POSLANEC_DICT[tokens[0]]] = int(tokens[1])
                    poslanec[const.HLASOVANIE_CELE_MENO] = info.text.strip()
                    poslanec_id = poslanec.pop(const.MONGO_ID)
                    entry[const.HLASOVANIE_INDIVIDUALNE][str(poslanec_id)] = poslanec
        return entry

class Poslanec(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique_ids = [const.MONGO_ID, const.POSLANEC_OBDOBIE]

    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        personal = soup.find("div", attrs={"class":"mp_personal_data"})
        for div in personal("div"):
            if div.find("strong") is not None:
                key = div.find("strong").text.strip().lower()
                entry[const.POSLANEC_INFO_DICT[key]] = div.find("span").text.strip()
        entry[const.POSLANEC_NARODENY] = datetime.strptime(
            entry[const.POSLANEC_NARODENY], "%d. %m. %Y")
        clenstvo = soup.find(
            "span", attrs={"id": "_sectionLayoutContainer_ctl01_ctlClenstvoLabel"})
        entry[const.POSLANEC_CLENSTVO] = {}
        for li in clenstvo.parent.parent("li"):
            text = li.text
            tokens = text.split("(")
            if len(tokens) == 1:
                res = ""
            else:
                res = tokens[1].split(")")[0].strip().capitalize()
            entry[const.POSLANEC_CLENSTVO][tokens[0].strip()] = res
        entry[const.POSLANEC_FOTO] = soup.find("div", attrs={"class": "mp_foto"}).find("img")["src"]
        return entry


class Zakon(HTMLParser):
    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        entry[const.ZAKON_POPIS] = self.strip(soup.find("h1"))
        main_soup = soup.find("div", attrs={"id": "_sectionLayoutContainer__panelContent"})
        missing_citanie1 = "I. čítanie" not in [s.text.strip() for s in main_soup("h2")]
        for span in main_soup("span"):
            span_id = self.add_one_id(span["id"], missing_citanie1)
            if const.ZAKON_ID_DICT[span_id] is not None:
                entry[const.ZAKON_ID_DICT[span_id]] = self.strip(span)
        entry[const.ZAKON_VYSLEDOK] = entry[const.ZAKON_VYSLEDOK][1:-1]
        if const.ZAKON_CITANIE1_SCHODZA in entry:
            entry[const.ZAKON_CITANIE1_SCHODZA] = int(entry[const.ZAKON_CITANIE1_SCHODZA])
        for field in [const.ZAKON_DATUM_DORUCENIA, const.ZAKON_PREROKOVANIE_GESTORSKY]:
            if field in entry:
                entry[field] = datetime.strptime(entry[field].split(",")[0].strip(), "%d. %m. %Y")
        self.add_zmeny(soup, entry, missing_citanie1)
        return entry
    
    def add_one_id(self, span_id, add_one):
        if add_one:
            tokens = span_id.split("_ctl0")
            if len(tokens) == 3:
                num = int(tokens[2][0])
                if num >= 2:
                    num += 1
                    tokens[2] = str(num) + tokens[2][1:]
                span_id = "_ctl0".join(tokens)
        return span_id

    def add_zmeny(self, soup, entry, add_one):
        if add_one:
            div_id = "_sectionLayoutContainer_ctl01_ctl04__PdnList__pdnListPanel"
        else:
            div_id = "_sectionLayoutContainer_ctl01_ctl05__PdnList__pdnListPanel"
        table = soup.find("div", attrs={"id": div_id})
        if table is not None:
            entry[const.ZAKON_ZMENY] = {}
            for tr in table.find("table")("tr"):
                zmena = {}
                tds = tr("td")
                zmena[const.ZAKON_ZMENY_CAS] = tds[0].text.strip()
                zmena[const.ZAKON_ZMENY_PREDKLADATEL] = tds[1].text.strip()
                zmena[const.ZAKON_ZMENY_URL] = tds[2].find("a")["href"]
                zmena_id = zmena[const.ZAKON_ZMENY_URL].split("=")[-1]
                zmena[const.ZAKON_ZMENY_DOKUMENT] = tds[3].find("a")["href"]
                if len(tds) == 5 and tds[4].text.strip() != "":
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_URL] = tds[4].find("a")["href"]
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_ID] = int(
                        zmena[const.ZAKON_ZMENY_HLASOVANIE_URL].split("=")[-1])
                    zmena[const.ZAKON_ZMENY_HLASOVANIE_VYSLEDOK] = tds[4].text.strip()
                entry[const.ZAKON_ZMENY][zmena_id] = zmena

class LegislativnaIniciativa(HTMLParser):
    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        entry[const.PREDLOZILZAKON_LIST] = {}
        table = soup.find("table", attrs={"class": "tab_zoznam paginated sortable"})
        if table is None:
            return entry
        for row in table("tr")[1:]:
            zakon = {}
            cols = row("td")
            zakon[const.ZAKON_NAZOV] = cols[0].text.strip()
            zakon[const.ZAKON_STAV] = cols[2].text.strip()
            zakon[const.ZAKON_DATUM_DORUCENIA] = datetime.strptime(
                cols[3].text.strip(), "%d. %m. %Y")
            zakon[const.ZAKON_NAVRHOVATEL] = cols[4].text.strip()
            zakon[const.ZAKON_DRUH] = cols[5].text.strip()
            zakon_id = cols[1].text.strip()
            entry[const.PREDLOZILZAKON_LIST][zakon_id] = zakon
        return entry

class HlasovanieTlace(HTMLParser):
    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        entry[const.HLASOVANIETLAC_LIST] = {}
        table = soup.find("table", attrs={"class": "tab_zoznam"})
        if table is None:
            return entry
        for row in table("tr")[1:]:
            hlasovanie = {}
            cols = row("td")
            hlasovanie[const.HLASOVANIE_SCHODZA] = int(cols[0].text.strip())
            hlasovanie[const.HLASOVANIE_CAS] = self.parse_date(cols[1].text.strip())
            hlasovanie[const.HLASOVANIE_CISLO] = int(cols[2].text.strip())
            hlasovanie[const.HLASOVANIE_NAZOV] = cols[4].text.strip()
            hlasovanie_id = cols[5].find("a")["href"].split("=")[-1]
            if hlasovanie_id != "":
                entry[const.HLASOVANIETLAC_LIST][hlasovanie_id] = hlasovanie
        return entry

    def parse_date(self, date):
        tokens = date.split(" ")
        formatted = " ".join(tokens[i].strip() for i in [0, -1])
        return datetime.strptime(formatted, "%d.%m.%Y %H:%M:%S")

class Zmena(HTMLParser):
    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        divs = [
            div 
            for div in soup.find("div", attrs={"class": "change_request_details"})("div") 
            if div["class"] != ["clear"]
        ]
        for div in divs:
            title = const.ZMENA_DICT[div.find("strong").text.strip()]
            if title in [const.ZMENA_NAZOV, const.ZMENA_PREDKLADATEL]:
                entry[title] = div.find("span").text.strip()
            if title in [const.ZMENA_SCHODZA, const.ZMENA_OBDOBIE]:
                entry[title] = int(div.find("span").text.strip())
            if title == const.ZMENA_DATUM:
                text = div.find("span").text.strip()
                try:
                    entry[title] = datetime.strptime(text, "%d. %m. %Y")
                except:
                    entry[title] = datetime.strptime(text, "%d. %m. %Y %H:%M")
            if title in [const.ZMENA_DALSI, const.ZMENA_PODPISANI]:
                entry[title] = [name.text.strip() for name in div("li")]
            if title == const.ZMENA_HLASOVANIE:
                a = div.find("a")
                if a is not None:
                    entry[title] = int(a["href"].split("=")[-1])
            dokument = soup.find("a", attrs={"target": "_blank"})
            if dokument is not None:
                entry[const.ZMENA_DOKUMENT] = dokument["href"]
        return entry
        