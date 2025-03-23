import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Visualisation", page_icon="📊", layout="centered")

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
    try:
        data = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
    except Exception as e:
        st.error(f"Erreur lors de la lecture des données: {e}")
    
    params = st.session_state['params']
    time_col = params['data_info']['time_col']
    
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
custom_max_value = params['data_info'].get('custom_max_value')  # Peut être None

# ---------------------------------------------------
# Interface utilisateur pour les paramètres dans la sidebar
# ---------------------------------------------------
with st.sidebar:
    st.header("Paramètres de visualisation")
    
    st.subheader("Données")
    
    year_range = st.slider(
        "Plage d'années",
        min_value=int(year_min),
        max_value=int(year_max),
        value=(int(year_min), int(year_max))
    )
    
    freq_options = {
        "Journalier": "D",
        "Hebdomadaire": "W",
        "Mensuel (fin)": "ME"
    }
    
    freq_display = st.selectbox(
        "Fréquence",
        options=list(freq_options.keys()),
        index=0,
        help="Journalier, Hebdomadaire, ou Mensuel (fin de mois)"
    )
    
    freq = freq_options[freq_display]
    
    st.subheader("Affichage")
    
    log_y = st.checkbox("Échelle logarithmique (log_y)", value=False)
    
    start_month = st.slider(
        "Mois de début de cycle",
        min_value=1,
        max_value=12,
        value=1,
        help="Définit le mois de début pour le cycle annuel"
    )
    
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
    
    st.session_state['params']['visualization']['year_min_visualization'] = year_range[0]
    st.session_state['params']['visualization']['year_min_visualization'] = year_range[1]
    st.session_state['params']['visualization']['freq'] = freq
    st.session_state['params']['visualization']['log_y'] = log_y
    st.session_state['params']['visualization']['focus_year'] = focus_year
    st.session_state['params']['visualization']['rolling_window'] = rolling_window
    st.session_state['params']['visualization']['start_month'] = start_month

# ---------------------------------------------------
# Mise à jour des paramètres pour cette session
# ---------------------------------------------------
year_min, year_max = year_range

st.header(f"Visualisation des chroniques pour {volume_col}")
st.write(f"Données chargées: **{time_col}** (temps) et **{volume_col}** (variable explorée)")
st.write(f"Période: {year_min} - {year_max}")

with st.expander("📄 Informations techniques"):
    st.markdown("""
    ### Gestion des semaines et du cycle annuel personnalisé

    #### Numérotation des semaines

    Les semaines utilisées ne suivent pas le calendrier ISO (lundi au dimanche). Elles sont calculées à partir du jour de l’année (`doy`) :

    ```text
    week_num = floor((doy - 1) / 7) + 1
    ```

    Chaque semaine contient 7 jours, et la 52e semaine regroupe tous les jours restants. Les 29 février sont supprimés et le 365e jour est rattaché à la dernière semaine (52), formant ainsi une semaine de 8 jours.

    ---

    #### Début d’année personnalisé (`start_month`)

    Il est possible de définir un mois de début du cycle annuel différent de janvier, par exemple octobre (`start_month = 10`).

    Cela entraîne :
    - Un recalcul des années : le cycle annuel commence en octobre d'une année N et se termine en septembre de l’année N+1.
    - Une reclassification des mois et des jours de l’année (le jour 1 correspond au 1er octobre).
    - Une adaptation des axes temporels dans les visualisations.

    **Exemple :** avec `start_month = 10`, janvier 2017 appartient au cycle de l'année 2017 (qui couvre oct. 2016 à sept. 2017).

    ---

    #### Conséquences sur le traitement

    - Les dates sont converties en `datetime` pour tous les traitements.
    - Les années incomplètes sont ignorées, ou interpolées si nécessaires.
    - Le cumul annuel peut être activé (`cumul=True`), basé sur le cycle défini.
    - Des moyennes par jour, semaine ou mois sont calculées selon `freq`.
    - Un lissage interannuel est possible via `rolling_window`.
    - En mode `statistics`, des bandes de quantiles sont générées avec comparaison à une année de référence.
    """)
# ---------------------------------------------------
# Filtrage des données
# ---------------------------------------------------
df["year"] = df[time_col].dt.year
df_filtered = df[df["year"].between(year_min, year_max)]

# Déterminer la valeur maximale pour la ligne de référence
max_volume = custom_max_value if custom_max_value is not None else df_filtered[volume_col].max()
max_volume_label = "Volume Maximal (personnalisé)" if custom_max_value is not None else "Volume Maximal"

# ---------------------------------------------------
# Chronique de Volume - Standard
# ---------------------------------------------------
st.header("Série temporelle chronologique")
tab1, tab2, tab3 = st.tabs(["Standard", "Moyenne glissante", "Comparaison"])

with tab1:
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month
    )

    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
    )
    
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'{max_volume_label} {max_volume:,.0f}'
    )

    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab2:
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month
    )

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
    
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'{max_volume_label} {max_volume:,.0f}'
    )

    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab3:
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='historical',
        start_month=start_month,
        focus_year=focus_year
    )

    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max
    )
    
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'{max_volume_label} {max_volume:,.0f}'
    )

    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

# ---------------------------------------------------
# Évolution du volume (cycle annuel)
# ---------------------------------------------------
st.header("Cycle annuel")
tab1, tab2 = st.tabs(["Standard", "Moyenne glissante"])

with tab1:
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='annual_cycle',
        start_month=start_month
    )

    plotter.add_series(
        df=df_filtered,
        time_col=time_col,
        var_col=volume_col,
        legend_name=f"{volume_col}",
        freq=freq,
        year_min=year_min,
        year_max=year_max,
    )
    
    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'{max_volume_label} {max_volume:,.0f}'
    )

    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

with tab2:
    plotter = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title=f"Volume ({volume_col})",
        x_range=(year_min, year_max),
        log_y=log_y,
        mode='annual_cycle',
        start_month=start_month
    )

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

    plotter.add_line(
        orientation='h',
        position=max_volume,
        line_dash='dash',
        col='all',
        color='red',
        label=f'{max_volume_label} {max_volume:,.0f}'
    )

    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

# ---------------------------------------------------
# Statistiques
# ---------------------------------------------------
st.header("Analyse statistique")

plotter = TimeSeriesPlot_Plotly(
    x_axis_title="Date",
    y_axis_title=f"Volume ({volume_col})",
    x_range=(year_min, year_max),
    log_y=log_y,
    mode='statistics',
    focus_year=focus_year,
    start_month=start_month
)

plotter.add_series(
    df=df_filtered,
    time_col=time_col,
    var_col=volume_col,
    legend_name=f"{volume_col}",
    freq=freq,
    year_min=year_min,
    year_max=year_max,
)

plotter.add_line(
    orientation='h',
    position=max_volume,
    line_dash='dash',
    col='all',
    color='red',
    label=f'{max_volume_label} {max_volume:,.0f}'
)

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
