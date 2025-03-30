import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
from pathlib import Path
from utils import get_data, get_logo_path



st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

st.subheader("Analyse du set de données d'entrainement")

df = get_data()

categories = df['category'].unique().tolist()

st.markdown("### Cliquez sur une catégorie :")

# Créer une grille de logos cliquables (4 par ligne)
n_cols = 11
rows = [categories[i:i + n_cols] for i in range(0, len(categories), n_cols)]

for row in rows:
    cols = st.columns(len(row))
    for col, cat in zip(cols, row):
        logo_path = get_logo_path(cat)
        if Path(logo_path).exists():
            if col.button("", key=cat):
                st.session_state["selected_category"] = cat
            col.image(logo_path, use_container_width=True, caption=cat)
        else:
            col.warning(f"Logo manquant pour {cat}")



# Ajout d'une option "Toutes"
st.markdown("---")
if st.button("Voir toutes les catégories"):
    st.session_state["selected_category"] = "Toutes"

# Récupération de la catégorie sélectionnée
selected_category = st.session_state.get("selected_category", None)

if selected_category:
    st.markdown(f"### ✅ Catégorie sélectionnée : **{selected_category}**")

    if selected_category != "Toutes":
        df_marque = df[df['category'] == selected_category]
        st.image(get_logo_path(selected_category), width=150)
    else:
        df_marque = df

    # Génération des données pour le treemap
    df_treemap = df_marque.groupby(['category', 'subcategory']).size().reset_index(name='count')

    # Création du treemap
    fig = px.treemap(df_treemap, 
                    path=['category', 'subcategory'],
                    values='count',
                    color='category'
                    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Cliquez sur un logo pour afficher les données.")


