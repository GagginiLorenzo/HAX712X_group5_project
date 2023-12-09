# Occitanie air quality explorer
L'objectif du projet est de créer une application web dans laquelle il sera possible de visualiser un ou plusieurs graphiques simultanément décrivant l'évolution d'une valeur de polluant en fonction d'une donnée du climat. Tout ceci pourra être conditionné en amont par d'autres choix notamment temporels. Cela permettra de visualiser différents types de graphiques concernant les polluants.


```{mermaid}
flowchart TD
    A[Zone] --> B[Condition]
    B --> D[Pollution]
    B --> E[Climat]
    E --> G[Graphique]
    D --> G
```

Le code s'articulera comme suit :


```{mermaid}
flowchart TD
    A[OpenDataSoft]
    B[Data Atmo Occitanie]
    C{{API REST}}
    D[Jupyter Notebook]
    E{{Jupyter Widgets}}
    F{{Quarto}}
    G[GitHub Pages]

    A-->C
    B-->C
    C-->D
    E-->D
    D-->F & E
    F-->G
```

De plus, nous créerons une carte intéractive cliquable de la région Occitanie à la précision du canton pour obtenir un traitement suffisamment fin, l'échelle du département étant à priori trop grande. Toutefois, nous serons peut-être amené à changer celà en fonction de l'exploration des données. 

Pour faire tout ça, nous nous organiserons en quatre phases  : 

* **phase 1** : la sélection des données
    - Restapi : demande python vers url
    - Parsing : découpage du fichier json en catégorie (date à priori)
    - Traduction : du json vers PythonDict
    - Liste des données sélectionnées
    
* **phase 2** : Traitement des données
    - Carte intéractive
    - Graphique
    
* **phase 3** : Interface utilisateur 

* **phase 4** : Documentation, Beamer 

Durant le développement du projet, l'IDE commun sera Jupyter-Notebook.

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


Nous avons donc créé deux branches et la branche principale(main) correspondant aux trois phases principales du projet :  le traitement des données (data) et la carte interactive (visu) et l'interface utilisateur (main). Ceci nous permettra de travailler en parallèle sur les différents aspects du projet dès que cela sera possible.

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

Pour la documentation, nous utiliserons la librairie Sphynx et pour la réalisation du diaporama de présentation, nous passerons par l'interface de Quarto. 

## Membres et contact

- Abchiche Thiziri : thiziri.abchiche@etu.umontpellier.fr
- Bernard-Reymond Guillaume : guillaume.bernard-reymond@etu.umontpellier.fr
- Hamomi Majda : majda.hamomi@etu.umontpellier.fr
- Gaggini Lorenzo : lorenzo.gaggini@etu.umontpellier.fr
- Ollier Julien : julien.ollier@etu.umontpellier.fr
