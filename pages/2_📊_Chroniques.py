import streamlit as st
import pandas as pd
import io

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(page_title="Visualisation", page_icon="📊", layout="wide")

# Titre de la page
st.title("📊 Visualisation des chroniques")
st.markdown("---")

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
        st.warning("Aucune donnée n'a été téléchargée. Veuillez retourner à la page Chargement pour télécharger vos données.")
        st.stop()
    
    if 'params' not in st.session_state:
        st.warning("Aucun paramètre n'a été configuré. Veuillez retourner à la page Chargement pour configurer vos paramètres.")
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

# ---------------------------------------------------
# Interface utilisateur pour les paramètres dans la sidebar
# ---------------------------------------------------
with st.sidebar:
    st.header("Paramètres de visualisation")
    
    # Section 1: Paramètres de plage et de fréquence
    st.subheader("Données")
    
    year_range = st.slider(
        "Plage d'années",
        min_value=int(year_min),
        max_value=int(year_max),
        value=(int(year_min), int(year_max))
    )
    
    freq = st.selectbox(
        "Fréquence d'échantillonnage",
        options=["D", "W", "ME"],
        index=0,
        help="D: Journalier, W: Hebdomadaire, ME: Fin de mois"
    )
    
    # Section 2: Paramètres d'affichage
    st.subheader("Affichage")
    
    log_y = st.checkbox("Échelle logarithmique (log_y)", value=False)
    
    start_month = st.slider(
        "Mois de début de cycle",
        min_value=1,
        max_value=12,
        value=1,
        help="Définit le mois de début pour le cycle annuel"
    )
    
    # Section 3: Paramètres d'analyse
    st.subheader("Analyse")
    
    focus_year = st.slider(
        "Année de référence",
        min_value=int(year_min),
        max_value=int(year_max),
        value=int(year_max-1),
        help="Année mise en évidence dans les analyses statistiques et comparatives"
    )
    
    rolling_window = st.slider(
        "Fenêtre glissante (années)",
        min_value=2,
        max_value=10,
        value=5,
        help="Nombre d'années utilisées pour le calcul de la moyenne mobile"
    )
    
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
    
    # Mise à jour des valeurs dans session_state
    st.session_state['params']['visualization']['year_min'] = year_range[0]
    st.session_state['params']['visualization']['year_max'] = year_range[1]
    st.session_state['params']['visualization']['freq'] = freq
    st.session_state['params']['visualization']['log_y'] = log_y
    st.session_state['params']['visualization']['focus_year'] = focus_year
    st.session_state['params']['visualization']['rolling_window'] = rolling_window
    st.session_state['params']['visualization']['start_month'] = start_month

# ---------------------------------------------------
# Mise à jour des paramètres pour cette session
# ---------------------------------------------------
year_min, year_max = year_range

# Afficher les informations des données chargées
st.header(f"Visualisation des chroniques pour {volume_col}")
st.write(f"Données chargées: **{time_col}** (temps) et **{volume_col}** (volume)")
st.write(f"Période: {year_min} - {year_max}")

# ---------------------------------------------------
# Filtrage des données
# ---------------------------------------------------
df["year"] = df[time_col].dt.year
df_filtered = df[df["year"].between(year_min, year_max)]

# ---------------------------------------------------
# Chronique de Volume - Standard
# ---------------------------------------------------
st.header("Série temporelle chronologique")
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
st.header("Cycle annuel")
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
st.header("Analyse statistique")

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
# Informations sur l'utilisation
# ---------------------------------------------------
with st.expander("💡 Conseils d'utilisation"):
    st.markdown("""
    ### Comment utiliser les visualisations
    
    - **Série temporelle** : Vue chronologique de l'évolution du volume
    - **Cycle annuel** : Compare les variations saisonnières entre les différentes années
    - **Analyse statistique** : Présente les médianes, quartiles et compare avec une année de référence
    
    Utilisez les paramètres dans la barre latérale pour personnaliser les visualisations selon vos besoins.
    
    Pour télécharger un graphique, cliquez sur l'icône d'appareil photo qui apparaît en haut à droite de chaque graphique lorsque vous passez votre souris dessus.
    """)
