import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)

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
