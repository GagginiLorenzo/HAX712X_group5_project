# Importation des bibliothèques nécessaires
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import random
import geopandas as gpd
from branca.colormap import linear
from ipyleaflet import Map, GeoJSON, Marker, CircleMarker, MarkerCluster
import ipywidgets

#Traitement des données 

# Suppression des avertissements
pd.options.mode.chained_assignment = None  # default='warn'

# Téléchargement des données pour le traitement de l'API pour la typographie
url_typo = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_poll,valeur,influence,date_debut&outSR=4326&f=json"

response_typo = requests.get(url_typo)

if response_typo.status_code == 200:
    data_typo = response_typo.json()
else:
    print(f"La requête a échoué avec le code d'état {response_typo.status_code}")

# Transformation des données pour le traitement de l'API pour la typographie
records_typo = data_typo.get('features', [])
records_data_typo = [record['attributes'] for record in records_typo]
df_atmo = pd.DataFrame(records_data_typo)
print(df_atmo)

# Graphique des valeurs des polluants en fonction du type de mesure
# Regroupement des valeurs par influence et moyenne
def graph_influ(ville):
    pol_influ = df_atmo.loc[df_atmo["nom_com"] == ville]
    print(pol_influ)
    pol_influ = pol_influ.groupby(['influence', 'nom_poll'])['valeur'].mean().round(1).unstack(level=0)
    polluants = pol_influ.index.tolist()
    
    # Configuration du graphique
    x = np.arange(len(polluants)) + 1
    width = 0.25
    multiplier = 0
    fig, ax = plt.subplots(constrained_layout=True)
    
    # Tracé des barres pour chaque attribut
    for attribute, measurement in pol_influ.items():
        print(f"Attribute: {attribute}")
        print(f"Measurement:\n{measurement}")
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1
    
    # Ajout des labels et de la légende
    ax.set_ylabel('µg/m³')
    ax.set_title('Influence du type de mesure à ' + str(ville))
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(polluants)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 160)
    plt.show()

# Traitement de l'API pour la semaine
url_semaine = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,nom_poll,valeur,date_debut&outSR=4326&f=json"

response_semaine = requests.get(url_semaine)

if response_semaine.status_code == 200:
    data_semaine = response_semaine.json()
else:
    print(f"La requête a échoué avec le code d'état {response_semaine.status_code}")

# Transformation des données pour le traitement de l'API pour la semaine
records_semaine = data_semaine.get("features", [])
records_data_semaine = [record["attributes"] for record in records_semaine]
df_atmo = pd.DataFrame(records_data_semaine)

df_atmo["date_debut"] = df_atmo["date_debut"] / 1000
df_atmo["date_debut"] = df_atmo["date_debut"].apply(
    lambda _: datetime.utcfromtimestamp(_)
)

# Fonction pour sélectionner la ville et le polluant
def selection(ville, polluant):
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_1 = df_atmo.loc[
        (df_atmo["nom_com"] == ville) & (df_atmo["nom_poll"] == polluant), :
    ]
    return df_1

# Fonction pour tracer le graphique
def graphique(ville, polluant):
    df_pv = selection(ville, polluant)
    stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)

    if nb_stations == 1:
        # Création d'une seule sous-figure
        fig, axes = plt.subplots(1, 1, figsize=(10, 5))
        axes = [axes]  # Placer l'unique axe dans une liste
    else:
        fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15), sharex=True)

    fig.suptitle(
        "Pollution selon le jour de la semaine à " + str(ville), fontsize=16)
    
    # Pour la légende
    jour = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    
    for i in range(nb_stations):
        # On ne garde que les données concernant la station en question
        df_pvs = df_pv.loc[df_pv["nom_station"] == stations[i]]
        df_pvs["date_debut"] = df_pvs["date_debut"].apply(
            lambda _: datetime.utcfromtimestamp(_ / 1000)
        )
        df_pvs = df_pvs.set_index(["date_debut"])
        df_pvs["weekday"] = df_pvs.index.weekday
        pollution_week = (
            df_pvs.groupby(["weekday", df_pvs.index.hour])["valeur"]
            .mean()
            .unstack(level=0)
        )
        
        # Tracé et étiquetage
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

# Traitement de la carte de la région Occitanie

url_occitanie = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_mensuelle_poll_princ/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_dept,nom_station,nom_poll,valeur&outSR=4326&f=json"

response_occitanie = requests.get(url_occitanie)

if response_occitanie.status_code == 200:
    data_occitanie = response_occitanie.json()
else:
    print(f"La requête a échoué avec le code d'état {response_occitanie.status_code}")

records_occitanie = data_occitanie.get('features', [])
combined_data_occitanie = [(record['geometry'], record['attributes']) for record in records_occitanie]
df_combined_occitanie = pd.DataFrame(combined_data_occitanie, columns=['geometry', 'attribute'])
df_combined_occitanie['x'] = df_combined_occitanie['geometry'].apply(lambda geo: geo['x'])
df_combined_occitanie['y'] = df_combined_occitanie['geometry'].apply(lambda geo: geo['y'])
df_combined_occitanie['nom_station'] = df_combined_occitanie['attribute'].apply(lambda attr: attr['nom_station'])
df_combined_occitanie['nom_poll'] = df_combined_occitanie['attribute'].apply(lambda attr: attr['nom_poll'])
df_combined_occitanie['valeur'] = df_combined_occitanie['attribute'].apply(lambda attr: attr['valeur'])
df_atmo_occitanie = df_combined_occitanie.drop(['geometry', 'attribute'], axis=1)

# Liste des villes et des polluants
villes_occitanie = df_atmo_occitanie["nom_station"].unique().tolist()
villes_occitanie.sort()
polluants_occitanie = df_atmo_occitanie["nom_poll"].unique().tolist()
polluants_occitanie.sort()
df_atmo_occitanie["nom_station"] = df_atmo_occitanie["nom_station"].str.title()
d_occitanie = dict(tuple(df_atmo_occitanie.groupby('nom_poll')))
dataO3_1_occitanie = d_occitanie['O3']
dataPM10_2_occitanie = d_occitanie['PM10']
dataNOX_3_occitanie = d_occitanie['NOX']
dataPM25_4_occitanie = d_occitanie['PM2.5']
dataNO_5_occitanie = d_occitanie['NO']
dataH2S_6_occitanie = d_occitanie['H2S']
dataSO2_7_occitanie = d_occitanie['SO2']
dataNO2_8_occitanie = d_occitanie['NO2']

# Créer un nouveau DataFrame avec les résultats
dataO3_occitanie = dataO3_1_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataPM10_occitanie = dataPM10_2_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataNOX_occitanie = dataNOX_3_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataPM25_occitanie = dataPM25_4_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataNO_occitanie = dataNO_5_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataH2S_occitanie = dataH2S_6_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataSO2_occitanie = dataSO2_7_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()
dataNO2_occitanie = dataNO2_8_occitanie.groupby(['nom_station', 'nom_poll']).max().reset_index()

# Charger les données des stations des villes dans la région Occitanie
df_occitanie = pd.DataFrame(dataNO2_occitanie).dropna(subset=['valeur'])

# Charger les données des départements
geojson_path_occitanie = "https://france-geojson.gregoiredavid.fr/repo/regions/occitanie/departements-occitanie.geojson"
response_occitanie = requests.get(geojson_path_occitanie)
geojson_occitanie = response_occitanie.json()

colormap_occitanie = linear.YlOrRd_09.scale(df_occitanie['valeur'].min(), df_occitanie['valeur'].max())

# Créer la carte avec ipyleaflet
mymap_occitanie = ipyleaflet.Map(center=(43.6, 2.5), zoom=7.5)

def random_color_occitanie(feature):
    return {
        'color': 'pink',
        'fillColor': random.choice(['red', 'yellow', 'green', 'orange']),
    }

# Ajouter la couche GeoJSON à la carte
geojson_layer_occitanie =  GeoJSON(
    data=geojson_occitanie,
    style={
        'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.2, 'weight': 1
    },
    hover_style={
        'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5
    },
    style_callback=random_color_occitanie
)
mymap_occitanie.add_layer(geojson_layer_occitanie)

# Ajouter la couche de marqueurs à la carte avec des couleurs basées sur l'intensité du polluant
markers_layer_occitanie = ipyleaflet.MarkerCluster(
    markers=[
        ipyleaflet.CircleMarker(
            location=(row['y'], row['x']),
            radius=10,  # Ajustez le rayon selon vos préférences
            color=colormap_occitanie.rgb_hex_str(row['valeur']),
            fill_color=colormap_occitanie.rgb_hex_str(row['valeur']),
            fill_opacity=0.9,
            popup=ipywidgets.HTML(value=f"<div style='font-family: Arial; padding: 10px;background-color: #dcffb8;'><strong>{row['nom_station']}</strong>"),    
            draggable=False,
        )
        for _, row in df_occitanie.iterrows()
    ]
)
mymap_occitanie.add_layer(markers_layer_occitanie)

# Afficher la carte
mymap_occitanie





