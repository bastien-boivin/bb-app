import streamlit as st

# Configuration de la page - doit être la première commande Streamlit
st.set_page_config(page_title="Reservoir Analysis", page_icon="💧", layout="wide")

# CSS pour masquer les éléments indésirables
hide_streamlit_style = """
<style>
    /* Cache le menu hamburger */
    #MainMenu {visibility: hidden;}
    
    /* Masque le pied de page */
    footer {visibility: hidden;}
    
    /* Masque le bouton de déploiement */
    .stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Redirection vers la page d'accueil
st.switch_page("pages/1_🏡_Home.py")