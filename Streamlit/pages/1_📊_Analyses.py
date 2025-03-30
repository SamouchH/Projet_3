import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

st.subheader("Analyse du set de données d'entrainement")

if 'data' in st.session_state:
    df = st.session_state.data

    # Liste des catégories disponibles dans le DataFrame
    categories_disponibles = df['category'].unique().tolist()
    
    # Ajout de l'option "Toutes" pour voir toutes les catégories
    list_marque = ['Toutes'] + categories_disponibles  

    # Sélection de la catégorie avec un menu déroulant
    selected_category = st.selectbox("Sélectionnez une catégorie :", list_marque)

    # Fonction pour générer le dataframe pour le treemap
    def generate_plot(df):
        return df.groupby(['category', 'subcategory']).size().reset_index(name='count')

    # Filtrer les données si une catégorie spécifique est sélectionnée
    if selected_category == "Toutes":
        df_marque = df  # Afficher toutes les catégories
    else:
        df_marque = df[df['category'] == selected_category]  # Filtrer la sélection

    # Génération des données pour le treemap
    df_treemap = generate_plot(df_marque)

    # Création du treemap avec Plotly
    fig = px.treemap(df_treemap, 
                    path=['category', 'subcategory'],  # Hiérarchie Catégorie -> Sous-catégorie
                    values='count',
                    color='category'
                    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)


