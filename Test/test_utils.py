import pytest
from Streamlit.utils import get_logo_path, get_labeling_dir, predict
import numpy as np

def test_get_logo_path():
    assert get_logo_path("PlayStation") == "logos/PlayStation.png"

def test_get_labeling_dir():
    path = get_labeling_dir()
    assert path.endswith("Labeller")

def test_predict():
    # Création d’un modèle mock
    class MockModel:
        def predict(self, image):
            return np.array([[0.1, 0.2, 0.6, 0.1]])  # max index = 2
        

    image_array = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
    prediction = predict(MockModel(), image_array)
    assert prediction == "Nintendo"