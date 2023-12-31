import cProfile
import requests
import ipyleaflet
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import random
from branca.colormap import linear
from ipyleaflet import Map, GeoJSON, Marker, CircleMarker, MarkerCluster

def random_color_occitanie(feature):
    return {
        'color': 'pink',
        'fillColor': random.choice(['red', 'yellow', 'green', 'orange']),
    }

def profile_and_create_map():
    # Profilage du traitement de la carte de la région Occitanie
    profiler_map = cProfile.Profile()
    profiler_map.enable()

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

    # Ajouter la couche GeoJSON à la carte
    geojson_layer_occitanie = GeoJSON(
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
    markers_layer_occitanie = MarkerCluster(
        markers=[
            CircleMarker(
                location=(row['y'], row['x']),
                radius=10,  # Ajustez le rayon selon vos préférences
                color=colormap_occitanie.rgb_hex_str(row['valeur']),
                fill_color=colormap_occitanie.rgb_hex_str(row['valeur']),
                fill_opacity=0.9,
                popup=widgets.HTML(value=f"<div style='font-family: Arial; padding: 10px;background-color: #dcffb8;'><strong>{row['nom_station']}</strong>"),
                draggable=False,
            )
            for _, row in df_occitanie.iterrows()
        ]
    )
    mymap_occitanie.add_layer(markers_layer_occitanie)

    # Afficher la carte
    mymap_occitanie

    profiler_map.disable()
    profiler_map.print_stats(sort='cumulative')

if __name__ == "__main__":
    profile_and_create_map()


#exécution du code dans un terminal
#Python -m cProfile -o Memoire_carte.prof .\Memoire_carte.py
#snakeviz .\Memoire_carte.prof