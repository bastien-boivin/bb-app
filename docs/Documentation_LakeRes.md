## Introduction

### Objectifs du document

### Contexte du projet

### Guide d'utilisation

## Bibliographie

### Modflow

#### Package DRN (drain)

#### Package SFR (Streamflow-Routing)

### Fuite du Lac (Leakage)

## Données

### DEM

#### BD-ALTI-75m

### Climatiques (passé)

### Projections climatiques

### Hydrologique

#### Stations de jaugeage

#### Hydrographie

#### Intermittence

### Géologique

### Données EBR

#### Abaque Bathymétrie

#### Données journalières

#### Scénarios de gestion

## Code - EBR

### App_EBR_Commun.py

#### Chargements des bibliothèques, modules et du dossier racines

Cette section permet l'importation de l'ensemble des librairies utilisées par le code, dont celles de Python, celles de librairies externes et les codes d'HydroModPy fonctionnant en POO (programmation orientée objet). Ces différentes librairies sont toutes incluses dans l'environnement Hydromodpy-0.1 préalablement installé.

En amont de ces librairies, une section # Filtrer les avertissements est à renseigner à chaque début de code afin que les alertes de DeprecationWarnings ne s'affichent pas, voir [6.1](#61-deprecationwarning).

#### LogManager

La class `LogManager` permet de gérer l'interface verbale entre l'utilisateur et le code, en faisant remonter des logs selon différentes classes avec plus ou moins de précisions et de messages selon le mode choisi. Pour paramétrer le LogManager, voir la section [5.4.2.1](#5421-class-logmanager).

#### Dossier utilisateur

La section `#%% Dossier Utilisateur` permet la création et la récupération des différents chemins sources (en dehors de celui d'HydroModPy, initialisé dans la première section) `out_path` et `data_path`. Le chemin `out_path` est initialisé lors de la première utilisation d'HydroModPy ou demandé en entrée dans le kernel. En appelant la fonction `root_folder_results()`, il crée une variable d'environnement Windows permanente contenant le chemin vers `out_path`.

Lors des lancements suivants, cette variable d'environnement sera automatiquement récupérée. Pour modifier cette variable d'environnement et donc le chemin de `out_path`, il faut appeler la fonction `update_root_folder_results()`.

Le chemin pour le fichier contenant l'ensemble des données propres au code est défini par la variable `data_path`. Dans le cadre de ce projet, ce dossier a été inclus dans `out_path`, simplifiant ainsi l'appel au chemin. Le fichier de données LakeRes se trouve donc dans `out_path`. Si `data_path` est vide, le code s'interrompt et renvoie un message d'erreur.

#### Paramétrisation

##### Paramètres généraux

- `first_year` : int, format AAAA, première année de la simulation
- `last_year` : int, format AAAA, dernière année de la simulation
- `sim_state` : str, steady ou transient
- `freq_input` : str, format D, W ou M, pas de temps de la simulation
- `subbassin` : bool, activation ou non des sous-bassins
- `load_geographic` : bool, indicateur pour charger les données géographiques
- `save_object` : bool, indicateur pour sauvegarder les objets géographiques
- `dis_perlen` : bool, indicateur pour utiliser le package DIS avec l'option PERLEN
- `model_name` : str, nom du modèle, utilisé pour l'enregistrement des fichiers Modflow
- `visual_plot` : bool, création ou non des figures
- `from_xyv` : list, coordonnées de l'exutoire choisi avec snap distance et buffer size

##### Paramètres cadres

- `box` : bool, indicateur pour définir la zone du modèle comme une boîte
- `sink_fill` : bool, indicateur pour remplir les dépressions dans le MNT
- `plot_cross` : bool, indicateur pour tracer des coupes transversales

##### Paramètres hydrauliques

- `nlay` : int, nombre de couches dans le modèle
- `lay_decay` : int, facteur de décroissance des couches
- `bottom` : float or None, élévation du fond de l'aquifère, unités : mètres ou matrice 2D
- `thick` : float, épaisseur de l'aquifère si bottom est None, unités : mètres
- `hk` : float, conductivité hydraulique horizontale, unités : m/jour
- `cond_decay` : float, facteur de décroissance de la conductivité
- `hk_vertical` : list or None, conductivité hydraulique verticale, si non renseigné égale à celle horizontale
- `cond_drain` : float, conductance du drain
- `sy` : float, rendement spécifique, unités : pourcentage
- `poro_decay` : float, facteur de décroissance de la porosité

##### Conditions aux limites

- `bc_left` : float or None, condition aux limites à gauche
- `bc_right` : float or None, condition aux limites à droite
- `sea_level` : str or float, niveau de la mer, unités

##### Paramètres de suivi des particules

- `zone_partic` : str, zone pour le suivi des particules, unités

#### Bassin Versant

Initialisation du chemin vers le mnt (`dem_path`), du nom du bassin versant (`watershed_name`) et initialisation de la classe `watershed_root.Watershed` avec création de l'objet de la simulation BV. Renseigné dans ce cas : `dem_path`, `out_path`, `load`, `watershed_name`, `from_xyv` et `save_object`. Voir section [5.1](#51-watershed_rootpy).

#### Données ponctuelles

#### Sous-Bassins

#### Recharge et Ruissellement de surface direct (données d'entrée)

##### Surfex

#### Barrage

##### Création du réservoir

Pour créer un réservoir (vide), il faut appeler la méthode `BV.add_lakeres()` contenue dans `watershed_root` qui appellera à son tour la classe `Lakeres` du fichier `lakeres.py`, afin de l'initialiser.

## HydroModPy

### Watershed_root.py

`watershed_root.py` est le module central de HydroModPy qui sert d'interface entre le code principal utilisant la classe `Watershed` et les modules spécialisés. Il permet de gérer et de coordonner les différentes fonctionnalités nécessaires à la modélisation hydrologique d'un bassin versant. Ce script facilite la création d'objets, l'intégration de données diverses via ses méthodes `add_*`, et l'exécution de simulations hydrogéologiques.

La classe `Watershed` est le cœur de ce module et fournit une structure complète pour la modélisation des bassins versants avec Modflow.

#### Initialisation (`__init__`)

**Paramètres d'entrée:**
- `dem_path` (str) : Chemin vers le Modèle Numérique de Terrain (MNT) initial. Obligatoire pour définir la topographie du bassin.
- `out_path` (str) : Chemin de sortie où seront stockés tous les résultats générés.
- `load` (bool, optionnel) : Si True, tente de charger un objet de bassin versant existant plutôt que d'en créer un nouveau. Par défaut False.
- `watershed_name` (str, optionnel) : Nom du bassin versant, utilisé pour nommer le dossier de résultats. Par défaut 'Default'.
- `from_lib` (str, optionnel) : Chemin vers un fichier CSV contenant une bibliothèque de bassins versants prédéfinis. Par défaut None.
- `from_dem` (list, optionnel) : Liste contenant le chemin du MNT et la taille des cellules [chemin, taille_cellule]. Par défaut None.
- `from_shp` (list, optionnel) : Liste contenant le chemin d'un shapefile et la taille du tampon [chemin, taille_tampon]. Par défaut None.
- `from_xyv` (list, optionnel) : Liste des coordonnées de l'exutoire et des paramètres de snap [x, y, distance_snap, taille_tampon, crs]. Par défaut None.
- `reg_fold` (str, optionnel) : Chemin vers un dossier contenant des résultats régionaux précalculés. Par défaut None.
- `bottom_path` (str, optionnel) : Chemin vers un raster représentant l'élévation du fond de l'aquifère. Par défaut None.
- `save_object` (bool, optionnel) : Si True, l'objet bassin versant créé est sauvegardé sur disque. Par défaut True.

**Variables d'instance:**
- `self.dem_path` (str) : Stocke le chemin vers le MNT initial.
- `self.out_path` (str) : Stocke le chemin de sortie pour les résultats.
- `self.load` (bool) : Indique si un objet existant doit être chargé.
- `self.watershed_name` (str) : Nom du bassin versant.
- `self.from_lib` (str) : Chemin vers la bibliothèque de bassins versants.
- `self.from_dem` (list) : Informations sur le MNT à utiliser.
- `self.from_shp` (list) : Informations sur le shapefile à utiliser.
- `self.from_xyv` (list) : Coordonnées de l'exutoire et paramètres associés.
- `self.reg_fold` (str) : Dossier contenant des résultats régionaux.
- `self.bottom_path` (str) : Chemin vers le raster du fond de l'aquifère.
- `self.bin_path` (str) : Chemin vers les exécutables externes (mf6, mfnwt, mp6, mp7) nécessaires aux simulations.

**Dossiers de travail générés:**
- `self.watershed_folder` (str) : Dossier principal du bassin versant (out_path/watershed_name).
- `self.stable_folder` (str) : Dossier pour les résultats stables (watershed_folder/results_stable).
- `self.simulations_folder` (str) : Dossier pour les résultats de simulations (watershed_folder/results_simulations).
- `self.add_data_folder` (str) : Dossier pour les données additionnelles (stable_folder/add_data).
- `self.figure_folder` (str) : Dossier pour les figures générées (stable_folder/_figures).

**Attributs importants:**
- `self.elt_def` (list) : Liste contenant les noms des éléments/modules définis dans l'objet bassin versant.

Le constructeur affiche d'abord le logo d'HydroModPy, puis initialise les chemins et dossiers mentionnés ci-dessus. Ensuite, selon la valeur de `load`, il essaie de charger un objet existant (`__load_object()`) ou en crée un nouveau (`__init_object()` suivi de `__create_object()`). Si `save_object` est True, il sauvegarde l'objet en utilisant `save_object()`.

#### Méthodes privées

##### `__load_object()`
**Description:** Méthode privée qui tente de charger un objet bassin versant sauvegardé précédemment.

**Retour:** (bool) True si l'objet a été chargé avec succès, False sinon.

**Fonctionnement:**
1. Vérifie l'existence du fichier 'watershed_object' dans le dossier du bassin versant.
2. Si le fichier existe, le charge avec pickle et vérifie que l'attribut 'geographic' est présent (obligatoire).
3. Recherche et importe tous les autres modules qui pourraient avoir été sauvegardés (subbasin, hydraulic, geology, etc.).
4. Pour chaque module chargé, l'ajoute à la liste `self.elt_def`.

##### `__init_object()`
**Description:** Méthode privée qui initialise les conditions pour générer un bassin versant.

**Fonctionnement:**
Cette méthode définit les paramètres de base en fonction de la source des données:
- Si `from_lib` est fourni, extrait les informations du bassin versant de la bibliothèque CSV.
- Si `from_dem` est fourni, utilise le MNT spécifié avec la résolution indiquée.
- Si `from_shp` est fourni, utilise le shapefile avec le tampon indiqué.
- Si `from_xyv` est fourni, utilise les coordonnées de l'exutoire avec les paramètres de snap.

Pour chaque source, initialise les variables appropriées:
- `self.cell_size`: Taille des cellules (résolution du MNT).
- `self.x_outlet`, `self.y_outlet`: Coordonnées de l'exutoire.
- `self.snap_dist`: Distance maximale pour snapper l'exutoire au réseau.
- `self.buff_percent`: Pourcentage de tampon pour le bassin versant.
- `self.crs_proj`: Système de coordonnées de référence.

##### `__create_object()`
**Description:** Méthode privée qui crée l'objet géographique du bassin versant.

**Fonctionnement:**
1. Initialise l'attribut `self.geographic` en appelant la classe `geographic.Geographic` avec les paramètres définis précédemment.
2. Ajoute 'geographic' à la liste `self.elt_def`.

Ce processus établit la structure spatiale fondamentale du bassin versant sur laquelle tous les autres modules s'appuieront.

#### Méthodes publiques de gestion d'objets

##### `save_object()`
**Description:** Sauvegarde l'objet bassin versant actuel sur disque.

**Fonctionnement:**
1. Si un fichier 'watershed_object' existe déjà, le supprime.
2. Crée un nouveau fichier 'watershed_object' et y sauvegarde l'instance actuelle avec pickle.

Cette méthode permet de sauvegarder l'état complet du bassin versant pour le charger ultérieurement sans avoir à recalculer toutes les données.

##### `display_object(dtype='watershed_dem')`
**Paramètres:**
- `dtype` (str, optionnel): Type de visualisation à générer. Options: 
  - 'watershed_dem': Affiche l'élévation du bassin versant (défaut).
  - 'watershed_geology': Affiche la géologie du bassin versant.
  - 'watershed_zones': Affiche les zones hydrauliques du bassin versant.

**Fonctionnement:**
Appelle la fonction appropriée du module `visualization_watershed` en fonction du type demandé pour générer et afficher une visualisation du bassin versant.

#### Méthodes d'ajout de données (`add_*`)

Les méthodes `add_*` permettent d'intégrer différents types de données et modules au bassin versant. Chaque méthode suit un schéma similaire:
1. Initialise le module approprié avec les paramètres pertinents.
2. Ajoute le nom du module à la liste `self.elt_def`.
3. Sauvegarde l'objet bassin versant mis à jour.

##### `add_climatic()`
Cette méthode sans paramètre ajoute des données climatiques au bassin versant. Elle initialise l'attribut `self.climatic` avec une instance de `climatic.Climatic` en fournissant uniquement le chemin de sortie. Les données climatiques sont essentielles pour modéliser les processus hydrologiques comme la recharge des nappes et le ruissellement. Après initialisation, la méthode ajoute 'climatic' à la liste `self.elt_def` et sauvegarde l'objet bassin versant mis à jour.

##### `add_driasclimat(driasclimat_path, list_models='all', list_vars='all')`
Cette méthode ajoute des données de projections climatiques Drias (source: drias-climat.fr) au bassin versant. Elle prend comme paramètre principal `driasclimat_path` (str) qui spécifie le chemin vers les données climatiques Drias. Les paramètres optionnels `list_models` et `list_vars` permettent respectivement de sélectionner les modèles climatiques et les variables d'intérêt, avec 'all' comme valeur par défaut pour inclure toutes les options disponibles. La méthode initialise `self.driasclimat` avec les données spécifiées, l'ajoute à `self.elt_def`, puis la stocke comme attribut de l'objet.

##### `add_driaseau(driaseau_path, list_models='all', list_vars='all')`
Cette méthode ajoute des données hydrologiques Drias Eau (source: drias-eau.fr) au bassin versant. Similaire à `add_driasclimat`, elle prend en paramètre principal `driaseau_path` (str) qui indique l'emplacement des données Drias Eau. Les paramètres optionnels `list_models` et `list_vars` fonctionnent de la même manière, permettant de filtrer les modèles et variables selon les besoins. Ces données sont particulièrement utiles pour étudier les projections futures des ressources en eau face au changement climatique.

##### `add_geology(geology_path, types_obs='GEO1M.shp', fields_obs='CODE_LEG')`
Cette méthode ajoute des données géologiques au bassin versant, généralement à partir des cartes géologiques du BRGM. Le paramètre principal `geology_path` (str) spécifie le chemin vers les données géologiques. Les paramètres optionnels `types_obs` (par défaut 'GEO1M.shp') et `fields_obs` (par défaut 'CODE_LEG') indiquent respectivement le nom du shapefile géologique et le champ contenant les codes géologiques. La méthode initialise `self.geology` avec ces données, l'ajoute à la liste des éléments définis, puis sauvegarde l'objet. Les données géologiques sont cruciales pour comprendre les propriétés des aquifères et leur comportement.

##### `add_hydraulic()`
Cette méthode sans paramètre ajoute des propriétés hydrauliques au modèle. Elle initialise l'attribut `self.hydraulic` en utilisant les dimensions du bassin versant définies dans `self.geographic`. Cet attribut contient les paramètres hydrauliques essentiels pour la modélisation des écoulements souterrains, tels que la conductivité hydraulique, le coefficient d'emmagasinement et les propriétés de drainage. Ces paramètres sont fondamentaux pour la simulation des flux d'eau souterrains dans Modflow.

##### `add_hydrography(hydrography_path, types_obs=['streams'], fields_obs=['FID'])`
Cette méthode ajoute des données sur le réseau hydrographique (cours d'eau) au bassin versant. Le paramètre principal `hydrography_path` (str) indique le chemin vers les données hydrographiques. Les paramètres optionnels `types_obs` (liste des noms de shapefiles, par défaut ['streams']) et `fields_obs` (liste des noms de champs, par défaut ['FID']) permettent de spécifier les fichiers et attributs à utiliser. La méthode initialise `self.hydrography` avec ces données et les intègre au modèle. Le réseau hydrographique est crucial pour comprendre les interactions entre eaux de surface et eaux souterraines.

##### `add_hydrometry(hydrometry_path, file_name)`
Cette méthode ajoute des données de débit mesurées aux stations hydrométriques. Elle prend deux paramètres obligatoires: `hydrometry_path` (str) qui spécifie le chemin vers les données hydrométriques, et `file_name` (str) qui indique le nom du fichier contenant ces données. La méthode initialise `self.hydrometry` avec ces informations et les associe aux données géographiques du bassin. Ces mesures permettent de calibrer et valider le modèle hydrologique en comparant les débits simulés aux débits observés.

##### `add_intermittency(intermittency_path, file_name)`
Cette méthode ajoute des données sur l'intermittence des cours d'eau (périodes d'assèchement). Comme pour `add_hydrometry`, elle requiert deux paramètres: `intermittency_path` (str) pour le chemin vers les données d'intermittence, et `file_name` (str) pour le nom du fichier spécifique. La méthode initialise `self.intermittency` avec ces données et les relie à la géographie du bassin. L'intermittence est particulièrement importante pour comprendre la dynamique des cours d'eau temporaires, fréquents dans certaines régions.

##### `add_oceanic(oceanic_path)`
Cette méthode ajoute des données océaniques au modèle, ce qui est particulièrement utile pour les bassins versants côtiers. Elle prend en paramètre `oceanic_path` (str) qui indique le chemin vers les données océaniques/marines. La méthode crée d'abord une instance vide de la classe `oceanic.Oceanic`, puis appelle sa méthode `extract_data` pour charger les données en fonction de la géographie du bassin. Les conditions marines peuvent influencer significativement les nappes côtières, notamment via les intrusions salines.

##### `add_piezometry()`
Cette méthode sans paramètre ajoute des données piézométriques au bassin versant. Elle initialise l'attribut `self.piezometry` en utilisant le chemin de sortie et les données géographiques du bassin. Les données piézométriques représentent les niveaux d'eau mesurés dans les puits et forages, et sont essentielles pour calibrer le modèle hydrogéologique en comparant les niveaux d'eau simulés aux observations réelles.

##### `add_settings()`
Cette méthode sans paramètre ajoute des paramètres spécifiques de configuration au modèle. Elle initialise simplement l'attribut `self.settings` avec une nouvelle instance de `settings.Settings`, sans aucun paramètre. Ces paramètres seront utilisés ultérieurement pour configurer les simulations Modflow et Modpath. Ils peuvent inclure des informations sur le type de simulation, les conditions aux limites, et divers paramètres de modélisation.

##### `add_safransurfex(safransurfex_path)`
Cette méthode ajoute des données de réanalyse climatique historique SAFRAN-SURFEX au modèle. Elle prend en paramètre `safransurfex_path` (str) qui indique le chemin vers ces données. La méthode initialise `self.safransurfex` avec ces données en les associant au shapefile du bassin versant, puis appelle une fonction `Merge` pour consolider les résultats. Les données SAFRAN-SURFEX fournissent des informations climatiques détaillées (précipitations, température, évapotranspiration) sur de longues périodes historiques, essentielles pour alimenter les modèles hydrologiques.

##### `add_lakeres()`
Cette méthode sans paramètre initialise un objet de gestion des lacs et réservoirs. Elle crée une instance de `lakeres.Lakeres` en utilisant le dossier stable du bassin versant comme paramètre, et l'assigne à `self.lakeres`. L'objet créé est initialement vide et sera configuré ultérieurement avec des informations spécifiques sur les lacs et réservoirs. Cet objet permet de modéliser l'influence de ces masses d'eau sur l'hydrologie du bassin versant, notamment les échanges avec les eaux souterraines et les modifications du régime hydrologique.

##### `add_streamflow_seepage()`
Cette méthode configure l'écoulement de suintement via le package SFR (Streamflow-Routing) au lieu du package DRN (Drain). Elle accepte de nombreux paramètres optionnels pour définir précisément les caractéristiques de cette percolation: `area` pour spécifier la zone d'application (rivière, bassin versant ou domaine entier), `mainstream_threshold` pour identifier le cours d'eau principal, `icalc` pour le mode de calcul, ainsi que divers paramètres hydrauliques comme l'épaisseur du lit (`thickm`), la profondeur (`depth`), la conductivité (`hcond`), etc. Cette méthode est particulièrement utile pour modéliser plus précisément les interactions entre les eaux de surface et les eaux souterraines, notamment les zones de résurgence et d'infiltration le long des cours d'eau.

##### `add_subbasin(add_path=None, sub_snap_dist=200)`
Cette méthode ajoute la fonctionnalité de sous-bassins versants au modèle, particulièrement utile pour les grands bassins. Elle prend deux paramètres optionnels: `add_path` (chemin vers des données additionnelles, par défaut None) et `sub_snap_dist` (distance maximale de snap pour les exutoires des sous-bassins, par défaut 200 unités). La méthode vérifie d'abord l'existence des attributs `hydrometry` et `intermittency`, les initialisant à None s'ils n'existent pas, puis crée l'objet `subbasin` en utilisant ces informations et les paramètres spécifiés. Les sous-bassins permettent une analyse plus détaillée des différentes zones du bassin versant et peuvent améliorer la précision du modèle global.

#### Méthodes de modélisation Modflow

##### `preprocessing_modflow(for_calib=False)`
Cette méthode prépare le modèle hydrogéologique Modflow pour la simulation. Le paramètre optionnel `for_calib` (bool, par défaut False) détermine si les résultats seront stockés dans le dossier de calibration plutôt que dans le dossier de simulations standard. La méthode initialise un objet `modflow.Modflow` avec tous les paramètres nécessaires, regroupés en plusieurs catégories: paramètres de workflow (dossier, nom du modèle), paramètres du modèle (configuration, limites), paramètres climatiques (recharge, ruissellement), paramètres hydrauliques (conductivité, emmagasinement), et informations sur les lacs/réservoirs et écoulements. Elle appelle ensuite la méthode `pre_processing()` de cet objet pour préparer les fichiers d'entrée de la simulation. La méthode retourne l'objet modèle Modflow initialisé pour utilisation ultérieure.

##### `processing_modflow(model_modflow, write_model=True, run_model=False)`
Cette méthode exécute la simulation Modflow préparée précédemment. Elle prend en paramètres l'objet `model_modflow` retourné par `preprocessing_modflow()`, ainsi que deux booléens optionnels: `write_model` (par défaut True) qui indique s'il faut écrire les fichiers d'entrée avant la simulation, et `run_model` (par défaut False) qui détermine si la simulation doit être effectivement exécutée. La méthode appelle simplement la fonction `processing()` de l'objet modèle et retourne un booléen indiquant si la simulation s'est exécutée avec succès. Cette séparation entre préparation et exécution permet de modifier les paramètres entre les deux étapes si nécessaire.

##### `postprocessing_modflow(model_modflow, ...)`
Cette méthode analyse et traite les résultats de la simulation Modflow. Elle prend en paramètre principal l'objet `model_modflow` après simulation, ainsi que de nombreux paramètres booléens optionnels qui permettent de sélectionner les types de sorties à générer: élévation de la nappe (`watertable_elevation`), profondeur de la nappe (`watertable_depth`), zones de suintement (`seepage_areas`), flux de drainage (`outflow_drain`), flux souterrains (`groundwater_flux`), stockage souterrain (`groundwater_storage`), flux d'accumulation (`accumulation_flux`), fuites des lacs (`lake_leakage`), indices de persistance (`persistency_index`), et différentes métriques d'intermittence (`intermittency_monthly`, `intermittency_weekly`, `intermittency_daily`). Un paramètre supplémentaire `export_all_tif` permet d'exporter des fichiers TIF pour tous les pas de temps simulés. La méthode appelle la fonction `post_processing()` de l'objet modèle avec ces paramètres pour générer les analyses demandées.

#### Méthodes de modélisation Modpath

##### `preprocessing_modpath(model_modflow, for_calib=False)`
Cette méthode prépare un modèle de suivi des particules (Modpath) basé sur les résultats de la simulation Modflow. Elle prend en paramètres l'objet `model_modflow` simulé et le booléen optionnel `for_calib` qui, comme pour Modflow, détermine le dossier de stockage des résultats. La méthode initialise un objet `modpath.Modpath` en utilisant les données géographiques du bassin et les résultats de Modflow, ainsi que divers paramètres de configuration spécifiés dans `settings`: zone de suivi des particules, division des cellules, direction de suivi, etc. Elle appelle ensuite la méthode `pre_processing()` de cet objet et le retourne pour utilisation ultérieure. Modpath permet de suivre le trajet de particules virtuelles dans l'écoulement souterrain, ce qui est utile pour étudier les temps de transit et les chemins d'écoulement.

##### `processing_modpath(model_modpath, write_model=True, run_model=False)`
Cette méthode exécute la simulation de suivi des particules avec Modpath. Similaire à `processing_modflow()`, elle prend en paramètres l'objet `model_modpath` préparé précédemment, ainsi que les booléens `write_model` et `run_model` qui contrôlent respectivement l'écriture des fichiers d'entrée et l'exécution de la simulation. La méthode appelle la fonction `processing()` de l'objet Modpath et retourne un booléen indiquant le succès de l'opération. Cette étape calcule effectivement les trajectoires des particules dans l'écoulement souterrain simulé par Modflow.

##### `postprocessing_modpath(model_modpath, ...)`
Cette méthode traite les résultats du suivi des particules Modpath. Elle prend en paramètre principal l'objet `model_modpath` après simulation, ainsi que plusieurs paramètres booléens qui contrôlent les sorties à générer: points finaux des particules (`ending_point`), points initiaux (`starting_point`), chemins complets (`pathlines_shp`), et positions intermédiaires (`particles_shp`). Un paramètre supplémentaire `random_id` permet de sélectionner aléatoirement un certain nombre de particules pour alléger les résultats. La méthode appelle la fonction `post_processing()` de l'objet Modpath pour générer ces sorties, qui sont typiquement des fichiers shapefile pour utilisation dans un SIG.

##### `filtprocessing_modpath(model_modpath, ...)`
Cette méthode filtre et analyse plus finement les résultats du suivi des particules. Elle prend en paramètre l'objet `model_modpath` ainsi que plusieurs paramètres booléens définissant les filtres à appliquer: normalisation des flux (`norm_flux`), filtrage temporel (`filt_time` pour convertir les jours en années et éliminer les particules à temps nul), filtrage des zones de suintement (`filt_seep` pour ne conserver que les particules finissant dans la première couche), filtrage des entrées/sorties (`filt_inout` pour éliminer les particules qui entrent et sortent dans la même cellule), et calcul de la distribution des temps de résidence (`calc_rtd`). Le paramètre `random_id` permet, comme précédemment, de sélectionner aléatoirement un nombre limité de particules. La méthode appelle la fonction `filt_processing()` de l'objet Modpath pour appliquer ces traitements, qui sont particulièrement utiles pour analyser les temps de transit et la vulnérabilité des aquifères.

#### Méthodes de post-traitement des résultats

##### `postprocessing_timeseries(model_modflow, model_modpath, ...)`
Cette méthode extrait et formate les séries temporelles des résultats de simulation Modflow et Modpath. Elle prend en paramètres les objets `model_modflow` et `model_modpath` simulés, ainsi que plusieurs paramètres de configuration: format datetime pour les indices (`datetime_format`), extraction des résultats par sous-bassin (`subbasin_results`), et calcul de l'intermittence à différentes échelles temporelles (`intermittency_monthly`, `intermittency_weekly`, `intermittency_daily`). La méthode vérifie d'abord que `model_modflow` n'est pas None, puis initialise un objet `timeseries.Timeseries` avec ces paramètres et les données géographiques et de réservoirs du bassin. Elle retourne cet objet, dont l'attribut `mfdata` contient les résultats au format CSV. Ces séries temporelles permettent d'analyser l'évolution des variables hydrologiques (débits, niveaux d'eau) au cours du temps, à l'échelle du bassin ou des sous-bassins.

##### `postprocessing_netcdf(model_modflow, datetime_format=True)`
Cette méthode convertit les résultats de simulation Modflow au format NetCDF, un format standard pour les données scientifiques multidimensionnelles. Elle prend en paramètres l'objet `model_modflow` simulé et le booléen optionnel `datetime_format` qui détermine si les indices temporels doivent utiliser le format datetime. La méthode vérifie que `model_modflow` n'est pas None, puis initialise un objet `netcdf.Netcdf` avec ces paramètres et les données géographiques du bassin. Elle retourne cet objet, qui contient les résultats formatés. Le format NetCDF facilite l'analyse et la visualisation des résultats avec d'autres outils scientifiques comme Python (xarray), R, ou des logiciels spécialisés comme Panoply ou ParaView.

### Watershed

#### Climatic.py

#### Driasclimat.py

#### Driaseau.py

#### Geographic.py

#### Geology.py

#### Hydraulic.py

#### Hydrography.py

#### Hydrometry.py

#### Intermittency.py

#### Lakeres.py

##### Libraries

L'accumulation des eaux de ruissellement peut également être calculée avec `pyproj`. Cela devrait être plus rapide car il n'est pas nécessaire d'écrire chaque fois dans un fichier. Mais il faut d'abord résoudre l'incompatibilité entre `pyproj` et d'autres modules.

##### \_\_init\_\_

La méthode `__init__` de la classe `Lakeres` est appelée lors de l'instanciation de l'objet de gestion des lacs/réservoirs. Elle requiert un argument, `stable_folder`, qui correspond au chemin vers le dossier où seront stockés les résultats stables liés à la simulation.

Lors de son exécution, cette méthode effectue les opérations suivantes :

- Construit le chemin complet `data_folder` pour le stockage des données spécifiques aux lacs/réservoirs en joignant `stable_folder` avec le sous-dossier "lakeres"
- Initialise plusieurs variables d'instance servant à stocker la configuration et les données propres à chaque lac/réservoir. Ces variables comprennent :
  - `n_lakeres` (int) : nombre de lacs/réservoirs définis
  - `indexes` (list) : liste des identifiants (`lake_id`)
  - `maskmx_by_lake` (dict) : dictionnaire associant chaque `lake_id` à son Mask
  - `mask_crs_by_lake` (dict) : dictionnaire associant chaque réservoir à sa projection
  - `bathymetry_by_lake` (dict) : dictionnaire stockant le chemin vers le raster de bathymétrie ou une option de calcul (par exemple, cuboid) pour chaque lac
  - `bathy_crs_by_lake` (dict) : dictionnaire des CRS associés aux bathymétrie
  - `ssmx_by_lake` (dict) : dictionnaire des niveaux d'eau maximum pour chaque lac
  - `volmx_by_lake` (dict) : dictionnaire des volumes maximum
  - `bdlknc_by_lake` (dict) : dictionnaire de la fuite de fond pour chaque lac
- Divers dictionnaires supplémentaires pour les débits et autres flux (`prcplk_by_lake`, `evaplk_by_lake`, `rnf_by_lake`, `rnf_acc_by_lake`, `wthdrw_by_lake`, `rtrn_by_lake`) ainsi que pour le niveau d'eau initial et le lien entre l'identifiant numérique et le `lake_id` (`lake_by_num_id`)
- `outlet_by_lake` et `ij_outlet_by_lake` qui permettent la définition de l'issue du lac

Le fonctionnement de cette méthode se veut déterministe : elle prépare l'environnement pour la manipulation ultérieure de définitions de lacs/réservoirs en instanciant les structures de données requises et en s'assurant que le chemin de données est correctement créé. La structure a été pensée sous forme de dictionnaire avec un seul objet réservoir pouvant contenir une infinité de lacs/réservoirs.

##### New_lakeres

La méthode `new_lakeres` initialise et configure un nouveau lac ou réservoir en utilisant divers paramètres géométriques et hydrologiques. Elle vérifie d'abord si l'identifiant du lac existe déjà. Si ce n'est pas le cas, elle attribue un nouvel identifiant. Ensuite, elle stocke les informations géométriques et les paramètres hydrologiques du lac ou réservoir dans des dictionnaires spécifiques. Enfin, elle met à jour les attributs du modèle pour inclure le nouveau lac ou réservoir.

Comme pour la classe `Climatic`, `Lakeres` fonctionne un peu de la même manière. Les variables décrites ci-dessous sont pour la plupart créées avec des valeurs par défaut `None` ou des valeurs données, et ensuite une série de fonctions sera appelée pour ajouter/mettre à jour une à une chaque variable.

- `maskmx` (str) : Chemin vers le fichier de masque (shapefile ou raster). Fonctionne avec les fichiers NetCDF?
- `lake_id` (optionnel) : La valeur par défaut est None
- `mask_crs` (TYPE, optionnel) : La valeur par défaut est None
- `bathymetry_raster` (str, optionnel) : La valeur par défaut est None
- `bathy_crs` (TYPE, optionnel) : La valeur par défaut est None
- `ssmx` (float, optionnel) : Niveau maximal du lac/réservoir. La valeur par défaut est None
- `volmx` (float, optionnel) : Volume maximal du lac. La valeur par défaut est None
- `bdlknc` (float, optionnel) : La valeur de fuite de fond du lac qui est par défaut à 86400 m/d (= 1 m/s), valeur issue de la bibliographie à réfléchir
- `prcplk` (float | array | file_path(str), optionnel) : Entrée pour les précipitations sur le lac/réservoir. La valeur par défaut est 0 m/d, comme pour les trois paramètres suivants, `prcplk` peut être défini par :
  - float : même valeur pour toutes les périodes
  - pd.DataFrame : avec les temps en index. Les temps choisis doivent également être présents dans watershed.climatic
  - file path : un fichier .csv, une carte .tif ou un fichier .nc espace-temps
- `evaplk` (float | array | file_path(str) | mode(str), optionnel) : Entrée pour l'évaporation du lac/réservoir. La valeur par défaut est 0 m/d, `evaplk` peut également être défini par `from_climatic` : les valeurs sont extraites de watershed.climatic < 0
- `rnf` (float | array | file_path(str) | mode(str), optionnel) : Entrée pour le ruissellement vers le lac/réservoir. La valeur par défaut est 0 m/d, `rnf` peut également être défini par la chaîne indicatrice `from_climatic` : les valeurs sont extraites de watershed.climatic.runoff
- `rnf_acc` (bool, optionnel) : Un indicateur pour préciser si la valeur `rnf` sera :
  - False : utilisée par Modflow telle quelle (valeur positive = taux volumétrique, valeur négative = multiplicateur sans dimension)
  - True : interprétée comme un taux par unité de surface qui sera accumulé pour obtenir un taux volumétrique ajouté au lac. La valeur par défaut est False
- `wthdrw` (float | array | file_path(str), optionnel) : Entrée pour les flux anthropiques sur le lac (prélèvement et remplissage). La valeur par défaut est 0 m/d. `wthdrw` intègre la somme des prélèvements d'eau (valeurs positives) et des ajouts d'eau (valeurs négatives)
- `rtrn` (timeseries, optionnel) : Retour d'écoulement à la (aux) sortie(s) de chaque lac. Cette valeur est injectée dans le réseau de routage du débit des cours d'eau. Elle n'est pas prélevée du lac/réservoir (pour cela, le retour d'écoulement doit également être spécifié dans `wthdrw`)
- `outlet` (str, optionnel) : Chemins vers le fichier de sortie (shapefile, txt avec coordonnées)

##### Update a previous lake/reservoir

##### Remove a lake/reservoir

##### Update geometry and physical properties of the lake/reservoir

##### Update flows in and out of the lake/reservoir

##### Format all attributes into inputs for ModFlow

##### Update DEM files

##### Format outlets

##### Accumulate runoff

##### Display plot

#### Oceanic.py

#### Piezometry.py

#### Safransurfex.py

#### Settings.py

#### Sim2.py

#### Streamflow_seepage.py

#### Subbasin.py

### Modeling

#### Downslope.py

#### Modflow.py

#### Modpath.py

#### Netcdf.py

#### Timeseries.py

### Tools

#### Folder_root.py

#### Toolbox.py

##### Class LogManager

Le `LogManager` est conçu pour configurer et gérer la journalisation de l'application de manière flexible et adaptable.

**Initialisation du LogManager :**

Pour intégrer le LogManager dans un script, il suffit d'insérer les lignes suivantes :

```python
# Initialisation du LogManager en mode développement
log_manager = toolbox.LogManager(
    mode="dev",  # Utilisez mode="verbose" pour afficher les logs INFO et supérieurs, et mode="quiet" pour afficher les logs WARNING et supérieurs
    log_dir=root_dir,  # Spécifiez le répertoire de journalisation
    overwrite=False,  # Utilisez overwrite=True (par défaut) pour écraser les fichiers de log existants
    verbose_libraries=True  # Utilisez verbose_libraries=True pour afficher les logs des bibliothèques (avertissements et supérieurs, généralement masqués)
)
```

**Modes de Fonctionnement :**

- Mode dev :
  - Console : Affiche tous les messages de niveau DEBUG et supérieur (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Format : `[%(levelname)s] [%(name)s] [%(module)s:%(lineno)d] %(message)s`
- Mode verbose :
  - Console : Affiche les messages de niveau INFO et supérieur (INFO, WARNING, ERROR, CRITICAL)
  - Format : `[%(levelname)s] %(message)s`
- Mode quiet :
  - Console : Affiche les messages de niveau WARNING et supérieur (WARNING, ERROR, CRITICAL)
  - Format : `[%(levelname)s] %(message)s`

**Gestion des Bibliothèques Externes :**

Par défaut, le LogManager supprime les logs provenant de certaines bibliothèques externes pour éviter un terminal ou kernel surchargé. Voici la liste des bibliothèques dont les logs sont réduits au niveau CRITICAL :

```python
libraries_to_silence = [
    "fiona",
    "rasterio",
    "urllib3",
    "geopy",
    "matplotlib",
    "PIL",
]
```

Vous pouvez activer les logs des bibliothèques externes en définissant `verbose_libraries=True` lors de l'initialisation. Dans ce cas, les messages de niveau WARNING et supérieur seront affichés.

**Sauvegarde des Logs :**

- Fichier de log : Un fichier `dev.log` est automatiquement sauvegardé dans le dossier logs à la racine du projet
- Format : Les logs sont enregistrés dans le format dev pour inclure la provenance des messages (fichier et numéro de ligne)
- Écrasement : Par défaut, le fichier est écrasé à chaque nouvelle exécution. Pour ajouter les logs successifs, utilisez `overwrite=False`

**Logique des Niveaux de Logging :**

Les scripts situés dans `src/` ont été mis à jour pour respecter la logique suivante :

- `logging.debug` : Points d'étape détaillés (peut générer beaucoup de lignes, notamment dans les boucles)
- `logging.info` : Messages classiques équivalents aux print
- `logging.warning` : Avertissements nécessitant une attention particulière de l'utilisateur ou signalant une erreur mineure sans arrêt du code
- `logging.error` : Erreurs mettant fin à l'exécution du script
- `logging.critical` : Actuellement non utilisé

**Exceptions :**

Certains `print` sont conservés pour des raisons spécifiques :
- Affichage du logo d'HydroModPy
- Décompte des étapes (ex. "Étape 1/51") afin de ne pas surcharger le terminal

Actuellement, les `print` dans les fichiers d'exécution, comme les exemples, n'ont pas été mis à jour. Il reste à discuter si nous les conservons en tant que `print` ou si nous les remplaçons par des logs de niveau `logging.info()`.

**Changement de Syntaxe pour le Logging :**

La syntaxe utilisée pour les messages de logs a été modifiée, car le module logging ne permet pas d'insérer directement plusieurs variables dans une chaîne de caractères, comme c'est possible avec un simple print (par exemple : `print("Exemple" + A + B)` ou `print("Exemple", A, B)`). Pour formater les messages dans le contexte de logging, deux approches sont possibles :

- Utilisation des f-strings :
  - `logging.debug(f"Étape : {i} / {len(x)}")`
- Utilisation des Spécificateurs de Format, associés aux variables dans l'ordre :
  - `logging.debug("Étape : %s / %s", i, len(x))`
  - Liste des Principaux Spécificateurs Utiles :
    - `%s` : Pour les chaînes de caractères
    - `%d` : Pour les entiers
    - `%f` : Pour les nombres à virgule flottante

### Display

#### Export_vtuvtk.py

#### Visualization_results.py

#### Visualization_watershed.py

## Générale

###  DeprecationWarning

Les DeprecationWarning sont affichés dans le kernel lorsque des méthodes ou définitions d'une bibliothèque Python sont appelées et que ces dernières vont être supprimées dans une prochaine version. HydroModPy étant actuellement basé sur une version 3.8.10 de Python (version actuelle 3.13), beaucoup de DeprecationWarnings apparaissent. Pour éviter cela, les quatre lignes ci-dessous sont à inclure en début de script.

Supprimer l'affichage de ces messages ne pose aucun problème de fonctionnement à l'exécution du code.

```python
# Filtrer les avertissements (avant les imports)
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import pkg_resources  # A placer après DeprecationWarning car elle même obsolète...
warnings.filterwarnings('ignore', message='.*pkg_resources.*')
warnings.filterwarnings('ignore', message='.*declare_namespace.*')
```

## Idées

- Automatiser la sélection entre le chargement `True` ou `False` dans le script pour ne pas tout relancer. Par défaut mettre `True` si le nom de dossier existe déjà sauf si un paramètre force le contraire. Dans le cas où le dossier n'existe pas alors ne pas recharger.