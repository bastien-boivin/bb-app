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
from src.visualisation import plotly_chroniques
