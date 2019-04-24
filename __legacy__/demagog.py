import utils
import config

import numpy as np
from time import sleep
import pandas as pd


class Scraper:
    """A scraper for the stats from the webpage demagog.sk."""

    def __init__(self):
        """Initialize the base url and get the base soup."""
        self.base_url = "http://www.demagog.sk/politici"
        self.base_soup = utils.get_soup(self.base_url)

    def get_poslanci_urls(self):
        """Get a list of urls to pages of all politicians."""
        divs = self.base_soup(
            "div", attrs={"class": "speaker large-2 small-6 columns"})
        self.poslanci_urls = [div.find("a")["href"] for div in divs]
        self.n_poslanci = len(self.poslanci_urls)

    def get_poslanec_stats(self, i):
        """Get the stats for the ith politician from the list poslanci_urls."""
        stats = {}
        url_parts = self.poslanci_urls[i].split("/")[2:]
        stats["id"] = int(url_parts[0])
        url = "/".join([self.base_url] + url_parts)
        soup = utils.get_soup(url)
        pol = soup.find("div", attrs={"class": "row politician"})
        texts = pol.find("h1").text.strip().split("(")
        stats["Meno"] = utils.remove_multiple_spaces(texts[0].strip())
        stats["Klub"] = utils.remove_multiple_spaces(texts[1].strip()[:-1])
        counts = [int(s.text.strip())
                  for s in pol("span", attrs={"class": "veracityNumber"})]
        labels = config.DEMAGOG_LABELS
        for c, l in zip(counts, labels):
            stats[l] = c
        stats["Total"] = np.sum(counts)
        return stats

    def get_all_data(self):
        """Get all data for all politicians and store them."""
        self.get_poslanci_urls()
        all_stats = []
        for i in range(self.n_poslanci):
            all_stats.append(self.get_poslanec_stats(i))
            sleep(config.DELAY)  # scrape so that the server is not overloaded
            print(all_stats[-1]["Meno"] + " done! Total progress {}/{}".format(
                i + 1, self.n_poslanci
            ))
        self.stats = pd.DataFrame(all_stats)
        self.stats.to_hdf(config.FILE_DEMAGOG, config.HDF_KEY, format="table")
        print("Data stored to {}".format(config.FILE_DEMAGOG))
