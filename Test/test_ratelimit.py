import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)

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