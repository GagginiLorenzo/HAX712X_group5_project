# %%
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import requests


# %%
# lecture du dataframe

url = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/donnees-synop-essentielles-omm/records?refine=nom_reg%3A%22Occitanie%22&refine=date%3A%222023%22"

response = requests.get(url)

if response.status_code == 200:
    df_synop = response.json()
else:
    print(f"La requête a échoué avec le code d'état {response.status_code}")


# %%
results = df_synop.get("results", [])
df_synop = pd.DataFrame(results)

# %%
garder = ["date", "nom", "pres", "tc", "tminsolc", "nom_dept", "code_dep"]
df_synop = df_synop[garder]
df_synop["date"] = df_synop["date"].apply(lambda _: datetime.fromisoformat(_))
# %%
df_synop = df_synop[df_synop.date > "2022-09"]

# %%
# sélection de colonne avec au moins 70% de données non nulles
df_synop = df_synop.loc[:, df_synop.isnull().sum()/len(df_synop.index) <0.3]

# %%
# formatage date
df_synop["date"] = df_synop["date"].apply(lambda x: x.replace(tzinfo=None))

# %%
# test sur montpellier
montpeul = df_synop[df_synop["nom"] == "MONTPELLIER"]
montpeul = montpeul.set_index(["date"])

# %%
# graphique de la pression en moyenne par jour
def graphique(ville, param):
    df_synop1 = df_synop.loc[
        df_synop["nom"] == ville, :
    ]
    df_synop1 = df_synop1.set_index(["date"])
    fig, ax = plt.subplots(layout="constrained")
    ax.plot(df_synop1[param].resample("d").mean())
    for label in ax.get_xticklabels():
        label.set_ha("right")
        label.set_rotation(45)
    ax.set_title("Valeur de la " + str(param) + " à " + str(ville))
    ax.grid(True)
    plt.show()
# %%
