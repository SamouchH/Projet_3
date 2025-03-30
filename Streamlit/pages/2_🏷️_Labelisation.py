import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)
url_labeler = "https://github.com/SamouchH/Projet_3/blob/labelling/README.md"

st.subheader("Labelisation du set d'image")

st.markdown(
        """
    Avant d'entraîner nos modèles sur les images, nous avons d'abord procédé à une phase de **labellisation**.
    Cette étape essentielle nous a permis de construire des **batchs d'entraînements équilibrés**, en nous assurant que chaque catégorie soit correctement représentée.

    Pour cela, **Haroune** et **Armelle** ont utilisé un outil de labellisation d'image, conçu spécifiquement pour ce projet par Haroune.

    Voici un aperçu de l’interface de l’application :
    """
    )

img_path = "logos/labeller.jpg"
st.image(img_path, caption="Interface du labeler d'images", use_container_width=True)

st.markdown(f"👉 Vous pouvez tester l’outil vous-même en suivant ce lien : [Labeler GitHub]({url_labeler})")