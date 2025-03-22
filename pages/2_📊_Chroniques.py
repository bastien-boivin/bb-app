import os
import sys
import logging
import json
import pandas as pd
import streamlit as st
import io

# Configuration de la page Streamlit
st.set_page_config(page_title="Chroniques", page_icon="📊", layout="wide")

# ---------------------------------------------------
# Import de la classe TimeSeriesPlot_Plotly
# ---------------------------------------------------
from visualisation.plotly_chroniques import TimeSeriesPlot_Plotly

# ---------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------
def check_data_availability():
    """Vérifie si les données sont disponibles dans la session"""
    if 'uploaded_data' not in st.session_state:
        st.warning("Aucune donnée n'a été téléchargée. Veuillez retourner à la page d'accueil pour télécharger vos données.")
        if st.button("Retour à l'accueil"):
            st.switch_page("pages/1_🏡_Home.py")
        st.stop()
    
    if 'params' not in st.session_state:
        st.warning("Aucun paramètre n'a été configuré. Veuillez retourner à la page d'accueil pour configurer vos paramètres.")
        if st.button("Retour à l'accueil"):
            st.switch_page("pages/1_🏡_Home.py")
        st.stop()

def load_data():
    """Charge les données depuis la session"""
    csv_data = st.session_state['uploaded_data']
    data = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
    
    params = st.session_state['params']
    time_col = params['data_info']['time_col']
    
    # Convertir la colonne de temps en datetime
    data[time_col] = pd.to_datetime(data[time_col], errors='coerce')
    
    return data, params

# ---------------------------------------------------
# Vérification des données
# ---------------------------------------------------
check_data_availability()
df, params = load_data()

# ---------------------------------------------------
# Extraction des paramètres
# ---------------------------------------------------
time_col = params['data_info']['time_col']
volume_col = params['data_info']['volume_col']
year_min = params['visualization']['year_min']
year_max = params['visualization']['year_max']
freq = params['visualization']['freq']
log_y = params['visualization']['log_y']
focus_year = params['visualization']['focus_year']
rolling_window = params['visualization']['rolling_window']
start_month = params['visualization']['start_month']

# ---------------------------------------------------
# Titre et description
# ---------------------------------------------------
st.title("📊 Chroniques")
st.write(f"Visualisation des chroniques de {volume_col} sur la période {year_min}-{year_max}")

# ---------------------------------------------------
# Filtrage des données
# ---------------------------------------------------
df["year"] = df[time_col].dt.year
df_filtered = df[df["year"].between(year_min, year_max)]

# ---------------------------------------------------
# Interface utilisateur pour les paramètres
# ---------------------------------------------------
with st.sidebar:
    st.header("Paramètres")
    
    # Mise à jour des paramètres
    log_y = st.checkbox("Échelle logarithmique", value=log_y)
    freq = st.selectbox("Fréquence", ["D", "W", "ME"], index=["D", "W", "ME"].index(freq))
    focus_year = st.slider("Année de référence", year_min, year_max, focus_year)
    rolling_window = st.slider("Fenêtre glissante", 2, 10, rolling_window)
    start_month = st.slider("Mois de début", 1, 12, start_month)
    
    # Mise à jour des valeurs dans session_state
    st.session_state['params']['visualization']['log_y'] = log_y
    st.session_state['params']['visualization']['freq'] = freq
    st.session_state['params']['visualization']['focus_year'] = focus_year
    st.session_state['params']['visualization']['rolling_window'] = rolling_window
    st.session_state['params']['visualization']['start_month'] = start_month
    
    # Bouton pour réinitialiser les paramètres
    if st.button("Réinitialiser les paramètres"):
        st.session_state['params']['visualization'] = {
            "year_min": year_min,
            "year_max": year_max,
            "freq": "D",
            "log_y": False,
            "focus_year": year_max - 1,
            "rolling_window": 5,
            "start_month": 1
        }
        st.rerun()

# ---------------------------------------------------
# Chronique de Volume - Standard
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Standard", "Moyenne glissante", "Comparaison"])

with tab1:
    # Création du graphique
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month
    )

    # Ajout des séries
    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
    )
    
    # Déterminer la valeur maximale pour la ligne de référence
    max_volume = df_filtered[volume_col].max()
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'Volume Maximal {max_volume:,.0f}'
    )

    # Affichage du graphique
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab2:
    # Création du graphique avec moyenne glissante
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month
    )

    # Ajout des séries
    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
        rolling_window=rolling_window
    )
    
    # Ligne de référence
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'Volume Maximal {max_volume:,.0f}'
    )

    # Affichage du graphique
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab3:
    # Création du graphique de comparaison
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month,
        focus_year=focus_year
    )

    # Ajout des séries
    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max
    )
    
    # Ligne de référence
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'Volume Maximal {max_volume:,.0f}'
    )

    # Affichage du graphique
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

# ---------------------------------------------------
# Évolution du volume (cycle annuel)
# ---------------------------------------------------
st.header("Évolution du volume (cycle annuel)")
tab1, tab2 = st.tabs(["Standard", "Moyenne glissante"])

with tab1:
    # Création du graphique
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='annual_cycle',
        start_month=start_month
    )

    # Ajout des séries
    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
    )
    
    # Ligne de référence
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'Volume Maximal {max_volume:,.0f}'
    )

    # Affichage du graphique
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab2:
    # Création du graphique avec moyenne glissante
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='annual_cycle',
        start_month=start_month
    )

    # Ajout des séries
    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
        rolling_window=rolling_window
    )
    
    # Ligne de référence
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'Volume Maximal {max_volume:,.0f}'
    )

    # Affichage du graphique
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

# ---------------------------------------------------
# Statistiques
# ---------------------------------------------------
st.header("Statistiques")

# Création du graphique statistique
plotter = TimeSeriesPlot_Plotly(
    x_axis_title="Date",
    y_axis_title=f"Volume ({volume_col})",
    x_range=(year_min, year_max),
    log_y=log_y,
    mode='statistics',
    focus_year=focus_year,
    start_month=start_month
)

# Ajout des séries
plotter.add_series(
    df=df_filtered,
    time_col=time_col,
    var_col=volume_col,
    legend_name=f"{volume_col}",
    freq=freq,
    year_min=year_min,
    year_max=year_max,
)

# Ligne de référence
plotter.add_line(
    orientation='h',
    position=max_volume,
    line_dash='dash',
    col='all',
    color='red',
    label=f'Volume Maximal {max_volume:,.0f}'
)

# Affichage du graphique
plotter.fig = plotter.create_figure()
st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

# ---------------------------------------------------
# Téléchargement des graphiques
# ---------------------------------------------------
st.header("Téléchargement")
st.info("Pour télécharger un graphique, cliquez sur l'icône d'appareil photo dans la barre d'outils du graphique.")