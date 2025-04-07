import streamlit_app as st
import pandas as pd
import numpy as np
import cv2
import os
import ast

def main():
    st.title("Exploration des détections de logos")

    # Indiquez les chemins vers vos dossiers et CSV
    covers_folder = "images_folder"  # Pochettes
    logos_folder = "logo_folder"     # Logos
    csv_path = "resultats_detection.csv"  # CSV généré après détection
    debug_folder = "debug_detection"  # Dossier avec images de débogage

    # Lecture du CSV
    # Le CSV contient maintenant: cover_file, logo_file, found, corners, confidence
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du CSV: {e}")
        return

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

    # Onglets pour afficher différentes visualisations
    tab1, tab2, tab3 = st.tabs(["Résultat final", "Détection du cadre", "Amélioration"])

    # Chargement de l'image du résultat final (avec annotations)
    with tab1:
        cover_path = os.path.join(covers_folder, selected_cover)
        cover_img = cv2.imread(cover_path)

        if cover_img is None:
            st.error(f"Impossible de charger la pochette : {cover_path}")
        else:
            # Pour chaque ligne associée à cette pochette, on dessine les polygones détectés
            for idx, row in sub_df.iterrows():
                corners_str = row["corners"]
                confidence = row.get("confidence", 1.0)  # Utiliser 1.0 comme valeur par défaut si non présent
                
                if corners_str and corners_str != "None":
                    # corners est stocké sous forme de chaîne ; on le reconvertit en liste Python
                    corners = ast.literal_eval(corners_str)  # ex: [[x1, y1], [x2, y2], ...]
                    corners_np = np.array(corners, dtype=np.int32).reshape(-1, 1, 2)

                    # Couleur basée sur la confiance
                    color = (0, 255, 0)  # Vert par défaut
                    if "confidence" in row and row["confidence"] < 0.5:
                        color = (0, 255, 255)  # Jaune pour faible confiance
                        
                    # Dessiner le polygone dans l'image
                    cv2.polylines(cover_img, [corners_np], True, color, 3)
                    
                    # Suppression du texte à la demande de l'utilisateur

            # Convertir l'image de BGR (OpenCV) à RGB pour l'affichage Streamlit
            cover_img_rgb = cv2.cvtColor(cover_img, cv2.COLOR_BGR2RGB)

            # Afficher la pochette annotée dans Streamlit
            st.subheader("Pochette annotée")
            st.image(cover_img_rgb, caption=f"Pochette : {selected_cover}", use_column_width=True)

    # Onglet pour l'image de détection de cadre
    with tab2:
        debug_cover_path = os.path.join(debug_folder, f"cover_detect_{selected_cover}")
        if os.path.exists(debug_cover_path):
            debug_cover = cv2.imread(debug_cover_path)
            if debug_cover is not None:
                debug_cover_rgb = cv2.cvtColor(debug_cover, cv2.COLOR_BGR2RGB)
                st.subheader("Détection du cadre de la pochette")
                st.image(debug_cover_rgb, caption="Rectangle détecté", use_column_width=True)
        else:
            st.info("Image de détection de cadre non disponible.")
            
    # Onglet pour l'image améliorée
    with tab3:
        enhanced_path = os.path.join(debug_folder, f"enhanced_{selected_cover}")
        if os.path.exists(enhanced_path):
            enhanced_img = cv2.imread(enhanced_path)
            if enhanced_img is not None:
                enhanced_img_rgb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
                st.subheader("Image améliorée pour la détection")
                st.image(enhanced_img_rgb, caption="Image améliorée", use_column_width=True)
        else:
            st.info("Image améliorée non disponible.")

    # Affichage des logos détectés
    st.subheader("Logos détectés")
    cols = st.columns(3)  # Créer 3 colonnes pour afficher plusieurs logos côte à côte
    
    for idx, (_, row) in enumerate(sub_df.iterrows()):
        logo_file = row["logo_file"]
        found = row["found"]
        confidence = row.get("confidence", 1.0)  # Utiliser 1.0 comme valeur par défaut

        if found:
            # Charger et afficher l'image du logo
            logo_path = os.path.join(logos_folder, logo_file)
            logo_img = cv2.imread(logo_path)

            if logo_img is not None:
                logo_img_rgb = cv2.cvtColor(logo_img, cv2.COLOR_BGR2RGB)
                col_idx = idx % 3  # Répartir entre les 3 colonnes
                with cols[col_idx]:
                    conf_text = f" (Confiance: {confidence:.2f})" if "confidence" in row else ""
                    st.image(
                        logo_img_rgb,
                        caption=f"Logo détecté : {logo_file}{conf_text}",
                        use_column_width=True
                    )
            else:
                with cols[idx % 3]:
                    st.write(f"Impossible de charger le logo : {logo_path}")

if __name__ == "__main__":
    main()