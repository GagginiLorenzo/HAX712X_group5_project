# Occitanie air quality explorer

Le projet "Occitanie Air Quality Explorer" intègre deux ensembles de données essentiels, à savoir les données atmosphériques (données ATMO) représentant les niveaux de polluants, et les données météorologiques (données SYNOP) fournissant des informations sur les conditions climatiques. Cette approche combinée  permet aux utilisateurs d'explorer les interactions entre la qualité de l'air et les variables météorologiques.
L'objectif est de développer un site web interactif permettant aux utilisateurs de visualiser simultanément  plusieurs graphiques décrivant l'évolution d'une valeur de polluant en corrélation avec une donnée climatique spécifique.Il permet également d'afficher une carte interactive  offrant une représentation spatiale des données ATMO. Cette carte permet aux utilisateurs de visualiser la répartition géographique des stations de mesure et de comprendre la variabilité des concentrations de polluants dans la région. 

Découvrez par vous-même la qualité de l'air en Occitanie en visitant notre site web interactif : #lien que tu dois mettre ici Lorenzo


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

# description de la licence 

 La licence utilisée est MIT (Massachusetts Institute of Technology) qui est une licence open source largement utilisée.elle est mise en fichier dans la branche main.

 Permission d'Utilisation : Toute personne qui obtient une copie du logiciel est autorisée à l'utiliser, le copier, le modifier, le fusionner, le publier, le distribuer, le sous-licencier ou le vendre, et ceci gratuitement.

 Conditions de Licence : L'utilisateur doit inclure l'avis de copyright (copyright notice) indiqué dans le texte de la licence ainsi que l'avis de permission (permission notice) dans toutes les copies ou portions substantielles du logiciel.

 Absence de Garantie : Le logiciel est fourni "tel quel", sans aucune garantie. Les auteurs ou détenteurs du copyright ne fournissent aucune garantie explicite ou implicite, y compris, mais sans s'y limiter, les garanties de qualité marchande, d'adéquation à un usage particulier et d'absence de contrefaçon.

 *Responsabilité Limitée : En aucun cas, les auteurs ou détenteurs du copyright ne peuvent être tenus responsables de toute réclamation, dommage ou autre responsabilité, que ce soit dans le cadre d'une action contractuelle, délictuelle ou autre, découlant de l'utilisation du logiciel ou en relation avec celui-ci.



 


**Organisation temporelle du projet**

```{mermaid}
gantt
    title Occitanie air quality explorer
    dateFormat YYYY-MM-DD
    section Phase 1
        Brainstrorming 1 :a1, 2023-10-01, 10d
        Brainstorming 2  :after a1, 10d
        Snpashot : 2023-10-23
    section Development
        Sélection des données : a2, 2023-10-22, 30d
        Traitements des données : after a2, 15d
        Interface utilisateur   : 2023-11-01, 30d
        Coordination : 2023-11-15 , 23d
        Documentation : a3, after a2 , 10d
        Beamer : after a3, 5d
```




## Choix des données

La mesure de la quantité d'un polluant dépent du mois et de l'heure à laquelle elle est effectuée. En effet cette quantité dépend du moment de l'année : la consommation de gaz, donc la pollution qu'elle engendre, est plus importante en hiver qu'en été. L'heure de mesure joue aussi son rôle, et à titre d'exemple, on peut citer la pollution générée par les voitures aux heures de pointe. Nous sommes donc contraints de choisir le dataset Atmo intitulé : "Mesures horaires 1 an glissant". Le dataset est bien structuré et sera plutôt simple à manipuler. 

Une première exploration rapide semble montrer que ce n'est pas du tout le cas sur les données Synop. Si la station d'enregistrement est correcte, le reste par contre laisse à désirer. En exemple on peut citer qu'après un tri par région (Occitanie), la colonne "department (name)" mélange des valeurs numériques : numéro de département, des noms de départements, des noms de lieu ou station de relevé etc ... Nous devrons donc effectuer un gros tri des données en amont pour obtenir quelque-chose de véritablement exploitable et pertinent. Pour être en adéquation avec le dataset Atmo, nous en prendrons un qui se basera sur les mêmes données à savoir sur un an glissant. L'échelle horaire ne peut pas être précisée ici car les observations sont moins fréquentes et coordonnées.

## La sélection des données

Pour cette phase de sélection, nous utiliserons différents packages : 

     * Django qui semble adapté à nos besoins pour faire nos requêtes API (Apirest) ;
     * Python-json : pour manipuler le json ;
     * Panda : si nous choisissons plutôt d'utiliser des fichiers csv.
      
## Traitements des données

Les packages standards de traitements des données seront utilisés :

 * Pandas 
 * Numpy 
 * Scipy 
 
Il s'agira dans un premier temps de nettoyer les données pour obtenir des dataframes utilisables.
 
Afin d'obtenir notre carte intéractive, nous utiliserons l'ensemble des librairies Jupyter-Widget (Ipyleaflet, Threejs ...).

Exemple de visuel attendu : 

<center>
![](./Images/canton_occitanie.svg "Carte des cantons")
</center>

## Interface utilisateur

Sur cette même carte nous souhaiterions avoir des menus déroulants avec les différents choix de polluants comme l'exemple simpliste ci-dessous : 


<form>
<label for="pays">Sélectionnez le Polluant :</label>
<select id="pays" name="pays">
  <option value="france">NO2</option>
  <option value="espagne">CO2</option>
  <option value="belgique">SO2</option>
  <!-- Autres options -->
</select>
</form>


Puis en cliquant sur un canton, notre application afficherait le graphique désiré sur le contaon choisi.


Nous souhaiterions obtenir quelque-chose ressemblant à l'image ci-dessous :


![](./Images/dash_result.png "Résultat espéré")


Pour les graphiques, nous utiliserons les librairies classiques que sont : 

* Matplotlib 
* Seaborn 

Enfin pour la page web, nous nous servirons Quarto qui sintègre bien à l'ensemble de nos choix de packages pour notre projet.

## Documentation et beamer

Pour la réalisation du diaporama de présentation, nous utilisons quarto . 

## Membres et contact

- Abchiche Thiziri : thiziri.abchiche@etu.umontpellier.fr
- Bernard-Reymond Guillaume : guillaume.bernard-reymond@etu.umontpellier.fr
- Hamomi Majda : majda.hamomi@etu.umontpellier.fr
- Gaggini Lorenzo : lorenzo.gaggini@etu.umontpellier.fr
- Ollier Julien : julien.ollier@etu.umontpellier.fr

