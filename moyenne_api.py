# %%
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import requests

# supprimer les warnings
pd.options.mode.chained_assignment = None  # default='warn'

# %%
url = "https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=1%3D1&outFields=nom_com,nom_poll,valeur,date_debut,nom_station,nom_dept&outSR=4326&f=json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


# %%
records = data.get('features', [])
records_data = [record['attributes'] for record in records]
df_atmo = pd.DataFrame(records_data)

# renvoie le df avec les moyennes de chaque polluant par ville
moy_poll_ville = (
    df_atmo.groupby(["nom_com", "nom_poll"])["valeur"]
    .mean()
    .unstack(level=0)
)

# renvoie le df avec les moyennes de chaque polluant par département
moyenne_poll_dept = (
    df_atmo.groupby(["nom_dept", "nom_poll"])["valeur"]
    .mean()
    .unstack(level=0)
)


# %%
