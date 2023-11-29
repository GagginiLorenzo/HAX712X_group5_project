# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# %%
# lecture du dataframe
df_atmo = pd.read_csv("./data/donnees_atmo.csv")

# %%
# nettoyage df_atmo
df_atmo = df_atmo.drop(["date_fin", "statut_valid", "x_l93", "y_l93", "geom", "metrique"], axis=1)


# %%
# liste des villes et des polluants triés
villes = df_atmo["nom_com"].unique().tolist()
villes.sort()
polluants = df_atmo["nom_polluant"].unique().tolist()
polluants.sort()


# %%
# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_1 = df_atmo.loc[(df_atmo["nom_com"] == ville) & (df_atmo["nom_polluant"] == polluant), :]
    return df_1


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant):
    df_pv = selection(ville, polluant)
    stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)
    fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True)
    fig.suptitle("Pollution selon le jour de la semaine à Montpellier", fontsize=16)

    for i in range(nb_stations):
        df_pvs = df_pv.loc[df_pv["nom_station"] == stations[i]]
        df_pvs["date_debut"] = df_pvs["date_debut"].apply(
            lambda _: datetime.strptime(_, "%Y-%m-%d %H:%M:%S")
        )
        df_pvs = df_pvs.set_index(["date_debut"])
        df_pvs["weekday"] = df_pvs.index.weekday
        pollution_week = (
            df_pvs.groupby(["weekday", df_pvs.index.hour])["valeur"]
            .mean()
            .unstack(level=0)
        )
        axes[i].plot(pollution_week)
        axes[i].set_xticklabels(np.arange(0, 24), rotation=45)
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du " + str(polluant) + " à " + str(stations[i])
        )
        axes[i].legend(
        ).set_visible(True)
        axes[i].grid(True)

    plt.show()


# %%
