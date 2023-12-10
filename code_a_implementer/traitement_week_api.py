# %%
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# %%
# supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

# %%
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,nom_poll,valeur,date_debut&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


# %%
records = data.get("features", [])
records_data = [record["attributes"] for record in records]
df_atmo = pd.DataFrame(records_data)

df_atmo["date_debut"] = df_atmo["date_debut"] / 1000
df_atmo["date_debut"] = df_atmo["date_debut"].apply(
    lambda _: datetime.utcfromtimestamp(_)
)


# %%
# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_1 = df_atmo.loc[
        (df_atmo["nom_com"] == ville) & (df_atmo["nom_poll"] == polluant), :
    ]
    return df_1


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant):
    df_pv = selection(ville, polluant)
    stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)

    if nb_stations == 1:
        # Créer une seule sous-figure
        fig, axes = plt.subplots(1, 1, figsize=(10, 5))
        axes = [axes]  # Mettre l'unique axe dans une liste
    else:
        fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True)

    fig.suptitle(
        "Pollution selon le jour de la semaine à " + str(villes), fontsize=16)
    # pour la légende
    jour = ["lundi", "mardi", "mercredi",
            "jeudi", "vendredi", "samedi", "dimanche"]
    for i in range(nb_stations):
        # on ne garde que les données concernant la station en question
        df_pvs = df_pv.loc[df_pv["nom_station"] == stations[i]]
        # conversion du datetime unix en datetime
        df_pvs["date_debut"] = df_pvs["date_debut"].apply(
            lambda _: datetime.utcfromtimestamp(_ / 1000)
        )
        # on reindexe par le datetime
        df_pvs = df_pvs.set_index(["date_debut"])
        # colonne avec le numéro des jours
        df_pvs["weekday"] = df_pvs.index.weekday
        # on regroupe par jour et on fait la moyenne
        pollution_week = (
            df_pvs.groupby(["weekday", df_pvs.index.hour])["valeur"]
            .mean()
            .unstack(level=0)
        )
        # labellisation et légende
        axes[i].plot(pollution_week)
        axes[i].set_xticks(np.arange(0, 24))
        axes[i].set_xticklabels(np.arange(0, 24), rotation=45)
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du " + str(polluant) + " à " + str(stations[i])
        )
        axes[i].legend(jour, loc="lower left", bbox_to_anchor=(1, 0.1)).set_visible(
            True
        )
        axes[i].grid(True)

    plt.show()


# %%
