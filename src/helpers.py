import pandas as pd
import numpy as np
from datetime import datetime
import networkx as nx
from pyvis.network import Network
from scipy.stats.stats import pearsonr


def data_processing(path):
    data_temperature = pd.read_table(path, sep=",", names=["SOUID", "DATE", "TG", "Q_TG"], skiprows=range(0, 20))

    data_temperature.drop(data_temperature[data_temperature["Q_TG"] == 9].index, inplace=True)
    data_temperature["Year"] = [int(str(d)[:4]) for d in data_temperature.DATE]
    data_temperature["Month"] = [int(str(d)[4:6]) for d in data_temperature.DATE]
    data_temperature["Day"] = [int(str(d)[6:8]) for d in data_temperature.DATE]

    # Compute the day of the year for each year
    day_of_year = np.array(len(data_temperature["Day"]))

    adate = [datetime.strptime(str(date), "%Y%m%d") for date in data_temperature.DATE]
    data_temperature["Day_of_year"] = [d.timetuple().tm_yday for d in adate]
    data_temperature.TG = data_temperature.TG / 10.0

    return data_temperature


def to_monthly(df):
    Years = df.Year.unique()
    Months = df.Month.unique()
    data_M = pd.DataFrame(
        np.array(
            [
                [
                    df[(df.Year == y) & (df.Month == m)].TG.mean(),
                    df[(df.Year == y) & (df.Month == m)].TG.median(),
                    df[(df.Year == y) & (df.Month == m)].TG.std(),
                    y,
                    int(m),
                ]
                for y in Years
                for m in Months
            ]
        ),
        columns=["Mean", "Median", "Std", "Years", "Month"],
    )
    data_M = data_M.dropna()
    data_M["grid"] = np.array([y + float(m - 1) / 12 for y in Years for m in Months])[: np.shape(data_M)[0]]

    return data_M


def geo_correlation_net(dfs, names, y1, y2, t):
    nb_nodes = len(dfs)

    corr = np.zeros((nb_nodes, nb_nodes))

    for i in range(nb_nodes):
        for j in range(nb_nodes):
            df1 = dfs[i]
            df2 = dfs[j]

            d1 = df1[(df1.Year <= y2) & (df1.Year >= y1)]["TG"]
            d2 = df2[(df2.Year <= y2) & (df2.Year >= y1)]["TG"]

            if len(d1) == len(d2):
                corr[i, j] = pearsonr(d1, d2)[0]

    G = nx.Graph()
    nodes = [names[i] for i in range(nb_nodes)]
    G.add_nodes_from(nodes)

    edges = []

    for i in range(nb_nodes):
        for j in range(nb_nodes):
            if corr[i, j] >= t and i != j:
                edges.append((names[i], names[j]))

    G.add_edges_from(edges)

    return G
