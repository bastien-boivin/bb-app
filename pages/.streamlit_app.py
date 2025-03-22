import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Reservoir Analysis", page_icon="💧", layout="wide")

# Solution CSS améliorée pour masquer "main" de la sidebar
st.markdown("""
<style>
    /* Cache l'élément "main" de la barre latérale */
    section[data-testid="stSidebar"] ul {
        padding-bottom: 0;
    }
    
    section[data-testid="stSidebar"] ul li:first-child {
        display: none !important;
    }
    
    /* Rend ce fichier (main) invisible également sur les pages déployées */
    div[data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Renomme "Home" pour éviter la confusion */
    section[data-testid="stSidebar"] ul li:nth-child(2) p {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Redirection automatique vers Home
st.switch_page("pages/1_🏡_Home.py")