import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Reservoir Analysis", page_icon="💧", layout="wide")

# Titre de la page d'accueil
st.title("📊 Reservoir Water Volume Analysis")
st.markdown("---")

# Contenu de la page d'accueil
st.markdown("""
## 💧 Application d'analyse des réservoirs d'eau

Cette application vous permet d'analyser et de visualiser les données de volume d'eau des réservoirs.

### Fonctionnalités principales :
- **Chargement des données** : téléchargez vos fichiers CSV contenant les chroniques de données
- **Visualisation interactive** : explorez vos données avec différentes visualisations
  - Séries temporelles chronologiques
  - Cycles annuels
  - Analyse statistique avec année de référence

### Pour commencer :
1. Accédez à la page **Chargement des données** dans la barre latérale pour télécharger votre fichier CSV
2. Ensuite, rendez-vous sur la page **Visualisation** pour explorer vos données

Développé par le Département des Sciences Environnementales, Université de Rennes.
""")