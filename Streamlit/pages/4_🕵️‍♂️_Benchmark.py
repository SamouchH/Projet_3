import streamlit as st


st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

st.subheader("Analyse du set de données d'entrainement")

st.markdown(
    """
    Dans le cadre de notre projet, **Jimmy**, **Haroune** et **Alexandre** ont exploré plusieurs modèles de classification afin d’évaluer la meilleure approche pour notre jeu de données.

    L’objectif de ce benchmark est de comparer :
    - La **précision** des modèles
    - Le **temps d'entraînement**
    - La **capacité à généraliser** (via validation croisée)
    - Et leur **facilité d’intégration** dans notre application Streamlit

    👇 Retrouvez ci-dessous un aperçu de leurs travaux. Les détails techniques et résultats seront complétés au fur et à mesure de l’analyse.
    """
    )

st.markdown("""
    <style>
    div[data-baseweb="tab-list"] {
        justify-content: center;
        gap: 10rem;
    }
    </style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(['Alexandre', 'Haroune', 'Jimmy'])

with tab1:
    st.markdown(
    """
    Alexandre a travaillé sur la technologie OCR Tesseract.
Il a testé l'ensemble des méthodes de filtrage d’image afin d’évaluer celles offrant les meilleurs résultats avec Tesseract. Le filtre ayant donné les performances les plus satisfaisantes est le filtre de réduction de bruit (Denoised).

Lorsqu’un texte peut être extrait de l’image, celui-ci est ensuite analysé par un algorithme combinant un dictionnaire de référence, des expressions régulières, ainsi que plusieurs méthodes de similarité textuelle : Levenshtein, Jaro-Winkler, Char N-gram et FuzzyWuzzy.

À ce stade, la précision du système est très bonne, mais le rappel reste encore faible, ce qui signifie que nous ratons une partie des textes pertinents.

Les données extraites sont ensuite exploitées par plusieurs modèles de classification :

    Régression logistique — F1: 0.4362 | Accuracy: 0.5070 | Recall: 0.5070

    SVM — F1: 0.3498 | Accuracy: 0.4507 | Recall: 0.4507

    Random Forest — F1: 0.4536 | Accuracy: 0.5211 | Recall: 0.5211

    Gradient Boosting — F1: 0.4354 | Accuracy: 0.5070 | Recall: 0.5070

Par ailleurs, Alexandre a également développé un modèle de reconnaissance de logos permettant d’identifier les différentes plateformes (PlayStation, Xbox, etc.), avec une accuracy de 0.54.
    """
    )

with tab2:
    st.markdown(
    """
    Haroune a travaillé sur RapidOCR.
Les résultats obtenus avec cet outil donnent une précision de 47 % pour la catégorie et 48 % pour la sous-catégorie.

Ces performances relativement faibles s'expliquent en partie par le déséquilibre de la base de données, que vous pouvez visualiser via le treemap disponible dans la page "Analyse".
Par ailleurs, certaines images ne comportent ni logo identifiable, ni éléments textuels explicites permettant de faire le lien avec une catégorie comme PC Gaming.

Haroune s’est ensuite orienté vers l’expérimentation de modèles VLLM (Vision Language Large Models) tels que : Claude, OpenAI, Gemini, Mistral et DeepSeek.
    """
    )

with tab3:
    st.markdown(
    """
Jimmy a travaillé dans un premier temps avec DoctR, mais les résultats obtenus se sont révélés peu concluants : l'information textuelle n'était pas correctement extraite des images.

Il s’est ensuite orienté vers un réseau de neurones simple, dont la matrice de confusion a montré de bons résultats pour la classe PC Gaming, mais des performances plus faibles sur les autres catégories.
    """)
    img_path = "logos/cnn.png"
    st.image(img_path, caption="Matrice de confusion CNN", width=400)

    st.markdown(
        """
Par la suite, il a testé un modèle pré-entraîné, MobileNet V2, avec les résultats suivants :
Accuracy : 0.4623
Précision : 0.3107
    """)
    img_path = "logos/mobilenetv2.png"
    st.image(img_path, caption="Matrice de confusion MobileNet v2", width=400)

    st.markdown(
    """
Il a ensuite affiné ce modèle grâce à du fine-tuning, ce qui a permis d'améliorer les performances :
Accuracy : 0.5000
Précision : 0.5858

    """)
    img_path = "logos/MNV2_ft.png"
    st.image(img_path, caption="Matrice de confusion MobileNet v2 fine tune", width=400)

        st.markdown(
        """
Jimmy a entraîné un grad cam afon d'observer les zones reconnu par le modèle et nous pouvons constater que les zones ne sont pas les zones informatives qui nous intéresse.
    """)
    col1,col2 = st.columns(2)
    with col1:
        img_path = "logos/grad_cam1.png"
        st.image(img_path, caption="Grad cam sur une cartouche GameBoy", width=400)

    with col2:
        img_path = "logos/grad_cam2.png"
        st.image(img_path, caption="Grad cam sur le jeu Sims", width=400)
