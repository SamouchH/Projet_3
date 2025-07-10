from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Informations de base
    APP_NAME: str = "Projet_3 API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Sécurité JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./projet3_api.db"
    
    # CORS et sécurité
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",  # Streamlit
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501"
    ]
    
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1", 
        "0.0.0.0"
    ]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 heure en secondes
    
    # Modèle ML
    MODEL_PATH: str = "modele_cnn_transfer.h5"
    MODEL_CATEGORIES: List[str] = ["Playstation", "Xbox", "Nintendo", "PC Gaming"]
    IMAGE_SIZE: tuple = (150, 150)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "api.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # APIs externes
    NVIDIA_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Stockage des fichiers
    UPLOAD_DIR: str = "uploads"
    PREDICTIONS_DIR: str = "predictions"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PATH: str = "/metrics"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Création des répertoires nécessaires
        Path(self.UPLOAD_DIR).mkdir(exist_ok=True)
        Path(self.PREDICTIONS_DIR).mkdir(exist_ok=True)
        
        # Récupération des clés d'API depuis l'environnement
        self.NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        
        # Configuration pour la production
        if os.getenv("ENVIRONMENT") == "production":
            self.DEBUG = False
            self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)

# Instance globale des paramètres
settings = Settings()

# Validation des paramètres critiques
def validate_settings():
    """Validation des paramètres de configuration"""
    errors = []
    
    if settings.SECRET_KEY == "your-super-secret-key-change-this-in-production":
        errors.append("⚠️  SECRET_KEY doit être changée en production")
    
    if not Path(settings.MODEL_PATH).exists():
        errors.append(f"❌ Modèle non trouvé : {settings.MODEL_PATH}")
    
    if settings.NVIDIA_API_KEY is None and settings.ANTHROPIC_API_KEY is None:
        errors.append("⚠️  Aucune clé API configurée pour les services externes")
    
    return errors

# Affichage de la configuration au démarrage
def display_config():
    """Affichage de la configuration actuelle"""
    print("=" * 50)
    print(f"🚀 Configuration {settings.APP_NAME} v{settings.VERSION}")
    print("=" * 50)
    print(f"Debug mode: {'✅' if settings.DEBUG else '❌'}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Model: {settings.MODEL_PATH}")
    print(f"Rate limit: {settings.RATE_LIMIT_REQUESTS} req/{settings.RATE_LIMIT_WINDOW}s")
    print(f"Max file size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    print(f"Allowed origins: {len(settings.ALLOWED_ORIGINS)} domaines")
    
    # Validation
    validation_errors = validate_settings()
    if validation_errors:
        print("\n⚠️  Avertissements de configuration:")
        for error in validation_errors:
            print(f"   {error}")
    else:
        print("\n✅ Configuration validée")
    
    print("=" * 50) 