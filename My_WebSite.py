# Traitement data 
# Traitement typo api

# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# %%
# supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

# %%
# telechargement des données
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_poll,valeur,influence,date_debut&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


# %%
# trasformation données
records = data.get('features', [])
records_data = [record['attributes'] for record in records]
df_atmo = pd.DataFrame(records_data)


# %%
# graphique de la valeur des polluants selon le type de mesure
# on regroupe les valeurs selon l'influence en moyennisant
def graph_influ(villes):
    pol_influ = df_atmo.loc[df_atmo["nom_com"] == villes]
    print(pol_influ)
    pol_influ = pol_influ.groupby(['influence', 'nom_poll'])['valeur'].mean().round(1).unstack(level=0)
    polluants = pol_influ.index.tolist()
    # position des labels et tracé du graphique
    x = np.arange(len(polluants)) + 1  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0
    fig, ax = plt.subplots(layout='constrained')
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
    ax.legend(loc='upper left') #ncols=3
    ax.set_ylim(0, 160)
plt.show()
# %% 

#Traitement week api

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

#Traitement week 

#%%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# %%
# lecture du dataframe
df = pd.read_csv("./data/mesure_horaire_view.csv")

# %%
# nettoyage df
df = df.drop(["date_fin", "statut_valid", "x_l93", "y_l93", "geom", "metrique"], axis=1)

# %%
# liste des villes et des polluants
villes = df["nom_com"].unique().tolist()
villes.sort()
polluants = df["nom_polluant"].unique().tolist()
polluants.sort()

# %%
# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    df_1 = df.loc[(df["nom_com"] == ville) & (df["nom_polluant"] == polluant), :]
    return df_1


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant):
    df_pv = selection(ville, polluant)
    stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)
    fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15) , sharex=True)
    fig.suptitle('Pollution à Montpellier', fontsize=16)

    for i in range(nb_stations):
        df_pvs = df_pv.loc[df_pv["nom_station"] == stations[i]]
        df_pvs['date_debut'] = df_pvs['date_debut'].apply(lambda _:datetime.strptime(_,"%Y-%m-%d %H:%M:%S"))
        df_pvs = df_pvs.set_index(['date_debut'])
        df_pvs['weekday'] = df_pvs.index.weekday
        pollution_week = df_pvs.groupby(['weekday', df_pvs.index.hour])[
    'valeur'].mean().unstack(level=0)
        axes[i].plot(pollution_week)
        axes[i].set_xlabel("Date")
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du "
            + str(polluant)
            + " à "
            + str(stations[i])
        )
        axes[i].grid(True)

    plt.show()


# %%


#traitement year 

# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# %%
# lecture du dataframe
df_atmo = pd.read_csv("/home/guillaume/project_2023_2024/HAX712X_group5_project/data/donnees_atmo.csv")

#%%
def selection(ville, polluant):
    if ville == "MONTPELLIER":
        df_atmo["nom_station"] = df_atmo["nom_station"].replace(
            ["Montpelier Pere Louis Trafic"], "Montpelier Antigone Trafic"
        )
    df_1 = df_atmo.loc[
        (df_atmo["nom_com"] == ville) & (df_atmo["nom_polluant"] == polluant), :
    ]
    return df_1


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
        df_pvs["date_debut"] = df_pvs["date_debut"].apply(
            lambda _: datetime.strptime(_, "%Y-%m-%d %H:%M:%S")
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
        
    plt.savefig("year.svg", dpi=300, transparent=True)
    plt.show()


# %%

#data synop

# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# %%
# lecture du dateframe
df = pd.read_csv("./data/mesure_horaire_view.csv")

# %%
# nettoyage df
df = df.drop(["date_fin", "statut_valid", "x_l93", "y_l93", "geom", "metrique"], axis=1)

# %%
# liste des villes et des polluants
villes = df["nom_com"].unique().tolist()
villes.sort()
polluants = df["nom_polluant"].unique().tolist()
polluants.sort()


# %%
# fonction qui fait la sélection ville et polluant
def selection(ville, polluant):
    df_1 = df.loc[(df["nom_com"] == ville) & (df["nom_polluant"] == polluant), :]
    return df_1


# %%
test = selection(villes[3], polluants[0])
test2 = selection("MONTPELLIER", "NOX")


# fonction sur qui crée les listes pour le graphique
def liste(df, nb_heure):
    dates = df["date_debut"][1:nb_heure].to_list()
    formatting = "%Y-%m-%d %H:%M:%S"
    x = [datetime.strptime(date, formatting) for date in dates]
    y = df["valeur"][1:nb_heure].to_list()
    return x, y


# %%
# Fonction qui trace le graphique
def graphique(ville, polluant, nb_heure):
    df_pv = selection(ville, polluant)
    stations = df_pv["code_station"].unique()
    nom_stations = df_pv["nom_station"].unique()
    nb_stations = len(stations)
    fig, axes = plt.subplots(nb_stations, 1, figsize=(10, 15) , sharex=True)
    fig.suptitle('This is a somewhat long figure title', fontsize=16)

    for i in range(nb_stations):
        df_pvs = df_pv.loc[df_pv["code_station"] == stations[i]]
        donnees = liste(df_pvs, nb_heure)
        axes[i].bar(donnees[0], donnees[1])
        axes[i].set_xlabel("Date")
        axes[i].set_ylabel("Concentration en µg/m3")
        axes[i].set_title(
            "Concentration du "
            + str(polluant)
            + " à "
            + str(nom_stations[i])
            + " sur "
            + str(nb_heure)
            + " heures"
        )
        axes[i].grid(True)
        #axes[i].set_size_inches(9, 7)

    plt.show()


# %%