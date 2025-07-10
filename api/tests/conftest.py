import pytest
import asyncio
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path

# Configuration pour les tests asynchrones
@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour créer un event loop pour toute la session de test"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def temp_model_file():
    """Fixture pour créer un fichier modèle temporaire pour les tests"""
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        # Créer un faux fichier modèle (juste pour les tests)
        f.write(b"fake model content for testing")
        temp_path = f.name
    
    # Copier vers l'emplacement attendu par l'API
    model_path = Path("api/modele_cnn_transfer.h5")
    model_path.parent.mkdir(exist_ok=True)
    
    if not model_path.exists():
        with open(model_path, "wb") as f:
            f.write(b"fake model content for testing")
    
    yield temp_path
    
    # Nettoyage
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(temp_model_file):
    """Fixture pour configurer l'environnement de test"""
    # Configuration des variables d'environnement pour les tests
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./test_projet3_api.db"
    os.environ["LOG_LEVEL"] = "WARNING"  # Réduire les logs pendant les tests
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    
    # Créer les répertoires nécessaires
    test_dirs = ["api/logs", "api/uploads", "api/predictions", "api/data"]
    for directory in test_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Nettoyage après les tests
    test_db_path = Path("./test_projet3_api.db")
    if test_db_path.exists():
        test_db_path.unlink()

@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI"""
    from api.main import app
    return TestClient(app) 