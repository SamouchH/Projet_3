import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)

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