import streamlit as st
import pandas as pd
from utils import get_labeling_dir
import subprocess
import sys

st.set_page_config(
    page_title="Assistant vendeur",
    page_icon="👩‍💻",
)
url_labeler = "https://github.com/SamouchH/Projet_3/blob/labelling/README.md"
#url_labeler = "http://localhost:5173"

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

#st.markdown(f"[Ouvrir le labeller dans une nouvelle fenêtre]({url_labeler})", unsafe_allow_html=True)

# Add tab system for frontend and backend
tab1, tab2 = st.tabs(["Frontend (React)", "Backend (FastAPI)"])

with tab1:
    # Add instructions for running the labeling application
    st.markdown("## Interface de labellisation (Frontend React)")

    st.markdown(
        """
        L'application de labellisation est développée avec React et s'exécute localement. Suivez ces étapes pour démarrer le frontend :
        
        ```bash
        # Naviguez vers le répertoire de l'application
        cd labeling_plateform
        
        # Installez les dépendances (si ce n'est pas déjà fait)
        npm install
        
        # Démarrez l'application
        npm run dev
        ```
        
        **Accédez à l'application** en ouvrant votre navigateur à l'adresse :
        """
    )

    st.code("http://localhost:5173", language="bash")

    # Add a button to launch the application
    st.markdown("### Démarrer le frontend directement")

    # if st.button("Lancer l'interface de labellisation"):
    #     try:
    #         # Get the labeling directory path
    #         labeling_dir = get_labeling_dir()
            
    #         # Check if npm is available
    #         npm_check = subprocess.run(["npm", "--version"], 
    #                                     capture_output=True, 
    #                                     text=True,
    #                                     shell=True)
            
    #         if npm_check.returncode == 0:
    #             # Start the application using npm
    #             st.info("Démarrage de l'application React...")
                
    #             # On Windows, we need to use shell=True
    #             if sys.platform == 'win32':
    #                 process = subprocess.Popen(
    #                     "cd /d \"{}\" && npm run dev -- --host".format(labeling_dir), 
    #                     shell=True
    #                 )
    #             else:
    #                 # For Unix-based systems
    #                 process = subprocess.Popen(
    #                     "cd \"{}\" && npm run dev -- --host".format(labeling_dir),
    #                     shell=True
    #                 )
                
    #             st.success("Application démarrée ! Accédez-y à l'adresse : http://localhost:5173")
    #         else:
    #             st.error("npm n'est pas installé ou n'est pas disponible dans le PATH.")
    #             st.info("Veuillez installer Node.js et npm, puis réessayer.")
    #     except Exception as e:
    #         st.error(f"Erreur lors du démarrage de l'application : {str(e)}")
    #         st.info("Veuillez démarrer l'application manuellement en suivant les instructions ci-dessus.")

    # Add a link button to open the application in a new tab
    st.markdown(
        """
        <a href="http://localhost:5173" target="_blank">
            <button style="background-color:#4CAF50; color:white; border:none; padding:12px 20px; text-align:center; 
            text-decoration:none; display:inline-block; font-size:16px; margin:4px 2px; cursor:pointer; border-radius:4px;">
                Ouvrir l'interface de labellisation
            </button>
        </a>
        """, 
        unsafe_allow_html=True
    )

with tab2:
    st.markdown("## API de labellisation (Backend FastAPI)")
    
    st.markdown(
        """
        Le backend FastAPI fournit des endpoints pour sauvegarder et récupérer des données de labellisation. Pour démarrer le backend :
        
        ```bash
        # Naviguez vers le répertoire de l'application
        cd labeling_plateform
        
        # Installez les dépendances Python (si ce n'est pas déjà fait)
        pip install -r api-requirements.txt
        
        # Démarrez le serveur FastAPI
        python api_server.py
        ```
        
        **Accédez à la documentation de l'API** en ouvrant votre navigateur à l'adresse :
        """
    )
    
    st.code("http://localhost:8000/docs", language="bash")
    
    # Add a button to launch the FastAPI server
    st.markdown("### Démarrer le backend directement")
    
    if st.button("Lancer le serveur FastAPI"):
        try:
            # Get the labeling directory path
            labeling_dir = get_labeling_dir()
            
            # Start the FastAPI server
            st.info("Démarrage du serveur FastAPI...")
            
            # On Windows, we need to use shell=True
            if sys.platform == 'win32':
                process = subprocess.Popen(
                    "cd /d \"{}\" && python api_server.py".format(labeling_dir),
                    shell=True
                )
            else:
                # For Unix-based systems
                process = subprocess.Popen(
                    "cd \"{}\" && python api_server.py".format(labeling_dir),
                    shell=True
                )
            
            st.success("Serveur FastAPI démarré ! Documentation disponible à l'adresse : http://localhost:8000/docs")
        except Exception as e:
            st.error(f"Erreur lors du démarrage du serveur FastAPI : {str(e)}")
            st.info("Veuillez démarrer le serveur manuellement en suivant les instructions ci-dessus.")
    
    # Add a link button to open the API docs in a new tab
    st.markdown(
        """
        <a href="http://localhost:8000/docs" target="_blank">
            <button style="background-color:#1E88E5; color:white; border:none; padding:12px 20px; text-align:center; 
            text-decoration:none; display:inline-block; font-size:16px; margin:4px 2px; cursor:pointer; border-radius:4px;">
                Ouvrir la documentation de l'API
            </button>
        </a>
        """, 
        unsafe_allow_html=True
    )

# Add instructions for using the labeler
st.markdown(
    """
    ## Utilisation de l'application
    
    1. Cliquez sur le bouton d'upload pour sélectionner vos images
    2. Pour chaque image, choisissez une catégorie et une sous-catégorie
    3. Naviguez entre les images avec les boutons précédent/suivant
    4. Exportez vos annotations au format CSV en cliquant sur le bouton d'export
    
    👉 Vous pouvez également consulter le code source et les instructions sur GitHub : [Labeler GitHub]({})
    """.format(url_labeler)
)

# Add the highlighted section for the launcher script at the bottom with improved styling
st.markdown("---")
st.markdown("## Option alternative : démarrage rapide par script")

st.markdown(
    """
    <div style="background-color:#2E4057; padding:20px; border-radius:10px; margin-top:20px; border:1px solid #4CAF50;">
        <h3 style="color:#FF9F1C; margin-top:0;">⚡ Démarrage via script</h3>
        <p style="color:#FFFFFF;">Pour les utilisateurs avancés, vous pouvez lancer la plateforme complète (frontend et backend) en une seule commande :</p>
        <ol style="color:#FFFFFF;">
            <li>Ouvrez un terminal à la racine du projet</li>
            <li>Exécutez la commande ci-dessous :</li>
        </ol>
        <div style="background-color:#1E1E1E; padding:10px; border-radius:5px; margin-top:10px;">
            <code style="color:#569CD6;">python start_labeling.py</code>
        </div>
        <p style="color:#FFFFFF; margin-top:15px;">Ce script lancera automatiquement :</p>
        <ul style="color:#FFFFFF;">
            <li>Le frontend React à l'adresse <span style="color:#4EC9B0;">http://localhost:5173</span></li>
            <li>Le backend FastAPI à l'adresse <span style="color:#4EC9B0;">http://localhost:8000</span></li>
            <li>Optionnellement, l'application Streamlit si vous le souhaitez</li>
        </ul>
        <p style="color:#FFFFFF; font-style:italic; margin-top:15px;">Note : Utilisez Ctrl+C dans le terminal pour arrêter tous les services.</p>
    </div>
    """, 
    unsafe_allow_html=True
)