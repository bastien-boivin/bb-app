import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Chargement des données", page_icon="📤", layout="wide")

st.title("Chargement des données")
st.write("---")

st.header("Téléchargement des données")
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";")
        if len(df.columns) <= 1:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=",")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {e}, utilisez un séparateur comme ';' ou ','")
        st.stop()
    
    st.write("Aperçu des données:")
    st.dataframe(df.head())

    st.header("Sélection des colonnes")
    time_col = st.selectbox("Sélectionnez la colonne de temps", df.columns)
    volume_col = st.selectbox("Sélectionnez la colonne de volume", 
                            [col for col in df.columns if col != time_col],
                            index=0 if len(df.columns) > 1 else None)
    
    if len(df.columns) <= 1:
        st.warning("Votre fichier ne contient pas suffisamment de colonnes. Veuillez télécharger un fichier avec au moins deux colonnes.")
        st.stop()
    
    st.header("Format de la date")
    date_format = st.selectbox(
        "Format de la date dans le fichier",
        options=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "Autre"]
    )
    
    if date_format == "Autre":
        custom_format = st.text_input("Spécifiez le format (ex: %d-%m-%Y)", "%d-%m-%Y")
    
    # Date de conversion courante
    try:
        if date_format == "DD/MM/YYYY":
            df[time_col] = pd.to_datetime(df[time_col], dayfirst=True)
        elif date_format == "MM/DD/YYYY":
            df[time_col] = pd.to_datetime(df[time_col], dayfirst=False)
        elif date_format == "YYYY-MM-DD":
            df[time_col] = pd.to_datetime(df[time_col])
        elif date_format == "Autre" and custom_format:
            df[time_col] = pd.to_datetime(df[time_col], format=custom_format)
        
        st.write("Dates converties:")
        st.dataframe(df[[time_col]].head())
        
    except Exception as e:
        st.error(f"Erreur lors de la conversion des dates: {e}, utilisez un format de date valide comme \"DD/MM/YYYY\", \"MM/DD/YYYY\", \"YYYY-MM-DD\".")
        st.stop()

    st.header("Valeur maximale")
    max_data_value = df[volume_col].max()
    use_custom_max = st.checkbox("Définir une valeur maximale personnalisée")
    
    custom_max_value = None
    if use_custom_max:
        custom_max_value = st.number_input(
            "Valeur maximale", 
            value=float(max_data_value)
        )
    
    min_year = df[time_col].dt.year.min()
    max_year = df[time_col].dt.year.max()
    
    params = {
        "data_info": {
            "time_col": time_col,
            "volume_col": volume_col,
            "custom_max_value": custom_max_value
        },
        "visualization": {
            "year_min": int(min_year),
            "year_max": int(max_year),
            "freq": "D",
            "log_y": False,
            "focus_year": int(max_year-1),
            "rolling_window": 5,
            "start_month": 1
        }
    }
    
    st.session_state['params'] = params
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.session_state['uploaded_data'] = csv_data
    
    st.success("Données chargées avec succès. Vous pouvez maintenant accéder à la page Visualisation.")
    
    st.header("Résumé des données")
    st.write(f"Nombre d'enregistrements: {len(df)}")
    st.write(f"Période: {min_year} - {max_year}")
    st.write(f"Valeur minimale: {df[volume_col].min():.2f}")
    st.write(f"Valeur maximale: {max_data_value:.2f}")
    if custom_max_value:
        st.write(f"Valeur maximale personnalisée: {custom_max_value:.2f}")

else:
    st.info("Veuillez télécharger un fichier CSV pour commencer.")