import asyncio
import time
import io
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

from core.config import settings
from core.models import PredictionResult, PredictionResponse, PredictionStatus

logger = logging.getLogger(__name__)

class PredictionService:
    """Service de prédiction pour la classification d'images de jeux vidéo"""
    
    def __init__(self):
        self.model = None
        self.categories = settings.MODEL_CATEGORIES
        self.image_size = settings.IMAGE_SIZE
        self.is_model_loaded = False
        self.prediction_history = []  # En production, utiliser une base de données
    
    async def load_model(self):
        """Chargement du modèle TensorFlow"""
        if settings.ENVIRONMENT == "test":
            import inspect

            for frame in inspect.stack():
                if "test_admin" in frame.filename:
                    logger.info("Test admin détecté : on charge le vrai modèle même en mode test.")
                    break
                else:
                    logger.info("Mode test détecté : chargement du modèle ignoré.")
            
                    # faux modèle ave méthode predict simulée
                    class DummyModel:
                        def predict(self, x, verbose=0):
                            dummy_probs = np.array([[0.1] * len(settings.MODEL_CATEGORIES)])
                            dummy_probs[0][0] = 0.9
                            return dummy_probs
                    
                    self.model = DummyModel()
                    self.is_model_loaded = True
                    return
            
            try:
                logger.info(f"🔄 Chargement du modèle : {settings.MODEL_PATH}")
            
                # Chargement asynchrone du modèle
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None, 
                    lambda: load_model(settings.MODEL_PATH)
                )
                
                self.is_model_loaded = True
                logger.info("✅ Modèle chargé avec succès")
                
                # Test du modèle avec une image factice
                await self._test_model()
            
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement du modèle : {str(e)}")
                raise Exception(f"Impossible de charger le modèle : {str(e)}")
        
        async def _test_model(self):
            """Test du modèle avec une image factice"""
            try:
                # Création d'une image de test
                test_image = np.random.rand(*self.image_size, 3).astype(np.float32)
                test_image = np.expand_dims(test_image, axis=0)
                
                # Prédiction de test
                loop = asyncio.get_event_loop()
                prediction = await loop.run_in_executor(
                    None,
                    lambda: self.model.predict(test_image, verbose=0)
                )
                
                logger.info("✅ Test du modèle réussi")
                
            except Exception as e:
                logger.error(f"❌ Échec du test du modèle : {str(e)}")
                raise Exception(f"Le modèle ne fonctionne pas correctement : {str(e)}")
    
    def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Prétraitement de l'image pour la prédiction"""
        try:
            # Chargement de l'image depuis les bytes
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Redimensionnement
            image = image.resize(self.image_size)
            
            # Conversion en array numpy et normalisation
            image_array = np.array(image) / 255.0
            
            # Ajout de la dimension batch
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Erreur prétraitement image : {str(e)}")
            raise Exception(f"Impossible de traiter l'image : {str(e)}")
    
    async def predict_image(
        self, 
        image_bytes: bytes, 
        user_id: int,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prédiction de catégorie pour une image
        
        Args:
            image_bytes: Données binaires de l'image
            user_id: ID de l'utilisateur
            filename: Nom du fichier (optionnel)
            
        Returns:
            Dictionnaire avec les résultats de prédiction
        """
        start_time = time.time()
        
        try:
            if not self.is_model_loaded:
                raise Exception("Modèle non chargé")
            
            # Validation de la taille du fichier
            if len(image_bytes) > settings.MAX_FILE_SIZE:
                raise Exception(f"Fichier trop volumineux (max: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB)")
            
            # Prétraitement de l'image
            processed_image = self._preprocess_image(image_bytes)
            
            # Prédiction asynchrone
            loop = asyncio.get_event_loop()
            predictions = await loop.run_in_executor(
                None,
                lambda: self.model.predict(processed_image, verbose=0)
            )
            
            # Traitement des résultats
            probabilities = predictions[0]
            predicted_class_idx = np.argmax(probabilities)
            predicted_category = self.categories[predicted_class_idx]
            confidence = float(probabilities[predicted_class_idx])
            
            # Création du dictionnaire des probabilités
            prob_dict = {
                category: float(prob) 
                for category, prob in zip(self.categories, probabilities)
            }
            
            # Création du résultat
            prediction_result = PredictionResult(
                category=predicted_category,
                confidence=confidence,
                probabilities=prob_dict
            )
            
            # Calcul du temps de traitement
            processing_time = time.time() - start_time
            
            # Création de la réponse
            response = {
                "filename": filename,
                "prediction": prediction_result.dict(),
                "processing_time": processing_time,
                "timestamp": datetime.utcnow(),
                "user_id": user_id,
                "status": PredictionStatus.SUCCESS
            }
            
            # Sauvegarde dans l'historique
            await self._save_prediction_history(response)
            
            logger.info(
                f"Prédiction réussie - Utilisateur: {user_id}, "
                f"Catégorie: {predicted_category}, Confiance: {confidence:.3f}"
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_response = {
                "filename": filename,
                "prediction": None,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow(),
                "user_id": user_id,
                "status": PredictionStatus.ERROR,
                "error_message": str(e)
            }
            
            logger.error(f"Erreur prédiction - Utilisateur: {user_id}, Erreur: {str(e)}")
            
            # Sauvegarde de l'erreur dans l'historique
            await self._save_prediction_history(error_response)
            
            raise Exception(str(e))
    
    async def _save_prediction_history(self, prediction_data: Dict[str, Any]):
        """Sauvegarde de l'historique des prédictions"""
        try:
            # En production, sauvegarder en base de données
            self.prediction_history.append(prediction_data)
            
            # Limitation de l'historique en mémoire (garder les 1000 dernières)
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique : {str(e)}")
    
    async def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupération de l'historique des prédictions d'un utilisateur"""
        try:
            # Filtrage par utilisateur
            user_predictions = [
                pred for pred in self.prediction_history 
                if pred.get("user_id") == user_id
            ]
            
            # Tri par timestamp décroissant et limitation
            user_predictions.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            
            return user_predictions[:limit]
            
        except Exception as e:
            logger.error(f"Erreur récupération historique : {str(e)}")
            return []
    
    async def get_prediction_count(self) -> int:
        """Nombre total de prédictions"""
        return len([pred for pred in self.prediction_history if pred.get("status") == PredictionStatus.SUCCESS])
    
    async def get_predictions_today(self) -> int:
        """Nombre de prédictions aujourd'hui"""
        today = datetime.utcnow().date()
        return len([
            pred for pred in self.prediction_history 
            if (pred.get("timestamp", datetime.min).date() == today and 
                pred.get("status") == PredictionStatus.SUCCESS)
        ])
    
    async def get_top_categories(self, limit: int = 5) -> Dict[str, int]:
        """Top des catégories les plus prédites"""
        try:
            category_counts = {}
            
            for pred in self.prediction_history:
                if pred.get("status") == PredictionStatus.SUCCESS and pred.get("prediction"):
                    category = pred["prediction"].get("category")
                    if category:
                        category_counts[category] = category_counts.get(category, 0) + 1
            
            # Tri par nombre décroissant
            sorted_categories = sorted(
                category_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return dict(sorted_categories[:limit])
            
        except Exception as e:
            logger.error(f"Erreur calcul top catégories : {str(e)}")
            return {}
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Informations sur le modèle chargé"""
        if not self.is_model_loaded:
            return {"status": "not_loaded"}
        
        try:
            return {
                "status": "loaded",
                "categories": self.categories,
                "image_size": self.image_size,
                "model_path": settings.MODEL_PATH,
                "total_predictions": await self.get_prediction_count(),
                "predictions_today": await self.get_predictions_today()
            }
        except Exception as e:
            logger.error(f"Erreur info modèle : {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de l'état de santé du service"""
        return {
            "service": "prediction_service",
            "status": "healthy" if self.is_model_loaded else "unhealthy",
            "model_loaded": self.is_model_loaded,
            "categories_count": len(self.categories),
            "history_count": len(self.prediction_history)
        } 