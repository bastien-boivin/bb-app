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
1. Accédez à la page **Chargement des données** pour télécharger votre fichier CSV
2. Ensuite, rendez-vous sur la page **Visualisation** pour explorer vos données

Développé par le Département des Sciences Environnementales, Université de Rennes.
""")

# Affichage d'un exemple de visualisation
st.image("https://plotly.com/~empet/15073.png", caption="Exemple de visualisation de séries temporelles", use_column_width=True)

# Boutons de navigation
st.markdown("### Navigation")
col1, col2 = st.columns(2)

with col1:
    if st.button("📤 Chargement des données", use_container_width=True):
        st.switch_page("pages/1_📤_Chargement.py")

with col2:
    if st.button("📊 Visualisation", use_container_width=True):
        st.switch_page("pages/2_📊_Chroniques.py")

# CSS pour améliorer l'apparence
st.markdown("""
<style>
    /* Amélioration générale */
    h1, h2, h3 {
        color: #4682B4;
    }
    
    /* Personnalisation des boutons */
    .stButton button {
        background-color: #4682B4;
        color: white;
        font-weight: bold;
        border: none;
        padding: 15px;
        border-radius: 5px;
    }
    
    .stButton button:hover {
        background-color: #36648B;
    }
    
    /* Masquer le menu et le footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Bordure autour des sections */
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)