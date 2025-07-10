# 🎮 Projet_3 API - Documentation

## Vue d'ensemble

L'API Projet_3 est une **API REST sécurisée** dédiée à la classification automatique d'images de jeux vidéo. 
Le projet utilise un modèle de deep learning basé sur MobileNetV2 pour identifier automatiquement les plateformes de jeux (PlayStation, Xbox, Nintendo, PC Gaming).

## ✨ Fonctionnalités Principales

### 🔐 Authentification & Sécurité
- **JWT tokens** avec gestion des rôles (User/Admin)
- **Rate limiting** intelligent par utilisateur
- **Validation robuste** des données d'entrée
- **Headers de sécurité** (CORS, XSS Protection, etc.)
- **Tentatives de connexion** limitées avec verrouillage temporaire

### 🎯 Classification d'Images
- **Prédiction en temps réel** d'images de jeux vidéo
- **Support multi-formats** : JPG, PNG, WEBP
- **Traitement par lots** jusqu'à 10 images simultanément
- **Métadonnées détaillées** : confiance, probabilités, temps de traitement
- **Historique des prédictions** par utilisateur

### 📊 Administration
- **Dashboard admin** avec statistiques complètes
- **Gestion des utilisateurs** (création, modification, suppression)
- **Monitoring en temps réel** des performances
- **Métriques détaillées** d'utilisation

### 🛡️ Robustesse
- **Gestion d'erreurs** centralisée
- **Logging structuré** avec rotation automatique
- **Health checks** pour monitoring
- **Validation des fichiers** (taille, format, contenu)

## 🚀 Installation & Démarrage

### Démarrage Rapide

```bash
# 1. Clone du projet
git clone <repository_url>
cd Projet_3

# 2. Démarrage automatique de l'API
python start_api.py

# L'API sera disponible sur http://localhost:8080
# Documentation interactive : http://localhost:8080/docs
```

### Installation Manuelle

```bash
# 1. Installation des dépendances
cd api
pip install -r requirements.txt

# 2. Configuration de l'environnement
export SECRET_KEY="your-secret-key"
export NVIDIA_API_KEY="your-nvidia-key"  # Optionnel
export ANTHROPIC_API_KEY="your-anthropic-key"  # Optionnel

# 3. Démarrage du serveur
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Avec Docker

```bash
# 1. Construction de l'image
docker build -t projet3-api .

# 2. Démarrage avec Docker Compose
docker-compose up -d

# Services disponibles :
# - API : http://localhost:8080
# - PostgreSQL : localhost:5432
# - Redis : localhost:6379
# - Prometheus : http://localhost:9090
# - Grafana : http://localhost:3000
```

## 📚 Documentation de l'API

### Authentification

#### Connexion
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123!"
}
```

**Réponse :**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@projet3.com",
    "role": "admin"
  }
}
```

#### Inscription
```http
POST /auth/register
Content-Type: application/json

{
  "username": "nouveau_user",
  "email": "user@example.com",
  "password": "motdepasse123!"
}
```

### Classification d'Images

#### Prédiction Simple
```http
POST /predict/image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
```

**Réponse :**
```json
{
  "filename": "jeu_ps5.jpg",
  "prediction": {
    "category": "Playstation",
    "confidence": 0.924,
    "probabilities": {
      "Playstation": 0.924,
      "Xbox": 0.043,
      "Nintendo": 0.028,
      "PC Gaming": 0.005
    }
  },
  "processing_time": 0.245,
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 1,
  "status": "success"
}
```

#### Prédiction par Lots
```http
POST /predict/batch
Authorization: Bearer <token>
Content-Type: multipart/form-data

files: <multiple_image_files>
```

#### Historique des Prédictions
```http
GET /predict/history?limit=50
Authorization: Bearer <token>
```

### Administration (Admin uniquement)

#### Statistiques Globales
```http
GET /admin/stats
Authorization: Bearer <admin_token>
```

**Réponse :**
```json
{
  "users": 25,
  "predictions": 1247,
  "predictions_today": 89,
  "top_categories": {
    "Playstation": 456,
    "Nintendo": 342,
    "Xbox": 289,
    "PC Gaming": 160
  },
  "system_info": {
    "uptime": 1642248600.0,
    "version": "1.0.0"
  }
}
```

#### Gestion des Utilisateurs
```http
# Liste des utilisateurs
GET /admin/users?skip=0&limit=100
Authorization: Bearer <admin_token>

# Suppression d'un utilisateur
DELETE /admin/users/{user_id}
Authorization: Bearer <admin_token>
```

## 🔧 Configuration

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `SECRET_KEY` | Clé secrète JWT | `your-super-secret-key...` |
| `DATABASE_URL` | URL de la base de données | `sqlite:///./projet3_api.db` |
| `LOG_LEVEL` | Niveau de logging | `INFO` |
| `RATE_LIMIT_REQUESTS` | Limite de requêtes | `100` |
| `RATE_LIMIT_WINDOW` | Fenêtre de temps (sec) | `3600` |
| `MAX_FILE_SIZE` | Taille max fichier (bytes) | `10485760` (10MB) |
| `NVIDIA_API_KEY` | Clé API Nvidia | - |
| `ANTHROPIC_API_KEY` | Clé API Anthropic | - |

### Configuration du Modèle

```python
# api/core/config.py
MODEL_CATEGORIES = ["Playstation", "Xbox", "Nintendo", "PC Gaming"]
IMAGE_SIZE = (150, 150)
MODEL_PATH = "modele_cnn_transfer.h5"
```

## 📊 Monitoring & Métriques

### Health Check
```http
GET /health
```

### Métriques (si activées)
```http
GET /metrics
```

### Logs
Les logs sont disponibles dans le répertoire `api/logs/` avec rotation automatique.

**Format des logs :**
```
2024-01-15 10:30:00 | api.security | INFO | AUTH_SUCCESS | User: admin | IP: 192.168.1.100
2024-01-15 10:30:15 | api.prediction | INFO | PREDICTION | User: 1 | Category: Playstation | Confidence: 0.924 | Time: 0.245s
```

## 🛡️ Sécurité

### Authentification JWT
- **Tokens d'accès** : expiration 30 minutes
- **Tokens de rafraîchissement** : expiration 7 jours
- **Algorithme** : HS256
- **Payload** : user_id, username, role, exp

### Rate Limiting
- **100 requêtes par heure** par défaut
- **Identification** par IP + User-Agent
- **Headers de réponse** : `X-RateLimit-*`
- **Exemptions** : routes publiques (/health, /docs)

### Validation des Fichiers
- **Formats autorisés** : JPG, PNG, WEBP
- **Taille maximale** : 10MB
- **Validation du contenu** : vérification MIME type
- **Sécurité** : protection contre les uploads malveillants

### Headers de Sécurité
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 🐳 Déploiement

### Docker Production
```bash
# Construction optimisée pour la production
docker build -t projet3-api:prod .

# Démarrage avec configuration production
docker-compose -f docker-compose.prod.yml up -d
```

### Configuration Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name api.projet3.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🧪 Tests

### Tests Automatisés
```bash
# Installation des dépendances de test
pip install pytest pytest-asyncio

# Exécution des tests
pytest api/tests/ -v

# Tests avec couverture
pytest api/tests/ --cov=api --cov-report=html
```

### Tests d'Intégration
```python
# Exemple de test
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_image():
    # Test avec authentification
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "user123!"
    })
    token = login_response.json()["access_token"]
    
    with open("test_image.jpg", "rb") as f:
        response = client.post(
            "/predict/image",
            files={"file": f},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    assert "prediction" in response.json()
```

## 📋 Codes d'Erreur

| Code | Description |
|------|-------------|
| 400 | Requête invalide (format, validation) |
| 401 | Non authentifié |
| 403 | Non autorisé (rôle insuffisant) |
| 413 | Fichier trop volumineux |
| 422 | Erreur de validation des données |
| 429 | Trop de requêtes (rate limiting) |
| 500 | Erreur interne du serveur |

## 🔄 Versions & Changelog

### Version 1.0.0 (Actuelle)
- ✅ API REST complète
- ✅ Authentification JWT
- ✅ Classification d'images
- ✅ Interface d'administration
- ✅ Monitoring et métriques
- ✅ Sécurité avancée
- ✅ Documentation complète

### Roadmap
- 🔄 Intégration base de données PostgreSQL
- 🔄 Cache Redis pour les performances
- 🔄 API de génération de descriptions
- 🔄 Webhooks pour notifications
- 🔄 API GraphQL optionnelle

## 🆘 Support & Dépannage

### Problèmes Courants

**Modèle non trouvé**
```bash
# Vérifier la presence du modèle
ls -la modele_cnn_transfer.h5

# Copier depuis Streamlit si nécessaire
cp Streamlit/modele_cnn_transfer.h5 api/
```

**Erreur de permissions**
```bash
# Créer les répertoires nécessaires
mkdir -p api/{logs,uploads,predictions,data}
chmod 755 api/{logs,uploads,predictions,data}
```

**Problème de dépendances**
```bash
# Réinstaller les dépendances
pip install -r api/requirements.txt --force-reinstall
```


---

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails. 