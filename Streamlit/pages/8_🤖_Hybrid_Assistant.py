import streamlit as st
import numpy as np
from PIL import Image
import base64
import json
import re
import os
import requests
from io import BytesIO
from utils import generate_mistral_response

st.set_page_config(
    page_title="Hybrid Assistant",
    page_icon="🤖",
)

# Initializing session state variables
if "final_desc" not in st.session_state:
    st.session_state["final_desc"] = ""
if "pred_category" not in st.session_state:
    st.session_state["pred_category"] = ""
if "pred_subcategory" not in st.session_state:
    st.session_state["pred_subcategory"] = ""
if "pred_title" not in st.session_state:
    st.session_state["pred_title"] = ""

# Get API key from secrets
API_KEY = st.secrets["ANTHROPIC_API_KEY"]
MODEL_NAME = "claude-3-5-sonnet-20241022"

# Classification function using direct API requests to Claude
def classify_image_with_claude(image):
    """
    Classifies an image using direct API requests to Claude.
    
    Args:
        image (PIL.Image.Image): The image to classify
        
    Returns:
        tuple: (category, subcategory, title)
    """
    # Convert PIL image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Updated classification prompt that also asks for the game title
    classification_prompt = """You are a game labeler. Analyze this video game image and extract the following information:

    1. CATEGORY (choose exactly one):
    - PC Gaming
    - PlayStation
    - Nintendo
    - Xbox
    - SEGA [use uppercase only]
    - Autre [use only if none above match]

    2. SUBCATEGORY (choose exactly one):
    - Jeux PC
    - Jeux PS3
    - Jeux Nintendo DS
    - Jeux PS2
    - Jeux Xbox 360
    - Jeux Nintendo Wii
    - Jeux PS4
    - Jeux Game Boy Advance
    - Jeux PS1
    - Jeux Xbox One
    - Jeux PSP
    - Autre categorie [use only if none above match]

    3. GAME TITLE:
    Identify the exact title of the game shown in the image. If you can't determine the exact title, respond with "Jeu vidéo" (default value).

    Look for logos, platform indicators, game packaging format, and text on the box/cartridge to identify all information.

    RESPONSE FORMAT (use EXACTLY this structure):
    {
        "category": "CATEGORY",
        "subcategory": "SUBCATEGORY",
        "title": "EXACT GAME TITLE"
    }
    """
    
    # Set up the request payload
    payload = {
        "model": MODEL_NAME,
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg", 
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": classification_prompt
                    }
                ]
            }
        ]
    }
    
    # Set up the headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    try:
        # Make the API request
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the text content
            text_content = response_data['content'][0]['text']
            
            # Try to parse JSON from the response text
            json_match = re.search(r'(\{.*\})', text_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    classification = json.loads(json_str)
                    category = classification.get('category', 'Autre')
                    subcategory = classification.get('subcategory', 'Autre categorie')
                    title = classification.get('title', 'Jeu vidéo')
                    return category, subcategory, title
                except json.JSONDecodeError:
                    return "Autre", "Autre categorie", "Jeu vidéo"
            else:
                return "Autre", "Autre categorie", "Jeu vidéo"
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return "Autre", "Autre categorie", "Jeu vidéo"
    except Exception as e:
        st.error(f"Exception: {e}")
        return "Autre", "Autre categorie", "Jeu vidéo"

# Function to generate description using Claude
def generate_claude_description(prompt):
    """Generate a description using Claude API"""
    try:
        # Set up the request payload
        payload = {
            "model": MODEL_NAME,
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Set up the headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        # Make the API request
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data['content'][0]['text'].strip()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return "Erreur lors de la génération de la description."
    
    except Exception as e:
        st.error(f"Exception: {e}")
        return "Erreur lors de la génération de la description."

# Title and description
st.title("🤖 Hybrid Assistant")
st.markdown(
    """
## 🎮 Assistant de création d'annonces pour jeux vidéo

Cet assistant combine deux technologies d'IA avancées pour faciliter la création d'annonces:

1. **🔎 Claude** analyse l'image pour identifier la plateforme et la catégorie du jeu
2. **✍️ Mistral ou Claude** génère automatiquement une description attractive pour votre annonce

Téléchargez simplement une image, validez la classification, et obtenez une description prête à l'emploi!
"""
)

# Image upload
st.write("Téléchargez une image de jeu vidéo pour commencer :")
uploaded_file = st.file_uploader("📤 Uploadez une image au format JPG", type=["jpg", "jpeg", "png"])

# Apply classification if image is uploaded
if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file).convert('RGB')
    st.session_state["image_raw"] = np.array(image)
    st.session_state["image_pil"] = image
    
    # Display image
    st.image(st.session_state["image_raw"], caption="Image d'origine", use_container_width=True)
    
    # Classification button
    if st.button('Analyser l\'image avec Claude'):
        with st.spinner("Analyse de l'image en cours..."):
            # Use the PIL image if available, otherwise convert from numpy array
            if "image_pil" in st.session_state:
                image_to_analyze = st.session_state["image_pil"]
            else:
                image_to_analyze = Image.fromarray(st.session_state["image_raw"])
            
            # Call Claude for classification
            category, subcategory, title = classify_image_with_claude(image_to_analyze)
            
            # Store prediction in session state
            st.session_state["pred_category"] = category
            st.session_state["pred_subcategory"] = subcategory
            st.session_state["pred_title"] = title
            
            # Display results
            st.success(f"✅ Classification réussie!")
            
            # Display a more visual, card-like result
            st.markdown("""
            <style>
            .result-card {
                background-color: rgba(49, 51, 63, 0.7);
                border-radius: 10px;
                padding: 15px;
                border: 1px solid rgba(250, 250, 250, 0.2);
                margin-bottom: 20px;
            }
            .result-header {
                color: #4CAF50;
                font-size: 1.2em;
                margin-bottom: 10px;
            }
            .result-item {
                margin-bottom: 8px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-header">🎮 Analyse de l\'image</div>', unsafe_allow_html=True)
            
            # Show results in a nice format
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="result-item"><b>Catégorie</b>: {category}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="result-item"><b>Sous-catégorie</b>: {subcategory}</div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="result-item"><b>Titre identifié</b>: {title}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add a note about editing if needed
            st.info("💡 Vous pouvez modifier ces informations dans le formulaire ci-dessous si nécessaire.")

# Second part: Generate description with chosen model if we have a classification
if st.session_state.get("pred_category", "") and st.session_state.get("pred_subcategory", ""):
    st.markdown("---")
    st.subheader("📝 Créer votre annonce")
    
    # Form for the listing details
    titre = st.text_input("Titre de l'annonce", value=st.session_state.get("pred_title", ""))
    platform = st.text_input("Plateforme", value=f"{st.session_state['pred_category']} - {st.session_state['pred_subcategory']}")
    etat = st.selectbox(
        "État du produit",
        ["Sous Blister", "Neuf", "Très bon état", "Bon état", "État satisfaisant"]
    )
    prix = st.number_input("Prix (€)", min_value=0.0, max_value=1000.0, value=30.0, step=5.0)
    
    # Additional details (optional)
    with st.expander("Détails supplémentaires (facultatifs)"):
        notes = st.text_area("Notes ou spécificités", value="", placeholder="Ex: Edition collector, Jeu complet avec notice...")
        annee = st.text_input("Année de sortie", value="")
        genre = st.text_input("Genre", value="", placeholder="Ex: Aventure, FPS, RPG...")
    
    # Model selection
    model_choice = st.radio("Choisir le modèle pour générer la description :", ["Mistral", "Claude"])
    
    # Improved prompt for both models
    def build_prompt(model_type):
        base_prompt = f"""Tu es un expert en rédaction d'annonces pour jeux vidéo d'occasion. Rédige une description commerciale convaincante pour :

- Titre : {titre if titre else "Jeu vidéo"}
- Plateforme : {platform}
- État : {etat}
- Prix : {prix}€
        """
        
        # Add optional fields if provided
        if notes:
            base_prompt += f"\n- Spécificités : {notes}"
        if annee:
            base_prompt += f"\n- Année de sortie : {annee}"
        if genre:
            base_prompt += f"\n- Genre : {genre}"
        
        # Different instructions based on model
        if model_type == "Mistral":
            base_prompt += """

INSTRUCTIONS:
1. Crée un texte accrocheur en 3-4 phrases qui donne envie d'acheter
2. Utilise un ton enthousiaste, dynamique et inspirant
3. Inclus des points numérotés (1), (2), etc. pour structurer le message
4. Mentionne spécifiquement :
   - La valeur/rareté du jeu
   - L'état du produit (insiste sur la qualité)
   - Le rapport qualité/prix avantageux
5. Termine par une incitation à l'action (appel à acheter rapidement)

N'invente pas de détails fictifs sur le jeu ou ses fonctionnalités.
"""
        else:  # Claude
            base_prompt += """

INSTRUCTIONS:
1. Rédige une description captivante et professionnelle de 4-5 phrases
2. Utilise un style élégant qui met en valeur la qualité du produit
3. Structure le texte avec une introduction attrayante, un corps détaillé et une conclusion
4. Inclus des marqueurs numériques (1), (2), etc. pour organiser l'information
5. Mentionne explicitement:
   - Ce qui rend ce jeu spécial ou recherché
   - Les garanties liées à son état
   - Pourquoi c'est une opportunité à saisir à ce prix
6. Évoque le côté collection/nostalgie pour les jeux plus anciens
7. Termine par une formule qui crée un sentiment d'urgence

Reste factuel, sans inventer de caractéristiques.
"""
        return base_prompt
    
    # Generate description button
    if st.button(f"💡 Générer une description avec {model_choice}"):
        with st.spinner(f"L'IA {model_choice} rédige une description... ✍️"):
            prompt = build_prompt(model_choice)
            
            # Generate description using selected model
            if model_choice == "Mistral":
                description = generate_mistral_response(prompt)
            else:  # Claude
                description = generate_claude_description(prompt)
                
            st.session_state["final_desc"] = description
            st.success("✅ Description générée !")
    
    # Format the textarea with a custom style to make it more visible
    st.markdown("""
    <style>
    textarea {
        border: 1px solid #4CAF50 !important;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show the final form with the generated description
    with st.form('formulaire_annonce'):
        st.text_area("Description de l'annonce:", height=200, key="final_desc")
        submit = st.form_submit_button("💾 Valider l'annonce")
    
    if submit:
        st.balloons()
        st.success("🎉 Annonce enregistrée avec succès!")
        
        # Show a preview of the final announcement with improved styling
        st.markdown("### 🔍 Aperçu de votre annonce")
        
        st.markdown("""
        <style>
        .listing-preview {
            background-color: rgba(49, 51, 63, 0.7);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(250, 250, 250, 0.2);
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="listing-preview">', unsafe_allow_html=True)
        
        preview_col1, preview_col2 = st.columns([1, 2])
        
        with preview_col1:
            if "image_raw" in st.session_state:
                st.image(st.session_state["image_raw"], caption="Image du produit", use_container_width=True)
        
        with preview_col2:
            st.markdown(f"### {titre}")
            st.markdown(f"**Plateforme:** {platform}")
            st.markdown(f"**État:** {etat}")
            st.markdown(f"**Prix:** {prix}€")
            
            if genre or annee:
                details = []
                if genre:
                    details.append(f"Genre: {genre}")
                if annee:
                    details.append(f"Année: {annee}")
                st.markdown(f"**Détails:** {' | '.join(details)}")
                
            st.markdown("**Description:**")
            st.markdown(f"{st.session_state['final_desc']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add export options
        st.markdown("### 📤 Exporter votre annonce")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            st.download_button(
                label="📝 Exporter en texte",
                data=f"""
                {titre}
                
                Plateforme: {platform}
                État: {etat}
                Prix: {prix}€
                {f'Genre: {genre}' if genre else ''}
                {f'Année: {annee}' if annee else ''}
                
                Description:
                {st.session_state['final_desc']}
                """,
                file_name="annonce_jeu_video.txt",
                mime="text/plain",
            )
        
        with export_col2:
            st.markdown("🔗 Partagez directement sur :")
            st.button("LeBonCoin (simulation)", disabled=True)
            st.button("Vinted (simulation)", disabled=True)
            
else:
    # Show this if no image has been analyzed yet
    if uploaded_file is not None:
        st.info("👆 Cliquez sur 'Analyser l'image avec Claude' pour commencer.")
    else:
        st.info("⬆️ Veuillez télécharger une image pour commencer l'analyse.")
        
        # Example explanation at the bottom of the page
        st.markdown("""
        ### 🎮 Comment utiliser l'assistant hybride:
        
        1. **Téléchargez une image** de jeu vidéo (boîte, cartouche, etc.)
        2. **Analysez l'image avec Claude** pour détecter automatiquement:
           - La plateforme (PlayStation, Nintendo, etc.)
           - La catégorie spécifique (PS4, Game Boy Advance, etc.)
           - Le titre du jeu (quand il est visible sur l'image)
        3. **Complétez ou corrigez les informations** sur votre annonce
        4. **Choisissez le modèle d'IA** qui vous convient le mieux:
           - **Mistral**: Style dynamique et enthousiaste, idéal pour les annonces énergiques
           - **Claude**: Style élégant et détaillé, parfait pour les descriptions plus raffinées
        5. **Générez une description attractive** pour votre annonce
        6. **Validez et exportez** votre annonce
        
        Pour des résultats optimaux, utilisez des images où la boîte ou la cartouche du jeu est clairement visible et où le titre est lisible.
        """) 