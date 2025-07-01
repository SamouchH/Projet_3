import streamlit as st
import cv2
import numpy as np
from PIL import Image


st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)


st.markdown(
    """
Avant de tester les différents modèles, **Armelle** a exploré une large palette de traitements d’images afin d’améliorer la lisibilité des informations pour les algorithmes.
Parmi les méthodes testées : filtrage médian, réduction de bruit (denoising), binarisation adaptative, Canny, Watershed, Otsu, enhancement de contraste, dilatation/érosion, etc.

Après évaluation visuelle et expérimentation, notre choix s’est porté sur une combinaison de CLAHE (pour l'amélioration locale du contraste) et Sharpening (pour faire ressortir les contours), qui offrait le meilleur équilibre entre qualité et lisibilité.
"""
)

st.subheader("Exemple de traitement d'image : CLAHE et Sharpening")


uploaded_file = st.file_uploader("📤 Uploadez une image au format JPG", type=["jpg"])

if uploaded_file is not None:
    #Charger l'image
    image = Image.open(uploaded_file).convert('RGB')
    original = np.array(image)

    #Stocker dans session_state
    st.session_state['image_raw'] = original

    # Traitement CLAHE
    gray = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    clahe_rgb = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB)
    st.session_state["image_clahe"] = clahe_rgb

    # Traitement Sharpening
    kernel_sharpening = np.array([[-1, -1, -1],
                                [-1,  9, -1],
                                [-1, -1, -1]])
    sharpened = cv2.filter2D(original, -1, kernel_sharpening)
    st.session_state["image_sharp"] = sharpened

    # Combo : CLAHE puis sharpening
    combo = cv2.filter2D(clahe_rgb, -1, kernel_sharpening)
    st.session_state["image_combo"] = combo

    # Affichage
    st.markdown("### 🔍 Résultat des traitements")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.image(original, caption="Image originale", use_container_width=True)
    with col2:
        st.image(clahe_rgb, caption="Après CLAHE", use_container_width=True)
    with col3:
        st.image(sharpened, caption="Après Sharpening", use_container_width=True)
    with col4:
        st.image(combo, caption="CLAHE + Sharpening", use_container_width=True)

else:
    st.info("Veuillez uploader une image pour lancer le traitement.")

