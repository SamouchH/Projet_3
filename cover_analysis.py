# cover_analysis.py
import os
import cv2
from logo_loader import load_logos
from improved_logo_detection import detect_logo_in_cover

def analyze_game_covers(cover_folder, logo_folder, ratio_test=0.75, min_match_count=10, nfeatures_orb=3000):
    """
    Analyse toutes les couvertures de jeux pour détecter la présence de logos.
    Pour les logos problématiques ("nintendo_wii" et "nintendo_wiiu"), on impose un seuil plus sévère.
    """
    logos = load_logos(logo_folder, target_size=(200,200))
    results = {}
    # Seuils personnalisés pour logos problématiques
    custom_thresholds = {"nintendo_wii": 20, "nintendo_wiiu": 20}
    
    for file in os.listdir(cover_folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            cover_path = os.path.join(cover_folder, file)
            cover_img = cv2.imread(cover_path)
            if cover_img is None:
                continue
            detections = {}
            for logo_label, logo_img in logos.items():
                custom_min = custom_thresholds.get(logo_label, None)
                found, corners = detect_logo_in_cover(cover_img, logo_img, ratio_test, min_match_count, nfeatures_orb, custom_min_match=custom_min)
                if found:
                    detections[logo_label] = corners.tolist()  # Conserver les coins détectés
            results[file] = detections
    return results
