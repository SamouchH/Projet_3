# Assistant Vendeur AI - Projet 3

Une application Streamlit qui facilite la création d'annonces de vente de jeux vidéo grâce à l'intelligence artificielle.

## 🚀 Fonctionnalités principales

- **🔎 Classification d'images** avec Claude 3.5 pour identifier automatiquement la plateforme, la catégorie et le titre du jeu
- **✍️ Génération de descriptions** attractives avec Mistral ou Claude
- **🤖 Assistant hybride** combinant les forces des deux modèles d'IA
- **📊 Analyse de données** pour visualiser les distributions des catégories de jeux
- **🏷️ Outil de labelisation** pour étiqueter de nouvelles images de jeux

## 🖥️ Démarrage rapide

### Prérequis

- Docker et Docker Compose installés
- Une clé API pour Anthropic Claude (pour la classification d'images)
- Une clé API pour Mistral (optionnel, pour la génération de texte)

### Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/SamouchH/Projet_3.git
   cd Projet_3
   ```

2. Créez un fichier `.env` à la racine du projet avec vos clés API :
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-votre-clé-api
   OPENAI_API_KEY=sk-votre-clé-api (optionnel)
   ```

3. Lancez l'application Streamlit :

   **Sous Linux/macOS :**
   ```
   chmod +x run_streamlit_app.sh
   ./run_streamlit_app.sh
   ```

   **Sous Windows :**
   ```
   run_streamlit_app.bat
   ```

4. Accédez à l'application dans votre navigateur à l'adresse :
   ```
   http://localhost:8501
   ```

## 🤖 Utilisation de l'Assistant Hybride

L'assistant hybride est l'outil le plus complet de l'application:

1. Téléchargez une image de jeu vidéo (boîte, cartouche, etc.)
2. Cliquez sur "Analyser l'image avec Claude" pour détecter automatiquement:
   - La plateforme (PlayStation, Nintendo, etc.)
   - La catégorie spécifique (PS4, Game Boy Advance, etc.)
   - Le titre du jeu (quand il est visible sur l'image)
3. Complétez ou corrigez les informations si nécessaire (titre, état, prix, etc.)
4. Choisissez le modèle d'IA qui vous convient le mieux:
   - **Mistral**: Style dynamique et enthousiaste, idéal pour les annonces énergiques
   - **Claude**: Style élégant et détaillé, parfait pour les descriptions plus raffinées
5. Générez une description attractive pour votre annonce
6. Validez et exportez votre annonce

## 📄 Détail des pages

- **📊 [Analyses](/Analyses)** - Visualisation des données d'entraînement
- **🏷️ [Labelisation](/Labelisation)** - Outil d'étiquetage d'images
- **🔣 [Preprocessing](/Preprocessing)** - Traitement d'images avant analyse
- **🕵️‍♂️ [Benchmark](/Benchmark)** - Comparaison des performances des modèles
- **👩‍💻 [Assistant](/Assistant)** - Assistant basé sur Mistral
- **🔎 [Claude Assistant](/Claude_Assistant)** - Classification d'images avec Claude
- **🤖 [Hybrid Assistant](/Hybrid_Assistant)** - Assistant hybride Claude + Mistral (recommandé)
- **📚 [Documentation](/Documentation)** - Ressources et documentation

## 🛠️ Architecture technique

L'application utilise:
- **Streamlit** pour l'interface utilisateur
- **Anthropic Claude 3.5** pour l'analyse d'images et la génération de texte
- **Mistral 7B** pour la génération de descriptions
- **Docker** pour le déploiement

## 👥 Auteurs

- [Alexandre](https://github.com/alexdhn1)
- [Armelle](https://github.com/D41g0na)
- [Haroune](https://github.com/SamouchH)
- [Jimmy](https://github.com/JimmyRata)

## 📝 License

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.