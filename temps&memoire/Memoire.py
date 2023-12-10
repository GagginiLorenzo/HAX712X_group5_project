import cProfile
from memory_profiler import profile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import requests

# Fonction "graph_influ"

# Supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

# Téléchargement des données
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_poll,valeur,influence,date_debut&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")

# Transformation des données
records = data.get('features', [])
records_data = [record['attributes'] for record in records]
df_atmo = pd.DataFrame(records_data)

# Définir la variable "villes"
villes = "nom_com"  # Remplacez par le nom de la ville que vous souhaitez

# Fonction "graph_influ"
def graph_influ(villes):
    if 'influence' not in df_atmo.columns:
        print("La colonne 'influence' n'est pas présente dans le DataFrame.")
        return

    pol_influ = df_atmo.loc[df_atmo["nom_com"] == villes, ['influence', 'nom_poll', 'valeur']]
    
    if pol_influ.empty:
        print(f"Aucune donnée disponible pour la ville {villes}.")
        return
    pol_influ = df_atmo.loc[df_atmo["nom_com"] == villes, ['influence', 'nom_poll', 'valeur']]
    pol_influ = pol_influ.groupby(['influence', 'nom_poll'])['valeur'].mean().round(1).unstack(level=0)
    polluants = pol_influ.index.tolist()
    # Position des labels et tracé du graphique
    x = np.arange(len(polluants)) + 1  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0
    fig, ax = plt.subplots()
    for attribute, measurement in pol_influ.items():
        print(f"Attribute: {attribute}")
        print(f"Measurement:\n{measurement}")
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1
    ax.set_ylabel('µg/m³')
    ax.set_title('Influence du type de mesure à ' + str(villes))
    ax.set_xticks(x + width/2, polluants)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 160)
    plt.show()

# Profilage de la fonction "graph_influ"
@profile
def profile_graph_influ():
    profiler_graph_influ = cProfile.Profile()
    profiler_graph_influ.enable()
    graph_influ(villes)
    profiler_graph_influ.disable()
    profiler_graph_influ.dump_stats('My_Website_prof_graph_influ.prof')

# Fonction "selection"

# Supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,nom_poll,valeur,date_debut&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")

records = data.get("features", [])
records_data = [record["attributes"] for record in records]
df_atmo = pd.DataFrame(records_data)

ville = "nom_com"

df_atmo["date_debut"] = df_atmo["date_debut"] / 1000
df_atmo["date_debut"] = df_atmo["date_debut"].apply(
    lambda _: datetime.utcfromtimestamp(_)
)

# Fonction qui fait la sélection "ville" et "polluant"
def selection(ville, polluant):
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_1 = df_atmo.loc[
        (df_atmo["nom_com"] == ville) & (df_atmo["nom_poll"] == polluant), :
    ]
    return df_1

# Profilage de la fonction "selection"
@profile
def profile_selection():
    profiler_selection = cProfile.Profile()
    profiler_selection.enable()
    # Appel de la fonction à profiler
    df_selection = selection(ville, "Nom_du_polluant")
    profiler_selection.disable()
    profiler_selection.dump_stats('My_Website_prof_selection.prof')

# Fonction "graphique"

# Fonction qui trace le graphique
def graphique(ville, polluant):
    df_pv = selection(ville, polluant)
    stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)

    if nb_stations < 1:
        print(f"Aucune donnée disponible pour la ville {ville} et le polluant {polluant}.")
        return

    if nb_stations == 1:
        # Créer une seule sous-figure
        fig, axes = plt.subplots(1, 1, figsize=(10, 5))
        axes = [axes]  # Mettre l'unique axe dans une liste
    else:
        fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True)

    fig.suptitle(
        "Pollution selon le jour de la semaine à " + str(ville), fontsize=16)
    # Pour la légende
    jour = ["lundi", "mardi", "mercredi",
            "jeudi", "vendredi", "samedi", "dimanche"]
    for i in range(nb_stations):
        # On ne garde que les données concernant la station en question
        df_pvs = df_pv.loc[df_pv["nom_station"] == stations[i]]
        # Conversion du datetime unix en datetime
        df_pvs["date_debut"] = df_pvs["date_debut"].apply(
            lambda _: datetime.utcfromtimestamp(_ / 1000)
        )
        # On reindexe par le datetime
        df_pvs = df_pvs.set_index(["date_debut"])
        # Colonne avec le numéro des jours
        df_pvs["weekday"] = df_pvs.index.weekday
        # On regroupe par jour et on fait la moyenne
        pollution_week = (
            df_pvs.groupby(["weekday", df_pvs.index.hour])["valeur"]
            .mean()
            .unstack(level=0)
        )
        # Labellisation et légende
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


# Profilage de la fonction "graphique"
@profile
def profile_graphique():
    profiler_graphique = cProfile.Profile()
    profiler_graphique.enable()
    # Appel de la fonction à profiler
    graphique("nom_com", "Nom_du_polluant")
    profiler_graphique.disable()
    profiler_graphique.dump_stats('My_Website_prof_graphique.prof')

if __name__ == "__main__":
    # Appel des fonctions à profiler
    profile_graph_influ()
    profile_selection()
    profile_graphique()



#exécution du code dans un terminal
#Python -m cProfile -o Memoire.prof .\Memoire.py
#snakeviz .\Memoire.prof

 