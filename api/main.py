from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import logging
import time
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
import sys
from PIL import Image
import io

from core.config import get_settings
from core.security import verify_token, get_current_user, get_current_admin_user
from core.models import PredictionResponse, UserResponse, LoginRequest, StatsResponse, UserCreate
from services.prediction_service import PredictionService
from services.user_service import UserService
from core.database import init_db
from core.middleware import RateLimitMiddleware
from core.logging_config import setup_logging


# Configuration du logging
setup_logging()

# Ajout console stdout pour que les logs soient visibles dans Docker
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))
formatter = logging.Formatter("🌟 [%(asctime)s] %(levelname)s in %(name)s: %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.info("main bien chargé")

# Initialisation des settings
settings = get_settings()
logger.info(f"ENV: {os.environ.get('ENVIRONMENT')}")
logger.info(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# Initialisation de la base de données et des services
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Démarrage de l'API Projet_3...")
    await init_db()
    
    # Chargement du modèle de prédiction au démarrage
    app.state.prediction_service = PredictionService()
    await app.state.prediction_service.load_model()
    
    app.state.user_service = UserService()
    
    logger.info("✅ API Projet_3 démarrée avec succès")
    yield
    
    # Shutdown
    logger.info("🔄 Arrêt de l'API Projet_3...")

# Configuration de l'application FastAPI
app = FastAPI(
    title="Projet_3 API",
    description="""
    ## 🎮 API de Classification d'Images de Jeux Vidéo
    
    Cette API fournit des services de classification automatique d'images de jeux vidéo 
    avec authentification sécurisée et fonctionnalités d'administration.
    
    ### Fonctionnalités principales :
    - 🔐 **Authentification JWT** avec gestion des rôles
    - 🎯 **Classification d'images** : Détection automatique des plateformes de jeux
    - 📊 **Dashboard Admin** : Statistiques et gestion des utilisateurs
    - 🛡️ **Sécurité avancée** : Rate limiting, validation, monitoring
    - 📝 **Génération de descriptions** : Création automatique de textes d'annonces
    
    ### Catégories supportées :
    - PlayStation, Xbox, Nintendo, PC Gaming
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Configuration des middlewares de sécurité
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(RateLimitMiddleware)

# Schéma de sécurité
security = HTTPBearer()

# Routes publiques
@app.get("/", tags=["Info"])
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "🎮 Bienvenue sur l'API Projet_3",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs"
    }

@app.get("/health", tags=["Info"])
async def health_check():
    """Vérification de l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "model": "loaded",
            "api": "running"
        }
    }

# Routes d'authentification
@app.post("/auth/login", response_model=Dict[str, Any], tags=["Authentication"])
async def login(
    login_data: LoginRequest,
    user_service: UserService = Depends(lambda: app.state.user_service)
):
    """Connexion utilisateur avec génération de token JWT"""
    try:
        result = await user_service.authenticate_user(
            login_data.username, 
            login_data.password
        )
        logger.info(f"Connexion réussie pour l'utilisateur : {login_data.username}")
        return result
    except Exception as e:
        logger.error(f"Erreur de connexion pour {login_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides"
        )

@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(lambda: app.state.user_service)
):
    """Inscription d'un nouvel utilisateur"""
    try:
        user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        logger.info(f"Nouvel utilisateur créé : {user_data.username}")
        return user
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Routes d'inférence (protégées)
@app.post("/predict/image", response_model=PredictionResponse, tags=["Prediction"])
async def predict_image(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user),
    prediction_service: PredictionService = Depends(lambda: app.state.prediction_service)
):
    """
    Classification d'une image de jeu vidéo
    
    - **file**: Image au format JPG, PNG ou WEBP
    - **Retourne**: Catégorie prédite avec probabilités et métadonnées
    """
    try:
        # Validation du fichier
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image"
            )
        
        # Lecture et traitement de l'image
        image_bytes = await file.read()

        # tentatice de lecture avec PIL(détection image invalide)
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            logger.warning(f"Image invalide: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Fichier image invalide ou non lisible"
            )
        
        # Prédiction
        result = await prediction_service.predict_image(image_bytes, current_user["user_id"])
        
        logger.info(f"Prédiction réalisée par {current_user['username']}: {result['prediction']}")
        return result

    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )

@app.post("/predict/batch", response_model=List[PredictionResponse], tags=["Prediction"])
async def predict_batch(
    files: List[UploadFile] = File(...),
    current_user: Dict = Depends(get_current_user),
    prediction_service: PredictionService = Depends(lambda: app.state.prediction_service)
):
    """Classification en lot de plusieurs images"""
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images par batch"
        )
    
    results = []
    for file in files:
        try:
            image_bytes = await file.read()
            result = await prediction_service.predict_image(image_bytes, current_user["user_id"])
            results.append(result)
        except Exception as e:
            logger.error(f"Erreur sur l'image {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "error": str(e),
                "prediction": None
            })
    
    return results

@app.get("/predict/history", tags=["Prediction"])
async def get_prediction_history(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user),
    prediction_service: PredictionService = Depends(lambda: app.state.prediction_service)
):
    """Historique des prédictions de l'utilisateur"""
    try:
        history = await prediction_service.get_user_history(current_user["user_id"], limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes d'administration (admin uniquement)
@app.get("/admin/stats", response_model=StatsResponse, tags=["Admin"])
async def get_admin_stats(
    current_admin: Dict = Depends(get_current_admin_user),
    user_service: UserService = Depends(lambda: app.state.user_service),
    prediction_service: PredictionService = Depends(lambda: app.state.prediction_service)
):
    """Statistiques globales de l'API (admin uniquement)"""
    try:
        stats = {
            "users": await user_service.get_user_count(),
            "predictions": await prediction_service.get_prediction_count(),
            "predictions_today": await prediction_service.get_predictions_today(),
            "top_categories": await prediction_service.get_top_categories(),
            "system_info": {
                "uptime": time.time(),
                "version": "1.0.0"
            }
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/users", tags=["Admin"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: Dict = Depends(get_current_admin_user),
    user_service: UserService = Depends(lambda: app.state.user_service)
):
    """Liste des utilisateurs (admin uniquement)"""
    try:
        users = await user_service.get_users(skip=skip, limit=limit)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/users/{user_id}", tags=["Admin"])
async def delete_user(
    user_id: int,
    current_admin: Dict = Depends(get_current_admin_user),
    user_service: UserService = Depends(lambda: app.state.user_service)
):
    """Suppression d'un utilisateur (admin uniquement)"""
    try:
        await user_service.delete_user(user_id)
        logger.info(f"Utilisateur {user_id} supprimé par {current_admin['username']}")
        return {"message": "Utilisateur supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gestion d'erreurs globale
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 