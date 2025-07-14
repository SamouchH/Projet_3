from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Énumérations
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class PredictionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"

# Modèles d'authentification
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

# Modèles utilisateur
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    prediction_count: int = 0

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

# Modèles de prédiction
class PredictionRequest(BaseModel):
    filename: Optional[str] = None
    include_confidence: bool = True
    include_alternatives: bool = False

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v:Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if not v.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise ValueError('Format de fichier non supporté')
        return v

class PredictionResult(BaseModel):
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: Dict[str, float] = {}

class PredictionResponse(BaseModel):
    id: Optional[int] = None
    filename: Optional[str] = None
    prediction: PredictionResult
    alternatives: Optional[List[PredictionResult]] = None
    processing_time: float
    timestamp: datetime
    user_id: int
    status: PredictionStatus = PredictionStatus.SUCCESS
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class PredictionHistory(BaseModel):
    predictions: List[PredictionResponse]
    total_count: int
    page: int
    page_size: int

# Modèles administrateur
class StatsResponse(BaseModel):
    users: int
    predictions: int
    predictions_today: int
    top_categories: Dict[str, int]
    system_info: Dict[str, Any]

class UserStats(BaseModel):
    user_id: int
    username: str
    prediction_count: int
    last_prediction: Optional[datetime]
    favorite_category: Optional[str]

class SystemHealth(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    uptime: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

# Modèles de génération de texte
class DescriptionRequest(BaseModel):
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = "Très bon état"
    price: Optional[float] = None
    additional_info: Optional[str] = None

class DescriptionResponse(BaseModel):
    title: str
    description: str
    keywords: List[str]
    processing_time: float
    timestamp: datetime

# Modèles de fichiers
class FileInfo(BaseModel):
    filename: str
    content_type: str
    size: int
    is_valid: bool
    error_message: Optional[str] = None

# Modèles d'erreur
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime
    request_id: Optional[str] = None

class ValidationError(BaseModel):
    field: str
    message: str
    value: Any

# # Validateurs personnalisés
# class PredictionRequestValidator(BaseModel):
#     """Validateur pour les requêtes de prédiction"""
    
#     @validator('filename')
#     def validate_filename(cls, v):
#         if v and not v.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
#             raise ValueError('Format de fichier non supporté')
#         return v

# Modèles de réponse API standardisés
class APIResponse(BaseModel):
    """Modèle de réponse standardisé"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    """Modèle pour les réponses paginées"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

# Configuration des modèles
def configure_models():
    """Configuration globale des modèles Pydantic"""
    # Configuration pour la sérialisation JSON
    for model_class in [
        UserResponse, PredictionResponse, StatsResponse, 
        DescriptionResponse, SystemHealth
    ]:
        model_class.Config.json_encoders = {
            datetime: lambda v: v.isoformat()
        } 