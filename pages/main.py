import streamlit as st

st.logo("assets/images/Logo_Universite_Rennes.png", size="large")

pages = {
    "DashBoard": [
        st.Page("1_🏡_Home.py", title="Home"),
    ],
    "Visualisation": [
        st.Page("2_📊_Chroniques.py", title="Chroniques"),
    ],
    "Tools": [
        st.Page("5_🔧_Setup.py", title="Setup"),
    ],
}

pg = st.navigation(pages)
pg.run()