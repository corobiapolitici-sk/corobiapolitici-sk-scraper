import utils
import config

import pandas as pd
from time import sleep
import pickle


class Scraper:
    def __init__(self, start_id=-1, end_id=-1):
        if start_id == -1:
            self.start_id = 1
        else:
            self.start_id = start_id
        if end_id == -1:
            meta = pd.read_hdf(config.FILE_HLASY_METADATA)
            self.end_id = int(meta["tlac"].max())
        else:
            self.end_id = end_id
        self.data = {}

    def get_all_data(self):
        for i in range(self.start_id, self.end_id + 1):
            zk = Zakon(i)
            if "chyba" in zk.soup.text:
                continue
            if (zk.soup.find("span", attrs={
                    "id":
                    "_sectionLayoutContainer_ctl01_ctl00__DatumDoruceniaLabel"
                    }) is None):
                continue
            zk.get_all_data()
            self.data[i] = zk.data
            print("Zakony {} done! Total progress {}/{}".format(
                i, i - self.start_id + 1, self.end_id - self.start_id + 1
            ))
        self.store_data()

    def store_data(self):
        with open(config.FILE_ZAKONY, "wb") as f:
            pickle.dump(self.data, f)


class Zakon:
    def __init__(self, cislo):
        self.cislo = cislo
        self.url = ("https://www.nrsr.sk/web/Default.aspx?sid=zakony/zakon"
                    "&ZakZborID=13&CisObdobia=7&CPT={}".format(self.cislo))
        self.soup = utils.get_soup(self.url)
        self.data = {}

    def get_metadata(self):
        self.data["date"] = self.soup.find("span", attrs={
            "id": "_sectionLayoutContainer_ctl01_ctl00__DatumDoruceniaLabel"
            }).text.strip()
        self.data["navrhovatel"] = self.soup.find("span", attrs={
            "id": "_sectionLayoutContainer_ctl01_ctl00__NavrhovatelLabel"
            }).text.strip()
        self.parse_navrhovatel()
        self.data["stav"] = self.soup.find("span", attrs={
            "id": "_sectionLayoutContainer_ctl01__ProcessStateLabel"
            }).text.strip()
        self.data["vysledok"] = self.soup.find("span", attrs={
            "id": "_sectionLayoutContainer_ctl01__CurrentResultLabel"
            }).text.strip()[1:-1]

    def parse_navrhovatel(self):
        if "vláda" in self.data["navrhovatel"]:
            self.data["navrhovatel"] = "vláda"
        elif "výbor" in self.data["navrhovatel"]:
            self.data["navrhovatel"] = "výbor"
        elif "poslanci" in self.data["navrhovatel"]:
            if "(" in self.data["navrhovatel"]:
                poslanci = [
                    s.split("\xa0")[1] for s in self.data["navrhovatel"].split(
                        "(")[1][:-1].split(",")]
                names = pd.read_hdf(config.FILE_KLUBY).index
                poslanci = [names[names.str.contains(p)][0] for p in poslanci]
                self.data["navrhovatel"] = poslanci
            else:
                self.data["navrhovatel"] = []
        else:
            self.data["navrhovatel"] = []

    def get_zmeny(self):
        table = self.soup.find("div", attrs={
            "id": "_sectionLayoutContainer_ctl01_ctl05__PdnList__pdnListPanel"
            })
        if table is not None:
            self.data["zmeny"] = {}
            for tr in table.find("table")("tr"):
                tds = tr("td")
                cas = tds[0].text.strip()
                poslanec = utils.change_name_order(tds[1].text.strip())
                zmena_id = int(tds[2].find("a")["href"].split("=")[-1])
                document_id = int(tds[3].find("a")["href"].split("=")[-1])
                zm = Zmena(zmena_id)
                zm.get_data()
                sleep(config.DELAY)
                self.data["zmeny"][zmena_id] = {
                    "cas": cas, "poslanec": poslanec,
                    "document_id": document_id}
                for t in zm.data:
                    self.data["zmeny"][zmena_id][t] = zm.data[t]
        else:
            self.data["zmeny"] = {}

    def get_connections(self):
        meta = pd.read_hdf(config.FILE_HLASY_METADATA)
        meta = meta[meta["tlac"] == self.cislo]
        if len(meta) > 0:
            self.data["posledne"] = meta["Cas"].apply(
                lambda x: pd.to_datetime(x, dayfirst=True)).sort_values().index[-1]
        meta = meta["Nazov"]
        meta = meta[meta.str.contains("pozmeňujúcich a doplňujúcich")]
        meta = meta.apply(lambda s: s.split("Hlasovanie")[-1])
        ids = sorted(self.data["zmeny"].keys())
        names = [self.data["zmeny"][i]["poslanec"] for i in ids]
        counts = [0] * len(ids)
        for j, name in enumerate(names):
            if len([1 for n in names if n == name]) > 1:
                counts[j] = len([1 for n in names[:j+1] if n == name])
        for j, i in enumerate(ids):
            surname = names[j].split(" ")[-1]
            meta_name = meta[meta.str.contains(surname[:-1])]
            if counts[j] > 0:
                meta_name = meta_name[
                    meta_name.str.contains("{}. návrh".format(counts[j]))]
            self.data["zmeny"][i]["hlasovania"] = list(meta_name.index)

    def get_all_data(self):
        self.get_metadata()
        self.get_zmeny()
        self.get_connections()


class Zmena:
    def __init__(self, cislo):
        self.cislo = cislo
        self.url = ("https://www.nrsr.sk/web/Default.aspx?"
                    "sid=schodze/nrepdn_detail&id={}".format(self.cislo))
        self.soup = utils.get_soup(self.url)

    def get_data(self):
        self.data = {}
        for div in self.soup("div", attrs={"class": "grid_15 alpha omega"}):
            title = div.find("strong").text.strip()
            if title in ["Ďalší predkladatelia", "Podpísaní poslanci"]:
                self.data[title] = []
                for li in div("li"):
                    name = utils.change_name_order(li.text.strip())
                    self.data[title].append(name)
