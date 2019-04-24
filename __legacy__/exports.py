import pandas as pd

import config


def export_casy_vystupeni():
    data = pd.read_csv(config.NEO4J_ROZPRAVY_NODES_EDGES, header=None)
    data[3] = data[3].apply(lambda x: pd.to_datetime(x))
    data[4] = data[4].apply(lambda x: pd.to_datetime(x))
    dur = data[4] - data[3]
    dur[dur < pd.Timedelta(0)] += pd.Timedelta(days=1)
    data["dur"] = dur.apply(lambda x: int(x.total_seconds()) // 60)
    data.groupby([1])["dur"].sum().to_csv(
        "data/exports/vystupenia_minuty.csv", header=False)
    data.groupby([1, 2])["dur"].sum().to_csv(
        "data/exports/vystupenia_minuty_breakdown.csv", header=False)
