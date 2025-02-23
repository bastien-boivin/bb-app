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

# -----------------------------------------------------
# Configuration de la page Streamlit
# -----------------------------------------------------
st.set_page_config(page_title="Accueil", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
initialize_sidebar()

# -----------------------------------------------------
# Page content
# -----------------------------------------------------
st.title("Accueil")
