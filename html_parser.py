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

    def get(self, entry_id):
        query = {const.MONGO_ID: entry_id}
        entry = self.source_collection.get(query)
        if entry is None:
            self.log.info("No object with id %d in collection %r", 
                entry_id, self.target_collection.name)
            return
        if const.PARSE_ERROR_NOT_FOUND in entry[const.MONGO_HTML]:
            self.log.info("Object id %d corresponds to an empty page", entry_id)
            return
        return entry
    
    def extract_structure(self, entry):
        return entry

    def store(self, data):
        self.target_collection.update(data, const.MONGO_ID)

    def parse(self, entry_id):
        entry = self.get(entry_id)
        if entry is None:
            return
        entry = self.extract_structure(entry)
        if entry is None:
            self.log.info("Entry %d has invalid structure.", entry_id)
            return
        self.store(entry)
        self.log.info("Entry %d parsed!", entry_id)

    def parse_all(self):
        for i, entry in enumerate(self.source_collection.iterate_all()):
            entry_id = entry[const.MONGO_ID]
            target = self.target_collection.get({const.MONGO_ID: entry_id}, 
                projection=[const.MONGO_TIMESTAMP])
            if target is not None:
                source_insert = self.source_collection.get({const.MONGO_ID: entry_id},
                projection=[const.MONGO_TIMESTAMP])[const.MONGO_TIMESTAMP]
                if source_insert < target[const.MONGO_TIMESTAMP]:
                    self.log.info("Entry %d already parsed.", entry_id)
                    continue
            self.parse(entry_id)
            self.log.info("Overall progress: %d items parsed!", i+1)
        self.log.info("Parsing finished!")


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
        entry[const.HLASOVANIE_VYSLEDOK] = first_box("div")[4].find("span").text.strip()

        for result in second_box("div")[:-1]:
            key = result.find("strong").text.strip()
            item = int(result.find("span").text.strip())
            entry[const.HLASOVANIE_SUHRN_DICT[key]] = item

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

