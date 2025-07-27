import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)

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