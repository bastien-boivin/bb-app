import streamlit as st

st.set_page_config(page_title="Analysis chronicles", page_icon="📈", layout="wide")

st.markdown("""
## 💧 Application d'analyse de chroniques

Cette application vous permet d'analyser et de visualiser des données temporelles.

### Fonctionnalités principales :
- **Chargement des données** : téléchargez vos fichiers CSV contenant les chroniques de données
- **Visualisation interactive** : explorez vos données avec différentes visualisations
  - Séries temporelles chronologiques
  - Cycles annuels
  - Analyse statistique avec année de référence

### Pour commencer :
1. Accédez à la page **Chargement des données** dans la barre latérale pour télécharger votre fichier CSV
2. Ensuite, rendez-vous sur la page **Visualisation** pour explorer vos données

""")