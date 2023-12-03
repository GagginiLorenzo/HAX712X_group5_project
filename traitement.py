
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
df_atmo
