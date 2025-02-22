import os
import sys
import logging
import streamlit as st

from os.path import abspath, dirname
root_dir = dirname(dirname((abspath(__file__))))
sys.path.append(root_dir)

cwd = os.getcwd()
if cwd != root_dir:
    os.chdir(root_dir)

#% Modules
import src
import importlib
importlib.reload(src)
from src.toolbox import LogManager

log_manager = LogManager(mode="dev", # Utiliser mode="verbose" pour afficher les logs INFO et supérieur et mode="quiet" pour afficher les logs WARNING et supérieur
                         # log_dir="", # Utiliser log_dir pour spécifier le répertoire des logs
                         # overwrite=False # Utiliser overwrite=True pour écraser les fichiers de logs existants
                         # verbose_libraries=True # Utiliser verbose_libraries=True pour afficher les logs des bibliothèques (waring et supérieur)
                         )

st.set_page_config(
    page_title="Accueil",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Navigation")
st.title("Accueil")
st.write("Contenu de la page d'accueil")