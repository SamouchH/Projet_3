# logo_loader.py
import cv2
import os
import numpy as np

def load_logos(logo_folder, target_size=(200, 200)):
    """
    Charge les images de logo depuis un dossier, gère la transparence et les redimensionne à une taille cible.
    
    Args:
        logo_folder (str): Chemin du dossier contenant les logos.
        target_size (tuple): Taille cible (largeur, hauteur).
    
    Returns:
        dict: Dictionnaire {label: image_grayscale} où le label est extrait du nom de fichier.
    """
    logos = {}
    for file in os.listdir(logo_folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            label = os.path.splitext(file)[0].lower()
            path = os.path.join(logo_folder, file)
            # Charger en préservant le canal alpha s'il existe
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # Si l'image possède 4 canaux (RGBA), convertir les zones transparentes en blanc
                if len(img.shape) == 3 and img.shape[2] == 4:
                    b, g, r, a = cv2.split(img)
                    alpha = a / 255.0
                    # Créer un fond blanc
                    white = np.ones_like(b, dtype=np.uint8) * 255
                    b = np.uint8(b * alpha + white * (1 - alpha))
                    g = np.uint8(g * alpha + white * (1 - alpha))
                    r = np.uint8(r * alpha + white * (1 - alpha))
                    img = cv2.merge([b, g, r])
                # Si l'image est déjà sans alpha, rien à faire
                # Convertir en niveaux de gris et redimensionner
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
                logos[label] = resized
            else:
                print(f"Erreur lors du chargement du logo: {path}")
    return logos
