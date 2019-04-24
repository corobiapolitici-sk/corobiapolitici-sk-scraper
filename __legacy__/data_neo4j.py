import config
import utils

import pandas as pd
import numpy as np
import pickle


def process_hlasovania_metadata():
    meta = pd.read_hdf(config.FILE_HLASY_METADATA)
    all_stats = []
    connections = []
    for i in meta.index:
        row = meta.loc[i, :]
        stats = []
        stats.append(i)
        stats.append(utils.parse_datetime_csv(row["Cas"]))
        stats.append(str(int(row["CisObdobia"])))
        stats.append(str(int(row["CisSchodze"])))
        stats.append(str(int(row["Cislo"])))
        stats.append(row["Vysledok"])
        stats.append(row["Nazov"])
        stats.append("https://www.nrsr.sk/web/Default.aspx?sid=schodze/"
                     "hlasovanie/hlasovanie&ID={}".format(i))
        all_stats.append(stats)
        if not np.isnan(row["tlac"]):
            connections.append([i, str(int(row["tlac"]))])
    pd.DataFrame(all_stats).to_csv(config.NEO4J_HLASY_NODES,
                                   encoding="utf-8", header=False)
    pd.DataFrame(connections).to_csv(config.NEO4J_HLASY_ZAKONY_EDGES,
                                     encoding="utf-8", header=False)


def process_zakony():
    with open(config.FILE_ZAKONY, "rb") as f:
        zk = pickle.load(f)
    all_stats = []
    zmeny = []
    zmeny_predkladatelia = []
    zmeny_hlasovania = []
    zmeny_podpisani = []
    posledne_hlasovania = []
    navrhovatelia = []
    zakon_zmena = []
    for i in zk:
        for j in zk[i]["zmeny"]:
            zakon_zmena.append([i, j])

            zmena = []
            row = zk[i]["zmeny"][j]
            zmena.append(j)
            if len(row["cas"]) > 12:
                zmena.append(utils.parse_datetime_csv(row["cas"]))
            else:
                zmena.append(utils.parse_date_csv(row["cas"]))
            zmena.append(row["document_id"])
            zmena.append("https://www.nrsr.sk/web/Default.aspx?sid=schodze/"
                         "nrepdn_detail&id={}".format(j))
            zmeny.append(zmena)

            zmeny_predkladatelia.append([j, row["poslanec"]])
            if "Ďalší predkladatelia" in row:
                for predkladatel in row["Ďalší predkladatelia"]:
                    zmeny_predkladatelia.append([j, predkladatel])

            if "Podpísaní poslanci" in row:
                for poslanec in row["Podpísaní poslanci"]:
                    zmeny_podpisani.append([j, poslanec])

            for hl_id in row["hlasovania"]:
                zmeny_hlasovania.append([j, hl_id])
        stats = []
        row = zk[i]
        stats.append(i)
        stats.append(utils.parse_date_csv(row["date"]))
        stats.append(row["stav"])
        stats.append(row["vysledok"])
        stats.append("https://www.nrsr.sk/web/Default.aspx?sid=zakony/"
                     "cpt&ZakZborID=13&CisObdobia=7&ID={}".format(i))
        all_stats.append(stats)

        if "posledne" in row:
            posledne_hlasovania.append([i, row["posledne"]])

        if isinstance(row["navrhovatel"], str):
            navrhovatelia.append([i, row["navrhovatel"]])
        else:
            for poslanec in row["navrhovatel"]:
                navrhovatelia.append([i, poslanec])

        
    pd.DataFrame(zakon_zmena).to_csv(config.NEO4J_ZAKONY_ZMENY_EDGES,
                                     encoding="utf-8", header=False)
    pd.DataFrame(all_stats).to_csv(config.NEO4J_ZAKONY_NODES,
                                   encoding="utf-8", header=False)
    pd.DataFrame(zmeny).to_csv(config.NEO4J_ZMENY_NODES,
                               encoding="utf-8", header=False)
    pd.DataFrame(zmeny_podpisani).to_csv(config.NEO4J_ZMENY_PODPIS_EDGES,
                                         encoding="utf-8", header=False)
    pd.DataFrame(zmeny_hlasovania).to_csv(config.NEO4J_ZMENY_HLASOVANIA_EDGES,
                                          encoding="utf-8", header=False)
    pd.DataFrame(zmeny_predkladatelia).to_csv(
        config.NEO4J_ZMENY_PREDKLADATEL_EDGES, encoding="utf-8", header=False)
    pd.DataFrame(posledne_hlasovania).to_csv(config.NEO4J_ZAKON_POSLEDNE_EDGES,
                                             encoding="utf-8", header=False)
    pd.DataFrame(navrhovatelia).to_csv(config.NEO4J_ZAKON_NAVRHOVATEL_EDGES,
                                       encoding="utf-8", header=False)


def process_kluby():
    kluby = pd.read_hdf(config.FILE_KLUBY)
    all_stats = []
    for name in kluby.index:
        stats = []
        stats.append(name)
        klub = kluby[name]
        if "Poslanci" in klub:
            klub = "Nezaradení"
        else:
            klub = " ".join(klub.split(" ")[1:])
        stats.append(klub)
        all_stats.append(stats)
    pd.DataFrame(all_stats).to_csv(config.NEO4J_POSLANCI_KLUBY_EDGES,
                                   encoding="utf-8", header=False)

def process_hlasovania():
    hlasy = pd.read_hdf(config.FILE_HLASY)
    all_stats = []
    for i in hlasy.index:
        row = hlasy.loc[i, :].dropna()
        for name in row.index:
            if row[name] in config.HLASY_STATS_MEANING:
                all_stats.append([
                    i, name, config.HLASY_STATS_MEANING[row[name]]])
    pd.DataFrame(all_stats).to_csv(config.NEO4J_POSLANEC_HLASOVANIE_EDGES,
                                   encoding="utf-8", header=False)


def process_spektrum():
    opozicia = ["ĽS Naše Slovensko", "SaS", "OĽANO", "SME RODINA",
                "Nezaradení"]
    koalicia = ["SNS", "MOST - HÍD", "SMER - SD", "vláda"]
    stats = []
    for o in opozicia:
        stats.append(["opozícia", o])
    for k in koalicia:
        stats.append(["koalícia", k])
    pd.DataFrame(stats).to_csv(config.NEO4J_KLUBY_SPEKTRUM_EDGES,
                               encoding="utf-8", header=False)

def process_rozpravy():
    rz = pd.read_pickle(config.FILE_ROZPRAVY)
    rz["url"] = pd.Series(rz.index, rz.index).apply(
        lambda x: "http://tv.nrsr.sk/transcript?id={}".format(x))
    rz["start_time"] = rz["start_time"].values.astype(str)
    rz["end_time"] = rz["end_time"].values.astype(str)
    del rz["text"]
    rz.to_csv(config.NEO4J_ROZPRAVY_NODES_EDGES,
              encoding="utf-8", header=False)
