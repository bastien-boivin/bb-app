import os
import sys
import logging
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# -------------------------------------------------
# Configuration de la page
# -------------------------------------------------
st.set_page_config(page_title="Accueil", page_icon="🏠", layout="wide")

# -------------------------------------------------
# Titre de la page
# -------------------------------------------------
st.title("📊 Reservoir Water Volume Analysis")
st.markdown("---")

# -------------------------------------------------
# Instructions d'utilisation
# -------------------------------------------------
with st.expander("📌 Comment utiliser cette application", expanded=True):
    st.markdown("""
    ### Bienvenue dans l'application d'analyse des réservoirs d'eau

    Cette application vous permet de visualiser et d'analyser les données de volume d'eau des réservoirs.
    Pour commencer :

    1. **Téléchargez votre fichier CSV** contenant les données de chroniques
    2. **Sélectionnez les colonnes** pour le temps et les données de volume
    3. **Configurez les paramètres** de visualisation selon vos besoins
    4. Accédez à la page **Chroniques** pour visualiser les graphiques

    Le format attendu du CSV est un fichier avec une colonne de date et une colonne de volume.
    """)

# -------------------------------------------------
# Téléchargement de fichier
# -------------------------------------------------
st.header("1️⃣ Téléchargement des données")
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")

if uploaded_file is not None:
    # Tentative de lecture avec différents séparateurs
    try:
        # Essai avec séparateur point-virgule
        df = pd.read_csv(uploaded_file, sep=";")
        if len(df.columns) <= 1:  # Si une seule colonne est détectée, essayons avec une virgule
            uploaded_file.seek(0)  # Rembobiner le fichier
            df = pd.read_csv(uploaded_file, sep=",")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {e}")
        st.stop()
    
    # Afficher un aperçu des données
    st.write("Aperçu des données:")
    st.dataframe(df.head())
    
    # Sélection des colonnes
    st.header("2️⃣ Sélection des colonnes")
    time_col = st.selectbox("Sélectionnez la colonne de temps", df.columns)
    volume_col = st.selectbox("Sélectionnez la colonne de volume", 
                            [col for col in df.columns if col != time_col],
                            index=0 if len(df.columns) > 1 else None)
    
    # Afficher un message si aucune colonne de volume n'est disponible
    if len(df.columns) <= 1:
        st.warning("Votre fichier ne contient pas suffisamment de colonnes. Veuillez télécharger un fichier avec au moins deux colonnes.")
        st.stop()
    
    # Valider le format de la date et convertir si nécessaire
    st.header("3️⃣ Validation des données")
    with st.expander("Format de la date", expanded=True):
        date_format = st.selectbox(
            "Format de la date dans le fichier",
            options=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "Autre"],
            index=0
        )
        
        if date_format == "Autre":
            custom_format = st.text_input("Spécifiez le format (ex: %d-%m-%Y)", "%d-%m-%Y")
        
        # Prévisualisation de conversion de date
        try:
            if date_format == "DD/MM/YYYY":
                df[time_col] = pd.to_datetime(df[time_col], dayfirst=True)
            elif date_format == "MM/DD/YYYY":
                df[time_col] = pd.to_datetime(df[time_col], dayfirst=False)
            elif date_format == "YYYY-MM-DD":
                df[time_col] = pd.to_datetime(df[time_col])
            elif date_format == "Autre" and custom_format:
                df[time_col] = pd.to_datetime(df[time_col], format=custom_format)
            
            # Afficher les premières dates converties
            st.write("Dates converties (premières lignes):")
            st.dataframe(df[[time_col]].head())
            
        except Exception as e:
            st.error(f"Erreur lors de la conversion des dates: {e}")
            st.info("Veuillez sélectionner un autre format de date ou vérifier vos données.")
            st.stop()
    
    # Configuration des paramètres de visualisation
    st.header("4️⃣ Configuration des paramètres")
    
    # Déterminer l'année min et max des données
    min_year = df[time_col].dt.year.min()
    max_year = df[time_col].dt.year.max()
    
    col1, col2 = st.columns(2)
    with col1:
        # Paramètres pour la visualisation
        year_range = st.slider(
            "Plage d'années",
            min_value=int(min_year),
            max_value=int(max_year),
            value=(int(min_year), int(max_year))
        )
        
        freq = st.selectbox(
            "Fréquence",
            options=["D", "W", "ME"],
            index=0,
            help="D: Journalier, W: Hebdomadaire, ME: Fin de mois"
        )
        
        log_y = st.checkbox("Échelle logarithmique (log_y)", value=False)
    
    with col2:
        focus_year = st.slider(
            "Année de référence",
            min_value=int(min_year),
            max_value=int(max_year),
            value=int(max_year-1)
        )
        
        rolling_window = st.slider(
            "Fenêtre glissante",
            min_value=2,
            max_value=10,
            value=5
        )
        
        start_month = st.slider(
            "Mois de début",
            min_value=1,
            max_value=12,
            value=1
        )
    
    # Création du dictionnaire de paramètres
    params = {
        "data_info": {
            "time_col": time_col,
            "volume_col": volume_col,
        },
        "visualization": {
            "year_min": year_range[0],
            "year_max": year_range[1],
            "freq": freq,
            "log_y": log_y,
            "focus_year": focus_year,
            "rolling_window": rolling_window,
            "start_month": start_month
        }
    }
    
    # Enregistrer les paramètres et le dataframe dans la session Streamlit
    st.session_state['params'] = params
    
    # Convertir le dataframe en CSV pour le stocker dans la session
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.session_state['uploaded_data'] = csv_data
    
    # Message de confirmation
    st.success("✅ Configuration terminée ! Vous pouvez maintenant accéder à la page Chroniques pour visualiser vos données.")
    
    # Bouton pour aller à la page Chroniques
    if st.button("Aller à la page Chroniques"):
        st.switch_page("pages/2_📊_Chroniques.py")

else:
    # Afficher un message si aucun fichier n'est téléchargé
    st.info("Veuillez télécharger un fichier CSV pour commencer.")
    
    # Exemple de données
    st.markdown("### Exemple de format de données attendu:")
    example_data = pd.DataFrame({
        'time': ['01/01/2020', '02/01/2020', '03/01/2020', '04/01/2020', '05/01/2020'],
        'volume': [12500000, 12700000, 12900000, 13100000, 13300000]
    })
    st.dataframe(example_data)