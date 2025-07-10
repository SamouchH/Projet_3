import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

from .config import settings

def setup_logging():
    """Configuration du système de logging"""
    
    # Création du répertoire de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du format des logs
    log_format = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Suppression des handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler pour le fichier avec rotation
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / settings.LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Configuration spécifique pour l'application
    app_logger = logging.getLogger("api")
    app_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Désactivation des logs trop verbeux
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    
    # Log de démarrage
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info(f"🚀 Démarrage du logging - {datetime.now()}")
    logger.info(f"Niveau de log: {settings.LOG_LEVEL}")
    logger.info(f"Fichier de log: {log_dir / settings.LOG_FILE}")
    logger.info("=" * 50)

class StructuredLogger:
    """Logger structuré pour les événements spécifiques"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_authentication(self, username: str, success: bool, ip: str = "unknown"):
        """Log des tentatives d'authentification"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"AUTH_{status} | User: {username} | IP: {ip}")
    
    def log_prediction(self, user_id: int, category: str, confidence: float, processing_time: float):
        """Log des prédictions"""
        self.logger.info(
            f"PREDICTION | User: {user_id} | Category: {category} | "
            f"Confidence: {confidence:.3f} | Time: {processing_time:.3f}s"
        )
    
    def log_error(self, error_type: str, message: str, user_id: int = None):
        """Log des erreurs"""
        user_info = f"User: {user_id} | " if user_id else ""
        self.logger.error(f"ERROR_{error_type} | {user_info}{message}")
    
    def log_admin_action(self, admin_user: str, action: str, target: str = None):
        """Log des actions administrateur"""
        target_info = f"Target: {target} | " if target else ""
        self.logger.warning(f"ADMIN_ACTION | Admin: {admin_user} | Action: {action} | {target_info}")

# Instances globales
api_logger = StructuredLogger("api")
security_logger = StructuredLogger("security")
admin_logger = StructuredLogger("admin") 