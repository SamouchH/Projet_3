from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from contextlib import contextmanager
from datetime import datetime
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Configuration de la base de données
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèles de base de données
class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    prediction_count = Column(Integer, default=0)

class Prediction(Base):
    """Modèle prédiction"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    filename = Column(String(255), nullable=True)
    predicted_category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities = Column(Text, nullable=True)  # JSON string
    processing_time = Column(Float, nullable=False)
    status = Column(String(20), default="success", nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class APIKey(Base):
    """Modèle clé API"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

class LoginAttempt(Base):
    """Modèle tentatives de connexion"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    success = Column(Boolean, nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Fonctions utilitaires
def get_db() -> Session:
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager pour les opérations de base de données"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur base de données : {str(e)}")
        raise
    finally:
        db.close()

async def init_db():
    """Initialisation de la base de données"""
    try:
        logger.info("🔄 Initialisation de la base de données...")
        
        # Création des tables
        Base.metadata.create_all(bind=engine)
        
        # Création d'un utilisateur admin par défaut si nécessaire
        with get_db_context() as db:
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                from .security import hash_password
                admin_user = User(
                    username="admin",
                    email="admin@projet3.com",
                    password_hash=hash_password("admin123!"),
                    role="admin",
                    is_active=True
                )
                db.add(admin_user)
                logger.info("✅ Utilisateur admin créé : admin / admin123!")
        
        logger.info("✅ Base de données initialisée")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation base de données : {str(e)}")
        raise

def check_db_connection() -> bool:
    """Vérification de la connexion à la base de données"""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Erreur connexion base de données : {str(e)}")
        return False

# Fonctions CRUD pour les utilisateurs
class UserCRUD:
    """Opérations CRUD pour les utilisateurs"""
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password_hash: str, role: str = "user") -> User:
        """Création d'un utilisateur"""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Récupération d'un utilisateur par ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """Récupération d'un utilisateur par nom d'utilisateur"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Récupération d'un utilisateur par email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        """Liste des utilisateurs avec pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_last_login(db: Session, user_id: int):
        """Mise à jour de la dernière connexion"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def increment_prediction_count(db: Session, user_id: int):
        """Incrémentation du compteur de prédictions"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.prediction_count += 1
            db.commit()

# Fonctions CRUD pour les prédictions
class PredictionCRUD:
    """Opérations CRUD pour les prédictions"""
    
    @staticmethod
    def create_prediction(
        db: Session,
        user_id: int,
        filename: str,
        predicted_category: str,
        confidence: float,
        probabilities: str,
        processing_time: float,
        status: str = "success",
        error_message: str = None
    ) -> Prediction:
        """Création d'une prédiction"""
        prediction = Prediction(
            user_id=user_id,
            filename=filename,
            predicted_category=predicted_category,
            confidence=confidence,
            probabilities=probabilities,
            processing_time=processing_time,
            status=status,
            error_message=error_message
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    
    @staticmethod
    def get_user_predictions(db: Session, user_id: int, limit: int = 50):
        """Récupération des prédictions d'un utilisateur"""
        return db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_prediction_count(db: Session) -> int:
        """Nombre total de prédictions"""
        return db.query(Prediction).filter(Prediction.status == "success").count()
    
    @staticmethod
    def get_predictions_today(db: Session) -> int:
        """Nombre de prédictions aujourd'hui"""
        today = datetime.utcnow().date()
        return db.query(Prediction).filter(
            func.date(Prediction.created_at) == today,
            Prediction.status == "success"
        ).count()

# Utilitaires de migration
def create_tables():
    """Création de toutes les tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables créées")

def drop_tables():
    """Suppression de toutes les tables"""
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ Tables supprimées")

def reset_database():
    """Réinitialisation complète de la base de données"""
    drop_tables()
    create_tables()
    logger.info("✅ Base de données réinitialisée") 