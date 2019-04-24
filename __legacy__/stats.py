import pandas as pd
import numpy as np
import os

import config


def compute_hlasy_pie_tlace():
    """Prepare data for the hlasy pie charts."""
    if not os.path.isfile(config.FILE_HLASY):
        print("File {} does not exist locally!".format(config.FILE_HLASY))
    if not os.path.isfile(config.FILE_HLASY_METADATA):
        print("File {} does not exist locally!".format(
            config.FILE_HLASY_METADATA))
    hlasy = pd.read_hdf(config.FILE_HLASY)
    meta = pd.read_hdf(config.FILE_HLASY_METADATA)

    meta = meta[meta["tlac"].notnull()]
    id_vysledky = {s: meta.index[meta["Vysledok"] == "Návrh " + s]
                   for s in config.HLASY_STATS_VYSLEDOK}
    sts = {
        vysledok: hlasy.loc[id_vysledky[vysledok]].apply(
            lambda x: x.value_counts()).fillna(0)
        for vysledok in id_vysledky
        }
    for vysledok in sts:
        sts[vysledok].to_hdf(config.FILE_STATS_HLASY_PIE, vysledok,
                             format="table")


def prepare_pie_demagog():
    """Extract only the necessary columns and politication from demagog."""
    if not os.path.isfile(config.FILE_KLUBY):
        print("File {} does not exist locally!".format(config.FILE_KLUBY))
    if not os.path.isfile(config.FILE_DEMAGOG):
        print("File {} does not exist locally!".format(
            config.FILE_DEMAGOG))
    kluby = pd.read_hdf(config.FILE_KLUBY)
    dg = pd.read_hdf(config.FILE_DEMAGOG)
    names = kluby.index
    dg = dg[dg["Meno"].isin(names)]
    df = pd.DataFrame(dg[config.DEMAGOG_LABELS].values,
                      columns=config.DEMAGOG_LABELS,
                      index=dg["Meno"].values).T
    df.to_hdf(config.FILE_DEMAGOG_PIE, config.HDF_KEY, format="table")


def prepare_stats_rozpravy():
    """Extract only the summary stats from rozpravy."""
    if not os.path.isfile(config.FILE_ROZPRAVY):
        print("File {} does not exist locally!".format(config.FILE_ROZPRAVY))
    rz = pd.read_pickle(config.FILE_ROZPRAVY)
    sts = pd.DataFrame()
    # DURATION
    dur = rz["end_time"] - rz["start_time"]
    dur[dur < pd.Timedelta(0)] += pd.Timedelta(days=1)  # issue with midnight
    rz[config.ROZPRAVY_APP_LABELS[0]] = dur
    sts[config.ROZPRAVY_APP_LABELS[0]] = rz.groupby(["name"])[
        config.ROZPRAVY_APP_LABELS[0]].sum()
    dur_sort = sts[config.ROZPRAVY_APP_LABELS[0]].argsort()
    dur_vals = sts[config.ROZPRAVY_APP_LABELS[0]][dur_sort]
    dur_vals.to_pickle(config.FILE_ROZPRAVY_DURATION)

    # N_WORDS
    rz[config.ROZPRAVY_APP_LABELS[1]] = rz["text"].apply(
        lambda x: len(x.split(" ")))
    sts[config.ROZPRAVY_APP_LABELS[1]] = rz.groupby(["name"])[
        config.ROZPRAVY_APP_LABELS[0]].sum()
