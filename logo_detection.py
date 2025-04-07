# logo_detection.py
import cv2
import numpy as np

def detect_logo_in_image(game_cover, logos, threshold=0.7):
    """
    Détecte si un ou plusieurs logos sont présents dans une image de couverture de jeu.
    
    Args:
        game_cover (np.array): Image de couverture (niveaux de gris).
        logos (dict): Dictionnaire {label: logo_image} des logos chargés.
        threshold (float): Seuil de correspondance (entre 0 et 1).
        
    Returns:
        dict: Dictionnaire {label: score_max} pour les logos dont le score dépasse le seuil.
    """
    detections = {}
    for label, template in logos.items():
        # Appliquer le template matching
        res = cv2.matchTemplate(game_cover, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            detections[label] = max_val
    return detections

def detect_logos_in_game_cover(cover_path, logos, threshold=0.7):
    """
    Charge une image de couverture et détecte les logos présents.
    
    Args:
        cover_path (str): Chemin vers l'image de couverture.
        logos (dict): Dictionnaire des logos chargés.
        threshold (float): Seuil de détection.
    
    Returns:
        dict: Dictionnaire des détections.
    """
    image = cv2.imread(cover_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Erreur lors du chargement de l'image: {cover_path}")
        return {}
    return detect_logo_in_image(image, logos, threshold)
