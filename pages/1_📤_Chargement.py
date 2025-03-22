import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Chargement des données", page_icon="📤", layout="wide")

# Titre de la page sans formatage complexe
st.title("Chargement des données")
st.write("---")

# Téléchargement de fichier - version simplifiée
st.header("Téléchargement des données")
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
    st.header("Sélection des colonnes")
    time_col = st.selectbox("Sélectionnez la colonne de temps", df.columns)
    volume_col = st.selectbox("Sélectionnez la colonne de volume", 
                            [col for col in df.columns if col != time_col],
                            index=0 if len(df.columns) > 1 else None)
    
    # Afficher un message si aucune colonne de volume n'est disponible
    if len(df.columns) <= 1:
        st.warning("Votre fichier ne contient pas suffisamment de colonnes. Veuillez télécharger un fichier avec au moins deux colonnes.")
        st.stop()
    
    # Valider le format de la date et convertir si nécessaire
    st.header("Format de la date")
    date_format = st.selectbox(
        "Format de la date dans le fichier",
        options=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "Autre"]
    )
    
    if date_format == "Autre":
        custom_format = st.text_input("Spécifiez le format (ex: %d-%m-%Y)", "%d-%m-%Y")
    
    # Conversion de la date
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
        st.write("Dates converties:")
        st.dataframe(df[[time_col]].head())
        
    except Exception as e:
        st.error(f"Erreur lors de la conversion des dates: {e}")
        st.stop()

    # Valeur maximale personnalisée - version simplifiée
    st.header("Valeur maximale")
    
    # Calculer valeur maximale des données
    max_data_value = df[volume_col].max()
    
    # Option pour définir une valeur maximale personnalisée
    use_custom_max = st.checkbox("Définir une valeur maximale personnalisée")
    
    custom_max_value = None
    if use_custom_max:
        custom_max_value = st.number_input(
            "Valeur maximale", 
            value=float(max_data_value)
        )
    
    # Déterminer l'année min et max des données
    min_year = df[time_col].dt.year.min()
    max_year = df[time_col].dt.year.max()
    
    # Création du dictionnaire de paramètres
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
    
    # Enregistrer les paramètres et le dataframe dans la session Streamlit
    st.session_state['params'] = params
    
    # Convertir le dataframe en CSV pour le stocker dans la session
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.session_state['uploaded_data'] = csv_data
    
    # Message de confirmation
    st.success("Données chargées avec succès. Vous pouvez maintenant accéder à la page Visualisation.")
    
    # Résumé des données - version simplifiée
    st.header("Résumé des données")
    st.write(f"Nombre d'enregistrements: {len(df)}")
    st.write(f"Période: {min_year} - {max_year}")
    st.write(f"Valeur minimale: {df[volume_col].min():.2f}")
    st.write(f"Valeur maximale: {max_data_value:.2f}")
    if custom_max_value:
        st.write(f"Valeur maximale personnalisée: {custom_max_value:.2f}")

else:
    # Afficher un message si aucun fichier n'est téléchargé
    st.info("Veuillez télécharger un fichier CSV pour commencer.")