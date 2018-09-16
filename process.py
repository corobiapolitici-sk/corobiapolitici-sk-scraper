from bs4 import BeautifulSoup
import logging
from datetime import datetime

import constants as const
import storage
import utils



class Process:
    def __init__(self, db, conf, source_collection=None, target_collection=None):
        self.db = db
        self.conf = conf
        if source_collection is None:
            name = utils.get_collection_name(self, self.conf, const.CONF_MONGO_RAW)
            source_collection = storage.MongoCollection(self.db, name)
        if target_collection is None:
            name = utils.get_collection_name(self, self.conf, const.CONF_MONGO_PROCESSED)
            target_collection = storage.MongoCollection(self.db, name)
        self.source_collection = source_collection
        self.target_collection = target_collection
        self.base_url = ""
        self.log = logging.getLogger(str(self.__class__).split("'")[1])

    def get(self, entry_id):
        query = {const.MONGO_ENTRY_ID: entry_id}
        entry = self.source_collection.get(query)
        if entry is None:
            self.log.info("No object with id %d in collection %s", 
                entry_id, self.target_collection.name)
            return
        if const.PROCESS_ERROR_NOT_FOUND in entry[const.MONGO_HTML]:
            self.log.info("Object id %d corresponds to an empty page", entry_id)
            return
        return entry
    
    def extract_structure(self, entry):
        return entry

    def store(self, data):
        self.target_collection.update(data, const.MONGO_ENTRY_ID)

    def process(self, entry_id):
        entry = self.get(entry_id)
        if entry is None:
            return
        entry = self.extract_structure(entry)
        if entry is None:
            self.log.info("Entry %d has invalid structure.", entry_id)
            return
        self.store(entry)
        self.log.info("Entry %d processed!", entry_id)

    def process_all(self):
        results = self.source_collection.get_all({}, [const.MONGO_ENTRY_ID])
        entries = [res[const.MONGO_ENTRY_ID] for res in results if const.MONGO_ENTRY_ID in res]
        num_entries = len(entries)
        for i, entry_id in enumerate(entries):
            query = [{const.MONGO_ENTRY_ID: entry_id}, [const.MONGO_TIMESTAMP]]
            target = self.target_collection.get(*query)
            if target is not None:
                source_insert = self.source_collection.get(*query)[const.MONGO_TIMESTAMP]
                if source_insert < target[const.MONGO_TIMESTAMP]:
                    self.log.info("Entry %d already processed.", entry_id)
                    continue
            self.process(entry_id)
            self.log.info("Overall progress: %d / %d", i+1, num_entries)
        self.log.info("Processing finished!")


class Hlasovanie(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = const.URL_HLASOVANIA

    def extract_structure(self, entry):
        soup = BeautifulSoup(entry.pop(const.MONGO_HTML), features="lxml")
        try:
            first_box, second_box = soup("div", attrs={"class": "voting_stats_summary_full"})
        except:
            return
        
        for item in first_box("div")[0].find("a")["href"].split("&")[1:-1]:
            tokens = item.split("=")
            entry[tokens[0]] = int(tokens[1])
        time = first_box("div")[1].find("span").text.strip()
        entry[const.MONGO_TIME] = datetime.strptime(time, "%d. %m. %Y %H:%M")
        entry[const.MONGO_NUM] = int(first_box("div")[2].find("span").text.strip())
        entry[const.MONGO_TITLE] = first_box("div")[3].find("span").text.strip().replace(
            "\n", " ").replace("\r", " ").replace("  ", " ")
        entry[const.MONGO_RESULT] = first_box("div")[4].find("span").text.strip()

        entry[const.MONGO_SUMMARY] = {}
        for result in second_box("div")[:-1]:
            key = result.find("strong").text.strip()
            item = int(result.find("span").text.strip())
            entry[const.MONGO_SUMMARY][key] = item

        entry[const.MONGO_INDIVIDUAL] = {}
        table = soup.find("table", attrs={"class": "hpo_result_table"})
        for tr in table("tr"):
            for td in tr("td"):
                if ("class" in td.attrs and
                        td["class"][0] == "hpo_result_block_title"):
                    club = td.text.strip()
                elif td.text != "":
                    poslanec = {}
                    poslanec[const.MONGO_CLUB] = club
                    gen = td.children
                    poslanec[const.MONGO_VOTE] = next(gen).strip()
                    info = next(gen)
                    for item in info["href"].split("&")[1:]:
                        tokens = item.split("=")
                        poslanec[tokens[0]] = int(tokens[1])
                    poslanec[const.MONGO_NAME] = info.text.strip()
                    poslanec_id = poslanec.pop(const.PROCESS_POSLANEC_ID)
                    entry[const.MONGO_INDIVIDUAL][str(poslanec_id)] = poslanec
        return entry
        

