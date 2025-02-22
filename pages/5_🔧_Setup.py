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

#% Modules
import src
import importlib
importlib.reload(src)

# Définition du fichier de stockage des chemins
CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(root_dir, CONFIG_DIR, "paths.json")
print(CONFIG_FILE)

# Chemins par défaut
DEFAULT_PATHS = {
    "data_lake_path": "",            # Chemin du fichier Data_Lake (.csv)
    "folder_simu_path": "",          # Chemin du dossier de simulation
    "folder_output_path": "",        # Chemin du dossier de sortie
    "data_directory": "data/",       # Répertoire des fichiers de données
}

def ensure_config_file():
    """
    Vérifie que le dossier et le fichier de configuration existent.
    Crée le fichier JSON avec les valeurs par défaut si nécessaire.
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        logging.info(f"Création du dossier de configuration : {CONFIG_DIR}")

    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"Le fichier {CONFIG_FILE} n'existe pas. Création avec les valeurs par défaut.")
        save_paths(DEFAULT_PATHS)

def load_paths():
    """
    Charge les chemins depuis le fichier JSON.
    Retourne les valeurs par défaut si le fichier est absent ou corrompu.
    """
    ensure_config_file()  # Vérification avant chargement

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            logging.info("Fichier de configuration chargé avec succès.")
            return data
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Erreur lors du chargement de {CONFIG_FILE}: {e}. Réinitialisation aux valeurs par défaut.")
        save_paths(DEFAULT_PATHS)  # Réécriture du fichier corrompu
        return DEFAULT_PATHS

def save_paths(paths):
    """
    Sauvegarde les chemins mis à jour dans le fichier JSON.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(paths, file, indent=4)
            logging.info(f"Configuration sauvegardée dans {CONFIG_FILE}.")
    except IOError as e:
        logging.error(f"Échec de l'écriture dans {CONFIG_FILE}: {e}")

# Chargement des chemins enregistrés ou création initiale
paths = load_paths()

# Configuration de la page Streamlit
st.set_page_config(page_title="Configuration des chemins", page_icon="⚙️", layout="centered")

# Affichage du titre et de la description
st.title("⚙️ Configuration des chemins")
st.write("Définissez et modifiez les chemins de stockage utilisés par l'application.")

st.markdown("---")
st.subheader("📁 Définition des chemins")

# Interface de modification des chemins avec bulles d'information
for key, value in paths.items():
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
        help=help_message,
    )

    if new_value != paths[key]:  # Détection de modification
        paths[key] = new_value
        save_paths(paths)  # Mise à jour dans le fichier JSON
        st.success(f"✅ Chemin mis à jour : `{key}`")

st.markdown("---")
st.subheader("🔍 Chemins enregistrés")

# Bouton pour afficher le fichier JSON
if st.button("📂 Afficher les chemins enregistrés"):
    logging.debug("Affichage des chemins enregistrés demandé par l'utilisateur.")
    st.json(paths)

st.info("💾 Toutes les modifications sont enregistrées automatiquement.")