import cv2
import os
from pathlib import Path

# Chemins vers les dossiers
logos_folder = Path('logos_folder')
images_folder = Path('images_folder')

# Initialiser SIFT et FLANN
sift = cv2.SIFT_create()
FLANN_INDEX_KDTREE = 1
flann = cv2.FlannBasedMatcher(
    dict(algorithm=FLANN_INDEX_KDTREE, trees=5), 
    dict(checks=50)
)

# Charger et préparer les descripteurs des logos
logos_descriptors = {}
for logo_file in logos_folder.glob('*.jpg'):
    logo_img = cv2.imread(str(logo_file), cv2.IMREAD_GRAYSCALE)
    kp_logo, des_logo = sift.detectAndCompute(logo_img, None)
    if des_logo is not None:
        logos_descriptors[logo_file.stem] = (kp_logo, des_logo)
    else:
        print(f"⚠️  Pas de descripteurs pour {logo_file}")

# Fonction pour matcher un logo sur une image
def match_logo(img_des, logo_des, threshold=10):
    matches = flann.knnMatch(logo_des, img_des, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
    return len(good_matches) >= threshold, len(good_matches)

# Parcourir toutes les images du dossier
for image_file in images_folder.glob('*.jpg'):
    img = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)
    kp_img, des_img = sift.detectAndCompute(img, None)
    
    if des_img is None:
        print(f"⚠️  Aucun descripteur trouvé dans {image_file.name}")
        continue

    print(f"\n🔍 Image : {image_file.name}")

    found_any_logo = False
    # Comparer avec chaque logo
    for logo_name, (kp_logo, des_logo) in logos_descriptors.items():
        match, good_count = match_logo(des_img, des_logo)

        if match:
            found_any_logo = True
            print(f"Logo détecté : {logo_name} (Correspondances : {good_count})")

    if not found_any_logo:
        print(" Aucun logo trouvé dans cette image.")
