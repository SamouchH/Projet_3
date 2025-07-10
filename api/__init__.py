"""
Projet_3 API

API REST sécurisée pour la classification automatique d'images de jeux vidéo.

Fonctionnalités principales :
- Authentification JWT avec gestion des rôles
- Classification d'images basée sur MobileNetV2
- Interface d'administration
- Rate limiting et sécurité avancée
- Monitoring et métriques

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Équipe Projet_3"
__license__ = "MIT"

from .main import app
from .core.config import settings

__all__ = ["app", "settings"] 