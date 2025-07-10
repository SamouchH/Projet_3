import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from api.main import app

client = TestClient(app)

class TestHealthAndInfo:
    """Tests des endpoints de santé et d'information"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "timestamp" in data

class TestAuthentication:
    """Tests d'authentification"""
    
    def test_login_admin_success(self):
        """Test de connexion admin réussie"""
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["role"] == "admin"
    
    def test_login_user_success(self):
        """Test de connexion utilisateur réussie"""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "user123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "user"
    
    def test_login_invalid_credentials(self):
        """Test de connexion avec identifiants invalides"""
        response = client.post("/auth/login", json={
            "username": "invalid",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_register_new_user(self):
        """Test d'inscription d'un nouvel utilisateur"""
        response = client.post("/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "newpass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "user"
    
    def test_register_duplicate_username(self):
        """Test d'inscription avec nom d'utilisateur existant"""
        response = client.post("/auth/register", json={
            "username": "admin",
            "email": "admin2@test.com",
            "password": "password123!"
        })
        assert response.status_code == 400

class TestPrediction:
    """Tests de prédiction d'images"""
    
    @pytest.fixture
    def auth_token(self):
        """Fixture pour obtenir un token d'authentification"""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "user123!"
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def test_image(self):
        """Fixture pour créer une image de test"""
        # Création d'une image RGB de test
        img_array = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # Conversion en bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes
    
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

class TestAdmin:
    """Tests des fonctionnalités d'administration"""
    
    @pytest.fixture
    def admin_token(self):
        """Fixture pour obtenir un token admin"""
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123!"
        })
        return response.json()["access_token"]
    
    @pytest.fixture
    def user_token(self):
        """Fixture pour obtenir un token utilisateur"""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "user123!"
        })
        return response.json()["access_token"]
    
    def test_admin_stats_success(self, admin_token):
        """Test de récupération des statistiques admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "predictions" in data
        assert "predictions_today" in data
        assert "top_categories" in data
        assert "system_info" in data
    
    def test_admin_stats_forbidden_for_user(self, user_token):
        """Test que les stats admin sont interdites aux utilisateurs"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = client.get("/admin/stats", headers=headers)
        assert response.status_code == 403
    
    def test_admin_users_list(self, admin_token):
        """Test de liste des utilisateurs par admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) >= 2  # au moins admin et testuser

class TestRateLimit:
    """Tests de rate limiting"""
    
    def test_rate_limit_headers(self):
        """Test de la présence des headers de rate limiting"""
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123!"
        })
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

class TestValidation:
    """Tests de validation des données"""
    
    def test_login_missing_fields(self):
        """Test de connexion avec champs manquants"""
        response = client.post("/auth/login", json={
            "username": "admin"
            # password manquant
        })
        assert response.status_code == 422
    
    def test_register_invalid_email(self):
        """Test d'inscription avec email invalide"""
        response = client.post("/auth/register", json={
            "username": "testuser2",
            "email": "invalid-email",
            "password": "password123!"
        })
        assert response.status_code == 422
    
    def test_register_weak_password(self):
        """Test d'inscription avec mot de passe faible"""
        response = client.post("/auth/register", json={
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "123"  # Trop court
        })
        assert response.status_code == 422

class TestSecurity:
    """Tests de sécurité"""
    
    def test_security_headers(self):
        """Test de la présence des headers de sécurité"""
        response = client.get("/")
        
        # Vérification des headers de sécurité
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]
        
        for header in security_headers:
            assert header in response.headers
    
    def test_unauthorized_access_protected_endpoint(self):
        """Test d'accès non autorisé aux endpoints protégés"""
        response = client.get("/predict/history")
        assert response.status_code == 401
        
        response = client.get("/admin/stats")
        assert response.status_code == 401 