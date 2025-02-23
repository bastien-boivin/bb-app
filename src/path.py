import os
import sys
import json
import logging

from os.path import abspath, dirname
root_dir = dirname(dirname((abspath(__file__))))
sys.path.append(root_dir)

cwd = os.getcwd()
if cwd != root_dir:
    os.chdir(root_dir)
    logging.info(f"Changement du répertoire de travail vers {root_dir}")

# -----------------------------------------------------
# Modules
# -----------------------------------------------------
import src
import importlib
importlib.reload(src)

# -----------------------------------------------------
# Définition du fichier de stockage des chemins
# -----------------------------------------------------
CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(root_dir, CONFIG_DIR, "paths.json")

# -----------------------------------------------------
# Chemins par défaut
# -----------------------------------------------------
DEFAULT_PATHS = {
    "profiles": {},
    "default_paths": {
        "data_lake_path": "",            # Chemin du fichier Data_Lake (.csv)
        "folder_simu_path": "",          # Chemin du dossier de simulation
        "folder_output_path": "",        # Chemin du dossier de sortie
        "data_directory": "",            # Répertoire des fichiers de données
    },
    "selected_profile": None
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

def get_selected_profile():
    logging.debug("Appel de get_selected_profile")
    paths = load_paths()
    return paths.get("selected_profile", None)

def set_selected_profile(profile_name):
    logging.debug(f"Appel de set_selected_profile avec {profile_name}")
    paths = load_paths()
    paths["selected_profile"] = profile_name
    save_paths(paths)