# Occitanie air quality explorer

Le projet "Occitanie Air Quality Explorer" intègre deux ensembles de données essentiels, à savoir les données atmosphériques (données ATMOS) représentant les niveaux de polluants, et les données météorologiques (données SYNOP) fournissant des informations sur les conditions climatiques. Cette approche combinée permet aux utilisateurs d'explorer les interactions entre la qualité de l'air et les variables météorologiques.

L'objectif est de développer un site web interactif permettant aux utilisateurs de visualiser simultanément  plusieurs graphiques décrivant l'évolution d'une valeur de polluant en corrélation avec une donnée climatique spécifique.Il permet également d'afficher une carte interactive  offrant une représentation spatiale des données ATMO. Cette carte permet aux utilisateurs de visualiser la répartition géographique des stations de mesure et de comprendre la variabilité des concentrations de polluants dans la région. 

Découvrez par vous-même la qualité de l'air en Occitanie en visitant notre site web interactif : https://gagginilorenzo.github.io/HAX712X_group5_project/q.html


# Extrait de code du site ici : 
```python
---
title: Occitanie Quality Air Explorer
format: html
filters:
  - shinylive
---
### Carte des stations d'Occitanie
::: {.column-page}
```{shinylive-python}
#| standalone: true
#| viewerHeight: 1600
#| column: page

import matplotlib.pyplot as plt
import time
from ipywidgets import HTML, Layout
import ipyleaflet as L
import json
import random
import pandas as pd
from io import StringIO  # Importez StringIO depuis io
from shiny import App, render, ui,reactive 
from shinywidgets import output_widget, reactive_read, render_widget, register_widget
import pyodide.http
import pandas
from branca.colormap import LinearColormap, linear
from datetime import datetime
from shiny import App, Inputs, Outputs, Session, reactive, ui
polluant_atmos="'O3'","'NO2'","'NO'","'NOX'","'H2S'","'PM10'","'PM2.5'","'SO2'"

app_ui = ui.page_fluid(   
    ui.input_selectize("condition1", "polluant_atmos", polluant_atmos,multiple = True),
    ui.output_text_verbatim("info1"),
    ui.output_text_verbatim("Clicks"),
    output_widget("map",height='500px'),
    ui.output_plot("GRAPH_YEAR",height='800px')
    )

def server(input, output, session):

    def url0():
        vi=str(city.get())
        cond1 = "(nom_poll="+ ') AND ('.join(input.condition1())+')'
        return f"https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Mesure_horaire_(30j)_Region_Occitanie_Polluants_Reglementaires_1/FeatureServer/0/query?where=(nom_com='{vi}')AND{cond1}&outFields=nom_dept,nom_station,nom_com,nom_poll,valeur,date_debut,date_fin&outSR=4326&f=json"
    @reactive.Calc
    async def data0():
        response0 = await pyodide.http.pyfetch(url0())
        dat = await response0.json()
        r= dat
        return r 

```

# Description de la licence MIT

 La licence utilisée est MIT (Massachusetts Institute of Technology) qui est une licence open source largement utilisée.elle est mise en fichier dans la branche main.

 Permission d'Utilisation : Toute personne qui obtient une copie du logiciel est autorisée à l'utiliser, le copier, le modifier, le fusionner, le publier, le distribuer, le sous-licencier ou le vendre, et ceci gratuitement.

 Conditions de Licence : L'utilisateur doit inclure l'avis de copyright (copyright notice) indiqué dans le texte de la licence ainsi que l'avis de permission (permission notice) dans toutes les copies ou portions substantielles du logiciel.

 Absence de Garantie : Le logiciel est fourni "tel quel", sans aucune garantie. Les auteurs ou détenteurs du copyright ne fournissent aucune garantie explicite ou implicite, y compris, mais sans s'y limiter, les garanties de qualité marchande, d'adéquation à un usage particulier et d'absence de contrefaçon.

 *Responsabilité Limitée : En aucun cas, les auteurs ou détenteurs du copyright ne peuvent être tenus responsables de toute réclamation, dommage ou autre responsabilité, que ce soit dans le cadre d'une action contractuelle, délictuelle ou autre, découlant de l'utilisation du logiciel ou en relation avec celui-ci.


## Choix des données

La mesure de la quantité d'un polluant dépend du mois et de l'heure à laquelle elle est effectuée. En effet cette quantité dépend du moment de l'année : la consommation de gaz, donc la pollution qu'elle engendre, est plus importante en hiver qu'en été. L'heure de mesure joue aussi son rôle, et à titre d'exemple, on peut citer la pollution générée par les voitures aux heures de pointe. Nous sommes donc contraints de choisir le dataset Atmo intitulé : "Mesures horaires 1 an glissant". Toutefois ce jeu de données ne fonctionnant pas pour les appels API, nous nous sommes rabatttus sur les mesures journalières annuelles et les mesures horaires des 30 derniers jours.  

Une première exploration rapide semble montrer que ce n'est pas du tout le cas sur les données Synop. Si la station d'enregistrement est correcte, le reste par contre laisse à désirer. Toutefois, nous ne nous sommes intéressés qu'à peu de paramètres : pression et température, les autres ne nous semblant pas pertinents.

## Interface utilisée

Le projet est intégré dans une page Quarto. On y retrouve différentes capsules faites avec ShinyLive. 

Voici les différents packages utilisés selon les besoins :

* capsules d'affichage : shiny, shinylive, shinywidgets
* importation des données : pyodide
* traitement des données : json, pandas, numpy
* graphiques : matplotlib
* carte intéractive : ipyleaflet, ipywidgets, branca, 

## Membres et contact

- Abchiche Thiziri : thiziri.abchiche@etu.umontpellier.fr
- Bernard-Reymond Guillaume : guillaume.bernard-reymond@etu.umontpellier.fr
- Hamomi Majda : majda.hamomi@etu.umontpellier.fr
- Gaggini Lorenzo : lorenzo.gaggini@etu.umontpellier.fr

