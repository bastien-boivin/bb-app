import streamlit as st
from st_pages import Page, show_pages, add_page_title

# Configuration de la page
st.set_page_config(page_title="Reservoir Analysis", page_icon="💧", layout="wide")

# Ajout du titre de la page automatiquement
add_page_title()

# Définition de la structure de navigation
show_pages(
    [
        Page("🏡_Home.py", "Accueil", "🏠"),
        Page("pages/1_📤_Chargement.py", "Chargement des données", "📤"),
        Page("pages/2_📊_Chroniques.py", "Visualisation", "📊"),
    ]
)

# Contenu de la page d'accueil
st.markdown("## 💧 Application d'analyse des réservoirs d'eau")

st.markdown("""
Cette application vous permet d'analyser et de visualiser les données de volume d'eau des réservoirs.

### Fonctionnalités principales :
- **Chargement des données** : téléchargez vos fichiers CSV contenant les chroniques de données
- **Visualisation interactive** : explorez vos données avec différentes visualisations
  - Séries temporelles chronologiques
  - Cycles annuels
  - Analyse statistique avec année de référence

### Pour commencer :
1. Accédez à la page **Chargement des données** pour télécharger votre fichier CSV
2. Ensuite, rendez-vous sur la page **Visualisation** pour explorer vos données

Développé par le Département des Sciences Environnementales, Université de Rennes.
""")

# Affichage d'un exemple de visualisation
st.image("https://plotly.com/~empet/15073.png", caption="Exemple de visualisation de séries temporelles", use_column_width=True)

# Masquer le menu et le pied de page Streamlit
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)