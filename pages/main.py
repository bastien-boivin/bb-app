import os
import sys
import json
import logging
import streamlit as st

from os.path import abspath, dirname
root_dir = dirname(dirname((abspath(__file__))))
sys.path.append(root_dir)

cwd = os.getcwd()
if cwd != root_dir:
    os.chdir(root_dir)
    
# -----------------------------------------------------
# Modules
# -----------------------------------------------------
import src
import importlib
importlib.reload(src)

from src.toolbox import LogManager
# -----------------------------------------------------
# Setup LogManger for all pages in the application
# -----------------------------------------------------
log_manager = LogManager(mode="dev", # Utiliser mode="verbose" pour afficher les logs INFO et supérieur et mode="quiet" pour afficher les logs WARNING et supérieur
                         # log_dir="", # Utiliser log_dir pour spécifier le répertoire des logs
                         # overwrite=False # Utiliser overwrite=True pour écraser les fichiers de logs existants
                         # verbose_libraries=True # Utiliser verbose_libraries=True pour afficher les logs des bibliothèques (waring et supérieur)
                         )

st.logo("assets/images/Logo_Universite_Rennes.png", size="large")

pages = {
    "DashBoard": [
        st.Page("1_🏡_Home.py", title="Home"),
    ],
    "Visualisation": [
        st.Page("2_📊_Chroniques.py", title="Chroniques"),
    ],
    "Tools": [
        st.Page("5_🔧_Setup.py", title="Setup"),
    ],
}

pg = st.navigation(pages)
pg.run()