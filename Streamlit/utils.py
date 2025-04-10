import pandas as pd
import streamlit as st
from openai import OpenAI
import os
from tensorflow.keras.models import load_model as tf_load_model
import numpy as np

# Chargement csv pour EDA
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/SamouchH/Projet_3/streamlit/Streamlit/games_categories.csv"
    return pd.read_csv(url)

# data dans session state
def get_data():
    if 'data' not in st.session_state:
        st.session_state['data'] = load_data()
    return st.session_state['data']

# Display logo pour EDA
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

# LLM pour description
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

# Helper function to get the labeling platform directory
def get_labeling_dir():
    # Get the current Streamlit script directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Get the parent directory (project root)
    project_root = os.path.dirname(current_dir)
    # The labeling platform directory
    return os.path.join(project_root, "Labeller")

# Model cnn
category_labels = ["Playstation", "Xbox", "Nintendo", "PC Gaming"]

@st.cache_resource
def load_model(model_path="modele_cnn_transfer.h5"):
    model = tf_load_model(model_path)
    return model

def predict(model, image_array, cat_mapping=None):
    image = image_array / 255.0
    image = np.expand_dims(image, axis=0)
    prediction = model.predict(image)
    pred_index = np.argmax(prediction, axis=1)[0]
    category = cat_mapping[pred_index] if cat_mapping else pred_index
    return category