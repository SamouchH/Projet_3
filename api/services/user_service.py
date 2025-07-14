import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password, create_tokens, login_attempt_manager
from core.models import UserRole, UserCreate, UserResponse
from core.database import get_db

logger = logging.getLogger(__name__)

class UserService:
    """Service de gestion des utilisateurs"""
    
    def __init__(self):
        self.users_cache = {}  # En production, utiliser Redis
        self._init_default_users()
    
    def _init_default_users(self):
        """Initialisation des utilisateurs par défaut"""
        # Utilisateur admin par défaut
        admin_password = hash_password("admin123!")
        self.users_cache[1] = {
            "id": 1,
            "username": "admin",
            "email": "admin@projet3.com",
            "password_hash": admin_password,
            "role": UserRole.ADMIN,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "prediction_count": 0
        }
        
        # Utilisateur test par défaut
        user_password = hash_password("user123!")
        self.users_cache[2] = {
            "id": 2,
            "username": "testuser",
            "email": "test@projet3.com",
            "password_hash": user_password,
            "role": UserRole.USER,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "prediction_count": 0
        }
        
        logger.info("✅ Utilisateurs par défaut initialisés")
        logger.info("👤 Admin: admin / admin123!")
        logger.info("👤 User: testuser / user123!")
    
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authentification d'un utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Dictionnaire avec les tokens et informations utilisateur
        """
        try:
            # Vérification du verrouillage
            if login_attempt_manager.is_locked(username):
                raise Exception("Compte temporairement verrouillé suite à plusieurs tentatives échouées")
            
            # Recherche de l'utilisateur
            user = await self._get_user_by_username(username)
            if not user:
                login_attempt_manager.record_failed_attempt(username)
                raise Exception("Utilisateur non trouvé")
            
            # Vérification du mot de passe
            if not verify_password(password, user["password_hash"]):
                login_attempt_manager.record_failed_attempt(username)
                raise Exception("Mot de passe incorrect")
            
            # Vérification que l'utilisateur est actif
            if not user["is_active"]:
                raise Exception("Compte désactivé")
            
            # Mise à jour de la dernière connexion
            await self._update_last_login(user["id"])
            
            # Génération des tokens
            token_data = {
                "sub": user["username"],
                "user_id": user["id"],
                "role": user["role"]
            }
            
            tokens = create_tokens(token_data)
            
            # Enregistrement de la connexion réussie
            login_attempt_manager.record_successful_login(username)
            
            logger.info(f"Connexion réussie : {username} (ID: {user['id']})")
            
            return {
                **tokens,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur authentification {username}: {str(e)}")
            raise e
    
    async def create_user(
        self, 
        username: str, 
        email: str, 
        password: str,
        role: UserRole = UserRole.USER
    ) -> Dict[str, Any]:
        """
        Création d'un nouvel utilisateur
        
        Args:
            username: Nom d'utilisateur unique
            email: Adresse email unique
            password: Mot de passe (sera haché)
            role: Rôle de l'utilisateur
            
        Returns:
            Informations de l'utilisateur créé
        """
        try:
            # Validation de l'unicité
            if await self._get_user_by_username(username):
                raise Exception(f"Le nom d'utilisateur '{username}' existe déjà")
            
            if await self._get_user_by_email(email):
                raise Exception(f"L'email '{email}' est déjà utilisé")
            
            # Génération d'un nouvel ID
            new_id = max(self.users_cache.keys()) + 1 if self.users_cache else 1
            
            # Hachage du mot de passe
            password_hash = hash_password(password)
            
            # Création de l'utilisateur
            user_data = {
                "id": new_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "role": role,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "prediction_count": 0
            }
            
            # Sauvegarde en cache (en production, utiliser la base de données)
            self.users_cache[new_id] = user_data
            
            logger.info(f"Nouvel utilisateur créé : {username} (ID: {new_id})")
            
            # Retour des données publiques
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "role": user_data["role"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"],
                "prediction_count": user_data["prediction_count"]
            }
            
        except Exception as e:
            logger.error(f"Erreur création utilisateur {username}: {str(e)}")
            raise e
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupération d'un utilisateur par son ID"""
        user = self.users_cache.get(user_id)
        if user:
            # Retour des données publiques uniquement
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"],
                "prediction_count": user["prediction_count"]
            }
        return None
    
    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Récupération d'un utilisateur par nom d'utilisateur (données complètes)"""
        for user in self.users_cache.values():
            if user["username"] == username:
                return user
        return None
    
    async def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Récupération d'un utilisateur par email"""
        for user in self.users_cache.values():
            if user["email"] == email:
                return user
        return None
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Liste paginée des utilisateurs"""
        users = list(self.users_cache.values())
        users.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Pagination
        paginated_users = users[skip:skip + limit]
        
        # Retour des données publiques uniquement
        return [
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"],
                "prediction_count": user["prediction_count"]
            }
            for user in paginated_users
        ]
    
    async def get_user_count(self) -> int:
        """Nombre total d'utilisateurs"""
        return len(self.users_cache)
    
    async def update_user(
        self, 
        user_id: int, 
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Mise à jour d'un utilisateur"""
        if user_id not in self.users_cache:
            return None
        
        user = self.users_cache[user_id]
        
        # Champs autorisés à la mise à jour
        allowed_fields = ["email", "is_active", "role"]
        
        for field, value in updates.items():
            if field in allowed_fields:
                user[field] = value
        
        self.users_cache[user_id] = user
        
        logger.info(f"Utilisateur {user_id} mis à jour")
        
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """Suppression d'un utilisateur"""
        if user_id in self.users_cache:
            username = self.users_cache[user_id]["username"]
            del self.users_cache[user_id]
            logger.info(f"Utilisateur supprimé : {username} (ID: {user_id})")
            return True
        return False
    
    async def _update_last_login(self, user_id: int):
        """Mise à jour de la dernière connexion"""
        if user_id in self.users_cache:
            self.users_cache[user_id]["last_login"] = datetime.utcnow()
    
    async def increment_prediction_count(self, user_id: int):
        """Incrémentation du compteur de prédictions"""
        if user_id in self.users_cache:
            self.users_cache[user_id]["prediction_count"] += 1
    
    async def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Statistiques d'un utilisateur"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "user_id": user["id"],
            "username": user["username"],
            "prediction_count": user["prediction_count"],
            "last_login": user["last_login"],
            "account_age_days": (datetime.utcnow() - user["created_at"]).days,
            "is_active": user["is_active"]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de l'état de santé du service"""
        return {
            "service": "user_service",
            "status": "healthy",
            "total_users": len(self.users_cache),
            "active_users": len([u for u in self.users_cache.values() if u["is_active"]])
        } 