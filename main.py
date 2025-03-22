import streamlit as st

# Configuration de base pour l'application
st.set_page_config(page_title="Water Reservoir Analysis", page_icon="💧", layout="wide")

# Logo de l'application
st.image("assets/images/Logo_Universite_Rennes.png", width=300)

# Titre principal
st.title("Analyse des réservoirs d'eau")
st.write("Bienvenue dans l'application d'analyse des réservoirs d'eau.")
st.write("Utilisez la barre latérale pour naviguer entre les différentes pages de l'application.")

# Instructions
st.info("""
Pour commencer :
1. Allez sur la page **Home** pour télécharger vos données et configurer les paramètres
2. Ensuite, rendez-vous sur la page **Chroniques** pour visualiser vos données
""")