# Assistant Vendeur IA de Jeux Vidéo

Une plateforme intelligente facilitant la création d'annonces de vente de jeux vidéo grâce à l'intelligence artificielle.
Le projet se compose de deux modules complémentaires:

- Une ** API REST sécurisée** pour la classification d'images via deep learning (MobileNetV2)
- Une **application Streamlit** pour  créer des annonces enrichies avec Claude & Mistral.

---

## Fonctionnalités principales

### API (FastAPI)
- Authentification JWT + gestion des rôles
- Classification d'images en temps réel (PlayStation, Nintendo, etc.)
- Prédiction par lots + historique utilisateur
- Interface d'administration + statistiques
- Monitoring Prometheus + Grafana
- Tests unitaires et d'intégration inclus

### Application Streamlit
- Analyse visuelle des catégories de jeux
- Outil de labellisation d'images
- Générateur de description (Claude ou Mistral)
- Assistant hybride combinant image + texte
- Export facile des annonces

## Architecture du projet

PROJET_3/
├── api/ # Backend FastAPI
│ ├── core/ # Configuration, sécurité, modèles Pydantic
│ ├── services/ # Logique métier (auth, prédiction, admin)
│ ├── data/, logs/, uploads/ # Données & fichiers API
│ ├── modele_cnn_transfer.h5 # Modèle CNN entraîné
│ ├── main.py # Point d’entrée API
│ └── requirements.txt
│
├── Streamlit/ # Application Streamlit
│ ├── pages/ # Pages thématiques (EDA, assistant, etc.)
│ ├── logos/, .streamlit/ # Assets et config
│ ├── Home.py, utils.py # Page principale & utilitaires
│ └── modele_cnn_transfer.h5 # Modèle partagé avec l’API
│
├── Models/ # Notebooks d’expérimentation
│ └── dev_jimmy.ipynb, test_model.ipynb
│
├── Test/ # Tests automatisés
│ ├── test_api.py # Tests API
│ ├── test_utils.py # Tests fonctions
│ └── test_predict.jpg # Image de test
│
├── monitoring/ # Fichiers Prometheus/Grafana
│ └── prometheus.yml
│
├── docker-compose.yml # Démarrage de tous les services
├── Dockerfile (dans api/) # Image API
├── .env # Clés API Claude / Mistral
└── start_api.py # Lancement API manuel

## Prérequis
- Python 3.10+ (si non Docker)
- Docker & Docker Compose
- Clé API **Anthropic Claude** (obligatoire)
- Clé API **Mistral** (optionnelle)

---

## Installation & Lancement

### Lancement avec Docker (recommandé)

```bash
# 1. Cloner le projet
git clone https://github.com/SamouchH/Projet_3.git
cd Projet_3

# 2. Ajouter vos clés dans un fichier .env
echo -e "ANTHROPIC_API_KEY=votre_clé\nOPENAI_API_KEY=clé_optional" > .env

# 3. Lancer tous les services
docker-compose up --build -d

° API → http://localhost:8080 (Docs Swagger : /docs)

° Streamlit → http://localhost:8501

° Grafana → http://localhost:3000

° Prometheus → http://localhost:9090

## Lancer l'API manuellement
```bash
cd api
pip install -r requirements.txt
export SECRET_KEY="votre_clé"
export ANTHROPIC_API_KEY="votre_clé"
uvicorn main:app --reload --port 8080


## Lancer l'application Streamlit manuellement
```bash
cd Streamlit
pip install -r requirements.txt
streamlit run Home.py

## Lancer les Tests manuellement
```bash
cd Tests
pip install -r requirements.txt
pytest -v

## Utilisation de l'assistant hybride
1. Télécharger une image de jeu vidéo
2. Analyse automatique via Claude (plateforme,titre, etc.) ou catégorisation par modèle Deep Learning
3. Corrige les infos si besoin
4. Choisissez Claude ou Mistral pour la génération
5. Génère une annonce professionnelle
6. Télécharge/exporte l'annonce

## Équipe projet

- [Alexandre](https://github.com/alexdhn1)
- [Armelle](https://github.com/D41g0na)
- [Haroune](https://github.com/SamouchH)
- [Jimmy](https://github.com/JimmyRata)