import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

#client = TestClient(app)
@pytest.fixture
def client():
    """Fixture pour le client de test"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def admin_token(client):
    """Fixture pour obtenir un token admin"""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123!"
    })
    return response.json()["access_token"]
    
@pytest.fixture
def user_token(client):
    """Fixture pour obtenir un token utilisateur"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "user123!"
    })
    return response.json()["access_token"]


class TestAdmin:
    """Tests des fonctionnalités d'administration"""    

    def test_admin_stats_success(self,client, admin_token):
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
    
    def test_admin_stats_forbidden_for_user(self,client, user_token):
        """Test que les stats admin sont interdites aux utilisateurs"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = client.get("/admin/stats", headers=headers)
        assert response.status_code == 403
    
    def test_admin_users_list(self, client, admin_token):
        """Test de liste des utilisateurs par admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) >= 2  # au moins admin et testuser