# logo_detection_improved.py
import cv2
import numpy as np

def detect_logo_orb(cover_path, logos, min_match_count=10, ratio_threshold=0.75):
    """
    Utilise ORB pour détecter les logos dans une image de couverture.
    Pour chaque logo, on détecte les caractéristiques, on effectue des correspondances via BFMatcher,
    applique le ratio test de Lowe et compte les bons matches.
    
    Args:
        cover_path (str): Chemin vers l'image de couverture.
        logos (dict): Dictionnaire {label: logo_image} des logos préchargés (normalisés).
        min_match_count (int): Nombre minimum de bons matches pour considérer le logo comme détecté.
        ratio_threshold (float): Seuil pour le ratio test de Lowe.
    
    Returns:
        dict: Dictionnaire {logo_label: nombre_de_bons_matches} pour les logos détectés.
    """
    cover_img = cv2.imread(cover_path, cv2.IMREAD_GRAYSCALE)
    if cover_img is None:
        print(f"Erreur de chargement de {cover_path}")
        return {}
    
    # Créer l'objet ORB
    orb = cv2.ORB_create()
    kp_cover, des_cover = orb.detectAndCompute(cover_img, None)
    if des_cover is None:
        return {}
    
    detections = {}
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    
    for label, logo_img in logos.items():
        kp_logo, des_logo = orb.detectAndCompute(logo_img, None)
        if des_logo is None:
            continue
        
        matches = bf.knnMatch(des_logo, des_cover, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < ratio_threshold * n.distance:
                good_matches.append(m)
        if len(good_matches) >= min_match_count:
            detections[label] = len(good_matches)
    
    return detections
