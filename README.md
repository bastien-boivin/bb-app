# Notes pour le déploiement sur Streamlit Cloud

## Configuration de redirection

J'ai simplifié `main.py` pour qu'il redirige automatiquement vers la page Home. Cela permet de démarrer directement sur la page d'accueil avec le téléchargement des fichiers.

## Structure des dossiers pour Streamlit Cloud

Pour déployer sur Streamlit Cloud, assurez-vous que la structure de dossiers est la suivante :

```
répertoire_projet/
│
├── main.py                    # Redirection vers Home
│
├── pages/                     # Système natif de multi-pages Streamlit
│   ├── 1_🏡_Home.py           # Page d'accueil simplifiée
│   └── 2_📊_Chroniques.py     # Page de visualisation avec tous les paramètres
│
├── visualisation/             # Votre code d'origine pour les graphiques
│   └── plotly_chroniques.py   # Classe TimeSeriesPlot_Plotly sans modification
│
├── assets/                    # Ressources statiques
│   └── images/
│       └── Logo_Universite_Rennes.png
│
└── requirements.txt           # Dépendances de l'application
```

## Installation sur Streamlit Cloud

1. Créez un dépôt GitHub avec cette structure
2. Connectez-vous à [Streamlit Cloud](https://share.streamlit.io/)
3. Créez une nouvelle application en pointant vers votre dépôt GitHub
4. Sélectionnez `main.py` comme point d'entrée

## Modification de requirements.txt

Assurez-vous que requirements.txt contient toutes les dépendances nécessaires :

```
streamlit>=1.31.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
matplotlib>=3.7.0
```

## Gestion des données

Maintenant que l'application est configurée pour le web :
- Les utilisateurs peuvent télécharger leur propre fichier CSV depuis leur ordinateur
- Les paramètres de configuration sont tous dans la sidebar de la page Chroniques
- Aucune dépendance aux fichiers de configuration JSON ou aux chemins locaux

Cette approche facilitera grandement le déploiement et l'utilisation par d'autres personnes.