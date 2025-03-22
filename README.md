# Reservoir Water Volume Analysis

## Description
Application Streamlit pour l'analyse et la visualisation des données de volume d'eau de réservoirs. Cette version est spécialement conçue pour un déploiement web sur Streamlit Cloud.

## Fonctionnalités

- Upload de fichiers CSV contenant des données de chroniques
- Sélection flexible des colonnes de temps et de données
- Visualisation interactive de chroniques avec Plotly
- Plusieurs modes de visualisation :
  - Séries temporelles historiques
  - Cycle annuel
  - Analyse statistique
- Options de personnalisation :
  - Échelle logarithmique
  - Fenêtre glissante
  - Année de référence
  - Fréquence (journalière, hebdomadaire, mensuelle)
  - Mois de début pour le cycle annuel

## Installation locale

1. Clonez ce dépôt :
```bash
git clone https://github.com/votreusername/reservoir-analysis.git
cd reservoir-analysis
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
streamlit run main.py
```

## Déploiement sur Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://share.streamlit.io/) si ce n'est pas déjà fait
2. Connectez votre compte GitHub
3. Créez un nouveau déploiement en sélectionnant ce dépôt
4. Configurez le point d'entrée sur `main.py`

## Format de données attendu

L'application attend un fichier CSV avec au minimum :
- Une colonne de dates (format flexible)
- Une colonne de valeurs numériques (volumes)

Exemple :
```
time;cheze_vol
01/01/2020;12500000
02/01/2020;12700000
03/01/2020;12900000
```

## Licence

[MIT License](LICENSE)

## Contact

Pour toute question ou suggestion, veuillez contacter bastien.boivin@univ-rennes.fr