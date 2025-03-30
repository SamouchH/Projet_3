import streamlit as st

st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)


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

if "image_raw" in st.session_state:
    st.image(st.session_state["image_raw"], caption="Image d'origine", use_column_width=True)

    #Preprocessing d'image
    st.markdown("Pré-traitement utilisé: CLAHE & Sharpening")

    #Model
    if st.button('Lancer la catégorisation'):
        st.info('Modèle ici')

else:
    st.info("Aucune image disponible pour le moment.")

#Valeur d'essai
pred_marque = st.session_state.get("pred_marque","Jeux Playstation")
pred_platform = st.session_state.get("pred_platform","Playstation 4")

with st.form('form'):
    titre = st.text_input("Titre de l'annonce",value=pred_marque)
    platform = st.text_input("Platform", value=pred_platform)
    etat = st.selectbox(
        "État du produit",
        options=["Sous Blister", "Neuf", "Très bon état", "Bon état", "État satisfaisant"]
    )
    description = st.text_area("Desciption du produit", value="")

    submit = st.form_submit_button("Valider l'annonce")

if submit:
    st.success("Annonce enregistrée (simu)")
    st.write("**Titre:**", titre)
    st.write("**Platforme:**", platform)
    st.write("**État:**", etat)
    st.write("**Description:**", description)

