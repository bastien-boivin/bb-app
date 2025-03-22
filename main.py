import os
import sys
import logging
import streamlit as st

# Configuration de base pour l'application
st.set_page_config(page_title="Water Reservoir Analysis", page_icon="💧", layout="wide")

# Logo de l'application
st.image("assets/images/Logo_Universite_Rennes.png", width=300)

# Configuration des messages de log
logging.basicConfig(level=logging.INFO)

# Menu de navigation simplifié
pages = {
    "Home": [
        st.Page("pages/1_🏡_Home.py", title="Home"),
    ],
    "Visualization": [
        st.Page("pages/2_📊_Chroniques.py", title="Chroniques"),
    ],
}

pg = st.navigation(pages)
pg.run()