# improved_logo_detection.py
import cv2
import numpy as np

def preprocess_image(img, desired_width=600, desired_height=600, use_clahe=True):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    resized = cv2.resize(gray, (desired_width, desired_height), interpolation=cv2.INTER_AREA)
    if use_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        processed = clahe.apply(resized)
    else:
        processed = resized
    return processed

def detect_logo_in_cover(cover_img, logo_img, ratio_test=0.75, min_match_count=10, nfeatures_orb=3000, custom_min_match=None):
    """
    Détecte la présence d'un logo dans une image de couverture.
    Si custom_min_match est fourni, il remplace le seuil par défaut.
    """
    cover_prep = preprocess_image(cover_img, desired_width=600, desired_height=600, use_clahe=True)
    logo_prep  = preprocess_image(logo_img, desired_width=200, desired_height=200, use_clahe=True)
    
    orb = cv2.ORB_create(nfeatures=nfeatures_orb)
    kp_logo, des_logo = orb.detectAndCompute(logo_prep, None)
    kp_cover, des_cover = orb.detectAndCompute(cover_prep, None)
    
    if des_logo is None or des_cover is None or len(des_logo)==0 or len(des_cover)==0:
        return False, None
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des_logo, des_cover, k=2)
    
    good_matches = []
    for m, n in matches:
        if m.distance < ratio_test * n.distance:
            good_matches.append(m)
    
    # Utiliser custom_min_match s'il est défini
    required_matches = custom_min_match if custom_min_match is not None else min_match_count
    
    if len(good_matches) > required_matches:
        src_pts = np.float32([kp_logo[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
        dst_pts = np.float32([kp_cover[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is not None:
            h, w = logo_prep.shape
            corners = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
            transformed_corners = cv2.perspectiveTransform(corners, M)
            return True, transformed_corners
    return False, None
