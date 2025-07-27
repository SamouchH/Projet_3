import requests
import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)
BASE_URL = "http://api:8080"

def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")
    print(">>> Status Code:", response.status_code)
    print(">>> Response text:", response.text)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

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
