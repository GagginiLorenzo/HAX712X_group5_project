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
#graphique de la valeur des polluants le type de mesure
pol_influ = df.groupby(['influence','nom_polluant'])[
    'valeur'].mean().round(1).unstack(level=0)
polluants = pol_typo.index.tolist()

x = np.arange(len(polluants))  # the label locations
width = 0.8  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in pol_influ.items():
    offset = width * multiplier
    rects = ax.bar(3*x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3,)
    multiplier += 1

ax.set_ylabel('µg/m³')
ax.set_title('Influence du type de mesure')
ax.set_xticks(3*x + width, polluants)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 80)

plt.show()

# %%
#graphique de la valeur des polluants selon la typologie
pol_typo = df.groupby(['typologie','nom_polluant'])[
    'valeur'].mean().round(1).unstack(level=0)
polluants = pol_typo.index.tolist()

x = np.arange(len(polluants))  # the label locations
width = 0.8  # the width of the bars
multiplier = 1

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in pol_typo.items():
    offset = width * multiplier
    rects = ax.bar(3*x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3,)
    multiplier += 1

ax.set_ylabel('µg/m³')
ax.set_title('Influence de la typologie')
ax.set_xticks(3*x + width, polluants)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 80)

plt.show()

# %%
