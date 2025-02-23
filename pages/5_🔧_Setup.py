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

from src.config import initialize_sidebar
from src.path import load_paths, save_paths, DEFAULT_PATHS, get_selected_profile, set_selected_profile

# -----------------------------------------------------
# Configuration de la page Streamlit
# -----------------------------------------------------
st.set_page_config(page_title="Configuration des chemins", page_icon="⚙️", layout="centered")

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
initialize_sidebar()

# -----------------------------------------------------
# Chargement des chemins enregistrés ou création initiale
# -----------------------------------------------------
paths = load_paths()

# -----------------------------------------------------
# Page content
# -----------------------------------------------------
st.title("⚙️ Configuration des chemins")
st.write("Définissez et modifiez les chemins de stockage utilisés par l'application.")

# Affichage des chemins pour le site d'étude sélectionné
selected_profile = get_selected_profile()
if selected_profile:
    profile_paths = paths["profiles"][selected_profile]

    st.markdown("---")
    st.subheader(f"📁 Définition des chemins pour {selected_profile}")

    for key, value in profile_paths.items():
        help_message = ""
        if key == "data_lake_path":
            help_message = "Data_Lake, fichie .csv attendu."
        elif key == "folder_simu_path":
            help_message = "Répertoire des fichiers de simulation."
        elif key == "folder_output_path":
            help_message = "Répertoire des fichiers de sortie."
        elif key == "data_directory":
            help_message = "Répertoire où sont stockées les données."

        new_value = st.text_input(
            f"**{key.replace('_', ' ').capitalize()}**",
            value=value,
            help=help_message
            )
        
        if new_value != profile_paths[key]:  # Détection de modification
            profile_paths[key] = new_value
            save_paths(paths)  # Mise à jour dans le fichier JSON
            logging.info(f"Path updated: {key} for profile {selected_profile}")
            st.success(f"✅ Chemin mis à jour : `{key}` pour le profil `{selected_profile}`")

# Ajout de la gestion des profils de sites d'études
st.markdown("---")
st.subheader("🏢 Gestion des profils de sites d'études")

# Interface pour ajouter un nouveau profil
new_profile_name = st.text_input("Nom du nouveau profil de site d'étude", "")
if st.button("Ajouter un nouveau profil"):
    if new_profile_name:
        if new_profile_name not in paths["profiles"]:
            paths["profiles"][new_profile_name] = DEFAULT_PATHS["default_paths"].copy()
            save_paths(paths)
            st.success(f"✅ Nouveau profil ajouté : `{new_profile_name}`")
        else:
            st.error(f"Le profil `{new_profile_name}` existe déjà.")

# Interface pour supprimer des profils existants
if paths["profiles"]:
    st.subheader("Profils existants")
    for profile_name in list(paths["profiles"].keys()):
        if st.button(f"Supprimer le profil `{profile_name}`"):
            del paths["profiles"][profile_name]
            save_paths(paths)
            st.success(f"✅ Profil `{profile_name}` supprimé")
            if get_selected_profile() == profile_name:
                set_selected_profile(list(paths["profiles"].keys())[0] if paths["profiles"] else None)
