# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

# %%
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_journaliere_poll_princ/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,code_station,typologie,nom_poll,valeur,date_debut,influence&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


#%%
records = data.get("features", [])
records_data = [record["attributes"] for record in records]
df_atmo = pd.DataFrame(records_data)

#%%
# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    # suppression d'une station de Montpellier
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_atmo_1 = df_atmo.loc[
        (df_atmo["nom_com"] == ville) & (df_atmo["nom_poll"] == polluant), :
    ]
    return df_atmo_1


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant):
    # sélection : pas utile
    df_pv = selection(ville, polluant)
    # les différentes stations
    nom_stations = df_pv["nom_station"].unique()
    nb_stations = len(nom_stations)
    # plusieurs graphiques
    if nb_stations == 1:
        fig, axes = plt.subplots(1, 1, figsize=(10, 5), layout="constrained")  # Créer une seule sous-figure
        axes = [axes]  # Mettre l'unique axe dans une liste
    else:
        fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True, layout="constrained")
    # titre général
    fig.suptitle("Pollution au " + str(polluant) + " à " + str(ville), fontsize=16)

    for i in range(nb_stations):
        # on garde seulement les données de la station i
        df_pvs = df_pv.loc[df_pv["nom_station"] == nom_stations[i]]
        # transformation en datetime de date_debut
        df_pvs["date_debut"] = df_atmo["date_debut"].apply(
            lambda _: datetime.utcfromtimestamp(_ / 1000)
        )
        # datetime devient index
        df_pvs = df_pvs.set_index(["date_debut"])
        # on moyennise par jour
        axes[i].plot(df_pvs["valeur"].resample("d").mean())
        # labellisations et titre
        for label in axes[i].get_xticklabels():
            label.set_ha("right")
            label.set_rotation(45)
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du " + str(polluant) + " à " + str(nom_stations[i])
        )
        axes[i].grid(True)

    plt.show()


# %%
