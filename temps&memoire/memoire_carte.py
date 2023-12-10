import cProfile
import requests
import ipyleaflet
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
from datetime import datetime
from branca.colormap import linear
from ipyleaflet import Map, GeoJSON

def load_data():
    url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_mensuelle_poll_princ/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_poll,valeur,date_debut,date_fin&outSR=4326&f=json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print(f"La requête a échoué avec le code d'état {response.status_code}")

    records = data.get('features', [])
    # Extract 'geometry' and 'attribute' into a list of tuples
    combined_data = [(record['geometry'], record['attributes']) for record in records]
    # Create a DataFrame from the combined data
    df_combined = pd.DataFrame(combined_data, columns=['geometry', 'attribute'])
    # Extract values from 'geometry' and 'attribute'
    df_combined['x'] = df_combined['geometry'].apply(lambda geo: geo['x'])
    df_combined['y'] = df_combined['geometry'].apply(lambda geo: geo['y'])
    df_combined['nom_station'] = df_combined['attribute'].apply(lambda attr: attr['nom_station'])
    df_combined['nom_poll'] = df_combined['attribute'].apply(lambda attr: attr['nom_poll'])
    df_combined['valeur'] = df_combined['attribute'].apply(lambda attr: attr['valeur'])
    df_atmo =df_combined.drop(['geometry', 'attribute'], axis=1)

    return df_atmo

def process_data(df_atmo):
    villes = df_atmo["nom_station"].unique().tolist()
    villes.sort()
    polluants = df_atmo["nom_poll"].unique().tolist()
    polluants.sort()
    df_atmo["nom_station"]=df_atmo["nom_station"].str.title()
    d= dict(tuple(df_atmo.groupby('nom_poll')))
    dataO3_1 = d['O3']
    dataPM10_2 = d['PM10']
    dataNOX_3 = d['NOX']
    dataPM25_4 = d['PM2.5']
    dataNO_5 = d['NO']
    dataH2S_6 = d['H2S']
    dataSO2_7 = d['SO2']
    dataNO2_8= d['NO2']

    # Créer un nouveau DataFrame avec les résultats
    dataO3 = dataO3_1.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataPM10 =dataPM10_2.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataNOX = dataNOX_3.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataPM25 = dataPM25_4.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataNO = dataNO_5.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataH2S = dataH2S_6.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataSO2 = dataSO2_7.groupby(['nom_station', 'nom_poll']).max().reset_index()
    dataNO2 = dataNO2_8.groupby(['nom_station', 'nom_poll']).max().reset_index()
    

    return dataO3, dataPM10, dataNOX, dataPM25, dataNO, dataH2S, dataSO2, dataNO2

def load_geojson():
        # Charger les données des départements
    geojson_path = "https://france-geojson.gregoiredavid.fr/repo/regions/occitanie/departements-occitanie.geojson"
    response = requests.get(geojson_path)
    geojson = response.json()
    return geojson



def create_choropleth_map(df, geojson_communes):
    # Créer la carte choroplèthe avec ipyleaflet
    mymap = ipyleaflet.Map(center=(43.6, 2.5), zoom=7.5)

    # Créer une échelle de couleurs en fonction des valeurs de polluants
    colormap = linear.YlOrRd_09.scale(df['valeur'].min(), df['valeur'].max())

    mymap = ipyleaflet.Map(center=(43.6, 2.5), zoom=7.5)

    def random_color(feature):
        return {
            'color': 'pink',
            'fillColor': random.choice(['red', 'yellow', 'green', 'orange']),
        }
    # Ajouter la couche GeoJSON à la carte
    geojson_layer =  GeoJSON(
        data=geojson,
        style={
            'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.2, 'weight': 1
        },
        hover_style={
            'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5
        },
        style_callback=random_color
    )
    mymap.add_layer(geojson_layer)

    return mymap


def add_marker_layer(df):
    markers_layer = ipyleaflet.MarkerCluster(
        markers=[
            ipyleaflet.CircleMarker(
                location=(row['y'], row['x']),
                radius=10,  
                color=colormap.rgb_hex_str(row['valeur']),
                fill_color=colormap.rgb_hex_str(row['valeur']),
                fill_opacity=0.9,
                popup=ipywidgets.HTML(value=f"<div style='font-family: Arial; padding: 10px;background-color: #dcffb8;'><strong>{row['nom_station']}</strong>"),    
                draggable=False,
            )
            for _, row in df.iterrows()
        ]
    )
    mymap.add_layer(markers_layer)

def profile_and_save_map():
    # Profilage du chargement des données
    profiler_load_data = cProfile.Profile()
    profiler_load_data.enable()
    
    df_atmo = load_data()
    
    profiler_load_data.disable()
    profiler_load_data.print_stats(sort='cumulative')

    # Profilage du traitement des données
    profiler_process_data = cProfile.Profile()
    profiler_process_data.enable()

    dataO3, dataPM10, dataNOX, dataPM25, dataNO, dataH2S, dataSO2, dataNO2 = process_data(df_atmo)

    profiler_process_data.disable()
    profiler_process_data.print_stats(sort='cumulative')

    # Profilage de la création de la carte choroplèthe
    profiler_create_map = cProfile.Profile()
    profiler_create_map.enable()

    mymap = create_choropleth_map(df, geojson_communes)

    profiler_create_map.disable()
    profiler_create_map.print_stats(sort='cumulative')

    # Profilage de l'ajout de la couche de marqueurs
    profiler_add_markers = cProfile.Profile()
    profiler_add_markers.enable()

    add_marker_layer(df)

    profiler_add_markers.disable()
    profiler_add_markers.print_stats(sort='cumulative')

    # Profilage de la sauvegarde de la carte
    profiler_save_map = cProfile.Profile()
    profiler_save_map.enable()

    save_map(mymap)

    profiler_save_map.disable()
    profiler_save_map.print_stats(sort='cumulative')

if __name__ == "__main__":
    profile_and_save_map()