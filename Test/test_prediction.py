import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Fixture pour obtenir un token d'authentification"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "user123!"
    })
    return response.json()["access_token"]

@pytest.fixture
def test_image():
    """Fixture pour créer une image de test"""
    # Création d'une image RGB de test
    img_array = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Conversion en bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

class TestPrediction:
    """Tests de prédiction d'images"""    
    
    def test_predict_image_success(self, auth_token, test_image):
        """Test de prédiction d'image réussie"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test.jpg", test_image, "image/jpeg")}
        
        response = client.post("/predict/image", headers=headers, files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction" in data
        assert "category" in data["prediction"]
        assert "confidence" in data["prediction"]
        assert "probabilities" in data["prediction"]
        assert "processing_time" in data
        assert "timestamp" in data
        assert "user_id" in data
        assert data["status"] == "success"
    
    def test_predict_image_unauthorized(self, test_image):
        """Test de prédiction sans authentification"""
        files = {"file": ("test.jpg", test_image, "image/jpeg")}
        
        response = client.post("/predict/image", files=files)
        assert response.status_code == 401
    
    def test_predict_image_invalid_file(self, auth_token):

        """Test de prédiction avec fichier invalide"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        
        response = client.post("/predict/image", headers=headers, files=files)
        assert response.status_code == 400
    
    def test_predict_history(self, auth_token):
        """Test de récupération de l'historique"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/predict/history", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)