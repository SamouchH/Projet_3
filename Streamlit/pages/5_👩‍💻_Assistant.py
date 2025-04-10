import streamlit as st
import numpy as np
from PIL import Image
from utils import generate_mistral_response, load_model, predict, category_labels


st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

# Initialisation de la clé "final_desc" dans session_state si elle n'existe pas
if "final_desc" not in st.session_state:
    st.session_state["final_desc"] = ""

st.markdown(
    """
## 🎯 **Comment utiliser cette application ?**
- **1️⃣ Téléchargez vos images** : elles seront analysées pour identifier le produit.
- **2️⃣ Vérifiez les informations extraites** : ajustez si nécessaire.
- **3️⃣ Générez automatiquement une description** et affinez-la à votre convenance.
- **4️⃣ Exportez votre annonce** prête à être publiée !
"""
)

st.write("L'assistant utilisera l'image uploader dans la page Preprocessing, sinon uploader une nouvelle image:")
uploaded_file = st.file_uploader("📤 Uploadez une image au format JPG", type=["jpg"])

if uploaded_file is not None:
    #Charger l'image
    image = Image.open(uploaded_file).convert('RGB')
    st.session_state["image_raw"] = np.array(image)
    st.success("✅ Nouvelle image chargée avec succès !")

# Chargement du modèle
model = load_model()
if "image_raw" in st.session_state:
    st.image(st.session_state["image_raw"], caption="Image d'origine",  use_container_width=True)

    #Preprocessing d'image
    #st.markdown("Pré-traitement utilisé: CLAHE & Sharpening")

    #Model
    if st.button('Lancer la catégorisation'):
        pred_index = predict(model, st.session_state["image_raw"])
        pred_category = CATEGORY_LABELS[pred_index]
        st.session_state["pred_marque"] = pred_category
        st.success(f"✅ Catégorie prédite : **{pred_category}**")

else:
    st.info("Aucune image disponible pour le moment.")

#Valeur d'essai
#pred_marque = st.session_state.get("pred_marque","Jeux Playstation")
# pred_platform = st.session_state.get("pred_platform","Playstation 4")


titre = st.text_input("Titre de l'annonce",value="")
platform = st.text_input("Platform", value=pred_marque)
etat = st.selectbox(
    "État du produit",["Sous Blister", "Neuf", "Très bon état", "Bon état", "État satisfaisant"])
description = st.text_area("Desciption du produit (facultatif)", value="")

if st.button("💡 Générer une description avec l'assistant IA"):
    prompt = f"""
    Tu es un assistant de rédaction d'annonce. Propose une description accrocheuse pour un jeu vidéo d'occasion.
    
    - Titre : {titre}
    - Plateforme : {platform}
    - État : {etat}
    
    Rédige un texte fluide en français, en peu de phrases, convaincant et clair. Le texte doit reprendre les informations fournit.
    """
    with st.spinner("L'IA rédige une description... ✍️"):
        description = generate_mistral_response(prompt)
        st.session_state["final_desc"] = description
        st.success("✅ Description générée !")

with st.form('formulaire_annonce'):
    st.text_area("Proposition d'annonce:", height=200, key="final_desc")
    submit = st.form_submit_button("Valider l'annonce")

if submit:
    st.success("Annonce enregistrée (simu)")
    st.write("**Titre:**", titre)
    st.write("**Platforme:**", platform)
    st.write("**État:**", etat)
    st.write("**Description:**", st.session_state["final_desc"])

