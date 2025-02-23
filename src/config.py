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

# -----------------------------------------------------
# Modules
# -----------------------------------------------------
import src
import importlib
importlib.reload(src)

from src.path import load_paths, get_selected_profile, set_selected_profile

def initialize_sidebar():
    # Chargement des chemins enregistrés
    paths = load_paths()

    # Sidebar pour la sélection du site d'étude
    st.sidebar.title("Sélection du site d'étude :")

    # Récupérer le profil sélectionné par défaut
    # Enregistré dans le json, streamlit permet de le faire avec state mais plus logique en json
    default_profile = paths.get("selected_profile")

    # Option pour la liste déroulante, récupération des clés (site d'étude)
    profile_options = list(paths["profiles"].keys())

    # Sélection du profil avec une valeur par défaut
    selected_profile = st.sidebar.selectbox(
        "Site d'étude",
        options=profile_options,
        index=profile_options.index(default_profile) if default_profile in profile_options else 0
    )

    if selected_profile:
        set_selected_profile(selected_profile)
