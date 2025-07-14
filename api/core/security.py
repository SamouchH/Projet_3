from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import hashlib
import secrets
import logging
from typing import List

from .config import settings
from .models import TokenData, UserRole

logger = logging.getLogger(__name__)

# Configuration du hachage de mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma de sécurité Bearer
security = HTTPBearer()

class SecurityService:
    """Service de sécurité pour l'authentification et l'autorisation"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def hash_password(self, password: str) -> str:
        """Hachage sécurisé du mot de passe"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérification du mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Création d'un token d'accès JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Création d'un token de rafraîchissement"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> TokenData:
        """Vérification et décodage d'un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role: str = payload.get("role", "user")
            token_type: str = payload.get("type", "access")
            
            if username is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(username=username, user_id=user_id, role=role)
        
        except JWTError as e:
            logger.error(f"Erreur JWT : {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def create_api_key(self, user_id: int) -> str:
        """Génération d'une clé API pour un utilisateur"""
        raw_key = f"{user_id}:{secrets.token_hex(32)}:{datetime.utcnow().timestamp()}"
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validation d'une clé API"""
        # Implémentation simplifiée - en production, stocker en base
        return len(api_key) == 64 and api_key.isalnum()

# Instance globale du service de sécurité
security_service = SecurityService()

# Fonctions utilitaires pour l'authentification
def hash_password(password: str) -> str:
    """Fonction de hachage de mot de passe"""
    return security_service.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Fonction de vérification de mot de passe"""
    return security_service.verify_password(plain_password, hashed_password)

def create_tokens(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Création des tokens d'accès et de rafraîchissement"""
    access_token = security_service.create_access_token(user_data)
    refresh_token = security_service.create_refresh_token(user_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

def verify_token(token: str) -> TokenData:
    """Fonction de vérification de token"""
    return security_service.verify_token(token)

# Dépendances FastAPI pour l'authentification
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dépendance pour obtenir l'utilisateur actuel depuis le token JWT
    """
    try:
        token_data = verify_token(credentials.credentials)
        
        # Simulation de récupération depuis la base de données
        # En production, récupérer les données depuis la DB
        user_data = {
            "user_id": token_data.user_id,
            "username": token_data.username,
            "role": token_data.role
        }
        
        return user_data
    
    except Exception as e:
        logger.error(f"Erreur d'authentification : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dépendance pour vérifier que l'utilisateur actuel est administrateur
    """
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    
    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Dépendance pour l'authentification optionnelle
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Décorateurs de sécurité
def require_role(required_role: UserRole):
    """Décorateur pour vérifier le rôle d'un utilisateur"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or current_user.get('role') != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Rôle {required_role} requis"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Validation de sécurité pour les mots de passe
def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """
    Validation de la force d'un mot de passe
    Retourne (is_valid, errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if not any(c.isupper() for c in password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")
    
    if not any(c.islower() for c in password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")
    
    if not any(c.isdigit() for c in password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial")
    
    return len(errors) == 0, errors

# Gestion des tentatives de connexion
class LoginAttemptManager:
    """Gestionnaire des tentatives de connexion pour prévenir les attaques par force brute"""
    
    def __init__(self):
        self.attempts = {}  # En production, utiliser Redis ou une base de données
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def is_locked(self, identifier: str) -> bool:
        """Vérifie si un utilisateur/IP est verrouillé"""
        if identifier not in self.attempts:
            return False
        
        attempt_data = self.attempts[identifier]
        if attempt_data['count'] >= self.max_attempts:
            if datetime.utcnow() - attempt_data['last_attempt'] < timedelta(seconds=self.lockout_duration):
                return True
            else:
                # Réset après expiration du verrouillage
                del self.attempts[identifier]
        
        return False
    
    def record_failed_attempt(self, identifier: str):
        """Enregistre une tentative de connexion échouée"""
        if identifier not in self.attempts:
            self.attempts[identifier] = {'count': 0, 'last_attempt': datetime.utcnow()}
        
        self.attempts[identifier]['count'] += 1
        self.attempts[identifier]['last_attempt'] = datetime.utcnow()
    
    def record_successful_login(self, identifier: str):
        """Enregistre une connexion réussie et remet à zéro les tentatives"""
        if identifier in self.attempts:
            del self.attempts[identifier]

# Instance globale du gestionnaire de tentatives
login_attempt_manager = LoginAttemptManager() 