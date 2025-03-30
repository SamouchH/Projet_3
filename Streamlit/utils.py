import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/SamouchH/Projet_3/streamlit/Streamlit/games_categories.csv"
    return pd.read_csv(url)

def get_data():
    if 'data' not in st.session_state:
        st.session_state['data'] = load_data()
    return st.session_state['data']

def get_logo_path(category):
    logos = {
        "Arcade": "logos/Arcade.jpg",
        "Nintendo": "logos/Nintendo.png",
        "PlayStation": "logos/PlayStation.png",
        "SEGA": "logos/Sega.png",
        "Réalité Virtuelle": "logos/VR.png",
        "VTECH": "logos/Vtech.png",
        "Xbox": "logos/Xbox.png",
        "PC Gaming": "logos/gaming-pc.png",
        "Autre": "logos/More.png",
        "Outlier": "logos/outlier.png",
        "Mobile Gaming": "logos/games.png"
    }
    return logos.get(category, "logos/default.png")