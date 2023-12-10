# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import requests

#supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

#%%
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_journaliere_poll_princ/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,code_station,typologie,nom_poll,valeur,date_debut,influence&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


#%%
records = data.get('features', [])
records_data = [record['attributes'] for record in records]
df_atmo = pd.DataFrame(records_data)

# %%
df_atmo["date_debut"] = df_atmo["date_debut"]/1000
df_atmo["date_debut"] = df_atmo["date_debut"].apply(
            lambda _: datetime.utcfromtimestamp(_)
        )
# nettoyage df
#df = df.drop(["date_fin", "statut_valid", "x_l93", "y_l93", "geom", "metrique"], axis=1)

# %%
# liste des villes et des polluants
villes = df_atmo["nom_com"].unique().tolist()
villes.sort()
polluants = df_atmo["nom_poll"].unique().tolist()
polluants.sort()


# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    #suppression d'une station de Montpellier
    if ville == 'MONTPELLIER':
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(['Montpelier Pere Louis Trafic'], 'Montpelier Antigone Trafic')
    df_atmo_1 = df_atmo.loc[(df_atmo["nom_com"] == ville) & (df_atmo["nom_poll"] == polluant), :]
    return df_atmo_1


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant):
    #sélection : pas utile
    df_pv = selection(ville, polluant)
    #les différentes stations
    nom_stations = df_pv["nom_station"].unique()
    nb_stations = len(nom_stations)
    #plusieurs graphiques
    fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True)
    #titre général
    fig.suptitle("Pollution au " + str(polluant) + " à " + str(ville), fontsize=16)

    for i in range(nb_stations):
        #on garde seulement les données de la station i
        df_pvs = df_pv.loc[df_pv["nom_station"] == nom_stations[i]]
        #transformation en datetime de date_debut
        #df_pvs["date_debut"] = df_pvs["date_debut"].apply(
        #    lambda _: datetime.strptime(_, "%Y-%m-%d %H:%M:%S")
        #)
        #datetime devient index
        df_pvs = df_pvs.set_index(["date_debut"])
        #on moyennise par jour
        axes[i].plot(df_pvs["valeur"].resample("d").mean())
        #décorations et titre
        for label in axes[i].get_xticklabels():
            label.set_ha("right")
            label.set_rotation(45)
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du " + str(polluant) + " à " + str(nom_stations[i])
        )
        axes[i].grid(True)

    plt.show()

graphique("MONTPELLIER", "PM10")

# %%

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def graphique(ville, polluant):
    #sélection : pas utile
    df_pv = selection(ville, polluant)
    
    # Vérifier s'il y a au moins une station
    if df_pv.empty:
        print(f"Aucune donnée disponible pour {ville} et {polluant}.")
        return

    #les différentes stations
    nom_stations = df_pv["nom_station"].unique()
    nb_stations = len(nom_stations)

    # Créer un subplot interactif avec des sous-graphiques partageant l'axe X
    fig = make_subplots(rows=nb_stations, cols=1, shared_xaxes=True,
                        subplot_titles=[f"Concentration du {polluant} à {station}" for station in nom_stations],
                        vertical_spacing=0.1)

    for i, station in enumerate(nom_stations):
        #on garde seulement les données de la station i
        df_pvs = df_pv.loc[df_pv["nom_station"] == station]
        #transformation en datetime de date_debut
        #df_pvs["date_debut"] = pd.to_datetime(df_pvs["date_debut"])
        #datetime devient index
        df_pvs = df_pvs.set_index(["date_debut"])
        #on moyennise par jour
        df_resampled = df_pvs["valeur"].resample("d").mean()

        # Ajouter une trace à chaque sous-graphique
        trace = go.Scatter(x=df_resampled.index, y=df_resampled, mode='lines',
                           name=f"Concentration à {station}",
                           line=dict(width=2))
        fig.add_trace(trace, row=i+1, col=1)

        # Mettre à jour les propriétés de la mise en page du sous-graphique
        fig.update_xaxes(title_text="Date", row=i+1, col=1)
        fig.update_yaxes(title_text="Concentration en µg/m3", row=i+1, col=1)
        fig.update_layout(height=nb_stations*300, showlegend=False)

    # Mettre à jour le titre général
    fig.update_layout(title=f"Pollution au {polluant} à {ville}",
                      title_x=0.5, title_font_size=20)

    # Afficher le graphique interactif
    fig.show()

# Exemple d'utilisation
graphique("MONTPELLIER", "PM10")


# %%
