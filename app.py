import streamlit as st
import pandas as pd
import numpy as np
import cv2
import os
import ast

def main():
    st.title("Exploration des détections de logos")

    # Indiquez les chemins vers vos dossiers et CSV
    covers_folder = "images_folder"  # Pochettes
    logos_folder  = "logo_folder"      # Logos
    csv_path      = "resultats_detection.csv"           # CSV généré après détection

    # Lecture du CSV
    # Le CSV contient : cover_file, logo_file, found, corners
    df = pd.read_csv(csv_path)

    # Si le CSV contient bien des données
    if df.empty:
        st.warning("Le CSV est vide ou introuvable. Vérifiez le chemin et son contenu.")
        return

    # Récupérer la liste des pochettes disponibles
    covers = df["cover_file"].unique()
    if len(covers) == 0:
        st.warning("Aucune pochette n'est listée dans le CSV.")
        return

    # Sélecteur de pochette dans la barre latérale ou en haut de page
    selected_cover = st.selectbox("Sélectionnez une pochette :", covers)

    # Filtrer le DataFrame pour ne garder que les lignes liées à la pochette sélectionnée
    sub_df = df[df["cover_file"] == selected_cover]

    # Afficher le tableau de résultats pour la pochette sélectionnée
    st.subheader("Données extraites du CSV pour la pochette sélectionnée")
    st.dataframe(sub_df)

    # Chargement de l'image de la pochette
    cover_path = os.path.join(covers_folder, selected_cover)
    cover_img = cv2.imread(cover_path)

    if cover_img is None:
        st.error(f"Impossible de charger la pochette : {cover_path}")
        return

    # Pour chaque ligne associée à cette pochette, on dessine les polygones détectés
    for idx, row in sub_df.iterrows():
        corners_str = row["corners"]
        if corners_str and corners_str != "None":
            # corners est stocké sous forme de chaîne ; on le reconvertit en liste Python
            corners = ast.literal_eval(corners_str)  # ex: [[x1, y1], [x2, y2], ...]
            corners_np = np.array(corners, dtype=np.int32).reshape(-1, 1, 2)

            # Dessiner le polygone dans l'image
            cv2.polylines(cover_img, [corners_np], True, (0, 255, 0), 3)

    # Convertir l'image de BGR (OpenCV) à RGB pour l'affichage Streamlit
    cover_img_rgb = cv2.cvtColor(cover_img, cv2.COLOR_BGR2RGB)

    # Afficher la pochette annotée dans Streamlit
    st.subheader("Pochette annotée")
    st.image(cover_img_rgb, caption=f"Pochette : {selected_cover}", use_column_width=True)

    # Affichage des logos détectés
    st.subheader("Logos détectés")
    for idx, row in sub_df.iterrows():
        logo_file = row["logo_file"]
        found     = row["found"]

        if found:
            # Charger et afficher l'image du logo
            logo_path = os.path.join(logos_folder, logo_file)
            logo_img = cv2.imread(logo_path)

            if logo_img is not None:
                logo_img_rgb = cv2.cvtColor(logo_img, cv2.COLOR_BGR2RGB)
                st.image(
                    logo_img_rgb,
                    caption=f"Logo détecté : {logo_file}",
                    use_column_width=False
                )
            else:
                st.write(f"Impossible de charger le logo : {logo_path}")

if __name__ == "__main__":
    main()
