import utils
import config

import numpy as np
import pandas as pd
from time import sleep
import os


class Scraper:
    """Class to scrape all the hlasovanie from nrsr.sk."""

    def __init__(self, start_id=-1, end_id=-1):
        """Initialize scraper for all hlasovanie."""
        self.base_url = "https://www.nrsr.sk/web/"
        self.start_id, self.end_id = self.get_start_end_id()
        if start_id != -1:
            self.start_id = start_id
        if end_id != -1:
            self.end_id = end_id

    def get_start_end_id(self):
        """Get the id of the first and last hlasovanie."""
        soup = utils.get_soup(self.base_url +
                              "Default.aspx?sid=schodze/hlasovanie/schodze")
        url = soup.find(
            "div", id="_sectionLayoutContainer__panelContent"
            ).find("ul")("a")[-1].attrs["href"]
        url = self.base_url + url
        soup = utils.get_soup(url)
        first = int(soup.find(
            "table", attrs={"class": "tab_zoznam"}
            ).find("a")["href"].split("=")[-1])
        soup = utils.get_soup(self.base_url + "default.aspx?SectionId=108")
        hrefs = soup("a", attrs={
            "title": "Zobraziť detail hlasovania podľa klubov"})
        for s in hrefs:
            if "Hlasovanie" in s.text:
                break
        last = int(s["href"].split("=")[-1])
        return [first, last]

    def store_klub(self, hl):
        """Extract and store the most recent klub from hlasovanie hl."""
        kluby = pd.Series(dict(zip(hl.hlasy["name"], hl.hlasy["klub"])))
        if os.path.isfile(config.FILE_KLUBY):
            srs = pd.read_hdf(config.FILE_KLUBY)
            for name in kluby.index:
                srs[name] = kluby[name]
        else:
            srs = kluby
        srs.to_hdf(config.FILE_KLUBY, config.HDF_KEY, format="table")

    def get_tlac_hlasovania(self, tlac):
        """Get hlasovania related to given parlamentna tlac."""
        url = (self.base_url + "Default.aspx?sid=schodze/hlasovanie/"
               "vyhladavanie_vysledok&CPT={}").format(tlac)
        soup = utils.get_soup(url)
        table = soup.find("table", attrs={"class": "tab_zoznam"})
        if table is None:
            return []
        else:
            inds = [tr("td")[-1].find("a")["href"].split("=")[-1]
                    for tr in table("tr")[1:]]
            return [int(i) for i in inds if i != ""]

    def get_last_tlac_number(self):
        """Get the number of the last parlamentna tlac."""
        soup = utils.get_soup(self.base_url +
                              "Default.aspx?sid=zakony%2fprehlad%2fpredlozene")
        return int(soup.find("tr", attrs={"class": "tab_zoznam_nonalt"}
                             )("td")[1].text.strip())

    def get_all_tlac_hlasovania(self):
        """Get all the parlamentne tlace and their corresponding hlasovania."""
        last_tlac = self.get_last_tlac_number()
        self.tlace = {}
        for i in range(1, last_tlac + 1):
            self.tlace[i] = self.get_tlac_hlasovania(i)
            sleep(config.DELAY)
            print("Tlac {} done! Total progress {}/{}".format(i, i, last_tlac))

    def store_tlace(self):
        """Append the tlace data to the stored metadata."""
        if os.path.isfile(config.FILE_HLASY_METADATA):
            hl = pd.read_hdf(config.FILE_HLASY_METADATA)
            if "tlac" not in hl.columns:
                hl["tlac"] = np.nan
            for cislo_tlace in self.tlace:
                for id_hlasovania in self.tlace[cislo_tlace]:
                    hl.loc[id_hlasovania, "tlac"] = cislo_tlace
            hl.to_hdf(config.FILE_HLASY_METADATA, config.HDF_KEY,
                      format="table")
        else:
            print("Store the metadata first!")

    def get_all_data(self, get_tlace=True):
        """"Scrape all data and store them to data folder."""
        for hlasovanie_id in range(self.start_id, self.end_id + 1):
            hl = Hlasovanie(hlasovanie_id, get_all=False, store_all=False)
            sleep(config.DELAY)  # scrape so that the server is not overloaded
            if (hl.soup.find("table",
                             attrs={"class": "hpo_result_table"}) is None):
                continue
            else:
                hl.get_metadata()
                hl.get_hlasy()
                hl.store_metadata()
                hl.store_hlasy()
                self.store_klub(hl)
            print("Hlasovanie {} done! Total progress {}/{}".format(
                hlasovanie_id, hlasovanie_id - self.start_id + 1,
                self.end_id - self.start_id + 1
            ))
        print("All data stored to {}, {}, and {}".format(
            config.FILE_HLASY, config.FILE_KLUBY, config.FILE_HLASY_METADATA
        ))
        if get_tlace:
            self.get_all_tlac_hlasovania()
            self.store_tlace()
            print("File {} updated with tlace.".format(
                config.FILE_HLASY_METADATA))


class Hlasovanie:
    """Class for scraping a single hlasovanie given by hlasovanie_id."""

    def __init__(self, hlasovanie_id, get_all=True, store_all=True):
        """Initialize the class, optionally also getting and storing data."""
        self.id = hlasovanie_id
        self.soup = utils.get_soup(
            "https://www.nrsr.sk/web/Default.aspx?sid=schodze/"
            "hlasovanie/hlasklub&ID={}".format(hlasovanie_id))
        self.metadata = {}
        self.hlasy = []
        if get_all:
            self.get_metadata()
            self.get_hlasy()
        if store_all:
            self.store_metadata()
            self.store_hlasy()

    def get_metadata(self):
        """Process and store the metadata of a hlasovanie."""
        # PRVY BOX
        self.metadata = {}
        divs = self.soup.find(
            "div", attrs={"class": "voting_stats_summary_full"})
        # schodza
        soup = divs("div")[0]
        for item in soup.find("a")["href"].split("&")[1:-1]:
            tokens = item.split("=")
            self.metadata[tokens[0]] = int(tokens[1])
        # datum a cas
        soup = divs("div")[1]
        self.metadata["Cas"] = soup.find("span").text.strip()
        # cislo
        soup = divs("div")[2]
        self.metadata["Cislo"] = int(soup.find("span").text.strip())
        # nazov
        soup = divs("div")[3]
        self.metadata["Nazov"] = soup.find("span").text.strip().replace(
            "\n", " ").replace("\r", " ").replace("  ", " ")
        # vysledok
        soup = divs("div")[4]
        self.metadata["Vysledok"] = soup.find("span").text.strip()

        # DRUHY BOX
        divs = self.soup(
            "div", attrs={"class": "voting_stats_summary_full"})[1]
        for soup in divs("div")[:-1]:
            key = soup.find("strong").text.strip()
            item = int(soup.find("span").text.strip())
            self.metadata[key] = item
        self.metadata = pd.Series(self.metadata)

    def store_metadata(self):
        """Store metadata of hlasovanie processed by get_metadata."""
        if os.path.isfile(config.FILE_HLASY_METADATA):
            df = pd.read_hdf(config.FILE_HLASY_METADATA)
            df.loc[self.id, self.metadata.index] = self.metadata
        else:
            df = pd.DataFrame(dict(self.metadata), index=[self.id])
        df.to_hdf(config.FILE_HLASY_METADATA, config.HDF_KEY, format="table")

    def get_hlasy(self):
        """Process and store the actual data from a hlasovanie."""
        self.hlasy = []
        table = self.soup.find("table", attrs={"class": "hpo_result_table"})
        for tr in table("tr"):
            for td in tr("td"):
                if ("class" in td.attrs and
                        td["class"][0] == "hpo_result_block_title"):
                    klub = td.text.strip()
                elif td.text != "":
                    poslanec = {}
                    poslanec["klub"] = klub
                    gen = td.children
                    poslanec["hlas"] = next(gen).strip()
                    soup = next(gen)
                    for item in soup["href"].split("&")[1:]:
                        tokens = item.split("=")
                        poslanec[tokens[0]] = int(tokens[1])
                    poslanec["name"] = utils.change_name_order(
                        soup.text.strip())
                    self.hlasy.append(poslanec)
        self.hlasy = pd.DataFrame(self.hlasy)

    def store_hlasy(self):
        """Store data of hlasovanie processed by get_hlasy."""
        hl = dict(zip(self.hlasy["name"], self.hlasy["hlas"]))
        if os.path.isfile(config.FILE_HLASY):
            df = pd.read_hdf(config.FILE_HLASY)
            for col in hl.keys():
                if col not in df.columns:
                    df[col] = np.nan
            df.loc[self.id] = pd.Series(hl)
        else:
            df = pd.DataFrame(hl, index=[self.id])
        df.to_hdf(config.FILE_HLASY, config.HDF_KEY, format="table")
