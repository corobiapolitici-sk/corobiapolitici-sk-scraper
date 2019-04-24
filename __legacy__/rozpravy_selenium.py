from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import utils
import time
import pickle
import pandas as pd
import os
import config

class Scraper():

    def __init__(self):
        self.url = "https://www.nrsr.sk/web/Default.aspx?sid=schodze/rozprava/vyhladavanie&CisObdobia=7&PoslanecID={}"
        self.driver = webdriver.Firefox()

    def get_raw_data(self):
        for i in poslanci_ids:
            self.driver.get(self.url.format(i))
            j = 1
            while True:
                print("Poslanec {} page {} done!".format(i, j))
                time.sleep(config.DELAY)
                try:
                    html = self.driver.find_element_by_class_name("tab_zoznam").get_attribute("innerHTML")
                    with open("data/htmls/html_{}_{}.pkl".format(i, j), "wb") as f:
                        pickle.dump(html, f)
                except:
                    break
                j += 1
                try:
                    self.driver.find_element_by_class_name("pager").find_element_by_css_selector("a[href*='{}']".format(j)).click()
                except:
                    break

    def get_all_data(self):
        self.get_raw_data()
        
        self.df = pd.DataFrame(columns = ["cas", "schodza", "tlac", "meno", "klub", "druh"])
        for file in os.listdir("data/htmls/"):
            if "html" in file:
                with open("data/htmls/{}".format(file), "rb") as f:
                    h = pickle.load(f)
                soup = BeautifulSoup(h, "lxml")
                for entry in soup("tr", attrs={"class": "tab_zoznam_nalt"}):
                    d = {}
                    data = [t.text.strip() for t in entry("span")]
                    d["cas"] = data[0]
                    d["schodza"] = int(data[1].split(".")[0])
                    d["meno"] = utils.change_name_order(data[4])
                    d["klub"] = data[5]
                    d["druh"] = data[7].split("\n")[0]
                    if " " in data[2]:
                        if "," in data[2]:
                            d["tlac"] = int(data[2].split(" ")[1][:-1])
                            df = df.append(d, ignore_index=True)
                            d["tlac"] = int(data[2].split(" ")[2])
                        else:
                            d["tlac"] = int(data[2].split(" ")[1])
            
                    self.df = self.df.append(d, ignore_index=True)
        self.df.to_pickle("data/htmls/full.pkl")