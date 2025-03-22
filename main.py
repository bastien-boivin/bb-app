import streamlit as st

# Cette ligne doit être la première commande Streamlit
st.set_page_config(page_title="Redirection...", page_icon="💧", layout="wide")

# Masquer la barre latérale par défaut (cette méthode est compatible avec Streamlit Cloud)
st.markdown("""
<style>
    /* Cache les contrôles de page principaux */
    div[data-testid="collapsedControl"] {display: none;}
    
    /* Cache l'élément "main" de la barre latérale */
    section[data-testid="stSidebar"] {
        width: 0px;
        overflow: hidden;
    }
    
    /* Restaure la largeur normale du contenu */
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Message très bref avant redirection
st.spinner("Chargement...")

# Redirection immédiate vers Home (sans le préfixe "pages/")
st.switch_page("1_🏡_Home.py")