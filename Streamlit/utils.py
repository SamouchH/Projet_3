import pandas as pd
import streamlit as st
from openai import OpenAI

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


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

def generate_mistral_response(prompt, model="mistralai/mistral-7b-instruct-v0.2", temperature=0.7, max_tokens=300):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur : {e}"