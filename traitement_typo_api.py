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
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_journaliere_poll_princ/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_station,typologie,nom_poll,valeur,date_debut,influence&outSR=4326&f=json"

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
pol_influ = df_atmo.groupby(['influence', 'nom_poll'])[
    'valeur'].mean().round(1).unstack(level=0)
polluants = pol_influ.index.tolist()

# position des labels et tracé du graphique
x = np.arange(len(polluants)) +1  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in pol_influ.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel('µg/m³')
ax.set_title('Influence du type de mesure')
ax.set_xticks(x + width, polluants)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 90)

plt.show()

# %%
# graphique de la valeur des polluants selon la typologie
# on regrope par typologie et on moyennise selon les valeurs
pol_typo = df_atmo.groupby(['typologie', 'nom_poll'])[
    'valeur'].mean().round(1).unstack(level=0)
polluants = pol_typo.index.tolist()

  # the label locations
x = np.arange(len(polluants))
# the width of the bars
width = 0.25  
multiplier = -2
fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in pol_typo.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# labellisation
ax.set_ylabel('µg/m³')
ax.set_title('Influence de la typologie')
ax.set_xticks(x + width, polluants)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 90)

plt.show()

# %%
