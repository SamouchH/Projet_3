import streamlit as st


st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)

st.subheader("Analyse du set de données d'entrainement")

st.markdown(
    """
    Dans le cadre de notre projet, **Jimmy**, **Haroune** et **Alexandre** ont exploré plusieurs modèles de classification afin d'évaluer la meilleure approche pour notre jeu de données.

    L'objectif de ce benchmark est de comparer :
    - La **précision** des modèles
    - Le **temps d'entraînement**
    - La **capacité à généraliser** (via validation croisée)
    - Et leur **facilité d'intégration** dans notre application Streamlit

    👇 Retrouvez ci-dessous un aperçu de leurs travaux. Les détails techniques et résultats seront complétés au fur et à mesure de l'analyse.
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
Il a testé l'ensemble des méthodes de filtrage d'image afin d'évaluer celles offrant les meilleurs résultats avec Tesseract. Le filtre ayant donné les performances les plus satisfaisantes est le filtre de réduction de bruit (Denoised).

Lorsqu'un texte peut être extrait de l'image, celui-ci est ensuite analysé par un algorithme combinant un dictionnaire de référence, des expressions régulières, ainsi que plusieurs méthodes de similarité textuelle : Levenshtein, Jaro-Winkler, Char N-gram et FuzzyWuzzy.

À ce stade, la précision du système est très bonne, mais le rappel reste encore faible, ce qui signifie que nous ratons une partie des textes pertinents.

Les données extraites sont ensuite exploitées par plusieurs modèles de classification :

    Régression logistique — F1: 0.4362 | Accuracy: 0.5070 | Recall: 0.5070

    SVM — F1: 0.3498 | Accuracy: 0.4507 | Recall: 0.4507

    Random Forest — F1: 0.4536 | Accuracy: 0.5211 | Recall: 0.5211

    Gradient Boosting — F1: 0.4354 | Accuracy: 0.5070 | Recall: 0.5070

Par ailleurs, Alexandre a également développé un modèle de reconnaissance de logos permettant d'identifier les différentes plateformes (PlayStation, Xbox, etc.), avec une accuracy de 0.54.
    """
    )

with tab2:
    st.markdown(
    """
    Haroune a travaillé sur RapidOCR, une bibliothèque OCR performante basée sur les modèles PaddleOCR.
    
L'implémentation se déroule en plusieurs étapes :
1. **Détection de texte** : RapidOCR identifie les éléments textuels présents sur les images de jeux
2. **Post-traitement** : Le texte détecté est traité par un système de classification basé sur des mots-clés
3. **Matching de mots-clés** : Attribution d'un score pour chaque catégorie et sous-catégorie en fonction des correspondances

Comme on peut le voir sur l'exemple ci-dessous, RapidOCR détecte différents éléments textuels sur une boîte de jeu avec leurs scores de confiance respectifs. Plus le score est proche de 1, plus l'OCR est confiant dans sa détection :
    """
    )
    
    # Create columns for layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Directly embed example image using base64 for reliability
        from PIL import Image
        import io
        import base64
        import requests
        from io import BytesIO
        
        # Use a placeholder image - in the real application, replace this with the actual RapidOCR screenshot
        st.write("Visualisation de détection OCR :")
        
        # Load a sample game boy advance image for demonstration
        try:
            # Display the base image with the OCR bounding boxes
            st.image("logos/rapidocr_example.png", caption="Exemple de zones détectées par RapidOCR sur une boîte de jeu", use_container_width=True)
            st.caption("Note: Les zones vertes représentent les régions où du texte a été détecté avec la confiance associée.")
        except Exception as e:
            st.error(f"Impossible de charger l'image d'exemple: {e}")
            # Create a simple placeholder image
            img = Image.new('RGB', (600, 300), color = (240, 240, 240))
            st.image(img, caption="Placeholder - Image d'exemple non disponible", use_container_width=True)
    
    with col2:
        # Example text detection results
        st.markdown("""
        **Texte détecté par RapidOCR:**
        ```
        "Asterix" (0.93)
        "FOR" (0.85)
        "JEUX!" (0.94)
        "GAMEBOYADVANCE" (0.98)
        "&OBEF" (0.86)
        "PAF!" (0.96)
        "PARTOLITATSY" (0.85)
        "Nintendo" (0.96)
        ```
        
        Le texte détecté est ensuite utilisé pour la classification par catégorie et sous-catégorie.
        """)
    
    st.markdown(
    """
Le post-traitement utilise un dictionnaire de mots-clés spécifiques à chaque plateforme :
- Nintendo : ["nintendo", "game boy", "gameboy", "advance", "gba", "switch", "wii", "nes", "3ds", "ds"]
- PlayStation : ["playstation", "ps1", "ps2", "ps3", "ps4", "ps5", "sony"]
- Xbox : ["xbox", "microsoft", "360", "one", "series"]
    
Dans l'exemple ci-dessus, les mots-clés "nintendo" et "gameboy advance" permettent de classifier l'image dans la catégorie **Nintendo** et la sous-catégorie **Jeux Game Boy Advance**.

Le système attribue un score de confiance en calculant le ratio entre les mots-clés correspondants et le nombre total de mots-clés pour cette catégorie.
    
Les résultats obtenus avec cet outil donnent une précision de 47% pour la catégorie et 48% pour la sous-catégorie.
    """
    )
    
    # Add section for confusion matrix
    st.subheader("Matrice de confusion pour RapidOCR")
    
    try:
        # Try to load the confusion matrix image
        st.image("logos/confusion_matrix_rapidocr.png", caption="Matrice de confusion pour la classification par catégorie avec RapidOCR", use_container_width=True)
    except Exception as e:
        st.error(f"Impossible de charger la matrice de confusion: {e}")
        
    st.markdown("""
    La matrice de confusion ci-dessus révèle plusieurs informations intéressantes :
    
    - **Points forts** : RapidOCR est relativement performant pour la détection des jeux Nintendo (74%), PlayStation (77%) et repère correctement tous les jeux SEGA (100%).
    
    - **Faiblesses** : L'algorithme a tendance à classifier de nombreux jeux comme "Unknown" (inconnu), en particulier pour Xbox (100%) et SEGA (100%).
    
    - **Confusion spécifique** : 16% des jeux Nintendo sont incorrectement classifiés comme PC Gaming, tandis que 26% sont considérés comme inconnus. Pour PlayStation, 19% sont incorrectement classifiés comme inconnus.
    
    Cette matrice explique pourquoi l'accuracy globale reste à 47% - l'OCR parvient à bien détecter certaines catégories mais échoue complètement sur d'autres, souvent par manque d'indices textuels distinctifs.
    """)
    
    # Add subcategory confusion matrix
    st.subheader("Matrice de confusion pour les sous-catégories")
    
    try:
        # Try to load the subcategory confusion matrix image
        st.image("logos/confusion_subcat.png", caption="Matrice de confusion pour la classification par sous-catégorie avec RapidOCR", use_container_width=True)
    except Exception as e:
        st.error(f"Impossible de charger la matrice de confusion des sous-catégories: {e}")
        
    st.markdown("""
    Pour les sous-catégories, le modèle montre également des performances intéressantes :
    
    - **Excellentes performances** sur certaines sous-catégories spécifiques comme Game Boy, Game Boy Advance, Nintendo Switch, Nintendo Wii, PS1, Super Nintendo et les consoles Xbox (scores de 100%).
    
    - **Bonnes performances** sur Nintendo DS (71%), Jeux PS2 (89%), Jeux PS4 (75%).
    
    - **Performances moyennes** pour Jeux PC (68%) et Jeux PS3 (67%), avec une tendance à la confusion entre ces plateformes.
    
    - **Confusion notable** pour les jeux PS Vita qui sont classifiés comme PS1 dans 50% des cas.
    
    Ces résultats plus détaillés montrent que l'OCR est particulièrement efficace pour identifier les mentions explicites de plateformes spécifiques, mais peine à différencier certaines générations de consoles lorsque les indices textuels sont similaires.
    """)
    
    st.markdown(
    """
Ces performances relativement faibles s'expliquent par plusieurs facteurs :
- Le déséquilibre de la base de données, visualisable via le treemap de la page "Analyse"
- L'absence de texte ou logo distinctif sur certaines images
- Les limitations de l'OCR face aux polices stylisées des jeux vidéo
- La dépendance à des listes de mots-clés prédéfinies qui ne peuvent couvrir toutes les variations

La corrélation entre les résultats obtenus par RapidOCR et d'autres solutions comme Tesseract (utilisée par Alexandre) montre que l'OCR peut être un outil précieux pour la détection de certains types de jeux, mais n'est pas suffisante comme solution unique.

Haroune s'est ensuite orienté vers l'expérimentation de modèles VLLM (Vision Language Large Models) tels que : Claude, OpenAI, Gemini et Mistral, qui offrent une meilleure compréhension du contexte visuel grâce à l'apprentissage multimodal.
    """
    )

with tab3:
    st.markdown(
    """
Jimmy a travaillé dans un premier temps avec DoctR, mais les résultats obtenus se sont révélés peu concluants : l'information textuelle n'était pas correctement extraite des images.

Il s'est ensuite orienté vers un réseau de neurones simple, dont la matrice de confusion a montré de bons résultats pour la classe PC Gaming, mais des performances plus faibles sur les autres catégories.
    """)
    img_path = "logos/cnn.png"
    st.image(img_path, caption="Matrice de confusion CNN", use_container_width=True)

    st.markdown(
        """
Par la suite, il a testé un modèle pré-entraîné, MobileNet V2, avec les résultats suivants :
Accuracy : 0.4623
Précision : 0.3107
    """)
    img_path = "logos/mobilenetv2.png"
    st.image(img_path, caption="Matrice de confusion MobileNet v2", use_container_width=True)

    st.markdown(
    """
Il a ensuite affiné ce modèle grâce à du fine-tuning, ce qui a permis d'améliorer les performances :
Accuracy : 0.5000
Précision : 0.5858

    """)
    img_path = "logos/MNV2_ft.png"
    st.image(img_path, caption="Matrice de confusion MobileNet v2 fine tune", use_container_width=True)

    st.markdown(
        """
Jimmy a entraîné un **Grad-CAM** afin d'observer les zones activées par le modèle lors de la prédiction.  
Nous pouvons constater que ces zones ne correspondent pas toujours aux éléments informatifs attendus, comme les logos ou le texte présents sur l'image.
    
    """)
    col1,col2 = st.columns(2)
    with col1:
        img_path = "logos/grad_cam1.png"
        st.image(img_path, caption="Grad cam sur une cartouche GameBoy", use_container_width=True)

    with col2:
        img_path = "logos/grad_cam2.png"
        st.image(img_path, caption="Grad cam sur le jeu Sims", use_container_width=True)
